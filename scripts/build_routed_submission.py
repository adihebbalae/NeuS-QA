#!/usr/bin/env python3
"""Build routed TimeLogic submissions from two completed submissions.

This is pure post-processing: it never calls the VQA model or reruns NSVS.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annotations", required=True, help="Full TimeLogic annotation JSON")
    p.add_argument("--sub1", required=True, help="Baseline/full-video submission JSON")
    p.add_argument("--sub2", required=True, help="NSVS/FOI submission JSON")
    p.add_argument("--entries2", required=True, help="Merged NSVS entries JSON with metadata/FOI")
    p.add_argument("--output", required=True, help="EvalAI-ready routed submission JSON")
    p.add_argument("--summary", required=True, help="Routing summary JSON")
    p.add_argument("--details", required=True, help="Per-question routing details CSV")
    p.add_argument(
        "--variant",
        required=True,
        choices=["foi_confidence_proxy", "bucket_bf_mc_gt60"],
        help=(
            "foi_confidence_proxy: no-rerun proxy for unavailable Storm probability; "
            "bucket_bf_mc_gt60: route bf+mc+>60s to sub1, else sub2."
        ),
    )
    p.add_argument(
        "--max-foi-ratio",
        type=float,
        default=0.95,
        help="For foi_confidence_proxy, require FOI to cover less than this fraction of the full video.",
    )
    p.add_argument(
        "--min-foi-seconds",
        type=float,
        default=1.0,
        help="For foi_confidence_proxy, require FOI to be at least this many seconds long.",
    )
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def load_submission(path: str) -> dict[str, str]:
    rows = load_json(path)
    return {str(row["question_id"]): normalize_answer(row["answer_choice"]) for row in rows}


def normalize_answer(value: Any) -> str:
    text = str(value).strip()
    lower = text.lower()
    if lower in {"yes", "y", "true"}:
        return "Yes"
    if lower in {"no", "n", "false"}:
        return "No"
    if len(text) == 1:
        return text.upper()
    return text


def load_entries(path: str) -> dict[str, dict[str, Any]]:
    entries = load_json(path)
    out: dict[str, dict[str, Any]] = {}
    for entry in entries:
        metadata = entry.get("metadata", {})
        qid = str(metadata.get("question_id") or entry.get("question_id") or metadata.get("id"))
        out[qid] = entry
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


def foi_seconds(entry: dict[str, Any] | None) -> float | None:
    if not entry:
        return None
    foi = entry.get("frames_of_interest")
    fps = entry.get("metadata", {}).get("fps")
    if not valid_foi(foi) or not fps:
        return None
    return max(0.0, (float(foi[1]) - float(foi[0]) + 1.0) / float(fps))


def valid_foi(foi: Any) -> bool:
    return isinstance(foi, list) and len(foi) >= 2 and foi[0] != -1 and foi[1] != -1 and foi[1] >= foi[0]


def route_for_variant(
    variant: str,
    annotation: dict[str, Any],
    entry2: dict[str, Any] | None,
    max_foi_ratio: float,
    min_foi_seconds: float,
) -> tuple[str, str]:
    """Return (source, reason), where source is sub1 or sub2."""
    metadata = entry2.get("metadata", {}) if entry2 else {}
    mode = metadata.get("mode") or annotation.get("mode") or "unknown"
    source_dataset = metadata.get("source_dataset", "unknown")
    duration = duration_seconds(entry2)
    foi_len = foi_seconds(entry2)

    if variant == "bucket_bf_mc_gt60":
        if source_dataset == "bf" and mode == "mc" and duration is not None and duration > 60:
            return "sub1", "high_risk_bucket:bf+mc+>60s"
        return "sub2", "default_trust_nsvs"

    if variant == "foi_confidence_proxy":
        if not entry2:
            return "sub1", "missing_nsvs_entry"
        if not valid_foi(entry2.get("frames_of_interest")):
            return "sub1", "invalid_or_minus1_foi"
        if duration is None or foi_len is None:
            return "sub1", "missing_duration_or_foi_length"
        if foi_len < min_foi_seconds:
            return "sub1", "foi_too_short"
        ratio = foi_len / duration if duration > 0 else 1.0
        if ratio >= max_foi_ratio:
            return "sub1", "foi_near_full_video"
        return "sub2", "usable_cropped_foi_proxy"

    raise ValueError(f"unknown variant: {variant}")


def main() -> int:
    args = parse_args()
    annotations = load_json(args.annotations)
    sub1 = load_submission(args.sub1)
    sub2 = load_submission(args.sub2)
    entries2 = load_entries(args.entries2)

    submission: list[dict[str, str]] = []
    details: list[dict[str, Any]] = []
    source_counts: Counter = Counter()
    reason_counts: Counter = Counter()
    changed_from_sub1 = 0
    changed_from_sub2 = 0
    missing_answers = 0

    for annotation in annotations:
        qid = str(annotation["question_id"])
        entry2 = entries2.get(qid)
        source, reason = route_for_variant(
            args.variant,
            annotation,
            entry2,
            max_foi_ratio=args.max_foi_ratio,
            min_foi_seconds=args.min_foi_seconds,
        )
        ans1 = sub1.get(qid)
        ans2 = sub2.get(qid)
        if ans1 is None or ans2 is None:
            missing_answers += 1
        answer = ans2 if source == "sub2" else ans1
        if answer is None:
            answer = "A" if annotation.get("mode") == "mc" else "Yes"

        submission.append({"question_id": qid, "answer_choice": answer})
        source_counts[source] += 1
        reason_counts[reason] += 1
        changed_from_sub1 += int(answer != ans1)
        changed_from_sub2 += int(answer != ans2)

        metadata = entry2.get("metadata", {}) if entry2 else {}
        duration = duration_seconds(entry2)
        foi_len = foi_seconds(entry2)
        ratio = (foi_len / duration) if duration and foi_len is not None else None
        details.append(
            {
                "question_id": qid,
                "routed_source": source,
                "route_reason": reason,
                "answer": answer,
                "sub1_answer": ans1,
                "sub2_answer": ans2,
                "sub1_sub2_disagree": ans1 != ans2,
                "mode": metadata.get("mode") or annotation.get("mode") or "unknown",
                "source_dataset": metadata.get("source_dataset", "unknown"),
                "operator_guess": metadata.get("operator_guess", "unknown"),
                "duration_seconds": round(duration, 3) if duration is not None else "",
                "foi_seconds": round(foi_len, 3) if foi_len is not None else "",
                "foi_ratio": round(ratio, 4) if ratio is not None else "",
                "frames_of_interest": entry2.get("frames_of_interest") if entry2 else "",
            }
        )

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    os.makedirs(os.path.dirname(args.summary), exist_ok=True)
    os.makedirs(os.path.dirname(args.details), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(submission, f, indent=2)

    summary = {
        "variant": args.variant,
        "n": len(submission),
        "sources": dict(source_counts),
        "route_reasons": dict(reason_counts),
        "changed_from_sub1": changed_from_sub1,
        "changed_from_sub2": changed_from_sub2,
        "missing_answers": missing_answers,
        "output": args.output,
        "details": args.details,
        "notes": {
            "storm_probability_available": False,
            "storm_probability_note": (
                "Existing Sub #2 artifacts store thresholded NSVS/FOI outputs, not raw "
                "Storm satisfaction probabilities. The foi_confidence_proxy variant is "
                "therefore a no-rerun proxy, not the true Storm-probability gate."
            ),
        },
    }
    with open(args.summary, "w") as f:
        json.dump(summary, f, indent=2)

    with open(args.details, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0].keys()))
        writer.writeheader()
        writer.writerows(details)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
