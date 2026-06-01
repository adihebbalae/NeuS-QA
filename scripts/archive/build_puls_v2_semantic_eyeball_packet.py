#!/usr/bin/env python3
"""Build a 20-row semantic eyeball packet for PULS v2 rescued specs (no API)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import cv2

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = Path(
    "/mnt/Data/ah66742/timelogic/outputs/puls_v2_validation_148/results.jsonl"
)
DEFAULT_OUT = REPO / "diagnostics/puls_v2_prep/SEMANTIC_EYEBALL_PACKET.md"
DEFAULT_DETAILS = REPO / "diagnostics/puls_unknown_analysis/details.csv"
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_DURATION_CSV = REPO / "diagnostics/sub5b_failure_audit_v3/video_duration_audit.csv"
DEFAULT_VIDEO_ROOT = Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos")

AUDIT_DURATION_BUCKETS: list[tuple[str, float | None, float | None]] = [
    ("<10s", None, 10.0),
    ("10-30s", 10.0, 30.0),
    ("30-60s", 30.0, 60.0),
    ("60-180s", 60.0, 180.0),
    (">180s", 180.0, None),
]

STEM_PATTERNS = [
    (re.compile(r"throughout the video", re.I), "atemporal-MC · throughout"),
    (re.compile(r"do in the video", re.I), "atemporal-MC · in-video"),
    (re.compile(r"always co-occurs", re.I), "co-occurrence MC"),
    (re.compile(r"does not overlap", re.I), "non-overlap MC"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    p.add_argument("--details-csv", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--duration-csv", type=Path, default=DEFAULT_DURATION_CSV)
    p.add_argument("--video-root", type=Path, default=DEFAULT_VIDEO_ROOT)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--per-bucket", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def question_core(text: str) -> str:
    t = text.replace("\n", " ").strip()
    for marker in ("Is it Option", "Reply with"):
        if marker in t:
            t = t.split(marker)[0].strip()
    return t


def stem_tag(text: str) -> str:
    for pat, label in STEM_PATTERNS:
        if pat.search(text):
            return label
    return "other"


def pick_diverse(pool: list[dict], n: int, rng: random.Random) -> list[dict]:
    by_src: dict[str, list[dict]] = defaultdict(list)
    for row in pool:
        by_src[row.get("source_dataset") or "?"].append(row)
    for rows in by_src.values():
        rng.shuffle(rows)
    srcs = sorted(by_src, key=lambda s: -len(by_src[s]))
    chosen: list[dict] = []
    while len(chosen) < n:
        progressed = False
        for src in srcs:
            if by_src[src] and len(chosen) < n:
                chosen.append(by_src[src].pop(0))
                progressed = True
        if not progressed:
            break
    if len(chosen) < n:
        rest = [r for r in pool if r not in chosen]
        rng.shuffle(rest)
        chosen.extend(rest[: n - len(chosen)])
    return chosen[:n]


def duration_bucket(seconds: float | None) -> str:
    if seconds is None or (isinstance(seconds, float) and math.isnan(seconds)):
        return "unknown"
    for label, low, high in AUDIT_DURATION_BUCKETS:
        if low is not None and seconds < low:
            continue
        if high is not None and seconds >= high:
            continue
        return label
    return ">180s"


def probe_opencv(path: Path) -> dict[str, float | int | None]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"duration_seconds": None, "fps": None, "frame_count": None}
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    cap.release()
    duration = (frame_count / fps) if fps > 0 and frame_count > 0 else None
    return {
        "duration_seconds": round(duration, 2) if duration is not None else None,
        "fps": round(fps, 2) if fps else None,
        "frame_count": frame_count,
    }


def load_entries_by_qid(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(e["metadata"]["question_id"]): e
        for e in data
        if e.get("metadata", {}).get("question_id") is not None
    }


def load_duration_by_video(csv_path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not csv_path.is_file():
        return out
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["video_id"]] = row
    return out


def resolve_video_path(
    video_id: str, entry: dict | None, video_root: Path
) -> Path | None:
    if entry:
        raw = (entry.get("paths") or {}).get("video_path") or ""
        if raw:
            p = Path(raw)
            if p.is_file():
                return p
    candidate = video_root / video_id
    return candidate if candidate.is_file() else None


def video_meta_for_qid(
    qid: str,
    entries: dict[str, dict],
    durations: dict[str, dict[str, str]],
    video_root: Path,
    from_md: Path,
) -> tuple[str, str]:
    """Return (markdown video line, duration bucket label)."""
    entry = entries.get(qid, {})
    meta = entry.get("metadata", {})
    video_id = meta.get("video_id") or "unknown"
    path = resolve_video_path(video_id, entry, video_root)

    dur_row = durations.get(video_id, {})
    seconds = dur_row.get("duration_seconds")
    fps = dur_row.get("fps")
    frames = dur_row.get("frame_count")
    if seconds in (None, "") and path is not None:
        probed = probe_opencv(path)
        seconds = probed.get("duration_seconds")
        fps = fps or probed.get("fps")
        frames = frames or probed.get("frame_count")

    try:
        sec_f = float(seconds) if seconds not in (None, "") else None
    except (TypeError, ValueError):
        sec_f = None

    bucket = duration_bucket(sec_f)
    src = (meta.get("source_dataset") or video_id.split("_", 1)[0]).lower()
    confound = ""
    if bucket == "<10s" and src in {"star", "agqa"}:
        confound = " · ⚠ star/agqa short-clip"

    if path is None:
        return (
            f"**Video:** `{video_id}` *(file not found)* · length **{bucket}**",
            bucket,
        )

    rel = Path(os.path.relpath(path, from_md.parent)).as_posix()
    if sec_f is not None:
        len_str = f"**~{sec_f:g} s** (OpenCV"
        if frames and fps:
            len_str += f", {frames} frames @ {fps} fps"
        len_str += f") · `{bucket}`{confound}"
    else:
        len_str = f"**length unknown** (OpenCV probe failed) · `{bucket}`{confound}"

    return (
        f"**Video:** [{video_id}]({rel}) — {len_str}  \n"
        f"<sub>Ctrl+click link in Cursor preview · `{path}`</sub>",
        bucket,
    )


def load_questions(details_path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with details_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[str(row["question_id"])] = row.get("question_text") or ""
    return out


def format_baseline(row: dict) -> str:
    if row["baseline_reason"] == "empty_puls_output":
        return "*(empty — no props, no spec)*"
    spec = (row.get("baseline_spec") or "").strip() or "*(empty)*"
    n = row.get("baseline_n_props", 0)
    return f"**{n} prop** · `{spec}`"


def format_v2(row: dict) -> str:
    props = row.get("v2_propositions") or []
    spec = (row.get("v2_specification") or "").strip()
    prop_lines = "\n".join(f"  - `{p}`" for p in props) if props else "  - *(none)*"
    return f"**{len(props)} props**\n{prop_lines}\n- **spec:** `{spec}`"


def reviewer_prompt(bucket: str) -> str:
    if bucket == "empty_puls_output":
        return (
            "Does the generic hook match an **atemporal “which action”** MC (not a specific "
            "option, not a temporal before/after)? **Over-fire** = question has a real anchor "
            "but spec ignores it."
        )
    return (
        "Does the spec encode **anchor + candidate relation** (co-occur = simultaneous AND; "
        "non-overlap = negated joint presence)? **Over-fire** = only anchor restated; "
        "**under-fire** = `NOT anchor` alone without candidate slot."
    )


def render_row(
    row: dict,
    idx: int,
    questions: dict[str, str],
    entries: dict[str, dict],
    durations: dict[str, dict[str, str]],
    video_root: Path,
    out_path: Path,
) -> list[str]:
    qid = row["question_id"]
    core = question_core(questions.get(qid, ""))
    tag = stem_tag(core)
    video_line, _dur_bucket = video_meta_for_qid(
        qid, entries, durations, video_root, out_path
    )
    return [
        f"### {idx}. QID {qid} · `{row.get('source_dataset','?')}` · {tag}",
        "",
        video_line,
        "",
        f"> {core}",
        "",
        "**Baseline (v1):** " + format_baseline(row).replace("\n", " · "),
        "",
        "**PULS v2:**",
        *([f"- `{p}`" for p in (row.get("v2_propositions") or [])] or ["- *(none)*"]),
        f"- spec: `{(row.get('v2_specification') or '').strip()}`",
        "",
        f"**Check:** {reviewer_prompt(row['baseline_reason'])}",
        "",
        "**Verdict:** ☐ OK · ☐ Wrong intent · ☐ Ambiguous · Note: _________",
        "",
        "---",
        "",
    ]


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)
    rows = [
        json.loads(line)
        for line in args.results.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    questions = load_questions(args.details_csv)
    entries = load_entries_by_qid(args.entries) if args.entries.is_file() else {}
    durations = load_duration_by_video(args.duration_csv)
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("rescued"):
            by_bucket[row["baseline_reason"]].append(row)

    lines = [
        "# PULS v2 — semantic eyeball packet (20 min)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"Source: `{args.results}`",
        "",
        "## Risk (read once)",
        "",
        "A **well-formed-but-wrong** spec can be worse than empty PULS: empty → NSVS bypass → "
        "VQA prior (~42–60% Yes on unknown-family). Wrong-but-valid → NSVS runs → confident bad "
        "crop → answer flips empty-fallback would not cause. Structural 148/148 pass does not prove "
        "semantic correctness.",
        "",
        "## How to skim",
        "",
        f"1. **Bucket A** ({args.per_bucket} rows) — generic `person performs action in video`",
        f"2. **Bucket B** ({args.per_bucket} rows) — `AND` co-occur / `NOT (anchor AND candidate)` non-overlap",
        "3. **Ctrl+click** the **Video** link on each row to open the raw mp4 in Cursor (relative path from this file).",
        "4. Mark **OK / Wrong intent / Ambiguous** per row. Flag over-fire (Example 13 on non-generic stems).",
        "",
        "**Pass bar:** no more than ~2 clear Wrong intent per bucket before full val PULS re-run.",
        "",
        "---",
        "",
        "## Bucket A — was `empty_puls_output` (94 rows total)",
        "",
        reviewer_prompt("empty_puls_output"),
        "",
    ]

    bucket_a = pick_diverse(by_bucket.get("empty_puls_output", []), args.per_bucket, rng)
    for i, row in enumerate(bucket_a, 1):
        lines.extend(
            render_row(row, i, questions, entries, durations, args.video_root, args.out)
        )

    lines.extend(
        [
            "## Bucket B — was `operator_collapse_open_ended` (54 rows total)",
            "",
            reviewer_prompt("operator_collapse_open_ended"),
            "",
        ]
    )
    bucket_b = pick_diverse(by_bucket.get("operator_collapse_open_ended", []), args.per_bucket, rng)
    for i, row in enumerate(bucket_b, 1):
        lines.extend(
            render_row(row, i, questions, entries, durations, args.video_root, args.out)
        )

    lines.extend(
        [
            "## Sign-off",
            "",
            "| Bucket | OK | Wrong | Ambiguous | Block val re-run? |",
            "| --- | ---: | ---: | ---: | --- |",
            "| A (empty → generic) | | | | ☐ |",
            "| B (collapse → AND/NOT) | | | | ☐ |",
            "",
            "**Reviewer:** _____________ **Date:** _____________",
            "",
        ]
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[eyeball] wrote {args.out} ({len(bucket_a)} + {len(bucket_b)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
