#!/usr/bin/env python3
"""Build Sub #4 by judging Sub #1 vs Sub #2 disagreements with GPT-5.2 vision."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from typing import Any

from openai import OpenAI


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annotations", required=True)
    p.add_argument("--sub1", required=True)
    p.add_argument("--sub2", required=True)
    p.add_argument("--entries2", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--model", default="gpt-5.2")
    p.add_argument("--full-frames", type=int, default=6)
    p.add_argument("--foi-frames", type=int, default=6)
    p.add_argument("--image-detail", default="low", choices=["low", "auto", "high"])
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--max-output-tokens", type=int, default=512)
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def load_submission(path: str) -> dict[str, str]:
    return {str(r["question_id"]): normalize_answer(r["answer_choice"]) for r in load_json(path)}


def load_entries(path: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for entry in load_json(path):
        metadata = entry.get("metadata", {})
        qid = str(metadata.get("question_id") or entry.get("question_id") or metadata.get("id"))
        out[qid] = entry
    return out


def normalize_answer(value: Any) -> str:
    text = str(value).strip()
    low = text.lower()
    if low in {"yes", "y", "true"}:
        return "Yes"
    if low in {"no", "n", "false"}:
        return "No"
    if len(text) == 1:
        return text.upper()
    return text


def valid_answer(answer: str, mode: str) -> bool:
    if mode == "mc":
        return answer in {"A", "B", "C", "D"}
    if mode == "bool":
        return answer in {"Yes", "No"}
    return False


def valid_foi(foi: Any) -> bool:
    return isinstance(foi, list) and len(foi) >= 2 and foi[0] != -1 and foi[1] != -1 and foi[1] >= foi[0]


def parse_judge(raw: str | None) -> str | None:
    if not raw:
        return None
    text = raw.strip().upper()
    for token in ("SUB1", "SUB 1", "ANSWER1", "ANSWER 1", "CANDIDATE1", "CANDIDATE 1"):
        if token in text:
            return "sub1"
    for token in ("SUB2", "SUB 2", "ANSWER2", "ANSWER 2", "CANDIDATE2", "CANDIDATE 2"):
        if token in text:
            return "sub2"
    if text in {"1", "A"}:
        return "sub1"
    if text in {"2", "B"}:
        return "sub2"
    return None


def build_candidate_text(entry: dict[str, Any], ans1: str, ans2: str) -> str:
    metadata = entry.get("metadata", {})
    mode = metadata.get("mode", "unknown")
    question = metadata.get("cleaned_question") or entry.get("question", "")
    candidates = entry.get("candidates") or []
    foi = entry.get("frames_of_interest")
    nsvs = entry.get("nsvs", {}).get("output")
    target = entry.get("target_identification", {}).get("frame_window")
    puls = entry.get("puls", {})
    candidate_block = ""
    if mode == "mc":
        letters = ["A", "B", "C", "D"]
        candidate_block = "\nOptions:\n" + "\n".join(
            f"{letter}: {candidate}" for letter, candidate in zip(letters, candidates)
        )
    return (
        "Decide which candidate answer is correct for this TimeLogic video QA item.\n"
        "Use the full-video frames for global context and the NSVS interval frames for the retrieved temporal evidence.\n"
        "Return exactly one token: SUB1 or SUB2. Do not explain.\n\n"
        f"Question: {question}\n"
        f"Mode: {mode}\n"
        f"{candidate_block}\n\n"
        f"SUB1 answer from full-video baseline: {ans1}\n"
        f"SUB2 answer from NSVS interval pipeline: {ans2}\n\n"
        f"NSVS raw interval frames: {nsvs}\n"
        f"Sub #2 frames_of_interest after target_identification padding: {foi}\n"
        f"target_identification temporal extension template: {target}\n"
        f"Atomic propositions: {puls.get('proposition')}\n"
        f"Temporal logic spec: {puls.get('specification')}\n\n"
        "Which answer is correct? Reply exactly SUB1 or SUB2."
    )


def judge_one(
    client: OpenAI,
    model: str,
    entry: dict[str, Any],
    ans1: str,
    ans2: str,
    full_frames: int,
    foi_frames: int,
    image_detail: str,
    max_output_tokens: int,
) -> dict[str, Any]:
    from nsvqa.vqa.answer_timelogic import (
        _build_completion_kwargs,
        encode_jpeg,
        sample_frames,
    )

    video_path = entry["paths"]["video_path"]
    if not os.path.isfile(video_path):
        return {"choice": "sub1", "raw": None, "error": "video_missing", "num_images": 0}

    full = sample_frames(video_path, full_frames, None)
    foi_range = entry.get("frames_of_interest") if valid_foi(entry.get("frames_of_interest")) else None
    foi = sample_frames(video_path, foi_frames, foi_range)

    content: list[dict[str, Any]] = [{"type": "text", "text": "Full-video frames, sampled in temporal order:"}]
    num_images = 0
    for frame in full:
        encoded = encode_jpeg(frame)
        if encoded:
            num_images += 1
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": image_detail},
            })

    content.append({"type": "text", "text": "NSVS frames_of_interest frames, sampled in temporal order:"})
    for frame in foi:
        encoded = encode_jpeg(frame)
        if encoded:
            num_images += 1
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": image_detail},
            })

    content.append({"type": "text", "text": build_candidate_text(entry, ans1, ans2)})
    kwargs = _build_completion_kwargs(model, max_output_tokens=max_output_tokens)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict visual judge for temporal video QA. "
                    "Choose the answer that best matches the video evidence. "
                    "Reply with exactly SUB1 or SUB2."
                ),
            },
            {"role": "user", "content": content},
        ],
        store=False,
        **kwargs,
    )
    raw = resp.choices[0].message.content
    choice = parse_judge(raw)
    if choice not in {"sub1", "sub2"}:
        choice = "sub1"
        error = f"unparseable_judge_response:{raw!r}"
    else:
        error = None
    return {"choice": choice, "raw": raw, "error": error, "num_images": num_images}


def write_outputs(output_dir: str, submission: list[dict[str, str]], diag: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    with open(os.path.join(output_dir, "submission_sub4_tiebreak_gpt52.json"), "w") as f:
        json.dump(submission, f, indent=2)
    with open(os.path.join(output_dir, "judge_diag.json"), "w") as f:
        json.dump(diag, f, indent=2)
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> int:
    args = parse_args()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from nsvqa.utils.env_loader import load_env_file

    os.makedirs(args.output_dir, exist_ok=True)
    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(f"OPENAI_API_KEY not set and not found in {args.env_file}")

    annotations = load_json(args.annotations)
    sub1 = load_submission(args.sub1)
    sub2 = load_submission(args.sub2)
    entries2 = load_entries(args.entries2)
    client = OpenAI()

    print("[sub4] GPT-5.2 tiebreaker ensemble")
    print(f"[sub4] output_dir={args.output_dir}")
    print(f"[sub4] model={args.model} full_frames={args.full_frames} foi_frames={args.foi_frames} detail={args.image_detail}")
    print("[sub4] Design: copy agreements; judge only Sub #1 vs Sub #2 disagreements.")

    submission: list[dict[str, str]] = []
    diag: list[dict[str, Any]] = []
    counts: Counter = Counter()
    t0 = time.time()

    for i, ann in enumerate(annotations, start=1):
        qid = str(ann["question_id"])
        mode = ann["mode"]
        ans1 = sub1.get(qid)
        ans2 = sub2.get(qid)
        entry = entries2.get(qid)
        if not ans1 or not valid_answer(ans1, mode):
            ans1 = "A" if mode == "mc" else "Yes"
        if not ans2 or not valid_answer(ans2, mode):
            ans2 = ans1

        if ans1 == ans2:
            answer = ans1
            record = {"qid": qid, "mode": mode, "route": "agreement", "answer": answer}
            counts["agreement"] += 1
        elif not entry:
            answer = ans1
            record = {"qid": qid, "mode": mode, "route": "fallback_sub1_missing_entry", "answer": answer}
            counts["fallback_sub1_missing_entry"] += 1
        else:
            for attempt in range(3):
                try:
                    judged = judge_one(
                        client,
                        args.model,
                        entry,
                        ans1,
                        ans2,
                        args.full_frames,
                        args.foi_frames,
                        args.image_detail,
                        args.max_output_tokens,
                    )
                    break
                except Exception as exc:  # noqa: BLE001 - log and retry API/transport issues.
                    judged = {"choice": "sub1", "raw": None, "error": repr(exc), "num_images": 0}
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            answer = ans2 if judged["choice"] == "sub2" else ans1
            record = {
                "qid": qid,
                "mode": mode,
                "route": f"judge_{judged['choice']}",
                "answer": answer,
                "sub1_answer": ans1,
                "sub2_answer": ans2,
                **judged,
            }
            counts[record["route"]] += 1
            if judged.get("error"):
                counts["judge_errors"] += 1

        submission.append({"question_id": qid, "answer_choice": answer})
        diag.append(record)

        if i % 25 == 0 or i == len(annotations):
            summary = {
                "n": len(submission),
                "counts": dict(counts),
                "elapsed_seconds": round(time.time() - t0, 2),
                "model": args.model,
                "full_frames": args.full_frames,
                "foi_frames": args.foi_frames,
                "image_detail": args.image_detail,
            }
            write_outputs(args.output_dir, submission, diag, summary)
            print(f"[sub4] checkpoint {i}/{len(annotations)} counts={dict(counts)} elapsed={summary['elapsed_seconds']}s", flush=True)

    final_summary = {
        "n": len(submission),
        "counts": dict(counts),
        "elapsed_seconds": round(time.time() - t0, 2),
        "model": args.model,
        "full_frames": args.full_frames,
        "foi_frames": args.foi_frames,
        "image_detail": args.image_detail,
        "output": os.path.join(args.output_dir, "submission_sub4_tiebreak_gpt52.json"),
    }
    write_outputs(args.output_dir, submission, diag, final_summary)
    with open(os.path.join(args.output_dir, "DONE"), "w") as f:
        f.write(json.dumps(final_summary, indent=2) + "\n")
    print(f"[sub4] DONE {json.dumps(final_summary)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
