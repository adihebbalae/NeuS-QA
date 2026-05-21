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
    idx = nsvs_indices_flags(entry_b)
    reasons = suspicious_foi_reasons(entry_b)
    return {
        "mode": metadata.get("mode", "unknown"),
        "operator_guess": metadata.get("operator_guess", "unknown"),
        "source_dataset": metadata.get("source_dataset", "unknown"),
        "video_id": metadata.get("video_id", "unknown"),
        "duration_seconds": round(duration, 3) if duration is not None else None,
        "duration_bucket": duration_bucket(duration),
        "foi": foi,
        "foi_status": foi_status(foi),
        "foi_seconds": round(foi_seconds(entry_b), 3) if foi_seconds(entry_b) is not None else None,
        "nsvs_indices_any_empty": idx["any_empty"],
        "nsvs_indices_empty_count": idx["empty_count"],
        "foi_suspicious_reasons": ";".join(reasons) if reasons else "",
    }


def valid_foi(foi: Any) -> bool:
    return (
        isinstance(foi, list)
        and len(foi) >= 2
        and foi != [-1]
        and foi[0] != -1
        and foi[1] != -1
        and int(foi[0]) <= int(foi[1])
    )


def foi_seconds(entry: dict[str, Any] | None) -> float | None:
    if not entry:
        return None
    foi = entry.get("frames_of_interest")
    fps = entry.get("metadata", {}).get("fps")
    if not valid_foi(foi) or not fps:
        return None
    return max(0.0, (int(foi[1]) - int(foi[0]) + 1) / float(fps))


def foi_status(foi: Any) -> str:
    if not foi:
        return "missing"
    if isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1:
        return "-1"
    if valid_foi(foi):
        return "non_minus1"
    return "other"


def nsvs_indices_flags(entry: dict[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {
            "has_indices": False,
            "any_empty": False,
            "all_empty": False,
            "empty_count": 0,
            "total_arrays": 0,
        }
    indices = entry.get("nsvs", {}).get("indices")
    if not isinstance(indices, list) or not indices:
        return {
            "has_indices": False,
            "any_empty": False,
            "all_empty": False,
            "empty_count": 0,
            "total_arrays": 0,
        }
    empty_count = sum(1 for arr in indices if not arr)
    return {
        "has_indices": True,
        "any_empty": empty_count > 0,
        "all_empty": empty_count == len(indices),
        "empty_count": empty_count,
        "total_arrays": len(indices),
    }


def suspicious_foi_reasons(entry: dict[str, Any] | None, min_foi_seconds: float = 1.0) -> list[str]:
    if not entry:
        return ["missing_nsvs_entry"]
    reasons: list[str] = []
    foi = entry.get("frames_of_interest")
    if not foi:
        reasons.append("missing_foi")
    elif isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1:
        reasons.append("foi_minus_one")
    elif not valid_foi(foi):
        reasons.append("invalid_foi_bounds")

    raw = entry.get("nsvs", {}).get("output")
    if valid_foi(raw) and (not valid_foi(foi) or foi == [-1]):
        reasons.append("raw_nsvs_valid_final_minus_one")

    if valid_foi(foi) and valid_foi(raw):
        if int(foi[0]) > int(raw[0]) or int(foi[1]) < int(raw[1]):
            reasons.append("merged_foi_not_superset_raw_nsvs")

    idx = nsvs_indices_flags(entry)
    if idx["any_empty"]:
        reasons.append("empty_nsvs_indices_array")
    if not idx["has_indices"]:
        reasons.append("missing_nsvs_indices")

    foi_len = foi_seconds(entry)
    if foi_len is not None and foi_len < min_foi_seconds:
        reasons.append("foi_too_short")

    return reasons


def retrieval_quality_bucket(same_answer: bool, entry_b: dict[str, Any] | None) -> str:
    if same_answer:
        return "agree_with_sub_a"
    if not suspicious_foi_reasons(entry_b):
        return "disagree_foi_clean"
    return "disagree_foi_suspicious"


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

        retrieval_bucket = retrieval_quality_bucket(same, entries_b.get(qid))
        meta["retrieval_quality_bucket"] = retrieval_bucket

        for field in (
            "mode",
            "operator_guess",
            "source_dataset",
            "duration_bucket",
            "foi_status",
            "retrieval_quality_bucket",
        ):
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

    retrieval_path = os.path.join(args.out_dir, "retrieval_quality_buckets.csv")
    retrieval_rows = [
        row
        for row in details
        if row.get("retrieval_quality_bucket") in {"disagree_foi_clean", "disagree_foi_suspicious"}
    ]
    with open(retrieval_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(retrieval_rows)

    retrieval_summary = summary["buckets"].get("retrieval_quality_bucket", {})
    print("\nretrieval_quality_bucket (read on whether NSVS retrieval is helping):")
    for key in ("agree_with_sub_a", "disagree_foi_clean", "disagree_foi_suspicious"):
        if key in retrieval_summary:
            row = retrieval_summary[key]
            print(
                f"  {key}: total={row['total']} disagree={row['disagree']} "
                f"({row['disagree_pct']}% disagree within bucket)"
            )

    print(json.dumps(summary, indent=2))
    print(f"\nwrote: {summary_path}")
    print(f"wrote: {details_path}")
    print(f"wrote: {disagreements_path}")
    print(f"wrote: {retrieval_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
