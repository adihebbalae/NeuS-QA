#!/usr/bin/env python3
"""Offline analysis for Sub #5B test-phase run (no hidden labels).

Writes summary JSON + markdown report: pipeline health, submission distribution,
NSVS/FOI quality, VQA diagnostics, and val-vs-test sanity checks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from compare_submissions import (  # noqa: E402
    duration_bucket,
    duration_seconds,
    foi_status,
    load_entries,
    load_submission,
    valid_foi,
)
from nsvs_quality_probe import load_entries_from_dir, summarize  # noqa: E402


DEFAULT_BASE = "/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps"
DEFAULT_VAL_BASE = "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2"
DEFAULT_VAL_SUB = f"{DEFAULT_VAL_BASE}/submission_sub5b_paper_faithful_gpt52.json"
DEFAULT_OUT = "/mnt/Data/ah66742/timelogic/outputs/diagnostics/sub5b_test"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default=DEFAULT_BASE, help="Sub #5B test run output dir")
    p.add_argument("--val-base", default=DEFAULT_VAL_BASE, help="Val Sub #5B run for comparison")
    p.add_argument("--val-sub", default=DEFAULT_VAL_SUB, help="Val submission JSON")
    p.add_argument("--out-dir", default=DEFAULT_OUT, help="Diagnostics output directory")
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)


def pct(n: int, d: int) -> float:
    return 0.0 if d == 0 else round(100.0 * n / d, 2)


def distribution(rows: dict[str, str] | list[str]) -> dict[str, int]:
    if isinstance(rows, dict):
        values = list(rows.values())
    else:
        values = list(rows)
    return dict(Counter(values))


def distribution_by_mode(
    answers: dict[str, str],
    entries: dict[str, dict[str, Any]],
) -> dict[str, dict[str, int]]:
    out: dict[str, Counter] = defaultdict(Counter)
    for qid, ans in answers.items():
        mode = entries.get(qid, {}).get("metadata", {}).get("mode", "unknown")
        out[str(mode)][ans] += 1
    return {mode: dict(counter) for mode, counter in out.items()}


def bucket_breakdown(
    entries: dict[str, dict[str, Any]],
    field: str,
) -> dict[str, dict[str, int]]:
    buckets: dict[str, Counter] = defaultdict(Counter)
    for qid, entry in entries.items():
        metadata = entry.get("metadata", {})
        if field == "duration_bucket":
            value = duration_bucket(duration_seconds(entry))
        elif field == "foi_status":
            value = foi_status(entry.get("frames_of_interest"))
        else:
            value = str(metadata.get(field, "unknown"))
        buckets[value]["total"] += 1
        if valid_foi(entry.get("frames_of_interest")):
            buckets[value]["valid_foi"] += 1
    return {
        key: {"total": counter["total"], "valid_foi": counter.get("valid_foi", 0)}
        for key, counter in sorted(buckets.items())
    }


def upload_safety(dist: dict[str, int]) -> dict[str, Any]:
    total = sum(dist.values())
    top_label, top_n = Counter(dist).most_common(1)[0]
    top_pct = pct(top_n, total)
    return {
        "total_rows": total,
        "top_label": top_label,
        "top_count": top_n,
        "top_pct": top_pct,
        "upload_safe": top_n < total,
        "distribution": dist,
    }


def vqa_diagnostics(path: str) -> dict[str, Any]:
    rows = load_json(path)
    errors = [row for row in rows if row.get("error")]
    frame_counts = [int(row.get("num_frames") or 0) for row in rows]
    seconds = [float(row.get("seconds") or 0) for row in rows if row.get("seconds") is not None]
    return {
        "total_rows": len(rows),
        "error_count": len(errors),
        "error_qids": [str(row.get("qid")) for row in errors],
        "error_messages": [str(row.get("error"))[:200] for row in errors],
        "fallback_answers_on_error": {str(row.get("qid")): row.get("answer") for row in errors},
        "num_frames": {
            "min": min(frame_counts) if frame_counts else None,
            "max": max(frame_counts) if frame_counts else None,
            "zero_frames": sum(1 for n in frame_counts if n == 0),
            "median_bucket": Counter(frame_counts).most_common(1)[0] if frame_counts else None,
        },
        "vqa_seconds": {
            "mean": round(sum(seconds) / len(seconds), 2) if seconds else None,
            "max": round(max(seconds), 2) if seconds else None,
        },
    }


def compare_distributions(test_dist: dict[str, int], val_dist: dict[str, int]) -> dict[str, Any]:
    keys = sorted(set(test_dist) | set(val_dist))
    test_total = sum(test_dist.values())
    val_total = sum(val_dist.values())
    rows = []
    for key in keys:
        t = test_dist.get(key, 0)
        v = val_dist.get(key, 0)
        rows.append(
            {
                "label": key,
                "test_count": t,
                "test_pct": pct(t, test_total),
                "val_count": v,
                "val_pct": pct(v, val_total),
                "delta_pct": round(pct(t, test_total) - pct(v, val_total), 2),
            }
        )
    return {"rows": rows, "test_total": test_total, "val_total": val_total}


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Sub #5B Test Analysis",
        "",
        f"- Generated: {summary['generated_at']}",
        f"- Test run: `{summary['paths']['base']}`",
        f"- Val reference: `{summary['paths']['val_base']}`",
        "",
        "## Pipeline health",
        "",
    ]
    for name, ok in summary["artifacts"].items():
        lines.append(f"- {'✅' if ok else '❌'} {name}")
    lines.extend(
        [
            "",
            f"- Submission rows: **{summary['submission']['row_count']}** (expected 3000)",
            f"- Upload safety: **{'OK' if summary['submission']['upload_safe']['upload_safe'] else 'BAN RISK'}** "
            f"(top label `{summary['submission']['upload_safe']['top_label']}` "
            f"{summary['submission']['upload_safe']['top_pct']}%)",
            "",
            "## Submission distribution",
            "",
            "### Overall",
            "",
            "| label | count | pct |",
            "|---|---:|---:|",
        ]
    )
    total = summary["submission"]["row_count"]
    for label, count in Counter(summary["submission"]["upload_safe"]["distribution"]).most_common():
        lines.append(f"| {label} | {count} | {pct(count, total)}% |")

    lines.extend(["", "### By mode", ""])
    for mode, dist in summary["submission"]["by_mode"].items():
        mode_total = sum(dist.values())
        lines.append(f"**{mode}** (n={mode_total})")
        lines.append("")
        lines.append("| label | count | pct |")
        lines.append("|---|---:|---:|")
        for label, count in Counter(dist).most_common():
            lines.append(f"| {label} | {count} | {pct(count, mode_total)}% |")
        lines.append("")

    foi = summary["nsvs"]["foi"]
    val_foi = summary["val_comparison"]["nsvs_foi"]
    lines.extend(
        [
            "## NSVS / FOI quality (test)",
            "",
            f"- Non-empty FOI: **{foi['non_empty']}/{summary['nsvs']['total_entries']}** ({foi['non_empty_pct']:.2f}%)",
            f"- FOI `[-1]`: **{foi['minus_one']}/{summary['nsvs']['total_entries']}** ({foi['minus_one_pct']:.2f}%)",
            f"- Val non-empty FOI (reference): **{val_foi['non_empty_pct']:.2f}%** on processed entries",
            "",
            "## VQA diagnostics",
            "",
            f"- Errors: **{summary['vqa']['error_count']}**",
        ]
    )
    if summary["vqa"]["error_qids"]:
        lines.append(f"- Error QIDs: {', '.join(summary['vqa']['error_qids'])} (fallback answers: {summary['vqa']['fallback_answers_on_error']})")
    lines.extend(
        [
            f"- Zero-frame answers: **{summary['vqa']['num_frames']['zero_frames']}**",
            f"- Mean VQA latency: **{summary['vqa']['vqa_seconds']['mean']}s**",
            "",
            "## Breakdown by source dataset",
            "",
            "| source | total | valid FOI | valid FOI % |",
            "|---|---:|---:|---:|",
        ]
    )
    for source, row in summary["breakdowns"]["source_dataset"].items():
        lines.append(
            f"| {source} | {row['total']} | {row['valid_foi']} | {pct(row['valid_foi'], row['total'])}% |"
        )

    lines.extend(
        [
            "",
            "## Breakdown by duration bucket",
            "",
            "| bucket | total | valid FOI | valid FOI % |",
            "|---|---:|---:|---:|",
        ]
    )
    for bucket, row in summary["breakdowns"]["duration_bucket"].items():
        lines.append(
            f"| {bucket} | {row['total']} | {row['valid_foi']} | {pct(row['valid_foi'], row['total'])}% |"
        )

    lines.extend(
        [
            "",
            "## Val vs test answer distribution",
            "",
            "| label | test % | val % | delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in summary["val_comparison"]["answer_distribution"]["rows"]:
        lines.append(
            f"| {row['label']} | {row['test_pct']} | {row['val_pct']} | {row['delta_pct']:+} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- No hidden test labels locally — this is a pipeline/submission sanity report, not accuracy.",
            "- Upload to EvalAI test phase when ready; record score in `RESULTS.md`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    base = args.base
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    sub_path = os.path.join(base, "submission_sub5b_test_gpt52.json")
    entries_path = os.path.join(base, "merged", "entries.json")
    diag_path = os.path.join(base, "answers_gpt_5_2", "answers_diag.json")

    artifacts = {
        "DONE marker": os.path.isfile(os.path.join(base, "DONE")),
        "merged/entries.json": os.path.isfile(entries_path),
        "postprocess/postprocess_entries.json": os.path.isfile(
            os.path.join(base, "postprocess", "postprocess_entries.json")
        ),
        "answers_gpt_5_2/submission_partial.json": os.path.isfile(
            os.path.join(base, "answers_gpt_5_2", "submission_partial.json")
        ),
        "submission_sub5b_test_gpt52.json": os.path.isfile(sub_path),
        "answers_diag.json": os.path.isfile(diag_path),
    }

    answers = load_submission(sub_path)
    entries_list = load_entries_from_dir(base)
    entries = load_entries(entries_path)
    nsvs_summary = summarize(entries_list)

    val_entries = load_entries(os.path.join(args.val_base, "merged", "entries.json"))
    val_answers = load_submission(args.val_sub) if os.path.isfile(args.val_sub) else {}
    val_nsvs = summarize(load_entries_from_dir(args.val_base))

    summary: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "phase": "test",
        "pipeline": "Sub #5B paper-faithful @ 3fps + ffmpeg crop + gpt-5.2 VQA",
        "paths": {
            "base": base,
            "val_base": args.val_base,
            "out_dir": out_dir,
            "submission": sub_path,
        },
        "artifacts": artifacts,
        "submission": {
            "row_count": len(answers),
            "upload_safe": upload_safety(distribution(answers)),
            "by_mode": distribution_by_mode(answers, entries),
        },
        "nsvs": nsvs_summary,
        "vqa": vqa_diagnostics(diag_path),
        "breakdowns": {
            "source_dataset": bucket_breakdown(entries, "source_dataset"),
            "operator_guess": bucket_breakdown(entries, "operator_guess"),
            "duration_bucket": bucket_breakdown(entries, "duration_bucket"),
            "foi_status": bucket_breakdown(entries, "foi_status"),
            "mode": bucket_breakdown(entries, "mode"),
        },
        "val_comparison": {
            "nsvs_foi": val_nsvs["foi"],
            "answer_distribution": compare_distributions(distribution(answers), distribution(val_answers)),
            "foi_rate_delta_pct": round(
                nsvs_summary["foi"]["non_empty_pct"] - val_nsvs["foi"]["non_empty_pct"],
                2,
            ),
        },
        "merge_summary": load_json(os.path.join(base, "merged", "merge_summary.json"))
        if os.path.isfile(os.path.join(base, "merged", "merge_summary.json"))
        else None,
    }

    summary_path = os.path.join(out_dir, "summary.json")
    report_path = os.path.join(out_dir, "analysis.md")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    with open(report_path, "w") as f:
        f.write(render_markdown(summary))

    print(f"Wrote {summary_path}")
    print(f"Wrote {report_path}")
    print()
    print(render_markdown(summary))


if __name__ == "__main__":
    main()
