#!/usr/bin/env python3
"""Answer TimeLogic entries with a local OpenAI-compatible vision VLM."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from openai import OpenAI


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", required=True, help="postprocess_entries.json with paths.cropped_path")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--model", default="Qwen/Qwen2.5-VL-7B-Instruct")
    p.add_argument("--api-base", default="http://localhost:8000/v1")
    p.add_argument("--api-key", default="EMPTY")
    p.add_argument("--num-frames", type=int, default=16)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--sleep-seconds", type=float, default=0.0)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def encode_frame(frame: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    if not ok:
        raise ValueError("Could not encode frame")
    return base64.b64encode(buffer).decode("utf-8")


def sample_frames(video_path: str, num_frames: int) -> list[np.ndarray]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if frame_count <= 0:
        cap.release()
        return []
    if frame_count <= num_frames:
        indices = np.arange(frame_count, dtype=int)
    else:
        indices = np.linspace(0, frame_count - 1, num_frames, dtype=int)

    frames: list[np.ndarray] = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame_bgr = cap.read()
        if ok and frame_bgr is not None:
            frames.append(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    cap.release()
    return frames


def normalize_answer(raw: str | None, mode: str) -> tuple[str, str | None]:
    text = (raw or "").strip()
    upper = text.upper()
    if mode == "mc":
        match = re.search(r"\b([ABCD])\b", upper)
        if match:
            return match.group(1), None
        match = re.search(r"\b([1-4])\b", text)
        if match:
            return "ABCD"[int(match.group(1)) - 1], None
        return "A", f"unparseable_mc:{text!r}"

    low = text.lower()
    if re.search(r"\byes\b", low):
        return "Yes", None
    if re.search(r"\bno\b", low):
        return "No", None
    return "Yes", f"unparseable_bool:{text!r}"


def prompt_for(entry: dict[str, Any]) -> str:
    mode = entry.get("metadata", {}).get("mode", "mc")
    question = entry.get("question", "")
    candidates = entry.get("candidates", [])
    if mode == "mc":
        lines = [
            "Answer the multiple-choice video question using only the provided video frames.",
            "Return exactly one uppercase letter: A, B, C, or D.",
            "",
            f"Question: {question}",
            "",
            "Options:",
        ]
        for letter, candidate in zip("ABCD", candidates):
            lines.append(f"{letter}. {candidate}")
        return "\n".join(lines)

    return "\n".join(
        [
            "Answer the yes/no video question using only the provided video frames.",
            "Return exactly one word: Yes or No.",
            "",
            f"Question: {question}",
        ]
    )


def answer_one(client: OpenAI, args: argparse.Namespace, entry: dict[str, Any]) -> dict[str, Any]:
    metadata = entry.get("metadata", {})
    qid = str(metadata.get("question_id") or entry.get("question_id"))
    mode = metadata.get("mode", "mc")
    video_path = entry.get("paths", {}).get("cropped_path") or entry.get("paths", {}).get("video_path")
    frames = sample_frames(video_path, args.num_frames) if video_path else []
    if not frames:
        default = "A" if mode == "mc" else "Yes"
        return {
            "question_id": qid,
            "answer_choice": default,
            "mode": mode,
            "video_path": video_path,
            "num_frames": 0,
            "raw": None,
            "error": "no_frames_sampled",
        }

    content: list[dict[str, Any]] = [
        {"type": "text", "text": "The following images are sampled uniformly from the cropped video clip."}
    ]
    for frame in frames:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encode_frame(frame)}"},
            }
        )
    content.append({"type": "text", "text": prompt_for(entry)})

    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": content}],
        max_tokens=8,
        temperature=0.0,
    )
    raw = resp.choices[0].message.content
    answer, parse_error = normalize_answer(raw, mode)
    return {
        "question_id": qid,
        "answer_choice": answer,
        "mode": mode,
        "video_path": video_path,
        "num_frames": len(frames),
        "raw": raw,
        "error": parse_error,
    }


def load_completed(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)
    return {str(row["question_id"]): row for row in rows}


def write_outputs(output_dir: Path, diag: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "answers_diag.json").open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    with (output_dir / "submission_partial.json").open("w", encoding="utf-8") as f:
        json.dump(
            [{"question_id": row["question_id"], "answer_choice": row["answer_choice"]} for row in diag],
            f,
            indent=2,
        )
    with (output_dir / "answers_diag.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["question_id", "answer_choice", "mode", "video_path", "num_frames", "raw", "error"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in diag:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_json(args.entries)
    if args.limit is not None:
        entries = entries[: args.limit]
    completed = {} if args.overwrite else load_completed(output_dir / "answers_diag.json")

    client = OpenAI(api_key=args.api_key, base_url=args.api_base)
    diag: list[dict[str, Any]] = []
    for idx, entry in enumerate(entries, start=1):
        qid = str(entry.get("metadata", {}).get("question_id") or entry.get("question_id"))
        if qid in completed:
            result = completed[qid]
        else:
            try:
                result = answer_one(client, args, entry)
            except Exception as exc:  # noqa: BLE001 - checkpoint and keep moving.
                mode = entry.get("metadata", {}).get("mode", "mc")
                result = {
                    "question_id": qid,
                    "answer_choice": "A" if mode == "mc" else "Yes",
                    "mode": mode,
                    "video_path": entry.get("paths", {}).get("cropped_path"),
                    "num_frames": 0,
                    "raw": None,
                    "error": repr(exc),
                }
            completed[qid] = result
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)
        diag.append(result)
        if idx % 10 == 0 or result.get("error"):
            write_outputs(output_dir, list(completed.values()))
            print(f"[vqa-local] {idx}/{len(entries)} qid={qid} ans={result['answer_choice']} err={result.get('error')}")

    write_outputs(output_dir, list(completed.values()))
    print(f"[vqa-local] wrote {output_dir / 'submission_partial.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
