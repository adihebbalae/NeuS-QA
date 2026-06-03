#!/usr/bin/env python3
"""Extract representative frames for taxonomy clips (Task 4)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT, evenly_spaced_frames, video_path, write_json

MAX_DENSE_FRAMES = 30
LONG_CLIP_FRAME_COUNT = 6


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--taxonomy", type=Path, default=AFRL_ROOT / "taxonomy.json")
    p.add_argument("--frames-root", type=Path, default=AFRL_ROOT / "frames")
    return p.parse_args()


def video_meta(path: Path) -> tuple[float, int, float]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video: {path}")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    duration = (frame_count / fps) if fps > 0 and frame_count > 0 else 0.0
    cap.release()
    return fps, frame_count, duration


def frame_indices_for_clip(duration_s: float, frame_count: int, fps: float) -> list[int]:
    if duration_s < 2.0 and frame_count > 0:
        if frame_count <= MAX_DENSE_FRAMES:
            return list(range(frame_count))
        return evenly_spaced_frames(frame_count, MAX_DENSE_FRAMES)
    n = min(LONG_CLIP_FRAME_COUNT, max(4, frame_count))
    return evenly_spaced_frames(frame_count, n) if frame_count > 0 else []


def timestamp_for_index(frame_idx: int, fps: float) -> float:
    if fps <= 0:
        return 0.0
    return frame_idx / fps


def in_foi_window(ts: float, foi_window: list[float] | None) -> bool:
    if not foi_window or len(foi_window) < 2:
        return False
    start, end = float(foi_window[0]), float(foi_window[1])
    return start <= ts <= end


def extract_frame_ffmpeg(video: Path, ts: float, out_path: Path) -> bool:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{ts:.4f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode == 0 and out_path.is_file() and out_path.stat().st_size > 0


def extract_frame_opencv(video: Path, frame_idx: int, out_path: Path) -> bool:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return False
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return cv2.imwrite(str(out_path), frame)


def process_clip(record: dict[str, Any], frames_root: Path) -> dict[str, Any]:
    qid = record["qid"]
    split = record["split"]
    video_id = record.get("video_id")
    if not video_id:
        manifest_video = None
        raise RuntimeError(f"qid {qid} missing video_id — rebuild taxonomy from manifest")
    video = video_path(split, video_id) if video_id else None
    if video is None or not video.is_file():
        # fallback: load video_id from enriched manifest field if added later
        raise RuntimeError(f"video missing for qid {qid}: {video}")

    fps, frame_count, duration = video_meta(video)
    indices = frame_indices_for_clip(record.get("duration_s") or duration, frame_count, fps)
    foi_window = record.get("foi_window")
    dense_note = duration < 2.0 and frame_count > MAX_DENSE_FRAMES

    out_dir = frames_root / qid
    frame_records: list[dict[str, Any]] = []
    for frame_idx in indices:
        ts = timestamp_for_index(frame_idx, fps)
        foi = in_foi_window(ts, foi_window)
        suffix = "_foi" if foi else ""
        fname = f"frame_{frame_idx:05d}_t{ts:.2f}s{suffix}.png"
        out_path = out_dir / fname
        ok = extract_frame_ffmpeg(video, ts, out_path)
        if not ok:
            ok = extract_frame_opencv(video, frame_idx, out_path)
        if not ok:
            print(f"[frames] WARN qid={qid} failed frame {frame_idx}", flush=True)
            continue
        frame_records.append(
            {
                "path": str(out_path),
                "frame_idx": frame_idx,
                "timestamp_s": round(ts, 3),
                "in_foi_window": foi,
            }
        )

    record["frames"] = [f["path"] for f in frame_records]
    record["frames_meta"] = frame_records
    if dense_note:
        record["frames_note"] = f"<2s clip subsampled to {MAX_DENSE_FRAMES} frames (native {frame_count})"
    return record


def main() -> int:
    args = parse_args()
    taxonomy: list[dict[str, Any]] = json.loads(args.taxonomy.read_text(encoding="utf-8"))

    # Attach video_id from enriched manifest if missing
    manifest_path = AFRL_ROOT / "enriched_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        by_key = {(r["split"], r["qid"]): r for r in manifest}
        for rec in taxonomy:
            key = (rec["split"], rec["qid"])
            if key in by_key:
                rec.setdefault("video_id", by_key[key]["video_id"])

    updated: list[dict[str, Any]] = []
    for rec in taxonomy:
        print(f"[frames] qid={rec['qid']} split={rec['split']}", flush=True)
        updated.append(process_clip(rec, args.frames_root))

    # Write taxonomy without frames_meta in main JSON (keep spec clean)
    out_records = []
    for rec in updated:
        clean = {k: v for k, v in rec.items() if k != "frames_meta"}
        out_records.append(clean)

    write_json(args.taxonomy, out_records)
    print(f"[frames] updated {args.taxonomy} clips={len(out_records)}")
    total_frames = sum(len(r.get("frames") or []) for r in out_records)
    print(f"[frames] total frames extracted={total_frames}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
