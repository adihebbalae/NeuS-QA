#!/usr/bin/env python3
"""Analyze atemporal-MC prototype runs → report.md + per_row.csv.

Reads diagnostics/atemporal_mc_prototype/runs/qid_*.json and manifest.json.
Headline metric: median differentiation_gap (argmax NSVS score − runner-up).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_RUNS = REPO_ROOT / "diagnostics/atemporal_mc_prototype/runs"
DEFAULT_MANIFEST = REPO_ROOT / "diagnostics/atemporal_mc_prototype/manifest.json"
DEFAULT_REPORT_DIR = REPO_ROOT / "diagnostics/atemporal_mc_prototype/report"

LETTERS = ("A", "B", "C", "D")

GAP_SHIP = 0.20
GAP_INSPECT_LO = 0.05


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    return p.parse_args()


def load_manifest(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["qid"]: row for row in data.get("rows", [])}


def nsvs_score(choice: dict[str, Any] | None) -> float | None:
    if not choice:
        return None
    det = choice.get("detection_score") or {}
    prob = det.get("max_probability")
    if prob is not None:
        return float(prob)
    return None


def choice_by_letter(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for c in run.get("choices") or []:
        letter = c.get("choice_letter")
        if letter:
            out[str(letter)] = c
    return out


def argmax_runner_up(scores: dict[str, float | None]) -> tuple[str | None, float | None, float | None, float | None]:
    """Return (argmax_letter, argmax_score, runner_up_score, gap)."""
    valid = [(L, s) for L, s in scores.items() if s is not None]
    if not valid:
        return None, None, None, None
    valid.sort(key=lambda x: x[1], reverse=True)
    arg_letter, arg_score = valid[0]
    if len(valid) == 1:
        return arg_letter, arg_score, None, None
    _, run_score = valid[1]
    gap = arg_score - run_score
    return arg_letter, arg_score, run_score, gap


def recommendation_from_median(median_gap: float | None) -> tuple[str, str]:
    if median_gap is None:
        return "INSPECT", "No valid differentiation_gap values (runs missing or incomplete)."
    if median_gap >= GAP_SHIP:
        return (
            "SHIP",
            f"Median differentiation_gap {median_gap:.3f} ≥ {GAP_SHIP:.2f} — NSVS produces "
            "differentiated per-choice signal; scale atemporal-MC mode to all 88 Bucket-A rows for val.",
        )
    if median_gap >= GAP_INSPECT_LO:
        return (
            "INSPECT",
            f"Median differentiation_gap {median_gap:.3f} in [{GAP_INSPECT_LO:.2f}, {GAP_SHIP:.2f}) — "
            "mixed signal; review per-stratum and long-vs-short before scaling.",
        )
    return (
        "KILL",
        f"Median differentiation_gap {median_gap:.3f} < {GAP_INSPECT_LO:.2f} — NSVS scores are "
        "near-uniform across choices at this clip-length regime; do not scale this NSVS path. "
        "Recommend fallback: direct per-choice binary VQA (separate experiment).",
    )


def build_per_row(
    run: dict[str, Any],
    manifest_row: dict[str, Any] | None,
) -> dict[str, Any]:
    m = manifest_row or {}
    by_letter = choice_by_letter(run)

    row: dict[str, Any] = {
        "qid": run.get("qid"),
        "video_id": run.get("video_id") or m.get("video_id"),
        "source_dataset": run.get("source_dataset") or m.get("source_dataset"),
        "video_duration_sec": run.get("video_duration_sec") if run.get("video_duration_sec") is not None else m.get("video_duration_sec"),
        "stratum": run.get("stratum") or m.get("stratum"),
        "stem": run.get("stem") or m.get("stem"),
        "run_status": run.get("status"),
        "sub5b_current_answer": m.get("sub5b_current_answer", ""),
        "sub1_current_answer": m.get("sub1_current_answer", ""),
    }

    scores: dict[str, float | None] = {}
    for letter in LETTERS:
        c = by_letter.get(letter)
        opt = m.get("options") or []
        text = ""
        if c:
            text = c.get("option_text") or ""
        if not text and opt:
            text = next((o["text"] for o in opt if o.get("letter") == letter), "")
        score = nsvs_score(c)
        scores[letter] = score
        row[f"choice_{letter}_text"] = text
        row[f"choice_{letter}_spec"] = (c or {}).get("specification", "")
        row[f"choice_{letter}_proposition"] = (c or {}).get("proposition", "")
        row[f"choice_{letter}_nsvs_score"] = score if score is not None else ""
        row[f"choice_{letter}_n_windows"] = (c or {}).get("n_grounded_windows", "")
        row[f"choice_{letter}_satisfied"] = (c or {}).get("tl_satisfaction", "")

    arg_letter, arg_score, run_score, gap = argmax_runner_up(scores)
    row["argmax_choice"] = arg_letter or ""
    row["argmax_score"] = arg_score if arg_score is not None else ""
    row["runner_up_score"] = run_score if run_score is not None else ""
    row["differentiation_gap"] = gap if gap is not None else ""
    sub1 = str(row.get("sub1_current_answer") or "")
    row["argmax_matches_sub1"] = (
        bool(arg_letter and sub1 and arg_letter == sub1)
    )

    return row


def median_of(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def stratum_bucket(stratum: str) -> str:
    if stratum == "long_ct":
        return "long (CT ≥60s)"
    if stratum in ("short_star_agqa", "mid_agqa"):
        return "short (STAR/AGQA <10s)"
    return stratum or "unknown"


def render_report(
    per_rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    runs_dir: Path,
    gaps: list[float],
    median_gap: float | None,
    verdict: str,
    justification: str,
) -> str:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    n = len(per_rows)
    n_with_gap = len(gaps)

    lines.append("# Atemporal-MC prototype — analysis report")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append(f"Runs: `{runs_dir}` · Manifest rows: {len(manifest.get('rows', []))} · Analyzed: {n}")
    lines.append("")

    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"**{verdict}** — {justification}")
    lines.append("")

    lines.append("## Headline metric")
    lines.append("")
    if median_gap is None:
        lines.append("- **Median differentiation_gap:** *(no data)*")
    else:
        lines.append(f"- **Median differentiation_gap:** **{median_gap:.4f}** ({n_with_gap}/{n} rows with scores)")
    lines.append("")
    lines.append("Decision thresholds (mechanical):")
    lines.append(f"- **≥ {GAP_SHIP:.2f}** → **SHIP** — scale to all 88 Bucket-A rows for val submission.")
    lines.append(f"- **{GAP_INSPECT_LO:.2f}–{GAP_SHIP:.2f}** → **INSPECT** — mixed signal; per-stratum review.")
    lines.append(f"- **< {GAP_INSPECT_LO:.2f}** → **KILL** — no choice-level NSVS signal; use per-choice VQA fallback instead.")
    lines.append("")

    lines.append("## Per-stratum differentiation_gap")
    lines.append("")
    by_stratum: dict[str, list[float]] = defaultdict(list)
    for r in per_rows:
        g = r.get("differentiation_gap")
        if g != "" and g is not None:
            by_stratum[str(r.get("stratum", "unknown"))].append(float(g))
    if not by_stratum:
        lines.append("*(no gaps)*")
    else:
        lines.append("| Stratum | n | median gap | mean gap |")
        lines.append("|---------|---|------------|----------|")
        for strat in sorted(by_stratum):
            vals = by_stratum[strat]
            lines.append(
                f"| `{strat}` | {len(vals)} | {median_of(vals):.4f} | {statistics.mean(vals):.4f} |"
            )
    lines.append("")

    lines.append("### Long vs short (critical)")
    lines.append("")
    long_gaps: list[float] = []
    short_gaps: list[float] = []
    for r in per_rows:
        g = r.get("differentiation_gap")
        if g == "" or g is None:
            continue
        g = float(g)
        bucket = stratum_bucket(str(r.get("stratum", "")))
        if bucket.startswith("long"):
            long_gaps.append(g)
        elif bucket.startswith("short"):
            short_gaps.append(g)
    lines.append(f"- **Long (CT ≥60s):** n={len(long_gaps)}, median gap={median_of(long_gaps)}")
    lines.append(f"- **Short (STAR/AGQA <10s):** n={len(short_gaps)}, median gap={median_of(short_gaps)}")
    lines.append("")
    if long_gaps and short_gaps:
        ml, ms = median_of(long_gaps), median_of(short_gaps)
        if ml is not None and ms is not None:
            if ml >= GAP_SHIP and ms < GAP_INSPECT_LO:
                lines.append(
                    "> Long clips show differentiated NSVS scores while shorts are uniform — "
                    "failure mode is **NSVS-on-short-clips**, not the per-choice conditioning idea."
                )
            elif ml < GAP_INSPECT_LO and ms < GAP_INSPECT_LO:
                lines.append("> Both long and short strata show uniformly low gaps in this sample.")
            else:
                lines.append("> Mixed long/short pattern — see per-row table.")
    lines.append("")

    lines.append("## Argmax vs Sub #1 proxy (weak; n≈10, Sub #1 ≠ GT)")
    lines.append("")
    disagree_sub5b = [
        r for r in per_rows
        if r.get("argmax_choice")
        and r.get("sub5b_current_answer")
        and r["argmax_choice"] != r["sub5b_current_answer"]
    ]
    agree_sub1 = [
        r for r in disagree_sub5b
        if r.get("argmax_matches_sub1")
    ]
    lines.append(
        f"- Rows where **argmax ≠ Sub #5B** answer: **{len(disagree_sub5b)}** / {n}"
    )
    if disagree_sub5b:
        lines.append(
            f"- Of those, argmax **matches Sub #1**: **{len(agree_sub1)}** / {len(disagree_sub5b)} "
            f"({100 * len(agree_sub1) / len(disagree_sub5b):.0f}%)"
        )
    else:
        lines.append("- Of those, argmax matches Sub #1: *(none — argmax agreed with Sub #5B on all rows)*")
    lines.append("")
    lines.append("*Do not over-interpret; 10-row prototype only.*")
    lines.append("")

    lines.append("## Spec quality spot-check (PULS propositions per row)")
    lines.append("")
    for r in per_rows:
        qid = r.get("qid")
        lines.append(f"### QID {qid} · `{r.get('video_id')}` · {r.get('stratum')} · {r.get('run_status')}")
        lines.append("")
        lines.append(f"- Stem: {r.get('stem')}")
        lines.append(f"- Duration: {r.get('video_duration_sec')}s · Sub #5B: **{r.get('sub5b_current_answer')}** · Sub #1: **{r.get('sub1_current_answer')}**")
        lines.append(f"- Argmax: **{r.get('argmax_choice')}** (score {r.get('argmax_score')}, gap {r.get('differentiation_gap')})")
        lines.append("")
        for letter in LETTERS:
            prop = r.get(f"choice_{letter}_proposition") or "—"
            spec = r.get(f"choice_{letter}_spec") or "—"
            sc = r.get(f"choice_{letter}_nsvs_score")
            sat = r.get(f"choice_{letter}_satisfied")
            lines.append(
                f"- **{letter}:** `{prop}` · spec `{spec}` · "
                f"NSVS max_p={sc if sc != '' else '—'} · satisfied={sat}"
            )
        lines.append("")

    lines.append("## Per-row summary")
    lines.append("")
    lines.append("| qid | stratum | dur(s) | gap | argmax | Sub5B | Sub1 | match Sub1 |")
    lines.append("|-----|---------|--------|-----|--------|-------|------|------------|")
    for r in sorted(per_rows, key=lambda x: x.get("qid", 0)):
        lines.append(
            f"| {r.get('qid')} | {r.get('stratum')} | {r.get('video_duration_sec')} | "
            f"{r.get('differentiation_gap')} | {r.get('argmax_choice')} | "
            f"{r.get('sub5b_current_answer')} | {r.get('sub1_current_answer')} | "
            f"{r.get('argmax_matches_sub1')} |"
        )
    lines.append("")
    lines.append("Full columns: `report/per_row.csv`")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    manifest_data = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_by_qid = load_manifest(args.manifest)

    qid_files = sorted(args.runs_dir.glob("qid_*.json"))
    if not qid_files:
        print(f"No qid_*.json under {args.runs_dir}", file=sys.stderr)
        return 1

    per_rows: list[dict[str, Any]] = []
    for path in qid_files:
        run = json.loads(path.read_text(encoding="utf-8"))
        qid = run.get("qid")
        per_rows.append(build_per_row(run, manifest_by_qid.get(qid)))

    per_rows.sort(key=lambda r: r.get("qid", 0))

    gaps = [
        float(r["differentiation_gap"])
        for r in per_rows
        if r.get("differentiation_gap") not in ("", None)
    ]
    median_gap = median_of(gaps)
    verdict, justification = recommendation_from_median(median_gap)

    args.report_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.report_dir / "per_row.csv"

    csv_columns = [
        "qid",
        "video_id",
        "source_dataset",
        "video_duration_sec",
        "stratum",
        "stem",
    ]
    for letter in LETTERS:
        csv_columns.extend(
            [
                f"choice_{letter}_text",
                f"choice_{letter}_spec",
                f"choice_{letter}_nsvs_score",
                f"choice_{letter}_n_windows",
                f"choice_{letter}_satisfied",
            ]
        )
    csv_columns.extend(
        [
            "argmax_choice",
            "argmax_score",
            "runner_up_score",
            "differentiation_gap",
            "sub5b_current_answer",
            "sub1_current_answer",
            "argmax_matches_sub1",
            "run_status",
        ]
    )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_columns, extrasaction="ignore")
        w.writeheader()
        for r in per_rows:
            w.writerow(r)

    report_md = render_report(
        per_rows,
        manifest_data,
        args.runs_dir,
        gaps,
        median_gap,
        verdict,
        justification,
    )
    report_path = args.report_dir.parent / "report.md"
    report_path.write_text(report_md, encoding="utf-8")

    summary = {
        "n_rows": len(per_rows),
        "median_differentiation_gap": median_gap,
        "recommendation": verdict,
        "gaps": gaps,
    }
    (args.report_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Wrote {report_path}")
    print(f"Wrote {csv_path}")
    print(f"Recommendation: {verdict} — {justification}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
