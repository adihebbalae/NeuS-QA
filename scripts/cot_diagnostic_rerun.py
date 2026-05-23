#!/usr/bin/env python3
"""Re-run downstream VQA with a chain-of-thought prompt on failure-audit rows.

Uses the same cropped-clip source, frame budget, model, and image detail as Sub #5B
(`answer_cropped_entries.py` → gpt-5.2, 16 frames, low detail, full cropped clip).
Each audit row is answered twice so we can measure self-agreement and agreement
with the stored Sub #5B answer.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SELECTED_CSV = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v2" / "selected_rows.csv"
DEFAULT_OUT_DIR = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3"
DEFAULT_POSTPROCESS = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/postprocess/postprocess_entries.json"
)
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_NUM_FRAMES = 16
DEFAULT_IMAGE_DETAIL = "low"
DEFAULT_RUNS = 2
DEFAULT_TEMPERATURE = 0.0
SUB5B_ANSWER_COL = "sub5b_paper_faithful_fix2_answer"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--selected-csv", type=Path, default=DEFAULT_SELECTED_CSV)
    p.add_argument(
        "--postprocess-entries",
        type=Path,
        default=DEFAULT_POSTPROCESS,
        help="Sub #5B postprocess_entries.json (provides paths.cropped_path)",
    )
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--num-frames", type=int, default=DEFAULT_NUM_FRAMES)
    p.add_argument("--image-detail", default=DEFAULT_IMAGE_DETAIL, choices=["low", "auto", "high"])
    p.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--limit", type=int, default=None, help="Process only the first N audit rows")
    p.add_argument("--quiet", action="store_true")
    return p.parse_args()


def load_env_file(path: str) -> None:
    from nsvqa.utils.env_loader import load_env_file as _load

    _load(path)


def qid_from_entry(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    return str(metadata.get("question_id") or entry.get("question_id"))


def load_selected_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def index_entries(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        entries = json.load(f)
    return {qid_from_entry(entry): entry for entry in entries}


def prepare_sub5b_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Match `answer_cropped_entries.prepare_entries`: cropped clip, no FOI re-window."""
    prepared = copy.deepcopy(entry)
    cropped = prepared.get("paths", {}).get("cropped_path")
    if cropped:
        prepared["paths"]["video_path"] = cropped
    prepared["frames_of_interest"] = None
    return prepared


def sample_frames_with_indices(
    video_path: str,
    num_frames: int,
    frame_range: list | None = None,
) -> tuple[list[Any], list[int]]:
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total == 0:
        cap.release()
        return [], []

    if frame_range and frame_range != [-1] and len(frame_range) == 2:
        start, end = int(frame_range[0]), int(frame_range[1])
    else:
        start, end = 0, total - 1
    start = max(0, start)
    end = min(total - 1, end)
    if end <= start:
        start, end = 0, total - 1

    if (end - start + 1) <= num_frames:
        idxs = list(range(start, end + 1))
    else:
        idxs = np.linspace(start, end, num_frames, dtype=int).tolist()

    frames: list[Any] = []
    used_idxs: list[int] = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok and frame is not None:
            frames.append(frame)
            used_idxs.append(int(idx))
    cap.release()
    return frames, used_idxs


def build_cot_prompt(
    question: str,
    candidates: list[str],
    mode: str,
    num_images: int,
    puls_hint: str = "",
) -> tuple[str, str, list[str]]:
    frame_ref = (
        f"The {num_images} images above are temporally ordered. "
        f"Refer to them as Frame 1 through Frame {num_images} (Frame 1 is earliest)."
    )
    common_tail = (
        "\n\nThink step-by-step about what the frames show. "
        "Cite which frame numbers support your answer. "
        "Then on the final line write exactly one of:\n"
    )

    if mode == "mc":
        letters = ["A", "B", "C", "D"]
        formatted = "\n".join(f"{letter}: {candidate}" for letter, candidate in zip(letters, candidates))
        sys_p = (
            "You are a careful video-understanding assistant for a temporal-reasoning "
            "benchmark (CVPR 2026 TimeLogic). Reason step-by-step from the provided "
            "frames before giving a final multiple-choice answer."
        )
        user_t = (
            f"{frame_ref}\n\n"
            f"Question: {question}\n"
            f"{puls_hint}\n"
            f"Options:\n{formatted}"
            f"{common_tail}"
            "ANSWER: A\nANSWER: B\nANSWER: C\nANSWER: D"
        )
        return sys_p, user_t, letters

    if mode == "bool":
        sys_p = (
            "You are a careful video-understanding assistant for a temporal-reasoning "
            "benchmark (CVPR 2026 TimeLogic). Reason step-by-step from the provided "
            "frames before giving a final Yes/No answer."
        )
        user_t = (
            f"{frame_ref}\n\n"
            f"Question: {question}\n"
            f"{puls_hint}"
            f"{common_tail}"
            "ANSWER: Yes\nANSWER: No"
        )
        return sys_p, user_t, ["Yes", "No"]

    raise ValueError(f"unknown mode {mode!r}")


def parse_cot_answer(raw: str | None, valid_answers: list[str]) -> str:
    from nsvqa.vqa.answer_timelogic import parse_answer

    text = raw or ""
    match = re.search(r"ANSWER:\s*(\S+)", text, flags=re.IGNORECASE)
    if match:
        return parse_answer(match.group(1), valid_answers)
    return parse_answer(text, valid_answers)


def build_cot_completion_kwargs(model: str, temperature: float) -> dict[str, Any]:
    from nsvqa.vqa.answer_timelogic import _is_reasoning_model

    if _is_reasoning_model(model):
        return {
            "max_completion_tokens": 2048,
            "reasoning_effort": "low",
        }
    return {
        "max_tokens": 1024,
        "temperature": temperature,
    }


def answer_one_cot(
    client: OpenAI,
    model: str,
    entry: dict[str, Any],
    *,
    num_frames: int,
    image_detail: str,
    temperature: float,
) -> dict[str, Any]:
    from nsvqa.vqa.answer_timelogic import encode_jpeg, format_puls_hint

    metadata = entry.get("metadata", {})
    mode = metadata.get("mode")
    video_path = entry.get("paths", {}).get("video_path", "")
    question = metadata.get("cleaned_question") or entry.get("question", "")
    candidates = entry.get("candidates") or []
    foi = entry.get("frames_of_interest")

    default_answer = "A" if mode == "mc" else "Yes"
    if not metadata.get("video_present", True) or not video_path or not os.path.isfile(video_path):
        return {
            "answer": default_answer,
            "reasoning": "",
            "raw": None,
            "error": "video_missing_on_disk",
            "sampled_frame_indices": [],
            "num_frames": 0,
            "video_path": video_path,
        }

    frames, frame_indices = sample_frames_with_indices(video_path, num_frames, foi)
    if not frames:
        return {
            "answer": default_answer,
            "reasoning": "",
            "raw": None,
            "error": "no_frames_sampled",
            "sampled_frame_indices": [],
            "num_frames": 0,
            "video_path": video_path,
        }

    encoded = [encode_jpeg(frame) for frame in frames]
    encoded = [item for item in encoded if item]
    if not encoded:
        return {
            "answer": default_answer,
            "reasoning": "",
            "raw": None,
            "error": "all_frames_encoding_failed",
            "sampled_frame_indices": frame_indices,
            "num_frames": 0,
            "video_path": video_path,
        }

    puls_data = entry.get("puls") or {}
    puls_hint = format_puls_hint(
        puls_data.get("proposition"),
        puls_data.get("specification"),
    )
    sys_p, user_t, valid_answers = build_cot_prompt(
        question,
        candidates,
        mode,
        len(encoded),
        puls_hint=puls_hint,
    )

    user_content: list[dict[str, Any]] = []
    for blob in encoded:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{blob}", "detail": image_detail},
            }
        )
    user_content.append({"type": "text", "text": user_t})

    completion_kwargs = build_cot_completion_kwargs(model, temperature)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_p},
            {"role": "user", "content": user_content},
        ],
        store=False,
        **completion_kwargs,
    )
    message = resp.choices[0].message
    raw = message.content
    hidden_reasoning = getattr(message, "reasoning", None)
    reasoning_parts = [part for part in (hidden_reasoning, raw) if part]
    reasoning = "\n\n".join(str(part) for part in reasoning_parts)
    answer = parse_cot_answer(raw, valid_answers)
    return {
        "answer": answer,
        "reasoning": reasoning,
        "raw": raw,
        "hidden_reasoning": hidden_reasoning,
        "sampled_frame_indices": frame_indices[: len(encoded)],
        "num_frames": len(encoded),
        "video_path": video_path,
        "finish_reason": getattr(resp.choices[0], "finish_reason", None),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    self_agree = sum(1 for row in rows if row.get("self_agreement"))
    sub5b_both = sum(1 for row in rows if row.get("agrees_with_sub5b_both"))
    sub5b_any = sum(1 for row in rows if row.get("agrees_with_sub5b_any"))
    run1_sub5b = sum(1 for row in rows if row.get("agrees_with_sub5b_run1"))
    run2_sub5b = sum(1 for row in rows if row.get("agrees_with_sub5b_run2"))
    errors = sum(1 for row in rows if any(run.get("error") for run in row.get("runs", [])))

    answer_pairs = Counter(
        (row.get("sub5b_answer"), row["runs"][0]["answer"] if row.get("runs") else None)
        for row in rows
        if row.get("runs")
    )
    cot_run1 = Counter(row["runs"][0]["answer"] for row in rows if row.get("runs"))
    sub5b_answers = Counter(row.get("sub5b_answer") for row in rows)

    return {
        "rows": n,
        "errors": errors,
        "self_agreement_count": self_agree,
        "self_agreement_rate": round(self_agree / n, 3) if n else 0.0,
        "agrees_with_sub5b_run1_count": run1_sub5b,
        "agrees_with_sub5b_run2_count": run2_sub5b,
        "agrees_with_sub5b_both_count": sub5b_both,
        "agrees_with_sub5b_any_count": sub5b_any,
        "agrees_with_sub5b_both_rate": round(sub5b_both / n, 3) if n else 0.0,
        "sub5b_answer_distribution": dict(sub5b_answers),
        "cot_run1_answer_distribution": dict(cot_run1),
        "sub5b_vs_cot_run1_pairs": {f"{a}→{b}": c for (a, b), c in answer_pairs.items()},
    }


def render_summary_markdown(payload: dict[str, Any]) -> str:
    meta = payload["meta"]
    summary = payload["summary"]
    rows = payload["rows"]
    lines = [
        "# CoT Diagnostic Rerun (Sub #5B audit slice)",
        "",
        f"Generated: {meta['generated_at']}",
        "",
        "## Setup",
        "",
        f"- Model: `{meta['model']}`",
        f"- Frame budget: {meta['num_frames']} (same as Sub #5B cropped VQA)",
        f"- Image detail: `{meta['image_detail']}`",
        f"- Video source: `paths.cropped_path` from Sub #5B postprocess (full cropped clip; FOI ignored)",
        f"- Runs per row: {meta['runs_per_row']}",
        f"- Requested temperature: {meta['temperature']}",
    ]
    if meta.get("temperature_note"):
        lines.append(f"- Temperature note: {meta['temperature_note']}")
    lines.extend(
        [
            f"- Selected rows: `{meta['selected_csv']}`",
            f"- Postprocess entries: `{meta['postprocess_entries']}`",
            "",
            "## Headline",
            "",
            f"- Rows processed: **{summary['rows']}** ({summary['errors']} with API/frame errors)",
            f"- Self-agreement across {meta['runs_per_row']} CoT runs: **{summary['self_agreement_count']}/{summary['rows']}** ({summary['self_agreement_rate']:.1%})",
            f"- Agreement with Sub #5B (both runs): **{summary['agrees_with_sub5b_both_count']}/{summary['rows']}** ({summary['agrees_with_sub5b_both_rate']:.1%})",
            f"- Agreement with Sub #5B (run 1): **{summary['agrees_with_sub5b_run1_count']}/{summary['rows']}**",
            f"- Agreement with Sub #5B (run 2): **{summary['agrees_with_sub5b_run2_count']}/{summary['rows']}**",
            f"- Agreement with Sub #5B (either run): **{summary['agrees_with_sub5b_any_count']}/{summary['rows']}**",
            "",
            "## Distributions",
            "",
            f"- Sub #5B answers: `{summary['sub5b_answer_distribution']}`",
            f"- CoT run-1 answers: `{summary['cot_run1_answer_distribution']}`",
            f"- Sub #5B → CoT run-1 pairs: `{summary['sub5b_vs_cot_run1_pairs']}`",
            "",
            "## Per-row results",
            "",
            "| QID | Mode | Sub #5B | CoT r1 | CoT r2 | Self agree | Agree Sub #5B (both) |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        runs = row.get("runs") or []
        r1 = runs[0]["answer"] if len(runs) > 0 else "?"
        r2 = runs[1]["answer"] if len(runs) > 1 else "?"
        lines.append(
            f"| {row['question_id']} | {row.get('mode', '?')} | {row.get('sub5b_answer', '?')} | "
            f"{r1} | {r2} | {row.get('self_agreement')} | {row.get('agrees_with_sub5b_both')} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Sub #5B baseline answers come from the stored no-CoT gpt-5.2 cropped VQA run.",
            "- CoT prompts ask the model to cite supporting frame numbers before emitting `ANSWER: ...`.",
            "- Self-agreement measures whether two identical-config reruns land on the same letter/Yes/No.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(out_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "cot_traces.json"
    md_path = out_dir / "cot_summary.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_summary_markdown(payload), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(REPO_ROOT))
    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[cot-diagnostic] ERROR: OPENAI_API_KEY not set and not found in {args.env_file}", file=sys.stderr)
        return 1

    from nsvqa.vqa.answer_timelogic import _is_reasoning_model

    selected_rows = load_selected_rows(args.selected_csv)
    if args.limit is not None:
        selected_rows = selected_rows[: args.limit]
    entries_by_qid = index_entries(args.postprocess_entries)

    temperature_note = None
    if _is_reasoning_model(args.model) and args.temperature == 0.0:
        temperature_note = (
            f"{args.model} is a reasoning model and ignores temperature; "
            "using reasoning_effort='low' to mirror Sub #5B VQA settings."
        )

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "num_frames": args.num_frames,
        "image_detail": args.image_detail,
        "runs_per_row": args.runs,
        "temperature": args.temperature,
        "temperature_note": temperature_note,
        "selected_csv": str(args.selected_csv),
        "postprocess_entries": str(args.postprocess_entries),
        "prompt_style": (
            "Think step-by-step about what the frames show, cite which frames support your answer, "
            "then answer with a final `ANSWER:` line."
        ),
    }

    client = OpenAI()
    row_results: list[dict[str, Any]] = []

    for idx, csv_row in enumerate(selected_rows, start=1):
        qid = csv_row["question_id"]
        if qid not in entries_by_qid:
            print(f"[cot-diagnostic] skip qid={qid}: not in postprocess entries", file=sys.stderr)
            continue

        entry = prepare_sub5b_entry(entries_by_qid[qid])
        sub5b_answer = csv_row.get(SUB5B_ANSWER_COL, "")
        mode = entry.get("metadata", {}).get("mode", csv_row.get("mode", ""))
        runs: list[dict[str, Any]] = []

        if not args.quiet:
            print(f"[cot-diagnostic] qid={qid} ({idx}/{len(selected_rows)}) mode={mode} sub5b={sub5b_answer!r}")

        for run_idx in range(1, args.runs + 1):
            t0 = time.time()
            try:
                result = answer_one_cot(
                    client,
                    args.model,
                    entry,
                    num_frames=args.num_frames,
                    image_detail=args.image_detail,
                    temperature=args.temperature,
                )
            except Exception as exc:
                default = "A" if mode == "mc" else "Yes"
                result = {
                    "answer": default,
                    "reasoning": "",
                    "raw": None,
                    "error": repr(exc),
                    "sampled_frame_indices": [],
                    "num_frames": 0,
                    "video_path": entry.get("paths", {}).get("video_path"),
                }
            result["run"] = run_idx
            result["seconds"] = round(time.time() - t0, 2)
            runs.append(result)
            if not args.quiet:
                err = f" err={result['error']!r}" if result.get("error") else ""
                print(
                    f"  run {run_idx}: answer={result.get('answer')!r} "
                    f"frames={result.get('num_frames')} ({result.get('seconds')}s){err}"
                )

        answers = [run["answer"] for run in runs]
        self_agreement = len(set(answers)) == 1
        agrees_run1 = answers[0] == sub5b_answer if answers else False
        agrees_run2 = answers[1] == sub5b_answer if len(answers) > 1 else False

        row_results.append(
            {
                "question_id": qid,
                "mode": mode,
                "operator_guess": csv_row.get("operator_guess"),
                "source_dataset": csv_row.get("source_dataset"),
                "sub1_answer": csv_row.get("sub1_baseline_answer"),
                "sub5b_answer": sub5b_answer,
                "runs": runs,
                "self_agreement": self_agreement,
                "agrees_with_sub5b_run1": agrees_run1,
                "agrees_with_sub5b_run2": agrees_run2,
                "agrees_with_sub5b_both": agrees_run1 and agrees_run2,
                "agrees_with_sub5b_any": agrees_run1 or agrees_run2,
            }
        )

        payload = {
            "meta": meta,
            "summary": summarize_rows(row_results),
            "rows": row_results,
        }
        write_outputs(args.out_dir, payload)

    json_path, md_path = write_outputs(
        args.out_dir,
        {
            "meta": meta,
            "summary": summarize_rows(row_results),
            "rows": row_results,
        },
    )
    summary = summarize_rows(row_results)
    print(f"[cot-diagnostic] wrote {json_path}")
    print(f"[cot-diagnostic] wrote {md_path}")
    print(
        "[cot-diagnostic] self-agreement "
        f"{summary['self_agreement_count']}/{summary['rows']}; "
        "Sub #5B agreement (both runs) "
        f"{summary['agrees_with_sub5b_both_count']}/{summary['rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
