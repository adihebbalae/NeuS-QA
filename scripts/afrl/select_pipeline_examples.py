#!/usr/bin/env python3
"""Select 3-5 disagreement examples per pipeline stage for slides."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT, PIPELINE_STAGES, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--taxonomy-csv",
        type=Path,
        default=AFRL_ROOT / "test_pipeline_taxonomy.csv",
    )
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "pipeline_examples.json")
    p.add_argument("--per-stage", type=int, default=4, help="Examples per pipeline stage (3-5)")
    p.add_argument("--min-per-stage", type=int, default=3)
    return p.parse_args()


def load_taxonomy_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            if row.get("candidates"):
                try:
                    row["candidates"] = json.loads(row["candidates"])
                except json.JSONDecodeError:
                    row["candidates"] = []
            else:
                row["candidates"] = []
            if row.get("answers_agree_sub7b_baseline") == "false":
                row["answers_agree_sub7b_baseline"] = False
            elif row.get("answers_agree_sub7b_baseline") == "true":
                row["answers_agree_sub7b_baseline"] = True
            rows.append(row)
    return rows


def score_example(row: dict[str, Any], stage: str) -> tuple:
    op_unknown = 1 if row.get("operator_family") == "unknown" else 0
    has_spec = 0 if (row.get("our_spec") or "").strip() not in ("", "empty") else 1
    has_foi = 0 if "foi=[" in (row.get("nsvs_outcome") or "") else 1
    if stage == "cropped_foi":
        stage_bonus = (0 if has_foi == 0 else 1,)
    elif stage == "full_video_hinted":
        stage_bonus = (has_spec,)
    else:
        stage_bonus = (has_spec,)
    return (op_unknown, *stage_bonus, row.get("source", ""), row.get("mode", ""))


def pick_diverse(
    pool: list[dict[str, Any]], stage: str, n: int, used: set[str]
) -> list[dict[str, Any]]:
    ranked = sorted(pool, key=lambda r: score_example(r, stage))
    picked: list[dict[str, Any]] = []
    seen_source: set[str] = set()
    seen_family: set[str] = set()

    def try_add(row: dict[str, Any]) -> bool:
        if row["qid"] in used:
            return False
        picked.append(row)
        used.add(row["qid"])
        seen_source.add(row.get("source", ""))
        seen_family.add(row.get("operator_family", ""))
        return True

    for row in ranked:
        if len(picked) >= n:
            break
        src = row.get("source", "")
        fam = row.get("operator_family", "")
        if src not in seen_source or fam not in seen_family:
            try_add(row)

    for row in ranked:
        if len(picked) >= n:
            break
        try_add(row)

    return picked


def to_example_record(row: dict[str, Any]) -> dict[str, Any]:
    spec = (row.get("our_spec") or "").strip()
    if not spec or spec == "empty":
        spec_display = "empty"
    else:
        spec_display = spec
    return {
        "qid": row["qid"],
        "pipeline_stage": row["pipeline_stage"],
        "source": row.get("source"),
        "operator_family": row.get("operator_family"),
        "complexity_level": row.get("complexity_level"),
        "mode": row.get("mode"),
        "question": row.get("question"),
        "candidates": row.get("candidates") or [],
        "puls_spec": spec_display,
        "nsvs_outcome": row.get("nsvs_outcome") or "bypassed",
        "sub7b_answer": row.get("sub7b_answer"),
        "baseline_answer": row.get("baseline_answer"),
    }


def main() -> int:
    args = parse_args()
    rows = load_taxonomy_csv(args.taxonomy_csv)
    n_target = max(args.min_per_stage, min(args.per_stage, 5))
    used: set[str] = set()
    records: list[dict[str, Any]] = []

    for stage in PIPELINE_STAGES:
        pool = [
            r
            for r in rows
            if r.get("pipeline_stage") == stage
            and r.get("answers_agree_sub7b_baseline") is False
            and r.get("sub7b_answer")
            and r.get("baseline_answer")
        ]
        picks = pick_diverse(pool, stage, n_target, used)
        for row in picks:
            records.append(to_example_record(row))
        print(f"[examples] {stage}: pool={len(pool)} picked={len(picks)}")

    write_json(args.out, records)
    print(f"[examples] wrote {args.out} total={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
