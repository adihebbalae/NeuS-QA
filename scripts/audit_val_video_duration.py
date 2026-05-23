#!/usr/bin/env python3
"""Probe TimeLogic val video durations without ffprobe.

ffprobe/ffmpeg are not installed on this host (admin constraint). This script uses
OpenCV container metadata (frame_count, fps) — the same probe path already used
for QID 1809 calibration. Results are approximate vs ffprobe for some codecs.

Outputs:
  diagnostics/sub5b_failure_audit_v3/video_duration_audit.csv
  diagnostics/sub5b_failure_audit_v3/video_duration_audit.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ANN = Path("/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json")
DEFAULT_VIDEO_ROOT = Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos")
DEFAULT_OUT_DIR = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ann", type=Path, default=DEFAULT_ANN)
    p.add_argument("--video-root", type=Path, default=DEFAULT_VIDEO_ROOT)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument(
        "--phase",
        choices=("val", "test"),
        default="val",
        help="Label for report headings (default: val)",
    )
    p.add_argument(
        "--probe-backend",
        choices=("auto", "opencv", "ffprobe"),
        default="auto",
        help="auto prefers ffprobe when installed, else OpenCV",
    )
    return p.parse_args()


def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def source_dataset(video_id: str) -> str:
    return video_id.split("_", 1)[0] if "_" in video_id else "unknown"


def probe_opencv(path: Path) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"error": "opencv_open_failed"}
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    duration = (frame_count / fps) if fps > 0 and frame_count > 0 else None
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_seconds": round(duration, 6) if duration is not None else None,
        "width": width,
        "height": height,
    }


def probe_ffprobe(path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=avg_frame_rate,nb_frames,r_frame_rate,width,height",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"error": f"ffprobe_failed: {proc.stderr.strip()[:200]}"}
    data = json.loads(proc.stdout or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    def parse_rate(value: str | None) -> float | None:
        if not value or value in {"0/0", "N/A"}:
            return None
        if "/" in value:
            num, den = value.split("/", 1)
            den_f = float(den)
            return float(num) / den_f if den_f else None
        return float(value)

    fps = parse_rate(stream.get("avg_frame_rate")) or parse_rate(stream.get("r_frame_rate"))
    frame_count = int(stream.get("nb_frames")) if stream.get("nb_frames") not in (None, "N/A") else None
    duration = float(fmt["duration"]) if fmt.get("duration") not in (None, "N/A") else None
    if duration is None and fps and frame_count:
        duration = frame_count / fps
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_seconds": round(duration, 6) if duration is not None else None,
        "width": stream.get("width"),
        "height": stream.get("height"),
    }


def speed_flags(duration: float | None) -> dict[str, bool]:
    if duration is None:
        return {
            "flag_lt_2s": False,
            "flag_lt_1s": False,
            "flag_lt_0_5s": False,
            "speed_distortion_risk": False,
        }
    return {
        "flag_lt_2s": duration < 2.0,
        "flag_lt_1s": duration < 1.0,
        "flag_lt_0_5s": duration < 0.5,
        "speed_distortion_risk": duration < 2.0,
    }


def load_val_videos(ann_path: Path) -> tuple[list[str], Counter[str]]:
    with ann_path.open(encoding="utf-8") as f:
        rows = json.load(f)
    question_counts = Counter(row["video_id"] for row in rows)
    unique_videos = sorted(question_counts)
    return unique_videos, question_counts


def render_summary_markdown(
    *,
    phase: str,
    ann_path: Path,
    video_root: Path,
    backend: str,
    ffprobe_present: bool,
    rows: list[dict[str, Any]],
    question_counts: Counter[str],
) -> str:
    probed = [r for r in rows if not r.get("error")]
    missing = [r for r in rows if r.get("error") == "missing_on_disk"]
    failed = [r for r in rows if r.get("error") not in (None, "missing_on_disk")]

    def count_flag(key: str) -> int:
        return sum(1 for r in probed if r.get(key))

    by_source = Counter(r["source_dataset"] for r in probed)
    lt2_by_source = Counter(
        r["source_dataset"] for r in probed if r.get("flag_lt_2s")
    )

    lines = [
        f"# {phase.capitalize()} video duration audit (OpenCV)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Probe method",
        "",
    ]
    if backend == "ffprobe":
        lines.append("- Backend: **ffprobe** (ffmpeg installed).")
    else:
        lines.append(
            "- Backend: **OpenCV** (`cv2.VideoCapture` metadata) — **ffprobe not installed** on this host."
        )
        lines.append(
            "- Admin action needed for canonical container probes: `sudo apt install ffmpeg` "
            "(or run this script on a machine with ffprobe and `--probe-backend ffprobe`)."
        )
        lines.append(
            "- OpenCV durations matched QID 1809 calibration (`star_1SLTT.mp4`: 14 frames @ 25 fps → 0.56 s) "
            "but may diverge from ffprobe on some codecs."
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            f"- Annotations: `{ann_path}`",
            f"- Video root: `{video_root}`",
            f"- Unique {phase} videos referenced: **{len(rows)}**",
            f"- {phase.capitalize()} question rows referencing those videos: **{sum(question_counts.values())}**",
            f"- Probed successfully: **{len(probed)}**",
            f"- Missing on disk: **{len(missing)}**",
            f"- Probe errors: **{len(failed)}**",
            "",
            "## Speed-distortion flags (likely time-warped clips)",
            "",
            "Thresholds flag videos where temporal operators (`immediately_after`, `since`, …) "
            "may collapse at 1× playback (cf. QID 1809).",
            "",
            f"| Threshold | Videos | % of probed |",
            f"| --- | ---: | ---: |",
        ]
    )
    if probed:
        lines.extend(
            [
                f"| `< 2.0 s` | {count_flag('flag_lt_2s')} | {count_flag('flag_lt_2s') / len(probed) * 100:.1f}% |",
                f"| `< 1.0 s` | {count_flag('flag_lt_1s')} | {count_flag('flag_lt_1s') / len(probed) * 100:.1f}% |",
                f"| `< 0.5 s` | {count_flag('flag_lt_0_5s')} | {count_flag('flag_lt_0_5s') / len(probed) * 100:.1f}% |",
            ]
        )
    else:
        lines.extend(
            [
                "| `< 2.0 s` | 0 | — |",
                "| `< 1.0 s` | 0 | — |",
                "| `< 0.5 s` | 0 | — |",
            ]
        )
    lines.extend(
        [
            "",
            "## By source dataset (`< 2 s` / total probed)",
            "",
            "| Source | probed | `< 2 s` | `< 2 s` % |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for src in sorted(by_source):
        total = by_source[src]
        lt2 = lt2_by_source.get(src, 0)
        lines.append(f"| {src} | {total} | {lt2} | {lt2 / total * 100:.1f}% |")

    shortest = sorted(
        (r for r in probed if r.get("duration_seconds") is not None),
        key=lambda r: float(r["duration_seconds"]),
    )[:15]
    lines.extend(
        [
            "",
            "## Shortest probed videos (top 15)",
            "",
            "| video_id | duration (s) | fps | frames | question rows |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in shortest:
        lines.append(
            f"| {row['video_id']} | {row['duration_seconds']:.3f} | {row.get('fps')} | "
            f"{row.get('frame_count')} | {row.get('question_rows')} |"
        )

    if missing:
        lines.extend(["", "## Missing on disk", ""])
        for row in missing[:20]:
            lines.append(f"- `{row['video_id']}`")
        if len(missing) > 20:
            lines.append(f"- … and {len(missing) - 20} more")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- CSV: `video_duration_audit.csv`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    has_ffprobe = ffprobe_available()
    if args.probe_backend == "auto":
        backend = "ffprobe" if has_ffprobe else "opencv"
    else:
        backend = args.probe_backend
        if backend == "ffprobe" and not has_ffprobe:
            print("[video-audit] ERROR: ffprobe requested but not installed.", flush=True)
            return 1

    probe_fn = probe_ffprobe if backend == "ffprobe" else probe_opencv
    video_ids, question_counts = load_val_videos(args.ann)

    rows: list[dict[str, Any]] = []
    for i, video_id in enumerate(video_ids, start=1):
        path = args.video_root / video_id
        base = {
            "video_id": video_id,
            "source_dataset": source_dataset(video_id),
            "path": str(path),
            "question_rows": question_counts[video_id],
            "probe_backend": backend,
        }
        if not path.is_file():
            rows.append({**base, "error": "missing_on_disk"})
            continue
        result = probe_fn(path)
        flags = speed_flags(result.get("duration_seconds"))
        rows.append({**base, **result, **flags, "error": result.get("error")})
        if i % 100 == 0:
            print(f"[video-audit] probed {i}/{len(video_ids)}", flush=True)

    csv_path = args.out_dir / "video_duration_audit.csv"
    fieldnames = [
        "video_id",
        "source_dataset",
        "path",
        "question_rows",
        "probe_backend",
        "duration_seconds",
        "fps",
        "frame_count",
        "width",
        "height",
        "flag_lt_2s",
        "flag_lt_1s",
        "flag_lt_0_5s",
        "speed_distortion_risk",
        "error",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    md_path = args.out_dir / "video_duration_audit.md"
    md_path.write_text(
        render_summary_markdown(
            phase=args.phase,
            ann_path=args.ann,
            video_root=args.video_root,
            backend=backend,
            ffprobe_present=has_ffprobe,
            rows=rows,
            question_counts=question_counts,
        )
        + "\n",
        encoding="utf-8",
    )

    probed = [r for r in rows if not r.get("error")]
    lt2 = sum(1 for r in probed if r.get("flag_lt_2s"))
    print(f"[video-audit] backend={backend} ffprobe_installed={has_ffprobe}")
    print(f"[video-audit] wrote {csv_path}")
    print(f"[video-audit] wrote {md_path}")
    print(f"[video-audit] probed={len(probed)} lt2s={lt2}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
