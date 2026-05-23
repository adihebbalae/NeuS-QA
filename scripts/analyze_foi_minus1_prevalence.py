#!/usr/bin/env python3
"""Measure FOI == [-1] prevalence on the full Sub #5B val entries dump.

Compares the full 2000-row pipeline to the 25-row failure-audit slice so we can
tell whether high bypass rates in the audit are selection bias or global behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3" / "foi_minus1_prevalence.md"
DEFAULT_AUDIT_CSV = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v2" / "selected_rows.csv"

AUDIT_DURATION_BUCKETS: list[tuple[str, float | None, float | None]] = [
    ("<10s", None, 10.0),
    ("10-30s", 10.0, 30.0),
    ("30-60s", 30.0, 60.0),
    ("60-180s", 60.0, 180.0),
    (">180s", 180.0, None),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument(
        "--audit-csv",
        type=Path,
        default=DEFAULT_AUDIT_CSV,
        help="25-row audit selected_rows.csv for slice comparison",
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def qid_from_entry(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    return str(metadata.get("question_id") or entry.get("question_id") or entry.get("qid"))


def duration_seconds(entry: dict[str, Any]) -> float | None:
    metadata = entry.get("metadata", {})
    fps = metadata.get("fps")
    frame_count = metadata.get("frame_count")
    if not fps or not frame_count:
        return None
    return float(frame_count) / float(fps)


def audit_duration_bucket(seconds: float | None) -> str:
    if seconds is None or math.isnan(seconds):
        return "unknown"
    for label, low, high in AUDIT_DURATION_BUCKETS:
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


def foi_is_minus_one(foi: Any) -> bool:
    return foi == [-1] or (isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1)


def nsvs_bypassed(entry: dict[str, Any]) -> bool:
    """Match v3 audit packet NSVS_bypassed yes/partial signal."""
    nsvs = entry.get("nsvs", {})
    output = nsvs.get("output")
    indices = nsvs.get("indices") or []
    foi = entry.get("frames_of_interest")
    if output == [-1] or foi_is_minus_one(foi):
        return True
    if indices:
        empty_count = sum(1 for idxs in indices if not idxs)
        if empty_count == len(indices) or empty_count > 0:
            return True
    return False


def row_from_entry(entry: dict[str, Any]) -> dict[str, Any]:
    metadata = entry.get("metadata", {})
    duration = duration_seconds(entry)
    foi = entry.get("frames_of_interest")
    return {
        "question_id": qid_from_entry(entry),
        "operator_guess": metadata.get("operator_guess") or "unknown",
        "operator_family": operator_family(metadata.get("operator_guess") or "unknown"),
        "source_dataset": metadata.get("source_dataset") or "unknown",
        "duration_seconds": duration,
        "audit_duration_bucket": audit_duration_bucket(duration),
        "foi_minus_one": foi_is_minus_one(foi),
        "nsvs_bypassed": nsvs_bypassed(entry),
        "foi": foi,
    }


def bucket_table(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)

    table: list[dict[str, Any]] = []
    for bucket, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        n = len(items)
        minus_one = sum(1 for item in items if item["foi_minus_one"])
        bypassed = sum(1 for item in items if item["nsvs_bypassed"])
        table.append(
            {
                "bucket": bucket,
                "n": n,
                "foi_minus_one_n": minus_one,
                "foi_minus_one_pct": round(minus_one / n * 100, 1) if n else 0.0,
                "nsvs_bypassed_n": bypassed,
                "nsvs_bypassed_pct": round(bypassed / n * 100, 1) if n else 0.0,
            }
        )
    return table


def pct(n: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{n / total * 100:.1f}%"


def render_markdown(
    *,
    entries_path: Path,
    audit_csv: Path,
    all_rows: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
) -> str:
    n_all = len(all_rows)
    all_minus_one = sum(1 for row in all_rows if row["foi_minus_one"])
    all_bypassed = sum(1 for row in all_rows if row["nsvs_bypassed"])
    n_audit = len(audit_rows)
    audit_minus_one = sum(1 for row in audit_rows if row["foi_minus_one"])
    audit_bypassed = sum(1 for row in audit_rows if row["nsvs_bypassed"])

    op_table = bucket_table(all_rows, "operator_family")
    dur_table = bucket_table(all_rows, "audit_duration_bucket")
    audit_op_table = bucket_table(audit_rows, "operator_family")
    audit_dur_table = bucket_table(audit_rows, "audit_duration_bucket")

    lines = [
        "# FOI == [-1] prevalence (Sub #5B val)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Source",
        "",
        f"- Entries: `{entries_path}`",
        f"- Audit slice: `{audit_csv}` ({n_audit} QIDs)",
        f"- Processed rows in dump: **{n_all}** (EvalAI val is 2000; 17 source videos missing on disk)",
        "",
        "## Headline",
        "",
        f"- Full val rows (processed): **{n_all}**",
        f"- `frames_of_interest == [-1]`: **{all_minus_one}/{n_all} ({pct(all_minus_one, n_all)})**",
        f"- Audit slice `FOI == [-1]`: **{audit_minus_one}/{n_audit} ({pct(audit_minus_one, n_audit)})**",
        "",
        "For context, the v3 audit packet's broader `NSVS_bypassed` signal (FOI [-1], Storm [-1], or any empty proposition detections):",
        "",
        f"- Full val: **{all_bypassed}/{n_all} ({pct(all_bypassed, n_all)})**",
        f"- Audit slice: **{audit_bypassed}/{n_audit} ({pct(audit_bypassed, n_audit)})**",
        "",
        "## Interpretation",
        "",
    ]

    audit_minus_one_lift = (audit_minus_one / n_audit) - (all_minus_one / n_all) if n_audit and n_all else 0.0
    audit_bypass_lift = (audit_bypassed / n_audit) - (all_bypassed / n_all) if n_audit and n_all else 0.0

    if audit_bypass_lift > 0.15:
        lines.append(
            "- The audit slice's **NSVS_bypassed** rate is much higher than the full val baseline "
            f"(+{audit_bypass_lift * 100:.1f} pp). That points to **selection bias**: the disagreement "
            "audit over-samples rows where retrieval failed or was weak."
        )
    elif audit_bypass_lift > 0.05:
        lines.append(
            "- The audit slice is somewhat enriched for bypassed retrieval vs the full val baseline "
            f"(+{audit_bypass_lift * 100:.1f} pp), but not dramatically."
        )
    else:
        lines.append(
            "- The audit slice's bypass rate is close to the full-val rate; high bypass in the audit "
            "reflects **global pipeline behavior**, not slice selection."
        )

    if audit_minus_one_lift > 0.10:
        lines.append(
            f"- Strict `FOI == [-1]` is also enriched in the audit slice (+{audit_minus_one_lift * 100:.1f} pp vs full val)."
        )
    else:
        lines.append(
            f"- Strict `FOI == [-1]` alone is **not** the main driver of the audit's ~80% bypass signal "
            f"(audit {pct(audit_minus_one, n_audit)} vs full val {pct(all_minus_one, n_all)}). "
            "Most audit bypass rows still have a numeric FOI but empty/partial NSVS detections."
        )

    lines.extend(
        [
            "",
            "## Full val — by operator family",
            "",
            "| Operator family | n | FOI == [-1] | % | NSVS bypassed | % |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in op_table:
        lines.append(
            f"| {row['bucket']} | {row['n']} | {row['foi_minus_one_n']} | {row['foi_minus_one_pct']}% | "
            f"{row['nsvs_bypassed_n']} | {row['nsvs_bypassed_pct']}% |"
        )

    lines.extend(
        [
            "",
            "## Full val — by audit duration bucket",
            "",
            "| Duration bucket | n | FOI == [-1] | % | NSVS bypassed | % |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    bucket_order = [label for label, _, _ in AUDIT_DURATION_BUCKETS] + ["unknown"]
    dur_by_name = {row["bucket"]: row for row in dur_table}
    for bucket in bucket_order:
        if bucket not in dur_by_name:
            continue
        row = dur_by_name[bucket]
        lines.append(
            f"| {row['bucket']} | {row['n']} | {row['foi_minus_one_n']} | {row['foi_minus_one_pct']}% | "
            f"{row['nsvs_bypassed_n']} | {row['nsvs_bypassed_pct']}% |"
        )

    lines.extend(
        [
            "",
            "## Audit slice — by operator family",
            "",
            "| Operator family | n | FOI == [-1] | % | NSVS bypassed | % |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in audit_op_table:
        lines.append(
            f"| {row['bucket']} | {row['n']} | {row['foi_minus_one_n']} | {row['foi_minus_one_pct']}% | "
            f"{row['nsvs_bypassed_n']} | {row['nsvs_bypassed_pct']}% |"
        )

    lines.extend(
        [
            "",
            "## Audit slice — by audit duration bucket",
            "",
            "| Duration bucket | n | FOI == [-1] | % | NSVS bypassed | % |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    audit_dur_by_name = {row["bucket"]: row for row in audit_dur_table}
    for bucket in bucket_order:
        if bucket not in audit_dur_by_name:
            continue
        row = audit_dur_by_name[bucket]
        lines.append(
            f"| {row['bucket']} | {row['n']} | {row['foi_minus_one_n']} | {row['foi_minus_one_pct']}% | "
            f"{row['nsvs_bypassed_n']} | {row['nsvs_bypassed_pct']}% |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `FOI == [-1]` means Storm/target-ID merge produced no usable interval.",
            "- `NSVS bypassed` matches the v3 audit auto-triage field (yes or partial).",
            "- Duration buckets match the failure-audit packet stratification (<10s, 10-30s, …).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    entries = load_json(args.entries)
    all_rows = [row_from_entry(entry) for entry in entries]

    audit_qids: set[str] = set()
    if args.audit_csv.exists():
        with args.audit_csv.open(newline="", encoding="utf-8") as f:
            audit_qids = {row["question_id"] for row in csv.DictReader(f)}
    rows_by_qid = {row["question_id"]: row for row in all_rows}
    audit_rows = [rows_by_qid[qid] for qid in sorted(audit_qids, key=int) if qid in rows_by_qid]
    missing = sorted(audit_qids - set(rows_by_qid))
    if missing:
        print(f"[foi-prevalence] warning: audit QIDs missing from entries: {missing}", file=sys.stderr)

    markdown = render_markdown(
        entries_path=args.entries,
        audit_csv=args.audit_csv,
        all_rows=all_rows,
        audit_rows=audit_rows,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown + "\n", encoding="utf-8")

    n_all = len(all_rows)
    all_minus_one = sum(1 for row in all_rows if row["foi_minus_one"])
    all_bypassed = sum(1 for row in all_rows if row["nsvs_bypassed"])
    print(f"[foi-prevalence] wrote {args.out}")
    print(f"[foi-prevalence] full val FOI==[-1]: {all_minus_one}/{n_all} ({pct(all_minus_one, n_all)})")
    print(
        f"[foi-prevalence] full val NSVS bypassed: {all_bypassed}/{n_all} "
        f"({pct(all_bypassed, n_all)})"
    )
    if audit_rows:
        audit_minus_one = sum(1 for row in audit_rows if row["foi_minus_one"])
        audit_bypassed = sum(1 for row in audit_rows if row["nsvs_bypassed"])
        print(
            f"[foi-prevalence] audit slice FOI==[-1]: {audit_minus_one}/{len(audit_rows)} "
            f"({pct(audit_minus_one, len(audit_rows))})"
        )
        print(
            f"[foi-prevalence] audit slice NSVS bypassed: {audit_bypassed}/{len(audit_rows)} "
            f"({pct(audit_bypassed, len(audit_rows))})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
