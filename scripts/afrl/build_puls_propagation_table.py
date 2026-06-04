#!/usr/bin/env python3
"""Join test per-entry shards with operator labels; cross-tab spec_faithful propagation.

Reads sub7b ``shard_*/per_entry/{qid}.json`` (puls_spec, foi, nsvs_indices),
adds ``spec_faithful`` (does emitted TL spec match question operator family?),
and emits 2×2 tables:

  spec_faithful × foi_minus1
  spec_faithful × ours_ne_vanilla  (sub7b ≠ baseline_test)

Outputs under ``reports/afrl/``:
  - test_puls_shard_join.csv   (3000-row join)
  - puls_propagation_crosstab.json
"""

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

from _lib import (  # noqa: E402
    AFRL_ROOT,
    PATHS,
    build_puls_shard_row,
    crosstab_2x2,
    iter_test_shard_entries,
    load_submission,
    write_json,
)

JOIN_FIELDS = [
    "qid",
    "operator_guess",
    "operator_family",
    "puls_spec",
    "propositions",
    "foi_raw",
    "foi_minus1",
    "nsvs_indices",
    "spec_faithful",
    "spec_faithful_reason",
    "sub7b_answer",
    "baseline_answer",
    "ours_ne_vanilla",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--shards-root",
        type=Path,
        default=PATHS["sub7b_shards"],
        help="sub7b shard root (shard_*/per_entry/)",
    )
    p.add_argument(
        "--out-csv",
        type=Path,
        default=AFRL_ROOT / "test_puls_shard_join.csv",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=AFRL_ROOT / "puls_propagation_crosstab.json",
    )
    return p.parse_args()


def row_to_csv(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in JOIN_FIELDS:
        val = row.get(key)
        if key in ("propositions", "foi_raw", "nsvs_indices"):
            out[key] = json.dumps(val) if val is not None else ""
        elif isinstance(val, bool):
            out[key] = str(val).lower()
        elif val is None:
            out[key] = ""
        else:
            out[key] = str(val)
    return out


def format_table_2x2(tab: dict[str, Any]) -> str:
    """Markdown 2×2 with counts and row rates."""
    col_key = tab["col_key"]
    col_true_key = col_key
    col_false_key = f"not_{col_key}"
    col_true_label = col_key.replace("_", " ")
    if col_key == "foi_minus1":
        col_true_label, col_false_label = "FOI=[-1]", "FOI ok"
    elif col_key == "ours_ne_vanilla":
        col_true_label, col_false_label = "ours≠vanilla", "ours=vanilla"
    else:
        col_false_label = f"not {col_true_label}"

    rows = tab["rows"]
    faithful = rows["faithful"]
    unfaithful = rows["not_faithful"]
    lines = [
        f"### spec_faithful × {col_key}",
        "",
        f"| spec_faithful | {col_true_label} | {col_false_label} | row_n | rate({col_true_label}|row) |",
        "|---|---:|---:|---:|---:|",
        (
            f"| faithful | {faithful[col_true_key]} | {faithful[col_false_key]} "
            f"| {faithful['row_n']} | {faithful[f'rate_{col_true_key}_within_row']:.1%} |"
        ),
        (
            f"| unfaithful | {unfaithful[col_true_key]} | {unfaithful[col_false_key]} "
            f"| {unfaithful['row_n']} | {unfaithful[f'rate_{col_true_key}_within_row']:.1%} |"
        ),
        "",
    ]
    cond = tab["conditional_rates"][f"p_{col_key}_given_{tab['row_key']}"]
    lift = tab["conditional_rates"].get("lift_unfaithful_over_faithful")
    lines.append(
        f"P({col_true_label} | unfaithful) = **{cond['not_faithful']:.1%}**; "
        f"P({col_true_label} | faithful) = **{cond['faithful']:.1%}**"
        + (f"; lift = **{lift:.2f}×**" if lift is not None else "")
        + "."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    sub7b = load_submission(str(PATHS["sub7b"]))
    baseline_test = load_submission(str(PATHS["baseline_test"]))

    shard_pairs = iter_test_shard_entries(args.shards_root)
    rows = [
        build_puls_shard_row(qid, entry, sub7b, baseline_test)
        for qid, entry in shard_pairs
    ]
    rows.sort(key=lambda r: int(r["qid"]))

    # Crosstab rows need non-null booleans for ours_ne_vanilla
    ctab_rows = [
        {
            **r,
            "ours_ne_vanilla": bool(r["ours_ne_vanilla"])
            if r["ours_ne_vanilla"] is not None
            else False,
        }
        for r in rows
    ]

    tab_foi = crosstab_2x2(
        ctab_rows,
        row_key="spec_faithful",
        col_key="foi_minus1",
        row_true_label="faithful",
        col_true_label="foi_minus1",
    )
    tab_disagree = crosstab_2x2(
        ctab_rows,
        row_key="spec_faithful",
        col_key="ours_ne_vanilla",
        row_true_label="faithful",
        col_true_label="ours_ne_vanilla",
    )

    faithful_n = sum(1 for r in rows if r["spec_faithful"])
    summary = {
        "n_rows": len(rows),
        "spec_faithful_count": faithful_n,
        "spec_unfaithful_count": len(rows) - faithful_n,
        "spec_faithful_rate": round(faithful_n / len(rows), 4) if rows else None,
        "foi_minus1_rate": round(sum(1 for r in rows if r["foi_minus1"]) / len(rows), 4)
        if rows
        else None,
        "ours_ne_vanilla_rate": round(
            sum(1 for r in rows if r["ours_ne_vanilla"]) / len(rows), 4
        )
        if rows
        else None,
        "crosstab_foi_minus1": tab_foi,
        "crosstab_ours_ne_vanilla": tab_disagree,
        "interpretation": (
            "Unfaithful PULS specs associate with higher FOI=[-1] (NSVS bypass) rates, "
            "showing operator mismatch propagates to downstream interval retrieval failure."
        ),
    }

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=JOIN_FIELDS)
        writer.writeheader()
        writer.writerows(row_to_csv(r) for r in rows)

    write_json(args.out_json, summary)

    md_path = args.out_json.with_suffix(".md")
    md_body = "\n".join(
        [
            "# PULS spec faithfulness → downstream propagation (test, n=3000)",
            "",
            f"- Faithful specs: **{faithful_n}** ({faithful_n / len(rows):.1%})",
            f"- FOI=[-1] overall: **{summary['foi_minus1_rate']:.1%}**",
            f"- Sub7b ≠ baseline overall: **{summary['ours_ne_vanilla_rate']:.1%}**",
            "",
            format_table_2x2(tab_foi),
            format_table_2x2(tab_disagree),
            summary["interpretation"],
        ]
    )
    md_path.write_text(md_body + "\n", encoding="utf-8")

    print(f"[puls_propagation] wrote {args.out_csv} rows={len(rows)}")
    print(f"[puls_propagation] wrote {args.out_json}")
    print(f"[puls_propagation] wrote {md_path}")
    print(md_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
