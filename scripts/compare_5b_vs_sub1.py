#!/usr/bin/env python3
"""Compare fixed Sub #5B against Sub #1 with NSVS-quality slicing on disagreements.

Offline diagnostic only. Reuses field names and helpers from
`scripts/compare_submissions.py`. Intended to run once
`outputs/sub5b_paper_faithful_3fps_fix2/submission_sub5b_paper_faithful.json`
exists.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from compare_submissions import (  # noqa: E402
    duration_bucket,
    duration_seconds,
    foi_seconds,
    foi_status,
    load_entries,
    load_submission,
    score_delta_bounds,
    suspicious_foi_reasons,
    valid_foi,
    nsvs_indices_flags,
)


DEFAULT_SUB1 = "/home/ah66742/timelogic-data/outputs/baseline_cpu_v01/submission.json"
DEFAULT_SUB1_ENTRIES = "/home/ah66742/timelogic-data/outputs/baseline_cpu_v01/entries.json"
DEFAULT_SUB5B = (
    "/home/ah66742/timelogic-data/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_SUB5B_ENTRIES = (
    "/home/ah66742/timelogic-data/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_OUT = "/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sub1", default=DEFAULT_SUB1, help="Sub #1 submission JSON")
    parser.add_argument("--sub5b", default=DEFAULT_SUB5B, help="Sub #5B submission JSON")
    parser.add_argument("--entries-sub1", default=DEFAULT_SUB1_ENTRIES)
    parser.add_argument("--entries-sub5b", default=DEFAULT_SUB5B_ENTRIES)
    parser.add_argument("--score-sub1", type=float, default=50.5)
    parser.add_argument("--score-sub5b", type=float, help="EvalAI score for Sub #5B")
    parser.add_argument("--eval-n", type=int, default=2000)
    parser.add_argument("--out-dir", default=DEFAULT_OUT)
    return parser.parse_args()


def nsvs_quality_fields(entry: dict[str, Any] | None) -> dict[str, Any]:
    idx = nsvs_indices_flags(entry)
    reasons = suspicious_foi_reasons(entry)
    foi = entry.get("frames_of_interest") if entry else None
    metadata = entry.get("metadata", {}) if entry else {}
    duration = duration_seconds(entry)
    return {
        "foi_status": foi_status(foi),
        "foi_seconds": round(foi_seconds(entry), 3) if foi_seconds(entry) is not None else None,
        "foi_suspicious_reasons": ";".join(reasons) if reasons else "",
        "nsvs_indices_any_empty": idx["any_empty"],
        "nsvs_indices_empty_count": idx["empty_count"],
        "nsvs_indices_total_arrays": idx["total_arrays"],
        "foi_minus_one": bool(foi == [-1] or not foi),
        "foi_valid_non_empty": valid_foi(foi),
        "mode": metadata.get("mode", "unknown"),
        "operator_guess": metadata.get("operator_guess", "unknown"),
        "source_dataset": metadata.get("source_dataset", "unknown"),
        "duration_bucket": duration_bucket(duration),
    }


def main() -> int:
    args = parse_args()
    if not os.path.exists(args.sub5b):
        print(f"Missing Sub #5B submission: {args.sub5b}", file=sys.stderr)
        return 2

    os.makedirs(args.out_dir, exist_ok=True)

    sub1 = load_submission(args.sub1)
    sub5b = load_submission(args.sub5b)
    entries_sub1 = load_entries(args.entries_sub1)
    entries_sub5b = load_entries(args.entries_sub5b)

    common_qids = sorted(set(sub1) & set(sub5b), key=lambda x: int(x) if x.isdigit() else x)
    details: list[dict[str, Any]] = []
    same_answer = 0
    disagree = 0
    foi_quality_slices: dict[str, dict[str, int]] = {
        "disagree_foi_valid_non_empty": {"total": 0, "disagree": 0},
        "disagree_foi_minus_one": {"total": 0, "disagree": 0},
        "disagree_any_empty_prop": {"total": 0, "disagree": 0},
        "disagree_foi_suspicious": {"total": 0, "disagree": 0},
    }

    for qid in common_qids:
        ans_sub1 = sub1[qid]
        ans_sub5b = sub5b[qid]
        same = ans_sub1 == ans_sub5b
        same_answer += int(same)
        disagree += int(not same)
        entry5b = entries_sub5b.get(qid)
        quality = nsvs_quality_fields(entry5b)
        row = {
            "question_id": qid,
            "sub1_answer": ans_sub1,
            "sub5b_answer": ans_sub5b,
            "same_answer": same,
            **quality,
        }
        details.append(row)

        if quality["foi_valid_non_empty"]:
            foi_quality_slices["disagree_foi_valid_non_empty"]["total"] += 1
            foi_quality_slices["disagree_foi_valid_non_empty"]["disagree"] += int(not same)
        if quality["foi_minus_one"]:
            foi_quality_slices["disagree_foi_minus_one"]["total"] += 1
            foi_quality_slices["disagree_foi_minus_one"]["disagree"] += int(not same)
        if quality["nsvs_indices_any_empty"]:
            foi_quality_slices["disagree_any_empty_prop"]["total"] += 1
            foi_quality_slices["disagree_any_empty_prop"]["disagree"] += int(not same)
        if quality["foi_suspicious_reasons"]:
            foi_quality_slices["disagree_foi_suspicious"]["total"] += 1
            foi_quality_slices["disagree_foi_suspicious"]["disagree"] += int(not same)

    summary = {
        "name_sub1": "sub1_baseline",
        "name_sub5b": "sub5b_paper_faithful_fix2",
        "n_common": len(common_qids),
        "same_answer": same_answer,
        "disagree": disagree,
        "same_answer_pct": round(same_answer / len(common_qids) * 100, 2) if common_qids else 0.0,
        "disagree_pct": round(disagree / len(common_qids) * 100, 2) if common_qids else 0.0,
        "score_delta_bounds": score_delta_bounds(
            args.score_sub1,
            args.score_sub5b,
            args.eval_n,
            disagree,
        ),
        "foi_quality_slices": foi_quality_slices,
    }

    summary_path = os.path.join(args.out_dir, "summary.json")
    details_path = os.path.join(args.out_dir, "details.csv")
    disagreements_path = os.path.join(args.out_dir, "disagreements.csv")

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    fieldnames = list(details[0].keys()) if details else []
    with open(details_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(details)

    with open(disagreements_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row for row in details if not row["same_answer"])

    print(json.dumps(summary, indent=2))
    print(f"\nwrote: {summary_path}")
    print(f"wrote: {details_path}")
    print(f"wrote: {disagreements_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
