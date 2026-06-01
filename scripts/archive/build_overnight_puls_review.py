#!/usr/bin/env python3
"""Build overnight PULS failure review doc for AM eyeballing.

See diagnostics/puls_unknown_analysis/OVERNIGHT_PULS_PREP.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DETAILS = REPO_ROOT / "diagnostics" / "puls_unknown_analysis" / "details.csv"
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_VAL = Path("/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json")
DEFAULT_SUB5B = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_SUB1 = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json")
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "puls_unknown_analysis" / "overnight_review.md"
PROMPTS_PY = REPO_ROOT / "nsvqa" / "puls" / "prompts.py"

AUDIT_DURATION_BUCKETS: list[tuple[str, float | None, float | None]] = [
    ("<10s", None, 10.0),
    ("10-30s", 10.0, 30.0),
    ("30-60s", 30.0, 60.0),
    ("60-180s", 60.0, 180.0),
    (">180s", 180.0, None),
]

STEM_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)^what did the person", "What did the person …"),
    (r"(?i)^what action does the person", "What action does the person …"),
    (r"(?i)^which action", "Which action …"),
    (r"(?i)^how does the person", "How does the person …"),
    (r"(?i)^how did the person", "How did the person …"),
    (r"(?i)^does the person eventually", "Does the person eventually …"),
    (r"(?i)^is the person always", "Is the person always …"),
    (r"(?i)^is it true that person", "Is it true that person …"),
    (r"(?i)^do person .+ overlap", "Do person … overlap"),
    (r"(?i)^did the person", "Did the person …"),
    (r"(?i)^what happens", "What happens …"),
    (r"(?i)^what is the person", "What is the person …"),
]

OPERATOR_CUES = [
    "until",
    "since",
    "before",
    "after",
    "while",
    "when",
    "during",
    "always",
    "eventually",
    "overlap",
    "co-occur",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--details", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--val", type=Path, default=DEFAULT_VAL)
    p.add_argument("--sub5b", type=Path, default=DEFAULT_SUB5B)
    p.add_argument("--sub1", type=Path, default=DEFAULT_SUB1)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def load_submission(path: Path) -> dict[str, str]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for row in rows:
        qid = str(row.get("question_id") or row.get("qid"))
        ans = row.get("answer_choice") or row.get("answer") or ""
        out[qid] = str(ans).strip()
    return out


def duration_seconds(entry: dict | None) -> float | None:
    if not entry:
        return None
    metadata = entry.get("metadata", {})
    fps = metadata.get("fps")
    frame_count = metadata.get("frame_count")
    if not fps or not frame_count:
        return None
    return float(frame_count) / float(fps)


def duration_bucket(seconds: float | None) -> str:
    if seconds is None or math.isnan(seconds):
        return "unknown"
    for label, low, high in AUDIT_DURATION_BUCKETS:
        if low is not None and seconds < low:
            continue
        if high is not None and seconds >= high:
            continue
        return label
    return ">180s"


def clean_question_for_display(question: str) -> str:
    text = question.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def question_stem_sort_key(question: str) -> str:
    text = clean_question_for_display(question)
    text = re.sub(
        r"(?i)^The following is a multiple choice question with four possible answer choices: A, B, C, D\.\s*",
        "",
        text,
    )
    text = re.sub(r"(?i)\s*Reply with the chosen option in one character\.?\s*$", "", text)
    if " Is it Option " in text:
        text = text.split(" Is it Option ")[0].strip()
    return text.lower()


def classify_stem(question: str) -> str:
    text = clean_question_for_display(question)
    for pattern, label in STEM_PATTERNS:
        if re.search(pattern, text):
            return label
    words = text.split()[:6]
    return " ".join(words) + (" …" if len(text.split()) > 6 else "")


def word_count(question: str) -> int:
    text = clean_question_for_display(question)
    return len(text.split())


def format_options(entry: dict | None, question: str) -> str:
    candidates = entry.get("candidates") if entry else None
    if candidates and len(candidates) >= 2:
        letters = "ABCD"
        parts = []
        for i, opt in enumerate(candidates[:4]):
            parts.append(f"{letters[i]}: {opt}")
        return ", ".join(parts)
    match = re.search(
        r"Is it Option A:\s*(.+?),\s*Option B:\s*(.+?),\s*Option C:\s*(.+?),\s*Option D:\s*(.+?)(?:\.| Reply)",
        question,
        flags=re.I | re.DOTALL,
    )
    if match:
        return ", ".join(
            f"{letter}: {val.strip()}"
            for letter, val in zip("ABCD", match.groups(), strict=True)
        )
    return "—"


def extract_puls_prompt_template() -> str:
    text = PROMPTS_PY.read_text(encoding="utf-8")
    start = text.find('full_prompt = f"""')
    if start == -1:
        return "_Could not extract prompt template from prompts.py_"
    start += len('full_prompt = f"""')
    end = text.find('"""', start)
    template = text[start:end]
    return template.replace("{prompt}", "<QUESTION_TEXT>")


def operator_cue_counts(questions: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for q in questions:
        lower = q.lower()
        for cue in OPERATOR_CUES:
            if cue in lower:
                counts[cue] += 1
    return counts


def bucket_tally(rows: list[dict], entries_by_qid: dict[str, dict]) -> list[str]:
    modes = Counter(r["question_mode"] for r in rows)
    sources = Counter(r["source_dataset"] for r in rows)
    stems = Counter(classify_stem(r["question_text"]) for r in rows)
    lengths = [word_count(r["question_text"]) for r in rows]
    avg_len = sum(lengths) / len(lengths) if lengths else 0.0

    lines = [
        f"- Mode breakdown: **{modes.get('mc', 0)} MC**, **{modes.get('bool', 0)} bool**",
        "- Question-stem frequencies (top 10):",
    ]
    for stem, count in stems.most_common(10):
        lines.append(f"  - `{stem}`: **{count}**")
    lines.append("- Source dataset breakdown:")
    for src in sorted(sources):
        lines.append(f"  - **{src}**: {sources[src]}")
    lines.append(f"- Average question length: **{avg_len:.1f}** words")

    unique_stems = len(stems)
    top_stem_share = stems.most_common(1)[0][1] / len(rows) * 100 if rows and stems else 0
    lines.extend(
        [
            "",
            "**Pattern notes (auto, no fix proposals):**",
            f"- Unique stem buckets: **{unique_stems}**; top stem covers **{top_stem_share:.1f}%** of bucket.",
        ]
    )
    if modes.get("mc", 0) / len(rows) > 0.75 if rows else False:
        lines.append("- Failures are **MC-heavy** — likely MC template / candidate-parameterization gap.")
    elif modes.get("bool", 0) / len(rows) > 0.75 if rows else False:
        lines.append("- Failures are **bool-heavy**.")
    else:
        lines.append("- MC/bool split is **mixed** — inspect both prompt paths.")

    top_src = sources.most_common(1)[0] if sources else ("?", 0)
    lines.append(
        f"- Largest source slice: **{top_src[0]}** ({top_src[1]}/{len(rows)}). "
        f"{'Concentrated in short-clip sources.' if top_src[0] in {'agqa', 'star'} else 'Spread includes long-form sources.'}"
    )
    return lines


def render_row(
    row: dict,
    *,
    entry: dict | None,
    sub5b: dict[str, str],
    sub1: dict[str, str],
    bucket: str,
) -> list[str]:
    qid = row["question_id"]
    question = clean_question_for_display(row["question_text"])
    mode = row["question_mode"]
    source = row["source_dataset"]
    dur = duration_bucket(duration_seconds(entry))
    props = json.loads(row["propositions"]) if row["propositions"] else []
    spec = row["puls_spec"] or ""
    target = ""
    if entry:
        target = (entry.get("target_identification") or {}).get("explanation") or ""
        target = target.replace("\n", " ").strip()

    lines = [
        f"#### QID {qid} ({source}, {mode}, {dur})",
        "",
        f"**Question:** {question}",
    ]
    if mode == "mc":
        lines.append(f"**Options:** {format_options(entry, question)}")
    if bucket == "A":
        lines.append("**PULS output:** EMPTY (no spec, no propositions)")
    else:
        lines.append("**PULS output:**")
        lines.append(f"  - propositions: {props}")
        lines.append(f"  - spec: `{spec}`")
    if target:
        lines.append(f"**Target-ID padding:** {target[:400]}{'…' if len(target) > 400 else ''}")
    lines.append(f"**Sub #5B answer:** {sub5b.get(qid, '—')}")
    lines.append(f"**Sub #1 answer:** {sub1.get(qid, '—')}")
    lines.append("")
    return lines


def render_bucket(
    title: str,
    rows: list[dict],
    *,
    bucket_code: str,
    entries_by_qid: dict[str, dict],
    sub5b: dict[str, str],
    sub1: dict[str, str],
    extra_tally: list[str] | None = None,
) -> list[str]:
    rows = sorted(rows, key=lambda r: question_stem_sort_key(r["question_text"]))
    lines = [
        f"## {title}",
        "",
        "### Light tally (Cursor-computed, for Adi's morning skim)",
        "",
        *bucket_tally(rows, entries_by_qid),
    ]
    if extra_tally:
        lines.extend(["", *extra_tally])
    lines.extend(
        [
            "",
            "### Rows (sorted by question-stem alphabetically)",
            "",
        ]
    )
    for row in rows:
        lines.extend(render_row(row, entry=entries_by_qid.get(row["question_id"]), sub5b=sub5b, sub1=sub1, bucket=bucket_code))
    return lines


def main() -> int:
    args = parse_args()
    if not args.details.exists():
        print(f"Missing details: {args.details}", file=sys.stderr)
        return 2

    details = list(csv.DictReader(args.details.open(encoding="utf-8")))
    bucket_a = [r for r in details if r["category_reason"] == "empty_puls_output"]
    bucket_b = [r for r in details if r["category_reason"] == "operator_collapse_open_ended"]

    entries_by_qid: dict[str, dict] = {}
    if args.entries.exists():
        for entry in json.loads(args.entries.read_text(encoding="utf-8")):
            qid = str(entry.get("metadata", {}).get("question_id") or entry.get("question_id"))
            entries_by_qid[qid] = entry

    sub5b = load_submission(args.sub5b) if args.sub5b.exists() else {}
    sub1 = load_submission(args.sub1) if args.sub1.exists() else {}

    prompt_template = extract_puls_prompt_template()
    op_counts = operator_cue_counts([r["question_text"] for r in bucket_b])
    op_lines = [
        "- Operator-cue frequencies in questions:",
        *[f"  - `{cue}`: **{op_counts.get(cue, 0)}**" for cue in OPERATOR_CUES if op_counts.get(cue, 0)],
    ]
    if bucket_b:
        top_op = op_counts.most_common(1)[0] if op_counts else ("none", 0)
        op_lines.append(
            f"- Dominant cue: **{top_op[0]}** ({top_op[1]}/{len(bucket_b)} rows). "
            f"{'Single-cue concentration → targeted template fix.' if top_op[1] > len(bucket_b)*0.5 else 'Cues spread → broader temporal-encoding fix.'}"
        )

    lines = [
        f"# Overnight PULS review — bucket A ({len(bucket_a)} empty-PULS rows) + "
        f"bucket B ({len(bucket_b)} operator-collapse rows)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## PULS prompt currently in production",
        "",
        "From `nsvqa/puls/prompts.py` → `find_prompt()` (single user message; `{prompt}` filled per question):",
        "",
        "```",
        prompt_template,
        "```",
        "",
    ]
    lines.extend(
        render_bucket(
            f"Bucket A — empty PULS output ({len(bucket_a)} rows)",
            bucket_a,
            bucket_code="A",
            entries_by_qid=entries_by_qid,
            sub5b=sub5b,
            sub1=sub1,
        )
    )
    lines.append("")
    lines.extend(
        render_bucket(
            f"Bucket B — operator-collapse open-ended ({len(bucket_b)} rows)",
            bucket_b,
            bucket_code="B",
            entries_by_qid=entries_by_qid,
            sub5b=sub5b,
            sub1=sub1,
            extra_tally=op_lines,
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[overnight-puls] wrote {args.out}")
    print(f"[overnight-puls] bucket A={len(bucket_a)} bucket B={len(bucket_b)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
