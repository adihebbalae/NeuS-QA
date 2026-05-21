"""Summarize NSVS / FOI quality for TimeLogic per-entry artifacts.

Reads final `entries.json` and/or incremental `per_entry/*.json` outputs from
`scripts/run_timelogic.py` (including sharded `shard_*/per_entry/` trees).
Writes a markdown report with FOI coverage, length stats, proposition-detection
gaps, and target-identification padding direction mix.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any


DEFAULT_OUTPUT_DIRS = [
    "/home/ah66742/timelogic-data/outputs/sub5b_paper_faithful_3fps_fix2",
    "/home/ah66742/timelogic-data/outputs/nsvs_sub2_v2",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        action="append",
        default=[],
        help="Run output directory (repeatable). Defaults to common Sub #2 / Sub #5B paths.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Markdown report path. Default: <output-dir>/nsvs_quality_report.md",
    )
    parser.add_argument(
        "--label",
        default="",
        help="Human label for the report header (e.g. 'before FOI fix').",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Poll for new per_entry files until interrupted.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=30.0,
        help="Sleep interval between incremental polls.",
    )
    return parser.parse_args()


def discover_per_entry_globs(output_dir: str) -> list[str]:
    patterns = [
        os.path.join(output_dir, "per_entry", "*.json"),
        os.path.join(output_dir, "shard_*", "per_entry", "*.json"),
    ]
    paths: list[str] = []
    for pattern in patterns:
        paths.extend(glob.glob(pattern))
    return sorted(set(paths))


def load_entries_from_dir(output_dir: str) -> list[dict[str, Any]]:
    entries_path = os.path.join(output_dir, "entries.json")
    merged_path = os.path.join(output_dir, "merged", "entries.json")
    for candidate in (entries_path, merged_path):
        if os.path.exists(candidate):
            with open(candidate) as f:
                rows = json.load(f)
            if rows and isinstance(rows[0], dict) and "entry" in rows[0]:
                return [row["entry"] for row in rows if row.get("entry")]
            return rows

    rows: list[dict[str, Any]] = []
    for path in discover_per_entry_globs(output_dir):
        with open(path) as f:
            payload = json.load(f)
        entry = payload.get("entry")
        if entry:
            rows.append(entry)
    return rows


def load_all_entries(output_dirs: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_qids: set[str] = set()
    for output_dir in output_dirs:
        for entry in load_entries_from_dir(output_dir):
            qid = str(entry.get("metadata", {}).get("question_id"))
            if qid in seen_qids:
                continue
            seen_qids.add(qid)
            rows.append(entry)
    return rows


def is_valid_interval(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and value != [-1]
        and value[0] is not None
        and value[1] is not None
        and int(value[0]) <= int(value[1])
    )


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * pct
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def pct(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def parse_signed_seconds(text: str) -> int | None:
    match = re.search(r"([+-])\s*(\d+)", text)
    if not match:
        return None
    return int(match.group(1) + match.group(2))


def parse_target_padding(frame_window: Any) -> dict[str, Any]:
    raw = str(frame_window or "").strip()
    if not raw:
        return {
            "raw": raw,
            "before_start_sec": None,
            "after_end_sec": None,
            "direction": "missing",
        }

    lowered = raw.lower().replace(" ", "")
    if "start_time" in lowered or "end_time" in lowered:
        before = 0
        after = 0
        start_part = raw
        end_part = raw
        if "," in raw:
            start_part, end_part = raw.split(",", 1)
        start_match = re.search(r"start_time\s*-\s*(\d+)", start_part, flags=re.I)
        if start_match:
            before = int(start_match.group(1))
        end_match = re.search(r"end_time\s*\+\s*(\d+)", end_part, flags=re.I)
        if end_match:
            after = int(end_match.group(1))
        direction = classify_padding_direction(before, after)
        return {
            "raw": raw,
            "before_start_sec": before,
            "after_end_sec": after,
            "direction": direction,
            "format": "legacy_placeholder",
        }

    inner = raw.strip("[]")
    parts = [part.strip() for part in inner.split(",")]
    before = parse_signed_seconds(parts[0]) if parts else None
    after = parse_signed_seconds(parts[1]) if len(parts) > 1 else None
    if before is None or after is None:
        return {
            "raw": raw,
            "before_start_sec": before,
            "after_end_sec": after,
            "direction": "unparseable",
            "format": "unknown",
        }

    before = abs(before)
    after = abs(after)
    return {
        "raw": raw,
        "before_start_sec": before,
        "after_end_sec": after,
        "direction": classify_padding_direction(before, after),
        "format": "signed_padding",
    }


def classify_padding_direction(before: int, after: int) -> str:
    if before > 0 and after > 0:
        return "both"
    if before > 0:
        return "before_only"
    if after > 0:
        return "after_only"
    return "none"


def summarize(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(entries)
    non_empty_foi = 0
    foi_minus_one = 0
    foi_lengths_seconds: list[float] = []

    multi_prop_rows = 0
    multi_prop_any_zero_detection = 0

    padding_directions = Counter()
    padding_before_values = Counter()
    padding_after_values = Counter()
    padding_templates = Counter()

    for entry in entries:
        metadata = entry.get("metadata", {})
        fps = float(metadata.get("fps") or 1.0)
        foi = entry.get("frames_of_interest")

        if foi == [-1] or not foi:
            foi_minus_one += 1
        elif is_valid_interval(foi):
            non_empty_foi += 1
            foi_len = int(foi[1]) - int(foi[0]) + 1
            foi_lengths_seconds.append(foi_len / fps)

        propositions = entry.get("puls", {}).get("proposition") or []
        indices = entry.get("nsvs", {}).get("indices")
        if isinstance(propositions, list) and len(propositions) > 1 and isinstance(indices, list):
            multi_prop_rows += 1
            if any(not arr for arr in indices):
                multi_prop_any_zero_detection += 1

        ti = entry.get("target_identification") or {}
        padding = parse_target_padding(ti.get("frame_window"))
        padding_directions[padding["direction"]] += 1
        padding_templates[str(ti.get("frame_window", "")).strip()] += 1
        if padding.get("before_start_sec") is not None:
            padding_before_values[int(padding["before_start_sec"])] += 1
        if padding.get("after_end_sec") is not None:
            padding_after_values[int(padding["after_end_sec"])] += 1

    return {
        "total_entries": total,
        "foi": {
            "non_empty": non_empty_foi,
            "non_empty_pct": pct(non_empty_foi, total),
            "minus_one": foi_minus_one,
            "minus_one_pct": pct(foi_minus_one, total),
            "length_seconds": {
                "count": len(foi_lengths_seconds),
                "p25": percentile(foi_lengths_seconds, 0.25),
                "median": percentile(foi_lengths_seconds, 0.50),
                "p75": percentile(foi_lengths_seconds, 0.75),
                "p95": percentile(foi_lengths_seconds, 0.95),
            },
        },
        "multi_proposition": {
            "rows": multi_prop_rows,
            "any_zero_detection": multi_prop_any_zero_detection,
            "any_zero_detection_pct": pct(multi_prop_any_zero_detection, multi_prop_rows),
        },
        "target_padding": {
            "direction": dict(padding_directions),
            "before_start_sec": dict(padding_before_values),
            "after_end_sec": dict(padding_after_values),
            "top_templates": padding_templates.most_common(10),
        },
    }


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def render_markdown(
    summary: dict[str, Any],
    output_dirs: list[str],
    label: str,
    incremental: bool,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    foi = summary["foi"]
    multi = summary["multi_proposition"]
    padding = summary["target_padding"]
    title = label or "NSVS quality probe"
    lines = [
        f"# NSVS Quality Probe — {title}",
        "",
        f"- Generated: {now}",
        f"- Output dir(s): {', '.join(output_dirs)}",
        f"- Mode: {'incremental (latest snapshot)' if incremental else 'one-shot'}",
        f"- Entries analyzed: {summary['total_entries']}",
        "",
        "## FOI coverage",
        "",
        f"- Non-empty FOI: {foi['non_empty']}/{summary['total_entries']} ({foi['non_empty_pct']:.2f}%)",
        f"- FOI `[-1]`: {foi['minus_one']}/{summary['total_entries']} ({foi['minus_one_pct']:.2f}%)",
        "",
        "## FOI length (seconds, valid intervals only)",
        "",
        "| stat | value |",
        "|---|---:|",
        f"| count | {foi['length_seconds']['count']} |",
        f"| p25 | {fmt(foi['length_seconds']['p25'])} |",
        f"| median | {fmt(foi['length_seconds']['median'])} |",
        f"| p75 | {fmt(foi['length_seconds']['p75'])} |",
        f"| p95 | {fmt(foi['length_seconds']['p95'])} |",
        "",
        "## Multi-proposition zero-detection rate",
        "",
        "Rows with more than one PULS proposition where at least one `nsvs.indices` array is empty.",
        "",
        f"- Rows: {multi['rows']}",
        f"- Any zero-detection proposition: {multi['any_zero_detection']}/{multi['rows']} ({multi['any_zero_detection_pct']:.2f}%)",
        "",
        "## Target-ID padding direction",
        "",
        "Direction buckets classify parsed `target_identification.frame_window` padding relative to the NSVS interval.",
        "",
        "| direction | count | share |",
        "|---|---:|---:|",
    ]

    direction_total = sum(padding["direction"].values()) or 1
    for direction, count in sorted(padding["direction"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {direction} | {count} | {count / direction_total * 100:.2f}% |")

    lines.extend(
        [
            "",
            "### Parsed before/after second counts",
            "",
            f"- Before-start seconds: {dict(sorted(padding['before_start_sec'].items()))}",
            f"- After-end seconds: {dict(sorted(padding['after_end_sec'].items()))}",
            "",
            "### Top raw target-ID templates",
            "",
        ]
    )
    for template, count in padding["top_templates"]:
        lines.append(f"- `{template}`: {count}")

    return "\n".join(lines) + "\n"


def write_report(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def run_once(args: argparse.Namespace, output_dirs: list[str]) -> dict[str, Any]:
    entries = load_all_entries(output_dirs)
    summary = summarize(entries)
    report_path = args.report
    if not report_path:
        report_path = os.path.join(output_dirs[0], "nsvs_quality_report.md")
    content = render_markdown(summary, output_dirs, args.label, args.incremental)
    write_report(report_path, content)
    print(content)
    print(f"wrote: {report_path}")
    return summary


def main() -> int:
    args = parse_args()
    output_dirs = args.output_dir or DEFAULT_OUTPUT_DIRS

    if args.incremental:
        try:
            while True:
                summary = run_once(args, output_dirs)
                print(
                    f"[incremental] entries={summary['total_entries']} "
                    f"non_empty_foi={summary['foi']['non_empty']} "
                    f"sleep={args.poll_seconds}s",
                    file=sys.stderr,
                )
                time.sleep(args.poll_seconds)
        except KeyboardInterrupt:
            print("[incremental] stopped", file=sys.stderr)
            return 0

    run_once(args, output_dirs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
