#!/usr/bin/env python3
"""Post-run report for Sub #9 PULS v2 full val (straight pipeline, no routing).

Writes ``<base>/sub9_val_report.md`` with:
- Overall / per-category accuracy when ``--labels`` is provided (EvalAI export)
- 148-row target slice (94 empty-PULS + 54 operator-collapse from Diagnostic 2)
- Valid-FOI rate and NSVS error counts
- PULS v2 vs Sub #5B spec regression guard on non-target rows
- Total API spend estimate
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from postprocess.per_category_breakdown import (  # noqa: E402
    classify_nsvs,
    foi_valid,
    question_type,
)
from nsvqa.datamanager.timelogic import infer_operator  # noqa: E402

DEFAULT_BASE = Path("/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_val")
DEFAULT_DETAILS = REPO_ROOT / "diagnostics/puls_unknown_analysis/details.csv"
DEFAULT_SUB5B_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
TARGET_REASONS = frozenset({"empty_puls_output", "operator_collapse_open_ended"})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, default=DEFAULT_BASE)
    p.add_argument("--details-csv", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--sub5b-entries", type=Path, default=DEFAULT_SUB5B_ENTRIES)
    p.add_argument(
        "--labels",
        type=Path,
        help="Optional ground truth JSON (list[{question_id, answer_choice}] or {qid: answer})",
    )
    p.add_argument("--score", type=float, help="EvalAI AvgAcc percent (overall); recorded in report")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_labels(path: Path | None) -> dict[str, str]:
    if path is None or not path.is_file():
        return {}
    raw = load_json(path)
    if isinstance(raw, list):
        return {str(r["question_id"]): str(r["answer_choice"]) for r in raw}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    raise ValueError(f"unsupported labels format: {path}")


def target_qids(details_csv: Path) -> set[str]:
    qids: set[str] = set()
    with details_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category_reason") in TARGET_REASONS:
                qids.add(str(row["question_id"]))
    return qids


def normalize_spec(spec: str) -> str:
    s = (spec or "").strip()
    return re.sub(r"\s+", " ", s)


def spec_shape(spec: str) -> tuple[str, ...]:
    s = normalize_spec(spec)
    if not s:
        return ("empty",)
    ops = tuple(sorted(set(re.findall(r"\b(AND|OR|NOT|UNTIL|&|\||!)\b", s, flags=re.I))))
    props = tuple(sorted(re.findall(r'"([^"]+)"', s)))
    return ("spec", str(len(props)), ops, props[:3] if len(props) > 3 else props)


def accuracy_rows(
    preds: dict[str, str], labels: dict[str, str], qids: set[str] | None = None
) -> tuple[int, int, float | None]:
    if not labels:
        return 0, 0, None
    pool = qids if qids is not None else set(preds)
    scored = [q for q in pool if q in labels and q in preds]
    if not scored:
        return 0, 0, None
    correct = sum(1 for q in scored if preds[q] == labels[q])
    return correct, len(scored), 100.0 * correct / len(scored)


def per_category_accuracy(
    ann_by_qid: dict[str, dict],
    preds: dict[str, str],
    labels: dict[str, str],
) -> list[tuple[str, str, int, int, float]]:
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    for qid, ann in ann_by_qid.items():
        if qid not in labels or qid not in preds:
            continue
        mode = ann.get("mode") or "unknown"
        cat = infer_operator(ann.get("question") or "") or "unknown"
        buckets[(cat, question_type(mode))].append(qid)
    rows: list[tuple[str, str, int, int, float]] = []
    for (cat, qtype), bucket_qids in sorted(buckets.items()):
        c, n, acc = accuracy_rows(preds, labels, set(bucket_qids))
        if acc is not None:
            rows.append((cat, qtype, n, c, acc))
    return rows


def main() -> int:
    args = parse_args()
    base = args.base
    cfg_path = base / "config.json"
    cfg = load_json(cfg_path) if cfg_path.is_file() else {}
    ann_file = Path(cfg.get("ann_path") or "/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json")
    final = base / "submission_sub9_pulsv2_val.json"
    entries_path = base / "postprocess/postprocess_entries.json"
    breakdown_path = base / "per_category_breakdown.json"

    labels = load_labels(args.labels)
    target = target_qids(args.details_csv)

    annotations = load_json(ann_file)
    ann_by_qid = {str(a["question_id"]): a for a in annotations}
    submission = load_json(final) if final.is_file() else []
    preds = {str(r["question_id"]): str(r["answer_choice"]) for r in submission}

    entries = load_json(entries_path) if entries_path.is_file() else []
    entry_by_qid = {
        str(e.get("metadata", {}).get("question_id") or e.get("question_id")): e for e in entries
    }

    nsvs_counts: Counter[str] = Counter()
    foi_ok = 0
    n_entries = 0
    for entry in entry_by_qid.values():
        n_entries += 1
        nsvs_counts[classify_nsvs(entry)] += 1
        if foi_valid(entry.get("frames_of_interest")):
            foi_ok += 1
    foi_rate = 100.0 * foi_ok / n_entries if n_entries else 0.0

    overall_c, overall_n, overall_acc = accuracy_rows(preds, labels)
    t148_c, t148_n, t148_acc = accuracy_rows(preds, labels, target)

    spec_changes: list[dict[str, str]] = []
    shape_changes = 0
    sub5b_by_qid: dict[str, dict] = {}
    if args.sub5b_entries.is_file():
        sub5b_by_qid = {
            str(e.get("metadata", {}).get("question_id") or e.get("question_id")): e
            for e in load_json(args.sub5b_entries)
        }
    for qid, entry in entry_by_qid.items():
        if qid in target:
            continue
        old = normalize_spec((sub5b_by_qid.get(qid, {}).get("puls") or {}).get("specification") or "")
        new = normalize_spec((entry.get("puls") or {}).get("specification") or "")
        if spec_shape(old) != spec_shape(new):
            shape_changes += 1
            if len(spec_changes) < 5:
                spec_changes.append({"qid": qid, "v1_spec": old[:200], "v2_spec": new[:200]})

    spend_usd: float | None = None
    est_path = SCRIPT_DIR / "estimate_api_spend.py"
    try:
        spec = importlib.util.spec_from_file_location("estimate_api_spend", est_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            spend_usd = float(mod.retroactive_estimate(str(base), refresh=True).get("total_usd", 0.0))
    except Exception as exc:
        cost_path = base / "api_cost.json"
        if cost_path.is_file():
            spend_usd = float(load_json(cost_path).get("total_usd", 0.0))
        else:
            print(f"[analyze_sub9] spend estimate failed: {exc!r}", file=sys.stderr)

    lines = [
        "# Sub #9 PULS v2 — full val report (no routing)",
        "",
        f"- **Base:** `{base}`",
        f"- **Submission:** `{final}` ({len(submission)} rows)",
        f"- **Target slice:** {len(target)} qids (94 `empty_puls_output` + 54 `operator_collapse_open_ended`)",
        "",
        "## Overall val accuracy",
        "",
    ]
    if args.score is not None:
        lines.append(f"- **EvalAI AvgAcc (provided):** {args.score:.2f}%")
    if overall_acc is not None:
        lines.append(f"- **Local accuracy (--labels):** {overall_acc:.2f}% ({overall_c}/{overall_n})")
    else:
        lines.append(
            "- **Local accuracy:** not computed (no `--labels`). "
            "Upload submission to EvalAI val for AvgAcc, or pass `--labels` from an EvalAI export."
        )

    lines.extend(["", "## 148-row target slice", ""])
    if t148_acc is not None:
        lines.append(f"- **Accuracy on 148 target qids:** {t148_acc:.2f}% ({t148_c}/{t148_n})")
    else:
        lines.append("- **Accuracy on 148 target qids:** requires `--labels` (EvalAI row-level export).")
        if preds and target:
            sub5b_sub = Path(
                "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
                "submission_sub5b_paper_faithful_gpt52.json"
            )
            if sub5b_sub.is_file():
                sub5b_preds = {
                    str(r["question_id"]): str(r["answer_choice"]) for r in load_json(sub5b_sub)
                }
                changed = sum(
                    1
                    for q in target
                    if q in preds and q in sub5b_preds and preds[q] != sub5b_preds[q]
                )
                lines.append(
                    f"- **Answer delta vs Sub #5B (proxy, not GT):** {changed}/{len(target)} "
                    "target qids changed answer."
                )

    lines.extend(
        [
            "",
            "## Valid-FOI and NSVS errors",
            "",
            f"- **Valid-FOI rate:** {foi_rate:.1f}% ({foi_ok}/{n_entries})",
            "  - Compare: Sub #5B ~70.6%, Sub7b test rerun ~43%",
            "- **NSVS status counts:**",
        ]
    )
    for status, count in sorted(nsvs_counts.items()):
        lines.append(f"  - `{status}`: {count}")

    lines.extend(["", "## Per-category breakdown (16 operators × Bool/MCQ)", ""])
    if labels:
        lines.append("| category | type | n | correct | acc% |")
        lines.append("| --- | --- | ---: | ---: | ---: |")
        for cat, qtype, n, c, acc in per_category_accuracy(ann_by_qid, preds, labels):
            lines.append(f"| {cat} | {qtype} | {n} | {c} | {acc:.1f} |")
    elif breakdown_path.is_file():
        lines.append(
            f"- Row-level diagnostics (no GT accuracy): `{breakdown_path}` "
            f"({load_json(breakdown_path).get('row_count', '?')} rows)"
        )
    else:
        lines.append("- `per_category_breakdown.json` not found.")

    lines.extend(
        [
            "",
            "## PULS v2 regression guard (non-target rows)",
            "",
            f"- **Rows with changed spec shape (excl. 148 target):** {shape_changes}",
        ]
    )
    if spec_changes:
        lines.append("- **Sample shape changes (up to 5):**")
        for sample in spec_changes:
            lines.append(f"  - QID {sample['qid']}: v1 `{sample['v1_spec']}` → v2 `{sample['v2_spec']}`")
    else:
        lines.append("- No unexpected structural changes sampled (or Sub #5B entries missing).")

    lines.extend(
        [
            "",
            "## API spend",
            "",
            f"- **Estimated total:** ${spend_usd:.2f}" if spend_usd is not None else "- **Estimated total:** unknown",
            "",
            "## Caveat (Example 16 non-overlap)",
            "",
            "Example 16 encodes non-overlap as `candidate AND NOT anchor`; "
            "`diagnostics/puls_v2_prep/PROMPT_DIFF.md` documents `NOT(anchor AND candidate)` — "
            "not equivalent. Eyeball non-overlap rows inside the 148 before trusting that bucket.",
            "",
        ]
    )

    out_path = base / "sub9_val_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[analyze_sub9] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
