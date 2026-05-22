#!/usr/bin/env python3
"""Pre-score NSVS / FOI stats bucketed by operator_guess and source_dataset.

Read-only on merged entries. Safe to run while Sub #5B VQA is in flight.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from compare_submissions import (  # noqa: E402
    foi_seconds,
    foi_status,
    load_entries,
    nsvs_indices_flags,
    suspicious_foi_reasons,
    valid_foi,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", required=True, help="merged/entries.json")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--label", default="nsvs_bucket_breakdown")
    return p.parse_args()


def bucket_row(entry: dict[str, Any]) -> dict[str, Any]:
    meta = entry.get("metadata", {})
    foi = entry.get("frames_of_interest")
    idx = nsvs_indices_flags(entry)
    reasons = suspicious_foi_reasons(entry)
    props = entry.get("puls", {}).get("proposition") or []
    multi_prop = len(props) > 1
    return {
        "operator_guess": meta.get("operator_guess") or "unknown",
        "source_dataset": meta.get("source_dataset") or "unknown",
        "mode": meta.get("mode") or "unknown",
        "foi_valid": valid_foi(foi),
        "foi_minus_one": bool(foi == [-1] or (isinstance(foi, list) and foi and foi[0] == -1)),
        "foi_suspicious": bool(reasons),
        "any_empty_prop": idx["any_empty"],
        "multi_prop": multi_prop,
        "foi_seconds": foi_seconds(entry),
    }


def aggregate(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)

    out: list[dict[str, Any]] = []
    for bucket, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        n = len(items)
        foi_secs = [x["foi_seconds"] for x in items if x["foi_seconds"] is not None]
        out.append(
            {
                "bucket": bucket,
                "n": n,
                "foi_valid_pct": round(sum(x["foi_valid"] for x in items) / n * 100, 2),
                "foi_minus_one_pct": round(sum(x["foi_minus_one"] for x in items) / n * 100, 2),
                "foi_suspicious_pct": round(sum(x["foi_suspicious"] for x in items) / n * 100, 2),
                "any_empty_prop_pct": round(sum(x["any_empty_prop"] for x in items) / n * 100, 2),
                "median_foi_seconds": round(sorted(foi_secs)[len(foi_secs) // 2], 2) if foi_secs else None,
            }
        )
    return out


def main() -> int:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    entries = load_entries(args.entries)
    rows = [bucket_row(e) for e in entries.values()]
    n = len(rows)

    summary = {
        "label": args.label,
        "entries": args.entries,
        "n": n,
        "overall": {
            "foi_valid_pct": round(sum(r["foi_valid"] for r in rows) / n * 100, 2),
            "foi_minus_one_pct": round(sum(r["foi_minus_one"] for r in rows) / n * 100, 2),
            "foi_suspicious_pct": round(sum(r["foi_suspicious"] for r in rows) / n * 100, 2),
            "any_empty_prop_pct": round(sum(r["any_empty_prop"] for r in rows) / n * 100, 2),
        },
        "by_operator_guess": aggregate(rows, "operator_guess"),
        "by_source_dataset": aggregate(rows, "source_dataset"),
        "by_mode": aggregate(rows, "mode"),
    }

    json_path = os.path.join(args.out_dir, "nsvs_by_bucket.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    for field in ("by_operator_guess", "by_source_dataset", "by_mode"):
        csv_path = os.path.join(args.out_dir, f"nsvs_{field}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary[field][0].keys()) if summary[field] else [])
            writer.writeheader()
            writer.writerows(summary[field])

    print(json.dumps(summary["overall"], indent=2))
    print(f"\nwrote: {json_path}")
    print(f"operators: {len(summary['by_operator_guess'])} buckets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
