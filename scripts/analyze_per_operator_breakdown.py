#!/usr/bin/env python3
"""Per-operator-family Sub #1 vs Sub #5B breakdown on val.

Without local ground truth we cannot compute per-operator accuracy. This script
emits, for each operator family, agreement rate (Sub #1 answer == Sub #5B answer)
and Sub #5B FOI == [-1] rate from the offline comparison artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DETAILS = (
    REPO_ROOT.parent / "timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/details.csv"
)
DEFAULT_SUMMARY = (
    REPO_ROOT.parent / "timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2/summary.json"
)
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3" / "per_operator_breakdown.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--details-csv", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


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


def load_details(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def stats(items: list[dict[str, str]]) -> dict[str, Any]:
    n = len(items)
    agree = sum(1 for row in items if as_bool(row.get("same_answer", "")))
    foi_minus_one = sum(1 for row in items if row.get("foi_status") == "-1")
    return {
        "n": n,
        "agree": agree,
        "disagree": n - agree,
        "agree_pct": round(agree / n * 100, 1) if n else 0.0,
        "disagree_pct": round((n - agree) / n * 100, 1) if n else 0.0,
        "foi_minus_one": foi_minus_one,
        "foi_minus_one_pct": round(foi_minus_one / n * 100, 1) if n else 0.0,
    }


def pct(n: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{n / total * 100:.1f}%"


def render_family_table(rows: list[tuple[str, dict[str, Any]]]) -> list[str]:
    lines = [
        "| Operator | n | Agree | Disagree | Agree % | FOI == [-1] | FOI=-1 % |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, row in rows:
        lines.append(
            f"| {label} | {row['n']} | {row['agree']} | {row['disagree']} | "
            f"{row['agree_pct']}% | {row['foi_minus_one']} | {row['foi_minus_one_pct']}% |"
        )
    return lines


def render_markdown(
    *,
    details_path: Path,
    summary: dict[str, Any],
    all_rows: list[dict[str, str]],
    by_family: dict[str, list[dict[str, str]]],
) -> str:
    overall = stats(all_rows)
    score = summary.get("score_delta_bounds", {})
    score_a = score.get("score_a_pct")
    score_b = score.get("score_b_pct")

    lines = [
        "# Per-operator breakdown: Sub #1 vs Sub #5B (val)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Caveat",
        "",
        "EvalAI exposes **submission-level** scores only (Sub #1 **50.5%**, Sub #5B **53.35%** on val).",
        "There is no local ground-truth file, so **per-operator accuracy cannot be computed**.",
        "Tables below report:",
        "",
        "- **Agreement rate** — fraction of rows where Sub #1 and Sub #5B gave the same answer",
        "- **FOI == [-1] rate** — fraction of rows where Sub #5B merged `frames_of_interest` to `[-1]`",
        "",
        f"- Source: `{details_path}` ({overall['n']} rows)",
        "",
        "## Overall",
        "",
        f"- Agreement: **{overall['agree']}/{overall['n']} ({overall['agree_pct']}%)**",
        f"- Disagreement: **{overall['disagree']}/{overall['n']} ({overall['disagree_pct']}%)**",
        f"- Sub #5B `FOI == [-1]`: **{overall['foi_minus_one']}/{overall['n']} ({overall['foi_minus_one_pct']}%)**",
    ]
    if score_a is not None and score_b is not None:
        lines.append(
            f"- EvalAI accuracy (submission-level): Sub #1 **{score_a}%**, Sub #5B **{score_b}%** "
            f"(net **+{float(score_b) - float(score_a):.2f}** pts for Sub #5B)"
        )
    lines.append("")

    family_order = sorted(
        by_family,
        key=lambda fam: (-len(by_family[fam]), fam),
    )

    for family in family_order:
        items = by_family[family]
        family_stats = stats(items)
        guess_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in items:
            guess_groups[row.get("operator_guess") or "unknown"].append(row)

        lines.extend(
            [
                f"## Operator family: `{family}`",
                "",
                f"Family totals: **n={family_stats['n']}**, "
                f"agreement **{family_stats['agree_pct']}%**, "
                f"FOI=-1 **{family_stats['foi_minus_one_pct']}%**",
                "",
            ]
        )

        table_rows: list[tuple[str, dict[str, Any]]] = []
        if len(guess_groups) == 1:
            only_guess = next(iter(guess_groups))
            table_rows.append((only_guess, family_stats))
        else:
            table_rows.append(("**family total**", family_stats))
            for guess in sorted(guess_groups, key=lambda g: (-len(guess_groups[g]), g)):
                table_rows.append((guess, stats(guess_groups[guess])))

        lines.extend(render_family_table(table_rows))
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Operator family collapses raw `operator_guess` the same way as the failure-audit packet "
            "(`immediately_after` → `after`, etc.).",
            "- High agreement does not imply both submissions are correct — only that they match.",
            "- High FOI=-1 within a family flags weak NSVS/Storm retrieval, not necessarily worse accuracy.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    all_rows = load_details(args.details_csv)
    for row in all_rows:
        row["operator_family"] = operator_family(row.get("operator_guess", "unknown"))

    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_rows:
        by_family[row["operator_family"]].append(row)

    markdown = render_markdown(
        details_path=args.details_csv,
        summary=load_summary(args.summary_json),
        all_rows=all_rows,
        by_family=by_family,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown + "\n", encoding="utf-8")

    overall = stats(all_rows)
    print(f"[per-operator] wrote {args.out}")
    print(
        f"[per-operator] overall agreement {overall['agree']}/{overall['n']} "
        f"({overall['agree_pct']}%)"
    )
    print(
        f"[per-operator] overall FOI=-1 {overall['foi_minus_one']}/{overall['n']} "
        f"({overall['foi_minus_one_pct']}%)"
    )
    print(f"[per-operator] operator families: {len(by_family)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
