#!/usr/bin/env python3
"""Quantify Sub #5B A/Yes positional bias vs FOI / NSVS bypass status.

Offline diagnostic — zero API. Reads Sub #5B merged entries, Sub #1 answers,
and Sub #5B submission. Emits per-row details.csv and a markdown report with
answer-distribution tables and counterfactual swap estimates.
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

from compare_submissions import load_submission  # noqa: E402

DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_SUB5B = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_SUB1 = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json")
DEFAULT_DETAILS_CSV = [
    REPO_ROOT / "diagnostics" / "sub1_vs_sub5b_fix2" / "details.csv",
    Path("/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/details.csv"),
]
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "sub5b_bias_quantification"
EVAL_N = 2000
SCORE_SUB1 = 50.5
SCORE_SUB5B = 53.35


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--sub5b", type=Path, default=DEFAULT_SUB5B)
    p.add_argument("--sub1", type=Path, default=DEFAULT_SUB1)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--score-sub1", type=float, default=SCORE_SUB1)
    p.add_argument("--score-sub5b", type=float, default=SCORE_SUB5B)
    p.add_argument("--eval-n", type=int, default=EVAL_N)
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_details_csv() -> dict[str, dict[str, str]] | None:
    for path in DEFAULT_DETAILS_CSV:
        if not path.exists():
            continue
        rows: dict[str, dict[str, str]] = {}
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                qid = str(row["question_id"])
                rows[qid] = row
        return rows
    return None


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


def nsvs_indices_flags(entry: dict[str, Any]) -> dict[str, int | bool]:
    indices = entry.get("nsvs", {}).get("indices")
    if not isinstance(indices, list) or not indices:
        return {"total_arrays": 0, "empty_count": 0, "all_empty": False, "any_empty": False}
    empty_count = sum(1 for arr in indices if not arr)
    return {
        "total_arrays": len(indices),
        "empty_count": empty_count,
        "all_empty": empty_count == len(indices),
        "any_empty": empty_count > 0,
    }


def classify_foi_status(entry: dict[str, Any] | None) -> str:
    """clean / partial / bypassed / missing_video."""
    if entry is None:
        return "missing_video"
    foi = entry.get("frames_of_interest")
    idx = nsvs_indices_flags(entry)
    if foi_is_minus_one(foi) or idx["all_empty"]:
        return "bypassed"
    if idx["any_empty"]:
        return "partial"
    return "clean"


def question_mode(metadata: dict[str, Any]) -> str:
    mode = (metadata.get("mode") or "unknown").lower()
    return "bool" if mode == "bool" else "mc"


def pct(n: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{n / total * 100:.1f}%"


def pct_num(n: int, total: int) -> float:
    if not total:
        return 0.0
    return round(n / total * 100, 1)


def distribution_table(
    rows: list[dict[str, Any]],
    answer_key: str = "sub5b_answer",
    group_key: str = "foi_status",
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[group_key])].append(row)

    table: list[dict[str, Any]] = []
    for group, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        n = len(items)
        answers = Counter(item[answer_key] for item in items)
        bool_items = [item for item in items if item["question_mode"] == "bool"]
        mc_items = [item for item in items if item["question_mode"] == "mc"]
        yes_n = sum(1 for item in bool_items if item[answer_key] == "Yes")
        no_n = sum(1 for item in bool_items if item[answer_key] == "No")
        a_n = sum(1 for item in mc_items if item[answer_key] == "A")
        table.append(
            {
                "group": group,
                "n": n,
                "answers": dict(answers.most_common()),
                "bool_yes": yes_n,
                "bool_no": no_n,
                "bool_yes_pct": pct_num(yes_n, yes_n + no_n),
                "mc_a": a_n,
                "mc_n": len(mc_items),
                "mc_a_pct": pct_num(a_n, len(mc_items)),
            }
        )
    return table


def render_answer_counts(answers: dict[str, int]) -> str:
    order = ["Yes", "No", "A", "B", "C", "D"]
    parts = [f"{k}:{answers[k]}" for k in order if answers.get(k)]
    extras = [k for k in answers if k not in order]
    parts.extend(f"{k}:{answers[k]}" for k in sorted(extras))
    return " ".join(parts) if parts else "—"


def counterfactual_swap(
    rows: list[dict[str, Any]],
    *,
    slice_key: str,
    slice_values: set[str],
    score_sub1: float,
    score_sub5b: float,
    eval_n: int,
) -> dict[str, Any]:
    """Estimate accuracy delta if sub5b answers on slice_values rows become sub1."""
    slice_rows = [r for r in rows if r[slice_key] in slice_values]
    disagree = [r for r in slice_rows if r["sub5b_answer"] != r["sub1_answer"]]
    agree = [r for r in slice_rows if r["sub5b_answer"] == r["sub1_answer"]]

    n_slice = len(slice_rows)
    n_disagree = len(disagree)
    n_agree = len(agree)

    correct_sub5b = round(score_sub5b / 100 * eval_n)
    correct_sub1 = round(score_sub1 / 100 * eval_n)
    net_sub5b_minus_sub1 = correct_sub5b - correct_sub1

    # On all disagreements (full val), Sub #5B leads by net_sub5b_minus_sub1.
    total_disagree = sum(1 for r in rows if r["sub5b_answer"] != r["sub1_answer"])
    sub5b_win_rate_all_disagree = (
        (total_disagree + net_sub5b_minus_sub1) / (2 * total_disagree) if total_disagree else 0.5
    )
    sub1_win_rate_all_disagree = 1.0 - sub5b_win_rate_all_disagree

    scenarios: list[dict[str, Any]] = []
    for label, p_sub1_wins in [
        ("pessimistic_sub5b_wins_all", 0.0),
        ("overall_disagree_rate", sub1_win_rate_all_disagree),
        ("neutral_50_50", 0.5),
        ("optimistic_sub1_wins_all", 1.0),
    ]:
        # Delta correct vs current sub5b submission on slice disagreements only.
        delta_correct = (2 * p_sub1_wins - 1) * n_disagree
        delta_pp = delta_correct / eval_n * 100
        scenarios.append(
            {
                "label": label,
                "p_sub1_wins_on_slice_disagreements": round(p_sub1_wins, 3),
                "delta_correct_rows": round(delta_correct, 1),
                "delta_accuracy_pp": round(delta_pp, 2),
                "estimated_new_accuracy_pct": round(score_sub5b + delta_pp, 2),
            }
        )

    return {
        "slice_key": slice_key,
        "slice_values": sorted(slice_values),
        "n_slice": n_slice,
        "n_agree": n_agree,
        "n_disagree": n_disagree,
        "answers_changed": n_disagree,
        "current_sub5b_accuracy_pct": score_sub5b,
        "sub1_win_rate_all_disagree_proxy": round(sub1_win_rate_all_disagree, 3),
        "sub5b_win_rate_all_disagree_proxy": round(sub5b_win_rate_all_disagree, 3),
        "scenarios": scenarios,
    }


def build_rows(
    entries: list[dict[str, Any]],
    sub1: dict[str, str],
    sub5b: dict[str, str],
    details_csv: dict[str, dict[str, str]] | None,
) -> list[dict[str, Any]]:
    entries_by_qid: dict[str, dict[str, Any]] = {}
    for entry in entries:
        metadata = entry.get("metadata", {})
        qid = str(metadata.get("question_id") or entry.get("question_id"))
        entries_by_qid[qid] = entry

    all_qids = sorted(set(sub1) | set(sub5b), key=lambda x: int(x) if x.isdigit() else x)
    rows: list[dict[str, Any]] = []
    for qid in all_qids:
        entry = entries_by_qid.get(qid)
        metadata = entry.get("metadata", {}) if entry else {}
        foi_status = classify_foi_status(entry)
        idx = nsvs_indices_flags(entry) if entry else nsvs_indices_flags({})
        sub1_answer = sub1.get(qid, "")
        sub5b_answer = sub5b.get(qid, "")
        if details_csv and qid in details_csv:
            d = details_csv[qid]
            sub1_answer = d.get("sub1_baseline_answer") or d.get("sub1_answer") or sub1_answer
            sub5b_answer = (
                d.get("sub5b_paper_faithful_fix2_answer") or d.get("sub5b_answer") or sub5b_answer
            )
        if entry:
            mode = question_mode(metadata)
        elif sub5b_answer in {"Yes", "No"}:
            mode = "bool"
        elif sub5b_answer in {"A", "B", "C", "D"}:
            mode = "mc"
        else:
            mode = "unknown"
        rows.append(
            {
                "question_id": qid,
                "foi_status": foi_status,
                "sub5b_answer": sub5b_answer,
                "sub1_answer": sub1_answer,
                "same_answer": sub1_answer == sub5b_answer,
                "question_mode": mode,
                "operator_guess": metadata.get("operator_guess", "unknown"),
                "operator_family": operator_family(metadata.get("operator_guess", "unknown")),
                "source_dataset": metadata.get("source_dataset", "unknown"),
                "foi": entry.get("frames_of_interest") if entry else None,
                "nsvs_indices_empty_count": idx["empty_count"],
                "nsvs_indices_total_arrays": idx["total_arrays"],
                "has_entry": entry is not None,
            }
        )
    return rows


def render_markdown(
    *,
    rows: list[dict[str, Any]],
    entries_path: Path,
    sub5b_path: Path,
    sub1_path: Path,
    details_path: Path | None,
    score_sub1: float,
    score_sub5b: float,
    eval_n: int,
) -> str:
    n = len(rows)
    n_with_entry = sum(1 for r in rows if r["has_entry"])
    n_missing = n - n_with_entry

    foi_table = distribution_table(rows, answer_key="sub5b_answer", group_key="foi_status")
    bypassed_rows = [r for r in rows if r["foi_status"] == "bypassed"]
    sub5b_bypass = distribution_table(bypassed_rows, answer_key="sub5b_answer", group_key="question_mode")
    sub1_bypass = distribution_table(bypassed_rows, answer_key="sub1_answer", group_key="question_mode")
    op_table = distribution_table(rows, answer_key="sub5b_answer", group_key="operator_family")

    cf_bypassed = counterfactual_swap(
        rows,
        slice_key="foi_status",
        slice_values={"bypassed"},
        score_sub1=score_sub1,
        score_sub5b=score_sub5b,
        eval_n=eval_n,
    )
    cf_bypass_partial = counterfactual_swap(
        rows,
        slice_key="foi_status",
        slice_values={"bypassed", "partial"},
        score_sub1=score_sub1,
        score_sub5b=score_sub5b,
        eval_n=eval_n,
    )
    cf_missing = counterfactual_swap(
        rows,
        slice_key="foi_status",
        slice_values={"missing_video"},
        score_sub1=score_sub1,
        score_sub5b=score_sub5b,
        eval_n=eval_n,
    )

    lines = [
        "# Sub #5B A/Yes positional bias quantification",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Sources",
        "",
        f"- Entries: `{entries_path}` ({n_with_entry} processed rows)",
        f"- Sub #5B submission: `{sub5b_path}`",
        f"- Sub #1 submission: `{sub1_path}`",
    ]
    if details_path:
        lines.append(f"- Sub #1 answers cross-check: `{details_path}`")
    lines.extend(
        [
            f"- EvalAI val rows: **{eval_n}** ({n_missing} missing-video defaults without entries)",
            "",
            "## Headline",
            "",
            f"- Sub #5B EvalAI accuracy: **{score_sub5b}%** ({round(score_sub5b / 100 * eval_n)} est. correct)",
            f"- Sub #1 EvalAI accuracy: **{score_sub1}%** ({round(score_sub1 / 100 * eval_n)} est. correct)",
            f"- Net Sub #5B − Sub #1: **+{round(score_sub5b - score_sub1, 2)} pp**",
            "",
            "### FOI status prevalence",
            "",
            "| FOI status | n | % |",
            "| --- | ---: | ---: |",
        ]
    )
    foi_counts = Counter(r["foi_status"] for r in rows)
    for status in ["clean", "partial", "bypassed", "missing_video"]:
        if status not in foi_counts:
            continue
        count = foi_counts[status]
        lines.append(f"| {status} | {count} | {pct(count, n)} |")

    lines.extend(
        [
            "",
            "Classification: **clean** = FOI ≠ `[-1]` and all proposition detections non-empty; "
            "**partial** = some empty detection arrays; **bypassed** = FOI `[-1]` or all detection arrays empty; "
            "**missing_video** = no pipeline entry (17 default-answer rows).",
            "",
            "## Table 1 — Sub #5B answer distribution × FOI status",
            "",
            "Does the A/Yes skew concentrate in bypassed rows?",
            "",
            "| FOI status | n | Sub #5B answers | bool Yes% | mc A% |",
            "| --- | ---: | --- | ---: | ---: |",
        ]
    )
    for row in foi_table:
        lines.append(
            f"| {row['group']} | {row['n']} | {render_answer_counts(row['answers'])} | "
            f"{row['bool_yes_pct']}% ({row['bool_yes']}/{row['bool_yes'] + row['bool_no']}) | "
            f"{row['mc_a_pct']}% ({row['mc_a']}/{row['mc_n']}) |"
        )

    lines.extend(
        [
            "",
            "## Table 2 — Sub #5B vs Sub #1 on bypassed rows",
            "",
            "If Sub #1 is more uniform on the same bypassed slice, that quantifies positional-prior size.",
            "",
            "### Sub #5B (bypassed)",
            "",
            "| Mode | n | Answers | Yes% or A% |",
            "| --- | ---: | --- | ---: |",
        ]
    )
    for row in sub5b_bypass:
        mode = row["group"]
        if mode == "bool":
            pct_label = f"{row['bool_yes_pct']}% Yes"
            ans = f"Yes:{row['bool_yes']} No:{row['bool_no']}"
        else:
            pct_label = f"{row['mc_a_pct']}% A"
            ans = render_answer_counts(row["answers"])
        lines.append(f"| {mode} | {row['n']} | {ans} | {pct_label} |")

    lines.extend(
        [
            "",
            "### Sub #1 (same bypassed rows)",
            "",
            "| Mode | n | Answers | Yes% or A% |",
            "| --- | ---: | --- | ---: |",
        ]
    )
    for row in sub1_bypass:
        mode = row["group"]
        if mode == "bool":
            pct_label = f"{row['bool_yes_pct']}% Yes"
            ans = f"Yes:{row['bool_yes']} No:{row['bool_no']}"
        else:
            pct_label = f"{row['mc_a_pct']}% A"
            ans = render_answer_counts(row["answers"])
        lines.append(f"| {mode} | {row['n']} | {ans} | {pct_label} |")

    lines.extend(
        [
            "",
            "## Table 3 — Sub #5B answer distribution by operator family",
            "",
            "| Operator family | n | Sub #5B answers | bool Yes% | mc A% |",
            "| --- | ---: | --- | ---: | ---: |",
        ]
    )
    for row in op_table:
        lines.append(
            f"| {row['group']} | {row['n']} | {render_answer_counts(row['answers'])} | "
            f"{row['bool_yes_pct']}% | {row['mc_a_pct']}% |"
        )

    def render_cf(title: str, cf: dict[str, Any]) -> list[str]:
        out = [
            f"### {title}",
            "",
            f"- Slice size: **{cf['n_slice']}** rows ({', '.join(cf['slice_values'])})",
            f"- Agree Sub #1 = Sub #5B: **{cf['n_agree']}** (swap is a no-op)",
            f"- Disagree: **{cf['n_disagree']}** (answers would change)",
            "",
            "Proxy for Sub #1 win rate on *all* val disagreements "
            f"(from aggregate scores): **{cf['sub1_win_rate_all_disagree_proxy']:.1%}** "
            f"(Sub #5B **{cf['sub5b_win_rate_all_disagree_proxy']:.1%}**).",
            "",
            "| Scenario | p(Sub #1 right on slice disagreements) | Δ correct rows | Δ accuracy (pp) | Est. new accuracy |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for sc in cf["scenarios"]:
            out.append(
                f"| {sc['label']} | {sc['p_sub1_wins_on_slice_disagreements']:.1%} | "
                f"{sc['delta_correct_rows']:+.1f} | {sc['delta_accuracy_pp']:+.2f} | "
                f"{sc['estimated_new_accuracy_pct']:.2f}% |"
            )
        out.append("")
        return out

    lines.extend(
        [
            "",
            "## Table 4 — Counterfactual: swap Sub #5B → Sub #1 on bypass rows",
            "",
            "No hidden labels — accuracy deltas are **estimates** from row-wise answer swaps "
            "under stated assumptions about who is correct on disagreements.",
            "",
        ]
    )
    lines.extend(render_cf("Bypassed only (`foi_status=bypassed`)", cf_bypassed))
    lines.extend(render_cf("Bypass + partial (`bypassed` ∪ `partial`)", cf_bypass_partial))
    if cf_missing["n_slice"]:
        lines.extend(render_cf("Missing-video defaults (`missing_video`)", cf_missing))

    # Interpretation heuristics
    bypass_row = next((r for r in foi_table if r["group"] == "bypassed"), None)
    clean_row = next((r for r in foi_table if r["group"] == "clean"), None)
    partial_row = next((r for r in foi_table if r["group"] == "partial"), None)

    lines.extend(["## Interpretation", ""])
    if bypass_row and clean_row:
        yes_lift = bypass_row["bool_yes_pct"] - clean_row["bool_yes_pct"]
        a_lift = bypass_row["mc_a_pct"] - clean_row["mc_a_pct"]
        lines.append(
            f"- **Bypassed vs clean (Sub #5B):** bool Yes rate {bypass_row['bool_yes_pct']}% vs "
            f"{clean_row['bool_yes_pct']}% ({yes_lift:+.1f} pp); mc A rate {bypass_row['mc_a_pct']}% vs "
            f"{clean_row['mc_a_pct']}% ({a_lift:+.1f} pp)."
        )
    if partial_row and clean_row:
        yes_lift = partial_row["bool_yes_pct"] - clean_row["bool_yes_pct"]
        a_lift = partial_row["mc_a_pct"] - clean_row["mc_a_pct"]
        lines.append(
            f"- **Partial vs clean:** bool Yes {partial_row['bool_yes_pct']}% vs {clean_row['bool_yes_pct']}% "
            f"({yes_lift:+.1f} pp); mc A {partial_row['mc_a_pct']}% vs {clean_row['mc_a_pct']}% ({a_lift:+.1f} pp). "
            "Partial rows show the largest Yes skew — weak/partial NSVS may share the same fallback pathology."
        )

    missing_rows = [r for r in rows if r["foi_status"] == "missing_video"]
    if missing_rows:
        miss_yes = sum(1 for r in missing_rows if r["sub5b_answer"] == "Yes")
        lines.append(
            f"- **Missing-video defaults:** all **{len(missing_rows)}** rows use Sub #5B default `Yes` "
            f"({miss_yes}/{len(missing_rows)} Yes) — strong positional prior independent of NSVS."
        )

    mid = next(
        (s for s in cf_bypassed["scenarios"] if s["label"] == "overall_disagree_rate"),
        None,
    )
    if mid:
        lines.append(
            f"- **Bypass-only swap at overall disagree proxy:** estimated "
            f"**{mid['delta_accuracy_pp']:+.2f} pp** → ~{mid['estimated_new_accuracy_pct']}% accuracy."
        )

    lines.extend(
        [
            "",
            "## Decision lever",
            "",
            "If bypass/partial rows show concentrated A/Yes skew *and* the counterfactual swap is neutral-or-positive "
            "under realistic Sub #1 win rates, the next val submission can route FOI=-1 / bypass fallbacks to Sub #1 "
            "answers (one-line config change, no new API).",
            "",
            "See `details.csv` for per-row `foi_status`, answers, and operator metadata.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.entries.exists():
        print(f"Missing entries: {args.entries}", file=sys.stderr)
        return 2
    if not args.sub5b.exists():
        print(f"Missing Sub #5B submission: {args.sub5b}", file=sys.stderr)
        return 2

    entries = load_json(args.entries)
    sub5b = load_submission(str(args.sub5b))
    sub1 = load_submission(str(args.sub1)) if args.sub1.exists() else {}
    details_csv = load_details_csv()
    details_path = next((p for p in DEFAULT_DETAILS_CSV if p.exists()), None)

    rows = build_rows(entries, sub1, sub5b, details_csv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    details_path_out = args.out_dir / "details.csv"
    fieldnames = list(rows[0].keys()) if rows else []
    with details_path_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report = render_markdown(
        rows=rows,
        entries_path=args.entries,
        sub5b_path=args.sub5b,
        sub1_path=args.sub1,
        details_path=details_path,
        score_sub1=args.score_sub1,
        score_sub5b=args.score_sub5b,
        eval_n=args.eval_n,
    )
    report_path = args.out_dir / "report.md"
    report_path.write_text(report + "\n", encoding="utf-8")

    print(f"[bias-quant] wrote {details_path_out} ({len(rows)} rows)")
    print(f"[bias-quant] wrote {report_path}")
    foi_counts = Counter(r["foi_status"] for r in rows)
    print(f"[bias-quant] foi_status: {dict(foi_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
