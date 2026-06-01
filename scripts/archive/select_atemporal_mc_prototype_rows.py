#!/usr/bin/env python3
"""Select a stratified 10-row prototype slice for atemporal-MC PULS mode.

Source pool: Bucket A atemporal which-action rows (empty_puls_output) from
diagnostics/puls_unknown_analysis/details.csv — stems matching the two templates:
  - What action does the person do throughout the video?
  - What does the person do in the video?

Output: diagnostics/atemporal_mc_prototype/manifest.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import cv2
except ImportError:
    cv2 = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DETAILS = REPO_ROOT / "diagnostics" / "puls_unknown_analysis" / "details.csv"
DEFAULT_DURATION_CSV = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3" / "video_duration_audit.csv"
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_SUB5B = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
    "submission_sub5b_paper_faithful_gpt52.json"
)
DEFAULT_SUB1 = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json")
DEFAULT_VIDEO_ROOT = Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos")
DEFAULT_OUT = REPO_ROOT / "diagnostics" / "atemporal_mc_prototype" / "manifest.json"

SELECTION_SEED = 20260526

STEM_THROUGHOUT = re.compile(
    r"what action does the person do throughout the video\s*\?",
    re.IGNORECASE,
)
STEM_IN_VIDEO = re.compile(
    r"what does the person do in the video\s*\?",
    re.IGNORECASE,
)

OPTION_RE = re.compile(
    r"Is it Option A:\s*(.+?),\s*Option B:\s*(.+?),\s*Option C:\s*(.+?),\s*Option D:\s*(.+?)(?:\.| Reply)",
    re.IGNORECASE | re.DOTALL,
)

STRATUM_TARGETS = {
    "short_star_agqa": 5,
    "mid_agqa": 3,
    "long_ct": 2,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--details", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--duration-csv", type=Path, default=DEFAULT_DURATION_CSV)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--sub5b", type=Path, default=DEFAULT_SUB5B)
    p.add_argument("--sub1", type=Path, default=DEFAULT_SUB1)
    p.add_argument("--video-root", type=Path, default=DEFAULT_VIDEO_ROOT)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--seed", type=int, default=SELECTION_SEED)
    p.add_argument("--probe-missing", action="store_true", help="OpenCV probe when duration missing")
    return p.parse_args()


def load_submission(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for row in rows:
        qid = str(row.get("question_id") or row.get("qid"))
        ans = row.get("answer_choice") or row.get("answer") or ""
        out[qid] = str(ans).strip()
    return out


def load_entries_by_qid(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(e["metadata"]["question_id"]): e
        for e in data
        if e.get("metadata", {}).get("question_id") is not None
    }


def parse_duration(value: str | float | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        f = float(value)
        return f if not math.isnan(f) else None
    except (TypeError, ValueError):
        return None


def load_duration_by_video(csv_path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    if not csv_path.is_file():
        return out
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d = parse_duration(row.get("duration_seconds"))
            if d is not None:
                out[row["video_id"]] = d
    return out


def probe_opencv(path: Path) -> float | None:
    if cv2 is None or not path.is_file():
        return None
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return None
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    cap.release()
    if fps > 0 and frame_count > 0:
        return round(frame_count / fps, 2)
    return None


def resolve_video_path(video_id: str, entry: dict | None, video_root: Path) -> Path | None:
    if entry:
        raw = (entry.get("paths") or {}).get("video_path") or ""
        if raw:
            p = Path(raw)
            if p.is_file():
                return p
    candidate = video_root / video_id
    return candidate if candidate.is_file() else None


def extract_stem(question: str) -> str:
    text = re.sub(r"\s+", " ", question.replace("\n", " ").strip())
    text = re.sub(
        r"(?i)^The following is a multiple choice question with four possible answer choices: A, B, C, D\.\s*",
        "",
        text,
    )
    text = re.sub(r"(?i)\s*Reply with the chosen option in one character\.?\s*$", "", text)
    if " Is it Option " in text:
        text = text.split(" Is it Option ")[0].strip()
    return text


def stem_template_label(stem: str) -> str:
    if STEM_THROUGHOUT.search(stem):
        return "throughout_the_video"
    if STEM_IN_VIDEO.search(stem):
        return "in_the_video"
    return "other"


def is_atemporal_which_action_stem(stem: str) -> bool:
    return bool(STEM_THROUGHOUT.search(stem) or STEM_IN_VIDEO.search(stem))


def parse_options(question: str, entry: dict | None) -> list[dict[str, str]]:
    candidates = entry.get("candidates") if entry else None
    if candidates and len(candidates) >= 2:
        letters = "ABCD"
        return [
            {"letter": letters[i], "text": str(opt).strip()}
            for i, opt in enumerate(candidates[:4])
        ]
    match = OPTION_RE.search(question)
    if match:
        return [
            {"letter": letter, "text": val.strip()}
            for letter, val in zip("ABCD", match.groups(), strict=True)
        ]
    return []


def duration_for_row(
    video_id: str,
    entry: dict | None,
    dur_by_video: dict[str, float],
    video_root: Path,
    probe_missing: bool,
) -> tuple[float | None, str]:
    """Return (seconds, source_tag)."""
    if video_id in dur_by_video:
        return dur_by_video[video_id], "video_duration_audit.csv"
    meta = (entry or {}).get("metadata") or {}
    fps = meta.get("fps")
    frame_count = meta.get("frame_count")
    if fps and frame_count:
        return round(float(frame_count) / float(fps), 2), "entries_metadata"
    if probe_missing:
        path = resolve_video_path(video_id, entry, video_root)
        if path:
            probed = probe_opencv(path)
            if probed is not None:
                return probed, "opencv_probe"
    return None, "missing"


def build_pool_row(
    detail: dict[str, str],
    entry: dict | None,
    dur_by_video: dict[str, float],
    video_root: Path,
    probe_missing: bool,
    sub5b: dict[str, str],
    sub1: dict[str, str],
) -> dict[str, Any] | None:
    question = detail["question_text"]
    stem = extract_stem(question)
    if not is_atemporal_which_action_stem(stem):
        return None

    qid = str(detail["question_id"])
    meta = (entry or {}).get("metadata") or {}
    video_id = meta.get("video_id") or ""
    source_dataset = (
        detail.get("source_dataset") or meta.get("source_dataset") or video_id.split("_", 1)[0]
    ).lower()
    duration_sec, duration_source = duration_for_row(
        video_id, entry, dur_by_video, video_root, probe_missing
    )
    options = parse_options(question, entry)
    if len(options) < 2:
        return None

    return {
        "qid": int(qid) if qid.isdigit() else qid,
        "video_id": video_id,
        "stem": stem,
        "stem_template": stem_template_label(stem),
        "options": options,
        "source_dataset": source_dataset,
        "video_duration_sec": duration_sec,
        "duration_source": duration_source,
        "sub5b_current_answer": sub5b.get(qid, ""),
        "sub1_current_answer": sub1.get(qid, ""),
    }


def stratum_for_row(row: dict[str, Any]) -> str | None:
    src = row["source_dataset"]
    dur = row["video_duration_sec"]
    if dur is None:
        return None
    if src in ("star", "agqa") and dur < 10:
        return "short_star_agqa"
    if src == "agqa" and 10 <= dur < 60:
        return "mid_agqa"
    if src == "ct" and dur >= 60:
        return "long_ct"
    return None


def mid_agqa_fallback_pool(
    pool: list[dict[str, Any]], exclude_qids: set[Any]
) -> list[dict[str, Any]]:
    """AGQA <10s rows not already picked for short_star_agqa."""
    return [
        r
        for r in pool
        if r["qid"] not in exclude_qids
        and r["source_dataset"] == "agqa"
        and r["video_duration_sec"] is not None
        and r["video_duration_sec"] < 10
    ]


def sample_stratum(
    candidates: list[dict[str, Any]],
    k: int,
    rng: random.Random,
) -> list[dict[str, Any]]:
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda r: (str(r["qid"]), r["video_id"]))
    if len(ordered) <= k:
        return ordered
    return rng.sample(ordered, k)


def select_rows(pool: list[dict[str, Any]], seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = random.Random(seed)
    notes: dict[str, Any] = {}
    pool_by_stratum: dict[str, list[dict[str, Any]]] = {k: [] for k in STRATUM_TARGETS}
    for row in pool:
        s = stratum_for_row(row)
        if s:
            pool_by_stratum[s].append(row)

    notes["pool_counts"] = {k: len(v) for k, v in pool_by_stratum.items()}
    notes["pool_total"] = len(pool)

    selected: list[dict[str, Any]] = []
    used_qids: set[Any] = set()

    # 1) short_star_agqa
    short = sample_stratum(pool_by_stratum["short_star_agqa"], STRATUM_TARGETS["short_star_agqa"], rng)
    for r in short:
        r = {**r, "stratum": "short_star_agqa"}
        selected.append(r)
        used_qids.add(r["qid"])

    # 2) mid_agqa — prefer 10–60s; fallback to short AGQA
    mid_primary = [r for r in pool_by_stratum["mid_agqa"] if r["qid"] not in used_qids]
    if len(mid_primary) >= STRATUM_TARGETS["mid_agqa"]:
        mid = sample_stratum(mid_primary, STRATUM_TARGETS["mid_agqa"], rng)
        notes["mid_agqa"] = "Filled from AGQA 10–60s pool."
    else:
        fallback = mid_agqa_fallback_pool(pool, used_qids)
        need = STRATUM_TARGETS["mid_agqa"]
        mid = sample_stratum(fallback, need, rng)
        notes["mid_agqa"] = (
            f"Requested AGQA 10–60s: {len(mid_primary)} eligible in pool of {len(pool)}; "
            f"filled {need} rows from AGQA <10s (adjacent short bucket)."
        )
    for r in mid:
        r = {**r, "stratum": "mid_agqa"}
        selected.append(r)
        used_qids.add(r["qid"])

    # 3) long_ct
    long_pool = [r for r in pool_by_stratum["long_ct"] if r["qid"] not in used_qids]
    long_rows = sample_stratum(long_pool, STRATUM_TARGETS["long_ct"], rng)
    if len(long_rows) < STRATUM_TARGETS["long_ct"]:
        notes["long_ct"] = (
            f"Undersupplied: wanted {STRATUM_TARGETS['long_ct']}, got {len(long_rows)} "
            f"(pool had {len(long_pool)} after exclusions)."
        )
    for r in long_rows:
        r = {**r, "stratum": "long_ct"}
        selected.append(r)
        used_qids.add(r["qid"])

    return selected, notes


def manifest_row(row: dict[str, Any]) -> dict[str, Any]:
    dur = row["video_duration_sec"]
    if isinstance(dur, float):
        dur = round(dur, 2)
    return {
        "qid": row["qid"],
        "video_id": row["video_id"],
        "stem": row["stem"],
        "options": row["options"],
        "source_dataset": row["source_dataset"],
        "video_duration_sec": dur,
        "stratum": row["stratum"],
        "sub5b_current_answer": row["sub5b_current_answer"],
        "sub1_current_answer": row["sub1_current_answer"],
    }


def main() -> None:
    args = parse_args()
    dur_by_video = load_duration_by_video(args.duration_csv)
    entries = load_entries_by_qid(args.entries)
    sub5b = load_submission(args.sub5b)
    sub1 = load_submission(args.sub1)

    pool: list[dict[str, Any]] = []
    skipped_no_options = 0
    with args.details.open(newline="", encoding="utf-8") as f:
        for detail in csv.DictReader(f):
            if detail.get("category_reason") != "empty_puls_output":
                continue
            qid = str(detail["question_id"])
            row = build_pool_row(
                detail,
                entries.get(qid),
                dur_by_video,
                args.video_root,
                args.probe_missing,
                sub5b,
                sub1,
            )
            if row is None:
                if detail.get("question_text") and is_atemporal_which_action_stem(
                    extract_stem(detail["question_text"])
                ):
                    skipped_no_options += 1
                continue
            pool.append(row)

    selected, stratum_notes = select_rows(pool, args.seed)
    stratum_counts = {k: 0 for k in STRATUM_TARGETS}
    for r in selected:
        stratum_counts[r["stratum"]] = stratum_counts.get(r["stratum"], 0) + 1

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "selection_seed": args.seed,
        "source": {
            "details_csv": str(args.details),
            "filter": 'category_reason == "empty_puls_output" AND atemporal which-action stem',
            "pool_size": len(pool),
        },
        "stratum_targets": STRATUM_TARGETS,
        "stratum_counts": stratum_counts,
        "stratum_notes": stratum_notes,
        "skipped_no_options": skipped_no_options,
        "rows": [manifest_row(r) for r in selected],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} ({len(selected)} rows, pool={len(pool)})")
    print("stratum_counts:", stratum_counts)
    for key, note in stratum_notes.items():
        if key.startswith("pool") or key == "pool_total":
            continue
        print(f"  {key}: {note}")


if __name__ == "__main__":
    main()
