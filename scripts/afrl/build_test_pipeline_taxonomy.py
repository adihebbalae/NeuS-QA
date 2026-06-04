#!/usr/bin/env python3
"""Export full test-split pipeline taxonomy CSV + summary JSON."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import (
    AFRL_ROOT,
    PATHS,
    PIPELINE_STAGES,
    build_test_row,
    entry_for_test,
    load_annotations,
    load_enriched_manifest,
    load_submission,
    write_json,
)

TAXONOMY_FIELDS = [
    "qid",
    "question",
    "mode",
    "candidates",
    "source",
    "operator_guess",
    "operator_family",
    "complexity_level",
    "our_spec",
    "pipeline_stage",
    "nsvs_outcome",
    "foi_window",
    "foi_success",
    "foi_raw",
    "sub7b_answer",
    "baseline_answer",
    "sub5b_test_answer",
    "answers_agree_sub7b_baseline",
    "answers_agree_sub7b_sub5b",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--manifest",
        type=Path,
        help="Reuse enriched_manifest.json test rows (skip shard walk)",
    )
    p.add_argument("--out-csv", type=Path, default=AFRL_ROOT / "test_pipeline_taxonomy.csv")
    p.add_argument("--out-summary", type=Path, default=AFRL_ROOT / "test_pipeline_summary.json")
    return p.parse_args()


def row_to_csv(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in TAXONOMY_FIELDS:
        val = row.get(key)
        if key == "candidates":
            out[key] = json.dumps(val) if val is not None else "[]"
        elif key in ("foi_window", "foi_raw"):
            out[key] = json.dumps(val) if val is not None else ""
        elif isinstance(val, bool):
            out[key] = str(val).lower()
        elif val is None:
            out[key] = ""
        else:
            out[key] = str(val)
    return out


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stage_counts = Counter(r["pipeline_stage"] for r in rows)
    disagree_baseline = sum(1 for r in rows if r.get("answers_agree_sub7b_baseline") is False)
    disagree_sub5b = sum(1 for r in rows if r.get("answers_agree_sub7b_sub5b") is False)
    missing_sub7b = sum(1 for r in rows if not r.get("sub7b_answer"))
    missing_baseline = sum(1 for r in rows if not r.get("baseline_answer"))
    missing_sub5b = sum(1 for r in rows if not r.get("sub5b_test_answer"))

    disagree_by_stage: dict[str, int] = {}
    for stage in PIPELINE_STAGES:
        pool = [r for r in rows if r["pipeline_stage"] == stage]
        disagree_by_stage[stage] = sum(
            1 for r in pool if r.get("answers_agree_sub7b_baseline") is False
        )

    return {
        "n_rows": len(rows),
        "pipeline_stage_counts": dict(stage_counts),
        "disagree_sub7b_baseline": disagree_baseline,
        "disagree_sub7b_sub5b": disagree_sub5b,
        "disagree_sub7b_baseline_by_stage": disagree_by_stage,
        "missing_sub7b_answer": missing_sub7b,
        "missing_baseline_answer": missing_baseline,
        "missing_sub5b_test_answer": missing_sub5b,
        "agree_rate_sub7b_baseline": round(
            sum(1 for r in rows if r.get("answers_agree_sub7b_baseline") is True) / len(rows), 4
        )
        if rows
        else None,
    }


def rows_from_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = load_enriched_manifest(manifest_path)
    return [r for r in manifest if r.get("split") == "test"]


def rows_from_annotations() -> list[dict[str, Any]]:
    sub7b = load_submission(str(PATHS["sub7b"]))
    baseline_test = load_submission(str(PATHS["baseline_test"]))
    sub5b_test = load_submission(str(PATHS["sub5b_test"]))
    rows: list[dict[str, Any]] = []
    for ann in load_annotations(PATHS["test_ann"]):
        qid = str(ann["question_id"])
        entry = entry_for_test(qid)
        rows.append(build_test_row(ann, entry, sub7b, baseline_test, sub5b_test))
    return rows


def main() -> int:
    args = parse_args()
    if args.manifest and args.manifest.is_file():
        rows = rows_from_manifest(args.manifest)
    else:
        rows = rows_from_annotations()

    rows.sort(key=lambda r: int(r["qid"]))

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TAXONOMY_FIELDS)
        writer.writeheader()
        writer.writerows(row_to_csv(r) for r in rows)

    summary = build_summary(rows)
    write_json(args.out_summary, summary)

    print(f"[taxonomy] wrote {args.out_csv} rows={len(rows)}")
    print(f"[taxonomy] wrote {args.out_summary}")
    print(f"[taxonomy] stages={summary['pipeline_stage_counts']}")
    print(
        f"[taxonomy] disagree sub7b vs baseline={summary['disagree_sub7b_baseline']} "
        f"agree_rate={summary['agree_rate_sub7b_baseline']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
