#!/usr/bin/env python3
"""Build a 50-question stratified subsample for NSVS backend ablation.

35 Sub#1 != Sub#5B disagreements + 15 Sub#1 == Sub#5B agreements (control),
each stratified by temporal operator family.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_DIAG = Path("/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2")
DEFAULT_SUB1 = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json")
DEFAULT_SUB5B = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)

MUST_COVER_FAMILIES = [
    "since",
    "until",
    "during",
    "always_before",
    "always_after",
    "before",
    "after",
]


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


def load_json(path: Path) -> list | dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_submission(path: Path) -> dict[str, str]:
    rows = load_json(path)
    return {str(r["question_id"]): r["answer_choice"] for r in rows}


def load_disagreement_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_agreement_rows(
    sub1: dict[str, str],
    sub5b: dict[str, str],
    entries_by_qid: dict[str, dict],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for qid in sorted(sub1.keys(), key=lambda x: int(x) if x.isdigit() else x):
        if sub1.get(qid) != sub5b.get(qid):
            continue
        entry = entries_by_qid.get(qid, {})
        meta = entry.get("metadata", {})
        rows.append(
            {
                "question_id": qid,
                "sub1_baseline_answer": sub1[qid],
                "sub5b_paper_faithful_fix2_answer": sub5b[qid],
                "same_answer": "True",
                "mode": meta.get("mode", ""),
                "operator_guess": meta.get("operator_guess", "unknown"),
                "source_dataset": meta.get("source_dataset", ""),
            }
        )
    return rows


def enrich_row(row: dict[str, str]) -> dict[str, str]:
    out = dict(row)
    out["operator_family"] = operator_family(row.get("operator_guess", ""))
    out["disagree_flag"] = row.get("same_answer", "False") == "False"
    out["stratum"] = "disagree" if out["disagree_flag"] else "agree"
    return out


def diversity_score(row: dict, selected: list[dict]) -> tuple:
    op_counts = Counter(r["operator_family"] for r in selected)
    src_counts = Counter(r.get("source_dataset", "") for r in selected)
    s = 0.0
    s += max(0, 2 - op_counts[row["operator_family"]]) * 5
    s += max(0, 2 - src_counts.get(row.get("source_dataset", ""), 0)) * 2
    if row["operator_family"] in {"until", "since"}:
        s += 2
    return (-s, int(row["question_id"]))


def select_stratified(pool: list[dict], n: int) -> list[dict]:
    candidates = [enrich_row(r) for r in pool]
    selected: list[dict] = []
    selected_qids: set[str] = set()

    for family in MUST_COVER_FAMILIES:
        fam_pool = [
            r for r in candidates
            if r["operator_family"] == family and r["question_id"] not in selected_qids
        ]
        if not fam_pool:
            continue
        fam_pool.sort(key=lambda r: int(r["question_id"]))
        pick = fam_pool[0]
        selected.append(pick)
        selected_qids.add(pick["question_id"])

    while len(selected) < n:
        remaining = [r for r in candidates if r["question_id"] not in selected_qids]
        if not remaining:
            break
        remaining.sort(key=lambda r: diversity_score(r, selected))
        pick = remaining[0]
        selected.append(pick)
        selected_qids.add(pick["question_id"])

    selected.sort(key=lambda r: (r["stratum"], r["operator_family"], int(r["question_id"])))
    return selected[:n]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, help="Output directory for subsample artifacts")
    p.add_argument("--diag-dir", type=Path, default=DEFAULT_DIAG)
    p.add_argument("--sub1", type=Path, default=DEFAULT_SUB1)
    p.add_argument("--sub5b", type=Path, default=DEFAULT_SUB5B)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--n-disagree", type=int, default=35)
    p.add_argument("--n-agree", type=int, default=15)
    p.add_argument("--seed", type=int, default=0, help="Reserved for future tie-breaking")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _ = args.seed
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries_list = load_json(args.entries)
    entries_by_qid = {
        str(e["metadata"]["question_id"]): e for e in entries_list
    }

    sub1 = load_submission(args.sub1)
    sub5b = load_submission(args.sub5b)

    disagree_path = args.diag_dir / "disagreements.csv"
    if not disagree_path.is_file():
        raise SystemExit(f"Missing disagreements CSV: {disagree_path}")

    disagree_pool = load_disagreement_rows(disagree_path)
    agree_pool = build_agreement_rows(sub1, sub5b, entries_by_qid)

    selected_disagree = select_stratified(disagree_pool, args.n_disagree)
    selected_agree = select_stratified(agree_pool, args.n_agree)
    selected = selected_disagree + selected_agree

    qids = [r["question_id"] for r in selected]
    manifest = []
    for row in selected:
        manifest.append(
            {
                "question_id": row["question_id"],
                "operator_family": row["operator_family"],
                "operator_guess": row.get("operator_guess", ""),
                "disagree_flag": row["disagree_flag"],
                "stratum": row["stratum"],
                "sub1_answer": row.get("sub1_baseline_answer") or sub1.get(row["question_id"]),
                "sub5b_answer": row.get("sub5b_paper_faithful_fix2_answer") or sub5b.get(row["question_id"]),
                "mode": row.get("mode", ""),
                "source_dataset": row.get("source_dataset", ""),
            }
        )

    qid_path = out_dir / "subsample_qids.json"
    manifest_path = out_dir / "subsample_manifest.json"
    qid_path.write_text(json.dumps(qids, indent=2) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    op_counts = Counter(r["operator_family"] for r in manifest)
    stratum_counts = Counter(r["stratum"] for r in manifest)
    print(f"[subsample] wrote {len(qids)} qids -> {qid_path}")
    print(f"[subsample] stratum: {dict(stratum_counts)}")
    print(f"[subsample] operator_family: {dict(op_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
