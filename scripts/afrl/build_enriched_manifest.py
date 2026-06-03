#!/usr/bin/env python3
"""Build enriched manifest for all val+test qids (Task 2)."""

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
    duration_cache_key,
    entry_from_shard,
    foi_window_from_entry,
    load_annotations,
    load_duration_cache,
    load_submission,
    operator_family,
    our_answer_for_split,
    source_dataset,
    vanilla_answer_for_split,
    valid_foi,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--duration-cache", type=Path, default=AFRL_ROOT / "duration_cache.csv")
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "enriched_manifest.json")
    return p.parse_args()


def build_row(
    ann: dict[str, Any],
    split: str,
    duration_row: dict[str, str] | None,
    sub5b: dict[str, str],
    sub7b: dict[str, str],
    sub1: dict[str, str],
    baseline_test: dict[str, str],
) -> dict[str, Any]:
    qid = str(ann["question_id"])
    video_id = ann["video_id"]
    entry = entry_from_shard(qid, split)
    meta = (entry or {}).get("metadata") or {}
    puls = (entry or {}).get("puls") or {}

    duration_s = None
    length_bucket = "unknown"
    if duration_row:
        raw = duration_row.get("duration_s")
        if raw not in ("", None):
            duration_s = float(raw)
        length_bucket = duration_row.get("length_bucket") or "unknown"

    our_answer = our_answer_for_split(qid, split, sub5b, sub7b)
    vanilla = vanilla_answer_for_split(qid, split, sub1, baseline_test)
    operator_guess = meta.get("operator_guess") or "unknown"
    foi = (entry or {}).get("frames_of_interest")

    return {
        "qid": qid,
        "split": split,
        "source": source_dataset(video_id),
        "video_id": video_id,
        "duration_s": duration_s,
        "length_bucket": length_bucket,
        "mode": meta.get("mode") or ann.get("mode") or "",
        "operator_guess": operator_guess,
        "operator_family": operator_family(operator_guess),
        "question": (entry or {}).get("question") or ann.get("question") or "",
        "candidates": (entry or {}).get("candidates") or [],
        "gt": None,
        "expected_spec": None,
        "our_spec": puls.get("specification") or "",
        "our_answer": our_answer,
        "vanilla_vlm_answer": vanilla,
        "answers_agree": our_answer == vanilla if our_answer and vanilla else None,
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

    manifest: list[dict[str, Any]] = []
    missing_answers = 0
    for split, ann_path in [("val", PATHS["val_ann"]), ("test", PATHS["test_ann"])]:
        for ann in load_annotations(ann_path):
            qid = str(ann["question_id"])
            row = build_row(
                ann,
                split,
                duration_cache.get(duration_cache_key(split, qid)),
                sub5b,
                sub7b,
                sub1,
                baseline_test,
            )
            if not row["our_answer"] or not row["vanilla_vlm_answer"]:
                missing_answers += 1
            manifest.append(row)

    write_json(args.out, manifest)
    print(f"[manifest] wrote {args.out} rows={len(manifest)} missing_answers={missing_answers}")

    e1865 = next(r for r in manifest if r["qid"] == "1865")
    print(
        f"[manifest] spot-check 1865: split={e1865['split']} our_spec={e1865['our_spec'][:60]!r} "
        f"foi_window={e1865['foi_window']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
