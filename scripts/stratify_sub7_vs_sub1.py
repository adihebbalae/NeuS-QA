#!/usr/bin/env python3
"""Cross-tab Sub #7 vs Sub #1 by duration × operator family × source × FOI status.

Offline diagnostic — no API/GPU. Joins two submission JSONs with TimeLogic
annotations, OpenCV duration audit, and Sub #7 merged entries for FOI status.

When ground-truth labels are supplied (--labels), emits per-bucket accuracy and
Sub7 − Sub1 accuracy delta. Without labels (test phase default), row counts and
agreement rates are still reported; accuracy columns are left blank.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from compare_submissions import (  # noqa: E402
    foi_status,
    load_entries,
    load_submission,
    normalize_answer,
    valid_foi,
)
from nsvqa.datamanager.timelogic import infer_operator  # noqa: E402

STRAT_DURATION_BUCKETS: list[tuple[str, float | None, float | None]] = [
    ("<2s", None, 2.0),
    ("2-10s", 2.0, 10.0),
    ("10-60s", 10.0, 60.0),
    ("60-180s", 60.0, 180.0),
    (">180s", 180.0, None),
]

DURATION_BUCKET_ORDER = [label for label, _, _ in STRAT_DURATION_BUCKETS] + ["unknown"]

DEFAULT_SUB1 = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/submission.json")
DEFAULT_SUB7 = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/submission_sub7.json"
)
DEFAULT_ANN = Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json")
DEFAULT_DURATION_AUDIT = REPO_ROOT / "diagnostics" / "test_video_opencv_audit" / "video_duration_audit.csv"
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/merged/entries.json"
)
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "sub7_vs_sub1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sub1", type=Path, default=DEFAULT_SUB1, help="Sub #1 submission JSON")
    p.add_argument("--sub7", type=Path, default=DEFAULT_SUB7, help="Sub #7 submission JSON")
    p.add_argument("--ann-path", type=Path, default=DEFAULT_ANN, help="TimeLogic annotations JSON")
    p.add_argument(
        "--duration-audit",
        type=Path,
        default=DEFAULT_DURATION_AUDIT,
        help="OpenCV video_duration_audit.csv",
    )
    p.add_argument(
        "--entries",
        type=Path,
        default=DEFAULT_ENTRIES,
        help="Sub #7 merged/entries.json for FOI / metadata",
    )
    p.add_argument(
        "--labels",
        type=Path,
        help="Optional ground-truth JSON: list[{question_id, answer_choice}] or {qid: answer}",
    )
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--score-sub1", type=float, help="EvalAI aggregate accuracy for Sub #1 (percent)")
    p.add_argument("--score-sub7", type=float, help="EvalAI aggregate accuracy for Sub #7 (percent)")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def strat_duration_bucket(seconds: float | None) -> str:
    if seconds is None or math.isnan(seconds):
        return "unknown"
    for label, low, high in STRAT_DURATION_BUCKETS:
        if low is not None and seconds < low:
            continue
        if high is not None and seconds >= high:
            continue
        return label
    return ">180s"


def operator_family(operator: str) -> str:
    op = (operator or "unknown").lower()
    if op in {"always_before", "always_after"}:
        return op
    if "until" in op:
        return "until"
    if "since" in op:
        return "since"
    if "while" in op or "during" in op:
        return "during"
    if "before" in op:
        return "before"
    if "after" in op:
        return "after"
    return op


def source_from_video_id(video_id: str) -> str:
    name = (video_id or "").lower()
    for prefix in ("agqa_", "star_", "ct_", "bf_"):
        if name.startswith(prefix):
            return prefix.rstrip("_")
    return "unknown"


def foi_cleanliness(entry: dict[str, Any] | None) -> str:
    """Paper-facing FOI bucket: clean (valid non-[-1]) vs foi_minus1 vs missing."""
    if not entry:
        return "missing"
    foi = entry.get("frames_of_interest")
    status = foi_status(foi)
    if status == "-1":
        return "foi_minus1"
    if valid_foi(foi):
        return "clean"
    if status == "missing":
        return "missing"
    return "foi_minus1"


def load_duration_audit(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    out: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            vid = row.get("video_id", "").strip()
            raw = row.get("duration_seconds", "")
            if not vid or not raw:
                continue
            try:
                out[vid] = float(raw)
            except ValueError:
                continue
    return out


def load_labels(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    raw = load_json(path)
    if isinstance(raw, dict):
        return {str(k): normalize_answer(v) for k, v in raw.items()}
    if isinstance(raw, list):
        out: dict[str, str] = {}
        for row in raw:
            qid = str(row.get("question_id") or row.get("qid") or row.get("id"))
            ans = normalize_answer(row.get("answer_choice") or row.get("answer"))
            out[qid] = ans
        return out
    raise ValueError(f"unsupported labels format in {path}")


def duration_seconds_from_entry(entry: dict[str, Any] | None) -> float | None:
    if not entry:
        return None
    metadata = entry.get("metadata", {})
    fps = metadata.get("fps")
    frame_count = metadata.get("frame_count")
    if not fps or not frame_count:
        return None
    return float(frame_count) / float(fps)


def build_rows(
    *,
    sub1: dict[str, str],
    sub7: dict[str, str],
    annotations: list[dict[str, Any]],
    duration_by_video: dict[str, float],
    entries: dict[str, dict[str, Any]],
    labels: dict[str, str],
) -> list[dict[str, Any]]:
    ann_by_qid = {str(a["question_id"]): a for a in annotations}
    common_qids = sorted(set(sub1) & set(sub7), key=lambda q: int(q) if q.isdigit() else q)
    rows: list[dict[str, Any]] = []

    for qid in common_qids:
        ann = ann_by_qid.get(qid, {})
        entry = entries.get(qid)
        metadata = (entry or {}).get("metadata", {})
        video_id = str(ann.get("video_id") or metadata.get("video_id") or "unknown")
        duration = duration_by_video.get(video_id)
        if duration is None:
            duration = duration_seconds_from_entry(entry)

        operator_guess = metadata.get("operator_guess") or infer_operator(ann.get("question", ""))
        source = metadata.get("source_dataset") or source_from_video_id(video_id)
        foi_bucket = foi_cleanliness(entry)

        ans1 = sub1[qid]
        ans7 = sub7[qid]
        same = ans1 == ans7
        label = labels.get(qid)
        sub1_correct = label is not None and ans1 == label
        sub7_correct = label is not None and ans7 == label

        rows.append(
            {
                "question_id": qid,
                "duration_bucket": strat_duration_bucket(duration),
                "duration_seconds": round(duration, 3) if duration is not None else None,
                "operator_family": operator_family(operator_guess),
                "operator_guess": operator_guess,
                "source": str(source),
                "foi_status": foi_bucket,
                "sub1_answer": ans1,
                "sub7_answer": ans7,
                "same_answer": same,
                "label": label,
                "sub1_correct": sub1_correct if label is not None else None,
                "sub7_correct": sub7_correct if label is not None else None,
            }
        )
    return rows


def bucket_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        row["duration_bucket"],
        row["operator_family"],
        row["source"],
        row["foi_status"],
    )


def aggregate_buckets(rows: list[dict[str, Any]], *, has_labels: bool) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[bucket_key(row)].append(row)

    aggregates: list[dict[str, Any]] = []
    for key in sorted(groups.keys()):
        items = groups[key]
        n = len(items)
        agree = sum(1 for r in items if r["same_answer"])
        disagree = n - agree
        row: dict[str, Any] = {
            "duration_bucket": key[0],
            "operator_family": key[1],
            "source": key[2],
            "foi_status": key[3],
            "n": n,
            "agree": agree,
            "disagree": disagree,
            "agree_pct": round(100.0 * agree / n, 2) if n else 0.0,
        }
        if has_labels:
            labeled = [r for r in items if r["label"] is not None]
            ln = len(labeled)
            sub1_correct = sum(1 for r in labeled if r["sub1_correct"])
            sub7_correct = sum(1 for r in labeled if r["sub7_correct"])
            sub1_acc = round(100.0 * sub1_correct / ln, 2) if ln else None
            sub7_acc = round(100.0 * sub7_correct / ln, 2) if ln else None
            acc_delta = round(sub7_acc - sub1_acc, 2) if sub1_acc is not None and sub7_acc is not None else None
            row.update(
                {
                    "labeled_n": ln,
                    "sub1_correct": sub1_correct,
                    "sub7_correct": sub7_correct,
                    "sub1_acc_pct": sub1_acc,
                    "sub7_acc_pct": sub7_acc,
                    "acc_delta_sub7_minus_sub1_pct": acc_delta,
                }
            )
        aggregates.append(row)
    return aggregates


def overall_stats(rows: list[dict[str, Any]], *, has_labels: bool) -> dict[str, Any]:
    n = len(rows)
    agree = sum(1 for r in rows if r["same_answer"])
    out: dict[str, Any] = {
        "n": n,
        "agree": agree,
        "disagree": n - agree,
        "agree_pct": round(100.0 * agree / n, 2) if n else 0.0,
    }
    if has_labels:
        labeled = [r for r in rows if r["label"] is not None]
        ln = len(labeled)
        sub1_correct = sum(1 for r in labeled if r["sub1_correct"])
        sub7_correct = sum(1 for r in labeled if r["sub7_correct"])
        out.update(
            {
                "labeled_n": ln,
                "sub1_acc_pct": round(100.0 * sub1_correct / ln, 2) if ln else None,
                "sub7_acc_pct": round(100.0 * sub7_correct / ln, 2) if ln else None,
                "acc_delta_sub7_minus_sub1_pct": round(
                    100.0 * (sub7_correct - sub1_correct) / ln, 2
                )
                if ln
                else None,
            }
        )
    return out


def render_summary_md(
    *,
    rows: list[dict[str, Any]],
    aggregates: list[dict[str, Any]],
    has_labels: bool,
    paths: dict[str, str],
    score_sub1: float | None,
    score_sub7: float | None,
) -> str:
    overall = overall_stats(rows, has_labels=has_labels)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Sub #7 vs Sub #1 stratification",
        "",
        f"_Generated {ts}_",
        "",
        "## Inputs",
        "",
        f"- Sub #1: `{paths['sub1']}`",
        f"- Sub #7: `{paths['sub7']}`",
        f"- Annotations: `{paths['ann']}`",
        f"- Duration audit: `{paths['duration_audit']}`",
        f"- Entries (FOI): `{paths['entries']}`",
        f"- Labels: `{paths['labels']}`" if has_labels else "- Labels: **none** (accuracy columns omitted)",
        "",
        "## Overall",
        "",
        f"- Common rows: **{overall['n']}**",
        f"- Agreement (Sub7 == Sub1): **{overall['agree']}/{overall['n']} ({overall['agree_pct']}%)**",
        f"- Disagreement: **{overall['disagree']}/{overall['n']}**",
    ]
    if score_sub1 is not None and score_sub7 is not None:
        lines.append(
            f"- EvalAI submission-level: Sub #1 **{score_sub1}%**, Sub #7 **{score_sub7}%** "
            f"(net **{score_sub7 - score_sub1:+.2f}** pts for Sub #7)"
        )
    if has_labels:
        lines.extend(
            [
                f"- Labeled rows: **{overall['labeled_n']}**",
                f"- Sub #1 accuracy: **{overall['sub1_acc_pct']}%**",
                f"- Sub #7 accuracy: **{overall['sub7_acc_pct']}%**",
                f"- Δ (Sub7 − Sub1): **{overall['acc_delta_sub7_minus_sub1_pct']:+.2f} pp**",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "> TimeLogic test annotations have no local ground truth. Pass `--labels` to enable",
                "> per-bucket accuracy / Δ columns (e.g. val replay or EvalAI export).",
            ]
        )

    lines.extend(["", "## Cross-tab buckets", ""])
    if has_labels:
        lines.append(
            "| duration | operator | source | FOI | n | Sub1 acc | Sub7 acc | Δ (Sub7−Sub1) | agree |"
        )
        lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
        for row in sorted(
            aggregates,
            key=lambda r: (
                DURATION_BUCKET_ORDER.index(r["duration_bucket"])
                if r["duration_bucket"] in DURATION_BUCKET_ORDER
                else 99,
                r["operator_family"],
                r["source"],
                r["foi_status"],
            ),
        ):
            delta = row.get("acc_delta_sub7_minus_sub1_pct")
            delta_s = f"{delta:+.2f}" if delta is not None else "n/a"
            lines.append(
                f"| {row['duration_bucket']} | {row['operator_family']} | {row['source']} | "
                f"{row['foi_status']} | {row['n']} | {row['sub1_acc_pct']:.2f} | "
                f"{row['sub7_acc_pct']:.2f} | {delta_s} | {row['agree']} |"
            )
    else:
        lines.append("| duration | operator | source | FOI | n | agree | disagree | agree % |")
        lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: |")
        for row in sorted(
            aggregates,
            key=lambda r: (
                DURATION_BUCKET_ORDER.index(r["duration_bucket"])
                if r["duration_bucket"] in DURATION_BUCKET_ORDER
                else 99,
                r["operator_family"],
                r["source"],
                r["foi_status"],
            ),
        ):
            lines.append(
                f"| {row['duration_bucket']} | {row['operator_family']} | {row['source']} | "
                f"{row['foi_status']} | {row['n']} | {row['agree']} | {row['disagree']} | "
                f"{row['agree_pct']:.2f} |"
            )

    # Duration-only rollup for routing signal
    dur_counts = Counter(r["duration_bucket"] for r in rows)
    lines.extend(["", "## Duration rollup (routing signal)", ""])
    if has_labels:
        lines.append("| duration | n | Sub1 acc | Sub7 acc | Δ (Sub7−Sub1) |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for bucket in DURATION_BUCKET_ORDER:
            if bucket not in dur_counts:
                continue
            bucket_rows = [r for r in rows if r["duration_bucket"] == bucket]
            labeled = [r for r in bucket_rows if r["label"] is not None]
            ln = len(labeled)
            if not ln:
                continue
            s1 = sum(1 for r in labeled if r["sub1_correct"])
            s7 = sum(1 for r in labeled if r["sub7_correct"])
            a1 = 100.0 * s1 / ln
            a7 = 100.0 * s7 / ln
            lines.append(
                f"| {bucket} | {len(bucket_rows)} | {a1:.2f} | {a7:.2f} | {a7 - a1:+.2f} |"
            )
    else:
        lines.append("| duration | n | agree | disagree |")
        lines.append("| --- | ---: | ---: | ---: |")
        for bucket in DURATION_BUCKET_ORDER:
            if bucket not in dur_counts:
                continue
            bucket_rows = [r for r in rows if r["duration_bucket"] == bucket]
            agree = sum(1 for r in bucket_rows if r["same_answer"])
            lines.append(
                f"| {bucket} | {len(bucket_rows)} | {agree} | {len(bucket_rows) - agree} |"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Strata: duration (`<2s` / `2-10s` / `10-60s` / `60-180s` / `>180s`) × operator family "
            "× source × FOI (`clean` vs `foi_minus1`).",
            "- Duration prefers OpenCV audit CSV; falls back to entry metadata fps × frame_count.",
            "- Operator family collapses `operator_guess` the same way as failure-audit diagnostics.",
            "- FOI `clean` = valid non-`[-1]` window; `foi_minus1` = NSVS bypass / `[-1]` merged FOI.",
            "",
        ]
    )
    return "\n".join(lines)


def write_stratification_csv(path: Path, aggregates: list[dict[str, Any]], *, has_labels: bool) -> None:
    base_fields = [
        "duration_bucket",
        "operator_family",
        "source",
        "foi_status",
        "n",
        "agree",
        "disagree",
        "agree_pct",
    ]
    label_fields = [
        "labeled_n",
        "sub1_correct",
        "sub7_correct",
        "sub1_acc_pct",
        "sub7_acc_pct",
        "acc_delta_sub7_minus_sub1_pct",
    ]
    fieldnames = base_fields + (label_fields if has_labels else [])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(aggregates)


def run_stratification(
    *,
    sub1: dict[str, str],
    sub7: dict[str, str],
    annotations: list[dict[str, Any]],
    duration_by_video: dict[str, float],
    entries: dict[str, dict[str, Any]],
    labels: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = build_rows(
        sub1=sub1,
        sub7=sub7,
        annotations=annotations,
        duration_by_video=duration_by_video,
        entries=entries,
        labels=labels,
    )
    has_labels = bool(labels)
    aggregates = aggregate_buckets(rows, has_labels=has_labels)
    return rows, aggregates


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if not args.sub1.exists():
        print(f"[stratify] WARNING: missing Sub #1 submission: {args.sub1}", file=sys.stderr)
    if not args.sub7.exists():
        print(f"[stratify] WARNING: missing Sub #7 submission: {args.sub7} (placeholder ok)", file=sys.stderr)

    sub1 = load_submission(str(args.sub1)) if args.sub1.exists() else {}
    sub7 = load_submission(str(args.sub7)) if args.sub7.exists() else {}
    annotations = load_json(args.ann_path) if args.ann_path.exists() else []
    duration_by_video = load_duration_audit(args.duration_audit)
    entries = load_entries(str(args.entries)) if args.entries.exists() else {}
    labels = load_labels(args.labels)
    has_labels = bool(labels)

    rows, aggregates = run_stratification(
        sub1=sub1,
        sub7=sub7,
        annotations=annotations,
        duration_by_video=duration_by_video,
        entries=entries,
        labels=labels,
    )

    csv_path = args.out_dir / "stratification.csv"
    md_path = args.out_dir / "summary.md"
    write_stratification_csv(csv_path, aggregates, has_labels=has_labels)
    md_path.write_text(
        render_summary_md(
            rows=rows,
            aggregates=aggregates,
            has_labels=has_labels,
            paths={
                "sub1": str(args.sub1),
                "sub7": str(args.sub7),
                "ann": str(args.ann_path),
                "duration_audit": str(args.duration_audit),
                "entries": str(args.entries),
                "labels": str(args.labels) if args.labels else "none",
            },
            score_sub1=args.score_sub1,
            score_sub7=args.score_sub7,
        ),
        encoding="utf-8",
    )

    bucket_n = sum(row["n"] for row in aggregates)
    print(f"[stratify] rows={len(rows)} buckets={len(aggregates)} bucket_n_sum={bucket_n}")
    if bucket_n != len(rows):
        print("[stratify] WARNING: bucket counts do not sum to row count", file=sys.stderr)
    print(f"[stratify] wrote {csv_path}")
    print(f"[stratify] wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
