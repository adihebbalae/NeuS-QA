#!/usr/bin/env python3
"""PULS spec analysis for unknown-operator NSVS-bypassed val rows.

Offline diagnostic — zero API. Filters Sub #5B merged entries to
operator_guess=unknown with NSVS bypass, auto-categorizes PULS specs,
and emits report.md + details.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "puls_unknown_analysis"
SAMPLE_SEED = 42

TEMPORAL_Q = re.compile(
    r"\b(after|before|while|until|since|when|always|eventually|during|overlap|co-occur|occur)\b",
    re.I,
)
ABSTRACT_PROP = re.compile(
    r"(something|somewhere|someone|some_\w+|feel|think|emotion|co_occur|overlap)",
    re.I,
)
VISUAL_VERBS = re.compile(
    r"\b("
    r"hold|carry|throw|open|close|walk|sit|stand|take|put|pick|eat|drink|cut|wash|wear|"
    r"look|turn|push|pull|grab|touch|move|play|kick|hit|drop|place|reach|"
    r"holds|throws|opens|closes|walks|sits|stands|takes|puts|picks|eats|drinks|cuts|"
    r"washes|wears|looks|turns|pushes|pulls|grabs|touches|moves|plays|kicks|hits|drops|"
    r"places|reaches|washing|sitting|holding|carrying|throwing|opening|closing|walking|"
    r"standing|taking|putting|picking|eating|drinking|cutting|wearing|looking|turning|"
    r"pushing|pulling|grabbing|touching|moving|playing|kicking|hitting|dropping|placing|"
    r"reaching|tidying|talking|reading|writing|cooking|cleaning|smiling|laughing|"
    r"tidies|talks|reads|writes|cooks|cleans"
    r")\b",
    re.I,
)
OPEN_ENDED_Q = re.compile(r"\b(what|which|how)\b", re.I)
RELATION_Q = re.compile(r"\b(co-occur|overlap|always occur)\b", re.I)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--seed", type=int, default=SAMPLE_SEED)
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def qid_from_entry(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    return str(metadata.get("question_id") or entry.get("question_id"))


def foi_is_minus_one(foi: Any) -> bool:
    return foi == [-1] or (isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1)


def nsvs_bypassed(entry: dict[str, Any]) -> bool:
    """Match v3 audit NSVS_bypassed (FOI [-1], Storm [-1], or any empty split)."""
    nsvs = entry.get("nsvs", {})
    output = nsvs.get("output")
    indices = nsvs.get("indices") or []
    foi = entry.get("frames_of_interest")
    if output == [-1] or foi_is_minus_one(foi):
        return True
    if indices:
        empty_count = sum(1 for idxs in indices if not idxs)
        if empty_count > 0:
            return True
    return False


def prop_split(spec: str, prop: str) -> int:
    """Mirror PropertyChecker.check_split: 0 = before U, 1 = after U."""
    splits = spec.split(" U ")
    return 0 if prop in splits[0] else 1


def detection_count_per_prop(entry: dict[str, Any]) -> dict[str, int]:
    puls = entry.get("puls", {})
    props: list[str] = puls.get("proposition") or []
    spec: str = puls.get("specification") or ""
    indices: list[list[int]] = entry.get("nsvs", {}).get("indices") or []
    counts: dict[str, int] = {}
    for prop in props:
        split_idx = prop_split(spec, prop) if spec else 0
        if split_idx < len(indices):
            counts[prop] = len(indices[split_idx])
        else:
            counts[prop] = 0
    return counts


def is_groundable_prop(prop: str) -> bool:
    text = prop.replace("_", " ")
    if prop.startswith("subtitle_"):
        return True
    if ABSTRACT_PROP.search(text):
        return bool(re.search(r"(person_|man_|woman_|child_|people_)", prop))
    if VISUAL_VERBS.search(text):
        return True
    return bool(re.search(r"person_|man_|woman_|child_", prop))


def classify_row(entry: dict[str, Any]) -> tuple[str, str]:
    puls = entry.get("puls", {})
    props: list[str] = puls.get("proposition") or []
    spec = (puls.get("specification") or "").strip()
    question = entry.get("question") or ""
    counts = detection_count_per_prop(entry)
    indices = entry.get("nsvs", {}).get("indices") or []

    if not props or not spec:
        return "spec_un_groundable", "empty_puls_output"

    if not any(is_groundable_prop(p) for p in props):
        return "spec_un_groundable", "no_groundable_propositions"

    missing_from_spec = [p for p in props if p not in spec.replace('"', "")]
    if len(missing_from_spec) == len(props):
        return "unclassifiable", "propositions_not_in_spec"

    if OPEN_ENDED_Q.search(question) and TEMPORAL_Q.search(question):
        if " U " not in spec and len(props) == 1:
            return "spec_un_groundable", "operator_collapse_open_ended"

    if RELATION_Q.search(question):
        if len(props) < 2 or (" U " not in spec and "&" not in spec):
            return "spec_un_groundable", "relation_not_in_spec"

    if all(
        ABSTRACT_PROP.search(p.replace("_", " ")) and not VISUAL_VERBS.search(p.replace("_", " "))
        for p in props
    ):
        return "spec_un_groundable", "abstract_propositions"

    if not counts and props:
        return "unclassifiable", "no_indices_for_props"

    nonzero = sum(1 for v in counts.values() if v > 0)
    if nonzero == 0:
        return "spec_ok_no_detect", "zero_detections"

    if 0 < nonzero < len(counts):
        return "spec_partial", "mixed_prop_detections"

    if indices and any(idxs for idxs in indices) and any(not idxs for idxs in indices):
        return "spec_partial", "split_mixed_detections"

    if nonzero == len(counts) and sum(counts.values()) > 0:
        return "spec_partial", "detections_but_foi_failed"

    return "unclassifiable", "residual"


def row_record(entry: dict[str, Any]) -> dict[str, Any]:
    metadata = entry.get("metadata", {})
    category, reason = classify_row(entry)
    props = entry.get("puls", {}).get("proposition") or []
    counts = detection_count_per_prop(entry)
    indices = entry.get("nsvs", {}).get("indices") or []
    return {
        "question_id": qid_from_entry(entry),
        "question_text": (entry.get("question") or "").replace("\n", " ").strip(),
        "puls_spec": entry.get("puls", {}).get("specification") or "",
        "propositions": json.dumps(props),
        "detection_count_per_prop": json.dumps(counts),
        "nsvs_indices": json.dumps(indices),
        "category": category,
        "category_reason": reason,
        "question_mode": metadata.get("mode", "unknown"),
        "source_dataset": metadata.get("source_dataset", "unknown"),
        "foi": json.dumps(entry.get("frames_of_interest")),
        "nsvs_output": json.dumps(entry.get("nsvs", {}).get("output")),
    }


def pct(n: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{n / total * 100:.1f}%"


def sample_rows(
    rows: list[dict[str, Any]],
    category: str,
    n: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    pool = [r for r in rows if r["category"] == category]
    if not pool:
        return []

    by_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pool:
        by_reason[row["category_reason"]].append(row)

    chosen: list[dict[str, Any]] = []
    reasons = sorted(by_reason, key=lambda r: -len(by_reason[r]))
    for reason in reasons:
        if len(chosen) >= n:
            break
        candidates = by_reason[reason]
        pick = rng.choice(candidates)
        chosen.append(pick)

    remaining = [r for r in pool if r not in chosen]
    while len(chosen) < n and remaining:
        pick = rng.choice(remaining)
        chosen.append(pick)
        remaining.remove(pick)
    return chosen


def render_sample_block(row: dict[str, Any]) -> list[str]:
    props = json.loads(row["propositions"])
    counts = json.loads(row["detection_count_per_prop"])
    lines = [
        f"#### QID {row['question_id']} (`{row['category_reason']}`)",
        "",
        f"- **Question:** {row['question_text'][:500]}",
        f"- **Mode:** {row['question_mode']} | **Source:** {row['source_dataset']}",
        f"- **PULS spec:** `{row['puls_spec']}`",
        f"- **Propositions:** {props}",
        f"- **Detection counts:** {counts}",
        f"- **NSVS indices (split buckets):** {json.loads(row['nsvs_indices'])}",
        f"- **FOI:** {row['foi']} | **NSVS output:** {row['nsvs_output']}",
        "",
    ]
    return lines


def decision_recommendation(counts: Counter[str], total: int) -> str:
    ung_pct = counts["spec_un_groundable"] / total * 100 if total else 0
    ok_pct = counts["spec_ok_no_detect"] / total * 100 if total else 0
    partial_pct = counts["spec_partial"] / total * 100 if total else 0

    dominant = max(
        [
            ("spec_un_groundable", ung_pct),
            ("spec_ok_no_detect", ok_pct),
            ("spec_partial", partial_pct),
        ],
        key=lambda x: x[1],
    )

    if ung_pct > 40:
        rec = (
            f"**PULS prompt tuning is a high-leverage submission lever.** "
            f"`spec_un_groundable` is **{ung_pct:.1f}%** of the slice (>{40}% threshold). "
            "Many unknown-family questions get empty PULS output or operator-collapsed single-proposition specs "
            "that cannot encode the question's temporal semantics."
        )
    elif dominant[0] == "spec_ok_no_detect":
        rec = (
            f"**Detector quality is the primary lever** (GPT-5.2 NSVS swap experiment). "
            f"`spec_ok_no_detect` dominates at **{ok_pct:.1f}%** — PULS emits groundable visual propositions "
            "but InternVL2-8B finds zero matching windows."
        )
    elif dominant[0] == "spec_partial":
        rec = (
            f"**Temporal aggregation / Storm merge logic is the primary lever.** "
            f"`spec_partial` dominates at **{partial_pct:.1f}%** — some proposition splits fire detections "
            "but FOI still fails or splits are inconsistent."
        )
    else:
        rec = (
            "No single bucket clearly dominates; inspect `unclassifiable` samples and refine heuristics "
            "before committing engineering effort."
        )
    return rec


def render_markdown(
    *,
    entries_path: Path,
    rows: list[dict[str, Any]],
    unknown_total: int,
    samples: dict[str, list[dict[str, Any]]],
) -> str:
    total = len(rows)
    cat_counts = Counter(r["category"] for r in rows)
    reason_counts = Counter(r["category_reason"] for r in rows)

    lines = [
        "# PULS spec analysis — unknown operator family (NSVS-bypassed)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Sources",
        "",
        f"- Entries: `{entries_path}`",
        f"- Filter: `operator_guess == unknown` AND NSVS bypassed (FOI `[-1]`, Storm `[-1]`, or any empty detection split)",
        f"- Unknown-family rows in entries: **{unknown_total}**",
        f"- NSVS-bypassed unknown slice: **{total}** ({pct(total, unknown_total)} of unknown family)",
        "",
        "## Category counts",
        "",
        "| Category | n | % | Action lever |",
        "| --- | ---: | ---: | --- |",
        f"| spec_un_groundable | {cat_counts['spec_un_groundable']} | "
        f"{pct(cat_counts['spec_un_groundable'], total)} | PULS prompt fix |",
        f"| spec_ok_no_detect | {cat_counts['spec_ok_no_detect']} | "
        f"{pct(cat_counts['spec_ok_no_detect'], total)} | NSVS detector quality |",
        f"| spec_partial | {cat_counts['spec_partial']} | "
        f"{pct(cat_counts['spec_partial'], total)} | Temporal aggregation / Storm merge |",
        f"| unclassifiable | {cat_counts['unclassifiable']} | "
        f"{pct(cat_counts['unclassifiable'], total)} | Human inspection |",
        "",
        "### Reason codes (within category)",
        "",
        "| Reason | n |",
        "| --- | ---: |",
    ]
    for reason, count in reason_counts.most_common():
        lines.append(f"| `{reason}` | {count} |")

    lines.extend(
        [
            "",
            "## Decision recommendation",
            "",
            decision_recommendation(cat_counts, total),
            "",
            "### Classification rules (auto)",
            "",
            "- **spec_un_groundable:** empty PULS output; no frame-scorable propositions; open-ended temporal "
            "question collapsed to a single non-`UNTIL` proposition; co-occur/overlap questions without "
            "multi-prop `AND`/`UNTIL` structure.",
            "- **spec_ok_no_detect:** groundable spec but zero detection windows on every proposition split.",
            "- **spec_partial:** some proposition splits have detections and others do not, or detections exist "
            "but FOI still `[-1]`.",
            "- **unclassifiable:** propositions absent from spec or missing NSVS index mapping.",
            "",
            "Detection counts map each proposition to its `UNTIL` split bucket "
            "(same convention as `PropertyChecker.check_split`) — propositions sharing a split share a count.",
            "",
            "## Sampled rows (3 per category)",
            "",
        ]
    )

    category_titles = {
        "spec_un_groundable": "spec_un_groundable — PULS prompt fix",
        "spec_ok_no_detect": "spec_ok_no_detect — NSVS detector quality",
        "spec_partial": "spec_partial — temporal aggregation",
        "unclassifiable": "unclassifiable — human inspection",
    }
    for category in [
        "spec_un_groundable",
        "spec_ok_no_detect",
        "spec_partial",
        "unclassifiable",
    ]:
        lines.append(f"### {category_titles[category]}")
        lines.append("")
        cat_samples = samples.get(category, [])
        if not cat_samples:
            lines.append("_No rows in this category._")
            lines.append("")
            continue
        for row in cat_samples:
            lines.extend(render_sample_block(row))

    lines.extend(
        [
            "## Notes",
            "",
            "- `unknown` operator family is **23%** of val; **93.9%** NSVS-bypass rate on this family "
            f"({total}/{unknown_total} in this dump).",
            "- Empty PULS output (`empty_puls_output`, n="
            f"{reason_counts.get('empty_puls_output', 0)}) often corresponds to MC prompts where PULS returned "
            "no propositions — a strong PULS-side failure mode.",
            "- `operator_collapse_open_ended` flags What/Which/How + temporal cue questions reduced to a single "
            "proposition without `UNTIL` — PULS cannot represent the queried event.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.entries.exists():
        print(f"Missing entries: {args.entries}", file=sys.stderr)
        return 2

    entries = load_json(args.entries)
    unknown_all = [
        e for e in entries if (e.get("metadata", {}).get("operator_guess") or "") == "unknown"
    ]
    filtered = [e for e in unknown_all if nsvs_bypassed(e)]
    rows = [row_record(e) for e in filtered]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    details_path = args.out_dir / "details.csv"
    fieldnames = list(rows[0].keys()) if rows else []
    with details_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rng = random.Random(args.seed)
    samples = {
        cat: sample_rows(rows, cat, 3, rng)
        for cat in ["spec_un_groundable", "spec_ok_no_detect", "spec_partial", "unclassifiable"]
    }

    report = render_markdown(
        entries_path=args.entries,
        rows=rows,
        unknown_total=len(unknown_all),
        samples=samples,
    )
    report_path = args.out_dir / "report.md"
    report_path.write_text(report + "\n", encoding="utf-8")

    cat_counts = Counter(r["category"] for r in rows)
    print(f"[puls-unknown] wrote {details_path} ({len(rows)} rows)")
    print(f"[puls-unknown] wrote {report_path}")
    print(f"[puls-unknown] categories: {dict(cat_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
