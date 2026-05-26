#!/usr/bin/env python3
"""Build per-category breakdown at submission time for TimeLogic runs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", required=True, help="Run output root (writes per_category_breakdown.json here)")
    p.add_argument("--ann-path", required=True, help="TimeLogic annotations JSON")
    p.add_argument("--submission", required=True, help="Final submission JSON")
    p.add_argument("--entries", required=True, help="postprocess_entries.json")
    p.add_argument("--partial", required=True, help="VQA submission_partial.json for per-row diagnostics")
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def question_type(mode: str) -> str:
    return "MCQ" if mode == "mc" else "Boolean"


def classify_nsvs(entry: dict) -> str:
    meta = entry.get("metadata") or {}
    nsvs = entry.get("nsvs") or {}
    output = nsvs.get("output")
    indices = nsvs.get("indices") or []

    step_status = meta.get("step_status") or entry.get("step_status") or {}
    nsvs_status = step_status.get("nsvs", "")
    if isinstance(nsvs_status, str) and nsvs_status.startswith("error"):
        err = nsvs_status.lower()
        if "storm" in err or "model_check" in err:
            return "storm_error"
        return "error_other"

    if output == [-1] or not output:
        return "empty_detection"
    if indices and any(len(d) == 0 for d in indices):
        return "empty_detection"
    if isinstance(output, list) and len(output) == 2 and output[0] >= 0 and output[1] >= 0:
        return "ok"
    return "empty_detection"


def foi_valid(foi: list | None) -> bool:
    return isinstance(foi, list) and len(foi) == 2 and all(isinstance(x, int) for x in foi)


def crop_status(entry: dict) -> str:
    paths = entry.get("paths") or {}
    cropped = paths.get("cropped_path", "")
    video = paths.get("video_path", "")
    meta = entry.get("metadata") or {}
    if meta.get("crop_error"):
        return "error"
    if cropped and video and cropped == video:
        return "fallback_to_source"
    if cropped:
        return "ok"
    return "error"


def main() -> int:
    args = parse_args()
    annotations = load_json(args.ann_path)
    submission = load_json(args.submission)
    entries = load_json(args.entries)
    partial = load_json(args.partial)

    ann_by_qid = {str(a["question_id"]): a for a in annotations}
    entry_by_qid = {
        str(e.get("metadata", {}).get("question_id") or e.get("question_id")): e for e in entries
    }
    partial_by_qid = {str(r["question_id"]): r for r in partial}
    pred_by_qid = {str(r["question_id"]): r["answer_choice"] for r in submission}

    rows: list[dict[str, Any]] = []
    for qid, pred in pred_by_qid.items():
        ann = ann_by_qid.get(qid, {})
        entry = entry_by_qid.get(qid, {})
        meta = entry.get("metadata") or {}
        mode = ann.get("mode") or meta.get("mode") or "unknown"
        category = meta.get("operator_guess") or "unknown"
        foi = entry.get("frames_of_interest")
        paths = entry.get("paths") or {}
        vqa_path = paths.get("video_path") or paths.get("cropped_path") or ""

        rows.append(
            {
                "qid": qid,
                "category": category,
                "question_type": question_type(mode),
                "predicted_answer": pred,
                "nsvs_status": classify_nsvs(entry),
                "foi_valid": foi_valid(foi),
                "crop_status": crop_status(entry),
                "vqa_input_path": vqa_path,
                "from_partial": qid in partial_by_qid,
            }
        )

    out_path = os.path.join(args.base, "per_category_breakdown.json")
    payload = {
        "run_base": args.base,
        "ann_path": args.ann_path,
        "submission_path": args.submission,
        "row_count": len(rows),
        "rows": rows,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    summary: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for row in rows:
        key = (row["category"], row["question_type"])
        summary[key]["count"] += 1
        summary[key][f"nsvs_{row['nsvs_status']}"] += 1
        summary[key]["foi_valid"] += int(row["foi_valid"])
        summary[key][f"crop_{row['crop_status']}"] += 1

    print(f"\n[per_category] wrote {len(rows)} rows to {out_path}")
    print(f"[per_category] summary by category × question_type (no GT — accuracy skipped):")
    print(f"{'category':<22} {'type':<8} {'n':>5}  {'foi_ok':>6}  nsvs_ok  crop_ok")
    print("-" * 72)
    for (cat, qtype) in sorted(summary.keys()):
        c = summary[(cat, qtype)]
        n = c["count"]
        foi_ok = c.get("foi_valid", 0)
        nsvs_ok = c.get("nsvs_ok", 0)
        crop_ok = c.get("crop_ok", 0)
        print(f"{cat:<22} {qtype:<8} {n:>5}  {foi_ok:>6}  {nsvs_ok:>7}  {crop_ok:>7}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
