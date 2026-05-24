#!/usr/bin/env python3
"""Report NSVS gpt-5.2 backend ablation results on the 50-Q subsample."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_BASELINE_SUB = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_BASELINE_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def vote_key(row: dict) -> tuple:
    return (row.get("window_idx"), row.get("proposition"))


def compare_detection_logs(gpt_log: list[dict], internvl_log: list[dict]) -> dict[str, Any]:
    gpt_by = {vote_key(r): r for r in gpt_log}
    iv_by = {vote_key(r): r for r in internvl_log}
    keys = sorted(set(gpt_by) | set(iv_by), key=lambda k: (k[0] if k[0] is not None else -1, k[1] or ""))

    rows = []
    agree = 0
    for key in keys:
        g = gpt_by.get(key)
        iv = iv_by.get(key)
        g_yes = bool(g.get("is_detected")) if g else None
        iv_yes = bool(iv.get("is_detected")) if iv else None
        same = g_yes == iv_yes if g is not None and iv is not None else None
        if same:
            agree += 1
        rows.append(
            {
                "window_idx": key[0],
                "proposition": key[1],
                "gpt52_is_detected": g_yes,
                "internvl_is_detected": iv_yes,
                "votes_match": same,
                "gpt52_reasoning": (g or {}).get("reasoning") or (g or {}).get("reasoning_summary"),
                "internvl_confidence": (iv or {}).get("confidence"),
            }
        )

    comparable = sum(1 for r in rows if r["votes_match"] is not None)
    return {
        "n_windows": len(rows),
        "n_comparable": comparable,
        "n_vote_agree": agree,
        "vote_agree_rate": round(agree / comparable, 4) if comparable else None,
        "windows": rows,
    }


def foi_status(foi: Any) -> str:
    if foi == [-1] or not foi:
        return "minus_one"
    if isinstance(foi, list) and len(foi) == 2:
        return "valid"
    return "other"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", required=True, help="Ablation run base directory")
    p.add_argument("--baseline-sub", type=Path, default=DEFAULT_BASELINE_SUB)
    p.add_argument("--baseline-entries", type=Path, default=DEFAULT_BASELINE_ENTRIES)
    p.add_argument("--baseline-score", type=float, default=53.35)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    base = Path(args.base)
    report_dir = base / "report"
    per_q_dir = report_dir / "per_question"
    report_dir.mkdir(parents=True, exist_ok=True)
    per_q_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(base / "subsample_manifest.json")
    nsvs_entries = load_json(base / "nsvs" / "entries.json")
    nsvs_by_qid = {str(e["metadata"]["question_id"]): e for e in nsvs_entries}

    answers_path = base / "answers" / "submission_partial.json"
    answers_by_qid: dict[str, str] = {}
    if answers_path.is_file():
        for row in load_json(answers_path):
            answers_by_qid[str(row["question_id"])] = row["answer_choice"]

    answers_diag_path = base / "answers" / "answers_diag.json"
    vqa_diag_by_qid: dict[str, dict] = {}
    if answers_diag_path.is_file():
        for row in load_json(answers_diag_path):
            vqa_diag_by_qid[str(row.get("qid") or row.get("question_id"))] = row

    baseline_sub = {str(r["question_id"]): r["answer_choice"] for r in load_json(args.baseline_sub)}
    baseline_entries = {
        str(e["metadata"]["question_id"]): e for e in load_json(args.baseline_entries)
    }

    internvl_log_dir = base / "internvl_replay" / "internvl_detection_logs"
    if not internvl_log_dir.is_dir():
        internvl_log_dir = base / "internvl_detection_logs"

    head_to_head_lines: list[dict] = []
    per_question_summaries = []
    flip_vs_baseline = 0
    same_vs_baseline = 0
    vote_stats_by_op: Counter = Counter()
    vote_total_by_op: Counter = Counter()
    flip_by_stratum: Counter = Counter()
    flip_by_op: Counter = Counter()

    for row in manifest:
        qid = str(row["question_id"])
        entry = nsvs_by_qid.get(qid, {})
        baseline_entry = baseline_entries.get(qid, {})
        gpt_log = (entry.get("nsvs") or {}).get("detection_log") or []

        iv_path = internvl_log_dir / f"{qid}.json"
        internvl_log = load_json(iv_path) if iv_path.is_file() else []

        h2h = compare_detection_logs(gpt_log, internvl_log)
        for w in h2h["windows"]:
            if w["votes_match"] is False:
                head_to_head_lines.append({"question_id": qid, **w})

        new_answer = answers_by_qid.get(qid)
        baseline_answer = baseline_sub.get(qid)
        same_ans = new_answer == baseline_answer if new_answer and baseline_answer else None
        if same_ans is True:
            same_vs_baseline += 1
        elif same_ans is False:
            flip_vs_baseline += 1
            flip_by_stratum[row.get("stratum", "unknown")] += 1
            flip_by_op[row.get("operator_family", "unknown")] += 1

        baseline_foi = baseline_entry.get("frames_of_interest")
        new_foi = entry.get("frames_of_interest")
        vqa_diag = vqa_diag_by_qid.get(qid, {})

        pq = {
            "question_id": qid,
            "operator_family": row.get("operator_family"),
            "stratum": row.get("stratum"),
            "sub1_answer": row.get("sub1_answer"),
            "sub5b_baseline_answer": baseline_answer,
            "gpt52_pipeline_answer": new_answer,
            "same_as_sub5b_baseline": same_ans,
            "baseline_foi": baseline_foi,
            "gpt52_foi": new_foi,
            "foi_status_baseline": foi_status(baseline_foi),
            "foi_status_gpt52": foi_status(new_foi),
            "head_to_head": h2h,
            "nsvs_detection_log_gpt52": gpt_log,
            "nsvs_detection_log_internvl": internvl_log,
            "vqa_reasoning_summary": vqa_diag.get("reasoning_summary"),
            "vqa_raw": vqa_diag.get("raw"),
        }
        per_q_dir.joinpath(f"{qid}.json").write_text(
            json.dumps(pq, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        per_question_summaries.append(pq)

        op = row.get("operator_family", "unknown")
        if h2h["n_comparable"]:
            vote_stats_by_op[op] += h2h["n_vote_agree"]
            vote_total_by_op[op] += h2h["n_comparable"]

    api_cost_path = base / "nsvs" / "api_cost.json"
    api_cost = load_json(api_cost_path) if api_cost_path.is_file() else {}
    n_questions = len(manifest)
    total_usd = float(api_cost.get("estimated_total_usd") or 0.0)
    cost_per_q = round(total_usd / n_questions, 4) if n_questions else None

    stratum_counts = Counter(r.get("stratum") for r in manifest)
    op_counts = Counter(r.get("operator_family") for r in manifest)

    lines = [
        "# NSVS gpt-5.2 Backend Ablation — Subsample Report",
        "",
        f"- Base: `{base}`",
        f"- Questions: **{n_questions}** ({dict(stratum_counts)})",
        f"- Baseline Sub #5B EvalAI score: **{args.baseline_score}%** (proxy comparison only — no local GT)",
        "",
        "## Final answer vs Sub #5B baseline",
        "",
        f"- Same answer as baseline Sub #5B: **{same_vs_baseline}/{n_questions}**",
        f"- Flipped vs baseline Sub #5B: **{flip_vs_baseline}/{n_questions}**",
        f"- Flip by stratum: `{dict(flip_by_stratum)}`",
        f"- Flip by operator_family: `{dict(flip_by_op)}`",
        "",
        "> Proxy only: without labels we cannot measure true accuracy delta. "
        "If every flip were an improvement over baseline, max gain on this subsample "
        f"would be **+{2 * flip_vs_baseline / n_questions * 100:.2f} pp** (upper bound, not measured).",
        "",
        "## NSVS vote head-to-head (gpt-5.2 vs InternVL2-8B)",
        "",
    ]

    total_windows = sum(p["head_to_head"]["n_comparable"] for p in per_question_summaries)
    total_agree = sum(p["head_to_head"]["n_vote_agree"] for p in per_question_summaries)
    overall_vote_rate = round(total_agree / total_windows, 4) if total_windows else None
    lines.extend(
        [
            f"- Comparable window×proposition pairs: **{total_windows}**",
            f"- Vote agreement rate: **{overall_vote_rate}** ({total_agree}/{total_windows})",
            "",
            "### Vote agreement by operator_family",
            "",
            "| operator_family | agree | total | rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for op in sorted(vote_total_by_op.keys()):
        tot = vote_total_by_op[op]
        agr = vote_stats_by_op[op]
        rate = round(agr / tot, 3) if tot else 0
        lines.append(f"| {op} | {agr} | {tot} | {rate} |")

    lines.extend(
        [
            "",
            "## API cost (NSVS stage metered in run_timelogic)",
            "",
            f"- Estimated NSVS API total: **${total_usd:.4f}**",
            f"- Cost per question (NSVS only): **${cost_per_q}**",
            f"- Calls: {api_cost.get('calls', 'n/a')} "
            f"({api_cost.get('metered_calls', '?')} metered / {api_cost.get('heuristic_calls', '?')} heuristic)",
            f"- By stage: `{api_cost.get('by_stage_usd', {})}`",
            "",
            "## Operator coverage",
            "",
            f"`{dict(op_counts)}`",
            "",
            "## Artifacts",
            "",
            f"- Per-question: `{per_q_dir}`",
            f"- Head-to-head mismatches: `{report_dir / 'head_to_head_votes.jsonl'}`",
        ]
    )

    report_path = report_dir / "ablation_summary.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    h2h_path = report_dir / "head_to_head_votes.jsonl"
    with open(h2h_path, "w", encoding="utf-8") as f:
        for row in head_to_head_lines:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")

    summary_json = {
        "n_questions": n_questions,
        "same_vs_baseline_sub5b": same_vs_baseline,
        "flip_vs_baseline_sub5b": flip_vs_baseline,
        "vote_agree_rate": overall_vote_rate,
        "cost_per_question_usd_nsvs": cost_per_q,
        "estimated_total_usd_nsvs": total_usd,
        "stratum_counts": dict(stratum_counts),
        "operator_counts": dict(op_counts),
    }
    (report_dir / "ablation_summary.json").write_text(
        json.dumps(summary_json, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[report] wrote {report_path}")
    print(f"[report] same vs Sub5B: {same_vs_baseline}/{n_questions}, flips: {flip_vs_baseline}")
    print(f"[report] vote agree rate: {overall_vote_rate}, cost/q: ${cost_per_q}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
