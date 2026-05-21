#!/usr/bin/env python3
"""Compare two TimeLogic submissions and bucket answer disagreements.

This is an offline diagnostic. It does not use hidden labels, so "better" rows
are proxy labels only unless ground truth is supplied separately.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sub-a", required=True, help="First submission JSON, e.g. baseline")
    p.add_argument("--sub-b", required=True, help="Second submission JSON, e.g. NSVS")
    p.add_argument("--entries-a", help="Entries JSON for first submission")
    p.add_argument("--entries-b", help="Entries JSON for second submission")
    p.add_argument("--name-a", default="sub_a")
    p.add_argument("--name-b", default="sub_b")
    p.add_argument("--score-a", type=float, help="Aggregate EvalAI accuracy for A, in percent")
    p.add_argument("--score-b", type=float, help="Aggregate EvalAI accuracy for B, in percent")
    p.add_argument("--eval-n", type=int, help="Number of EvalAI rows used by score-a/score-b")
    p.add_argument("--out-dir", required=True, help="Directory for summary JSON and CSVs")
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def load_submission(path: str) -> dict[str, str]:
    rows = load_json(path)
    out: dict[str, str] = {}
    for row in rows:
        qid = str(row.get("question_id") or row.get("qid") or row.get("id"))
        ans = normalize_answer(row.get("answer_choice") or row.get("answer"))
        out[qid] = ans
    return out


def normalize_answer(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    lowered = text.lower()
    if lowered in {"yes", "y", "true"}:
        return "Yes"
    if lowered in {"no", "n", "false"}:
        return "No"
    if len(text) == 1:
        return text.upper()
    return text


def load_entries(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    rows = load_json(path)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        metadata = row.get("metadata", {})
        qid = str(metadata.get("question_id") or row.get("question_id") or row.get("qid") or metadata.get("id"))
        out[qid] = row
    return out


def duration_seconds(entry: dict[str, Any] | None) -> float | None:
    if not entry:
        return None
    metadata = entry.get("metadata", {})
    fps = metadata.get("fps")
    frame_count = metadata.get("frame_count")
    if not fps or not frame_count:
        return None
    return float(frame_count) / float(fps)


def duration_bucket(duration: float | None) -> str:
    if duration is None or math.isnan(duration):
        return "unknown"
    if duration < 2:
        return "<2s"
    if duration < 10:
        return "2-10s"
    if duration < 60:
        return "10-60s"
    return ">60s"


def metadata_for(qid: str, entries_a: dict[str, dict[str, Any]], entries_b: dict[str, dict[str, Any]]) -> dict[str, Any]:
    entry_b = entries_b.get(qid)
    entry_a = entries_a.get(qid)
    entry = entry_b or entry_a or {}
    metadata = entry.get("metadata", {})
    duration = duration_seconds(entry_b) or duration_seconds(entry_a)
    foi = entry_b.get("frames_of_interest") if entry_b else None
    return {
        "mode": metadata.get("mode", "unknown"),
        "operator_guess": metadata.get("operator_guess", "unknown"),
        "source_dataset": metadata.get("source_dataset", "unknown"),
        "video_id": metadata.get("video_id", "unknown"),
        "duration_seconds": round(duration, 3) if duration is not None else None,
        "duration_bucket": duration_bucket(duration),
        "foi": foi,
        "foi_status": foi_status(foi),
    }


def foi_status(foi: Any) -> str:
    if not foi:
        return "missing"
    if isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1:
        return "-1"
    if isinstance(foi, list) and len(foi) >= 2:
        return "non_minus1"
    return "other"


def add_bucket(
    buckets: dict[str, dict[str, Counter]],
    bucket_name: str,
    bucket_value: str,
    same: bool,
) -> None:
    counter = buckets[bucket_name][bucket_value]
    counter["total"] += 1
    if same:
        counter["same_answer"] += 1
    else:
        counter["disagree"] += 1


def finalize_bucket(counter: Counter) -> dict[str, Any]:
    total = counter["total"]
    disagree = counter["disagree"]
    same = counter["same_answer"]
    return {
        "total": total,
        "same_answer": same,
        "disagree": disagree,
        "disagree_pct": round(disagree / total * 100, 2) if total else 0.0,
        "sub_a_preferred_proxy": disagree,
        "sub_b_helped_known": "unknown_without_ground_truth",
    }


def score_delta_bounds(score_a: float | None, score_b: float | None, eval_n: int | None, disagreements: int) -> dict[str, Any] | None:
    if score_a is None or score_b is None or eval_n is None:
        return None
    correct_a = round(score_a / 100.0 * eval_n)
    correct_b = round(score_b / 100.0 * eval_n)
    net_a_minus_b = correct_a - correct_b
    out: dict[str, Any] = {
        "score_a_pct": score_a,
        "score_b_pct": score_b,
        "eval_n": eval_n,
        "estimated_correct_a": correct_a,
        "estimated_correct_b": correct_b,
        "net_a_minus_b_correct": net_a_minus_b,
        "note": (
            "Without labels, individual disagreeing rows cannot be marked helped/hurt. "
            "The net score delta only says A had this many more correct answers overall."
        ),
    }
    if disagreements >= abs(net_a_minus_b):
        max_b_helped_if_one_correct_per_disagreement = (disagreements - net_a_minus_b) / 2
        out["if_every_disagreement_has_exactly_one_correct_answer"] = {
            "a_better_count": (disagreements + net_a_minus_b) / 2,
            "b_better_count": max_b_helped_if_one_correct_per_disagreement,
        }
    return out


def main() -> int:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    sub_a = load_submission(args.sub_a)
    sub_b = load_submission(args.sub_b)
    entries_a = load_entries(args.entries_a)
    entries_b = load_entries(args.entries_b)

    common_qids = sorted(set(sub_a) & set(sub_b), key=lambda x: int(x) if x.isdigit() else x)
    only_a = sorted(set(sub_a) - set(sub_b))
    only_b = sorted(set(sub_b) - set(sub_a))

    details: list[dict[str, Any]] = []
    buckets: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    same_answer = 0
    disagree = 0
    answer_pair_counts: Counter = Counter()

    for qid in common_qids:
        ans_a = sub_a[qid]
        ans_b = sub_b[qid]
        same = ans_a == ans_b
        same_answer += int(same)
        disagree += int(not same)
        answer_pair_counts[(ans_a, ans_b)] += 1
        meta = metadata_for(qid, entries_a, entries_b)

        for field in ("mode", "operator_guess", "source_dataset", "duration_bucket", "foi_status"):
            add_bucket(buckets, field, str(meta[field]), same)

        details.append(
            {
                "question_id": qid,
                f"{args.name_a}_answer": ans_a,
                f"{args.name_b}_answer": ans_b,
                "same_answer": same,
                "proxy_label": "same_answer_unknown_correctness" if same else f"{args.name_a}_preferred_proxy",
                **meta,
            }
        )

    summary = {
        "name_a": args.name_a,
        "name_b": args.name_b,
        "n_a": len(sub_a),
        "n_b": len(sub_b),
        "n_common": len(common_qids),
        "n_only_a": len(only_a),
        "n_only_b": len(only_b),
        "same_answer": same_answer,
        "disagree": disagree,
        "same_answer_pct": round(same_answer / len(common_qids) * 100, 2) if common_qids else 0.0,
        "disagree_pct": round(disagree / len(common_qids) * 100, 2) if common_qids else 0.0,
        "sub_a_preferred_proxy_count": disagree,
        "sub_b_helped_count": "unknown_without_ground_truth",
        "score_delta_bounds": score_delta_bounds(args.score_a, args.score_b, args.eval_n, disagree),
        "buckets": {
            bucket_name: {
                bucket_value: finalize_bucket(counter)
                for bucket_value, counter in sorted(bucket_values.items())
            }
            for bucket_name, bucket_values in buckets.items()
        },
        "top_answer_pair_changes": [
            {"answer_a": a, "answer_b": b, "count": count}
            for (a, b), count in answer_pair_counts.most_common(20)
            if a != b
        ],
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
