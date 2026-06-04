#!/usr/bin/env python3
"""Build per-category agree-rate tables from test pipeline taxonomy."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT, PIPELINE_STAGES, SOURCE_ORDER, normalize_answer

DIMENSIONS: list[tuple[str, Callable[[dict[str, Any]], str]]] = [
    ("pipeline_stage", lambda r: r.get("pipeline_stage") or "unknown"),
    ("complexity_level", lambda r: str(r.get("complexity_level") or "unknown")),
    ("operator_family", lambda r: r.get("operator_family") or "unknown"),
    ("mode", lambda r: r.get("mode") or "unknown"),
    ("source", lambda r: r.get("source") or "unknown"),
]

FIELDNAMES = [
    "dimension",
    "slice_value",
    "n",
    "agree_rate_sub7b_baseline",
    "agree_rate_sub7b_sub5b",
    "foi_success_rate",
    "sub7b_top_answer",
    "sub7b_top_pct",
    "baseline_top_answer",
    "baseline_top_pct",
    "gt_available",
    "acc_sub7b",
    "acc_baseline",
    "acc_either",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--taxonomy-csv",
        type=Path,
        default=AFRL_ROOT / "test_pipeline_taxonomy.csv",
    )
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "accuracy_by_category.csv")
    p.add_argument(
        "--labels",
        type=Path,
        help="Optional GT labels JSON: list of {question_id, answer_choice} or dict qid->answer",
    )
    return p.parse_args()


def load_labels(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(r["question_id"]): normalize_answer(r["answer_choice"]) for r in data}
    if isinstance(data, dict):
        return {str(k): normalize_answer(v) for k, v in data.items()}
    raise ValueError("labels must be list or dict")


def load_taxonomy_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            for key in ("foi_success",):
                if row.get(key) == "true":
                    row[key] = True
                elif row.get(key) == "false":
                    row[key] = False
            for key in ("answers_agree_sub7b_baseline", "answers_agree_sub7b_sub5b"):
                v = row.get(key)
                if v == "true":
                    row[key] = True
                elif v == "false":
                    row[key] = False
                elif v == "":
                    row[key] = None
            rows.append(row)
    return rows


def agree_rate(rows: list[dict[str, Any]], field: str) -> float | None:
    labeled = [r for r in rows if r.get(field) is not None]
    if not labeled:
        return None
    ok = sum(1 for r in labeled if r[field] is True)
    return round(ok / len(labeled), 4)


def top_answer_pct(rows: list[dict[str, Any]], answer_key: str) -> tuple[str, float | None]:
    answers = [r.get(answer_key) or "" for r in rows if r.get(answer_key)]
    if not answers:
        return "", None
    top, count = Counter(answers).most_common(1)[0]
    return top, round(count / len(answers), 4)


def acc_on_labeled(
    rows: list[dict[str, Any]], labels: dict[str, str], answer_key: str
) -> float | None:
    correct = labeled = 0
    for r in rows:
        gt = labels.get(r["qid"])
        ans = r.get(answer_key) or ""
        if not gt or not ans:
            continue
        labeled += 1
        if ans == gt:
            correct += 1
    return round(correct / labeled, 4) if labeled else None


def acc_either(rows: list[dict[str, Any]], labels: dict[str, str]) -> float | None:
    correct = labeled = 0
    for r in rows:
        gt = labels.get(r["qid"])
        a = r.get("sub7b_answer") or ""
        b = r.get("baseline_answer") or ""
        if not gt or (not a and not b):
            continue
        labeled += 1
        if a == gt or b == gt:
            correct += 1
    return round(correct / labeled, 4) if labeled else None


def slice_order(dimension: str, values: list[str]) -> list[str]:
    if dimension == "pipeline_stage":
        return [v for v in PIPELINE_STAGES if v in values] + sorted(
            v for v in values if v not in PIPELINE_STAGES
        )
    if dimension == "source":
        return [v for v in SOURCE_ORDER if v in values] + sorted(
            v for v in values if v not in SOURCE_ORDER
        )
    if dimension == "complexity_level":
        order = ["1", "2", "3", "4", "5", "unknown"]
        return [v for v in order if v in values] + sorted(v for v in values if v not in order)
    return sorted(values)


def build_table_rows(
    all_rows: list[dict[str, Any]], labels: dict[str, str]
) -> list[dict[str, Any]]:
    gt_available = bool(labels)
    out: list[dict[str, Any]] = []

    for dim_name, key_fn in DIMENSIONS:
        by_value: dict[str, list[dict[str, Any]]] = {}
        for row in all_rows:
            by_value.setdefault(key_fn(row), []).append(row)

        for value in slice_order(dim_name, list(by_value.keys())):
            pool = by_value[value]
            n = len(pool)
            s7_top, s7_pct = top_answer_pct(pool, "sub7b_answer")
            bl_top, bl_pct = top_answer_pct(pool, "baseline_answer")
            foi_ok = sum(1 for r in pool if r.get("foi_success") is True)

            row_out: dict[str, Any] = {
                "dimension": dim_name,
                "slice_value": value,
                "n": n,
                "agree_rate_sub7b_baseline": agree_rate(pool, "answers_agree_sub7b_baseline"),
                "agree_rate_sub7b_sub5b": agree_rate(pool, "answers_agree_sub7b_sub5b"),
                "foi_success_rate": round(foi_ok / n, 4) if n else "",
                "sub7b_top_answer": s7_top,
                "sub7b_top_pct": s7_pct if s7_pct is not None else "",
                "baseline_top_answer": bl_top,
                "baseline_top_pct": bl_pct if bl_pct is not None else "",
                "gt_available": str(gt_available).lower(),
                "acc_sub7b": "",
                "acc_baseline": "",
                "acc_either": "",
            }
            if gt_available:
                row_out["acc_sub7b"] = acc_on_labeled(pool, labels, "sub7b_answer") or ""
                row_out["acc_baseline"] = acc_on_labeled(pool, labels, "baseline_answer") or ""
                row_out["acc_either"] = acc_either(pool, labels) or ""
            out.append(row_out)
    return out


def main() -> int:
    args = parse_args()
    rows = load_taxonomy_csv(args.taxonomy_csv)
    labels = load_labels(args.labels) if args.labels else {}

    out_rows = build_table_rows(rows, labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"[category] wrote {args.out} slices={len(out_rows)} gt_available={bool(labels)}")
    for dim in ("pipeline_stage", "source"):
        dim_rows = [r for r in out_rows if r["dimension"] == dim]
        for r in dim_rows[:6]:
            print(
                f"  {dim}/{r['slice_value']}: n={r['n']} "
                f"agree={r['agree_rate_sub7b_baseline']} foi={r['foi_success_rate']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
