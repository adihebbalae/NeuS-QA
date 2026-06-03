#!/usr/bin/env python3
"""Build accuracy-by-length CSV with interim metrics (Task 6)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT, LENGTH_BUCKET_ORDER, load_enriched_manifest, normalize_answer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=AFRL_ROOT / "enriched_manifest.json")
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "accuracy_by_length.csv")
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


def acc(correct: int, total: int) -> float | None:
    if total == 0:
        return None
    return round(correct / total, 4)


def main() -> int:
    args = parse_args()
    manifest = load_enriched_manifest(args.manifest)
    labels = load_labels(args.labels) if args.labels else {}
    gt_available = bool(labels)

    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manifest:
        bucket = row.get("length_bucket") or "unknown"
        buckets[bucket].append(row)

    fieldnames = [
        "length_bucket",
        "n",
        "acc_ours",
        "acc_vanilla_vlm",
        "acc_winner",
        "gt_available",
        "divergence_rate",
        "foi_success_rate",
    ]
    out_rows: list[dict[str, Any]] = []

    for bucket in LENGTH_BUCKET_ORDER:
        rows = buckets.get(bucket, [])
        if not rows:
            continue
        n = len(rows)
        diverged = sum(1 for r in rows if r.get("answers_agree") is False)
        foi_ok = sum(1 for r in rows if r.get("foi_success"))

        row_out: dict[str, Any] = {
            "length_bucket": bucket,
            "n": n,
            "acc_ours": "",
            "acc_vanilla_vlm": "",
            "acc_winner": "",
            "gt_available": str(gt_available).lower(),
            "divergence_rate": round(diverged / n, 4) if n else "",
            "foi_success_rate": round(foi_ok / n, 4) if n else "",
        }

        if gt_available:
            ours_correct = vanilla_correct = winner_correct = 0
            labeled = 0
            for r in rows:
                gt = labels.get(r["qid"])
                if not gt:
                    continue
                labeled += 1
                ours = r.get("our_answer") or ""
                vanilla = r.get("vanilla_vlm_answer") or ""
                if ours == gt:
                    ours_correct += 1
                if vanilla == gt:
                    vanilla_correct += 1
                if ours == gt or vanilla == gt:
                    winner_correct += 1
            if labeled:
                row_out["acc_ours"] = acc(ours_correct, labeled)
                row_out["acc_vanilla_vlm"] = acc(vanilla_correct, labeled)
                row_out["acc_winner"] = acc(winner_correct, labeled)

        out_rows.append(row_out)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"[accuracy] wrote {args.out} gt_available={gt_available}")
    for r in out_rows:
        print(
            f"  {r['length_bucket']:8} n={r['n']:4} div={r['divergence_rate']} "
            f"foi={r['foi_success_rate']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
