#!/usr/bin/env python3
"""Build enriched manifest for val and/or test qids."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import (
    AFRL_ROOT,
    PATHS,
    build_test_row,
    duration_cache_key,
    entry_for_test,
    entry_from_shard,
    foi_window_from_entry,
    load_annotations,
    load_duration_cache,
    load_submission,
    operator_complexity_level,
    operator_family,
    classify_pipeline_stage,
    our_answer_for_split,
    source_dataset,
    spec_for_row,
    nsvs_outcome_label,
    vanilla_answer_for_split,
    valid_foi,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--split",
        choices=("val", "test", "both"),
        default="both",
        help="Which split(s) to include (default: both)",
    )
    p.add_argument("--duration-cache", type=Path, default=AFRL_ROOT / "duration_cache.csv")
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "enriched_manifest.json")
    return p.parse_args()


def build_val_row(
    ann: dict[str, Any],
    duration_row: dict[str, str] | None,
    sub5b: dict[str, str],
    sub7b: dict[str, str],
    sub1: dict[str, str],
    baseline_test: dict[str, str],
    sub5b_test: dict[str, str],
) -> dict[str, Any]:
    qid = str(ann["question_id"])
    video_id = ann["video_id"]
    entry = entry_from_shard(qid, "val")
    meta = (entry or {}).get("metadata") or {}
    puls = (entry or {}).get("puls") or {}
    operator_guess = meta.get("operator_guess") or "unknown"
    foi = (entry or {}).get("frames_of_interest")

    duration_s = None
    length_bucket = "unknown"
    if duration_row:
        raw = duration_row.get("duration_s")
        if raw not in ("", None):
            duration_s = float(raw)
        length_bucket = duration_row.get("length_bucket") or "unknown"

    our_answer = our_answer_for_split(qid, "val", sub5b, sub7b)
    vanilla = vanilla_answer_for_split(qid, "val", sub1, baseline_test)

    return {
        "qid": qid,
        "split": "val",
        "source": source_dataset(video_id),
        "video_id": video_id,
        "duration_s": duration_s,
        "length_bucket": length_bucket,
        "mode": meta.get("mode") or ann.get("mode") or "",
        "operator_guess": operator_guess,
        "operator_family": operator_family(operator_guess),
        "complexity_level": operator_complexity_level(operator_guess),
        "question": (entry or {}).get("question") or ann.get("question") or "",
        "candidates": (entry or {}).get("candidates") or [],
        "gt": None,
        "expected_spec": None,
        "our_spec": spec_for_row(entry),
        "pipeline_stage": classify_pipeline_stage(entry),
        "nsvs_outcome": nsvs_outcome_label(entry),
        "our_answer": our_answer,
        "vanilla_vlm_answer": vanilla,
        "sub7b_answer": sub7b.get(qid, ""),
        "baseline_answer": vanilla,
        "sub5b_test_answer": sub5b_test.get(qid, ""),
        "answers_agree": our_answer == vanilla if our_answer and vanilla else None,
        "answers_agree_sub7b_baseline": None,
        "answers_agree_sub7b_sub5b": None,
        "foi_window": foi_window_from_entry(entry),
        "foi_success": valid_foi(foi) if entry else False,
        "foi_raw": foi,
        "gt_available": False,
    }


def main() -> int:
    args = parse_args()
    duration_cache = load_duration_cache(args.duration_cache)
    sub5b = load_submission(str(PATHS["sub5b"]))
    sub7b = load_submission(str(PATHS["sub7b"]))
    sub1 = load_submission(str(PATHS["sub1"]))
    baseline_test = load_submission(str(PATHS["baseline_test"]))
    sub5b_test = load_submission(str(PATHS["sub5b_test"]))

    splits: list[tuple[str, Path]] = []
    if args.split in ("val", "both"):
        splits.append(("val", PATHS["val_ann"]))
    if args.split in ("test", "both"):
        splits.append(("test", PATHS["test_ann"]))

    manifest: list[dict[str, Any]] = []
    missing_answers = 0
    for split, ann_path in splits:
        for ann in load_annotations(ann_path):
            qid = str(ann["question_id"])
            if split == "test":
                entry = entry_for_test(qid)
                row = build_test_row(ann, entry, sub7b, baseline_test, sub5b_test)
            else:
                row = build_val_row(
                    ann,
                    duration_cache.get(duration_cache_key(split, qid)),
                    sub5b,
                    sub7b,
                    sub1,
                    baseline_test,
                    sub5b_test,
                )
            if split == "test":
                if not row["sub7b_answer"] or not row["baseline_answer"]:
                    missing_answers += 1
            elif not row["our_answer"] or not row["vanilla_vlm_answer"]:
                missing_answers += 1
            manifest.append(row)

    write_json(args.out, manifest)
    print(f"[manifest] wrote {args.out} rows={len(manifest)} missing_answers={missing_answers}")

    if args.split in ("test", "both"):
        test_rows = [r for r in manifest if r["split"] == "test"]
        if test_rows:
            from collections import Counter

            stages = Counter(r["pipeline_stage"] for r in test_rows)
            print(f"[manifest] test pipeline_stage: {dict(stages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
