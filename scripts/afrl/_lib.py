"""Shared helpers for AFRL taxonomy / accuracy-by-length reports."""

from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from compare_submissions import (  # noqa: E402
    duration_bucket,
    load_submission,
    normalize_answer,
    valid_foi,
)

AFRL_ROOT = Path("/mnt/Data/ah66742/timelogic/reports/afrl")

PATHS = {
    "val_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json"),
    "test_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json"),
    "val_videos": Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos"),
    "test_videos": Path("/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json"),
    "sub1": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json"),
    "sub5b": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
        "submission_sub5b_paper_faithful_gpt52.json"
    ),
    "sub7b": Path("/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/submission_sub7b.json"),
    "baseline_test": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/submission.json"),
    "sub5b_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2"),
    "sub7b_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful"),
}

LENGTH_BUCKET_ORDER = ["<2s", "2-10s", "10-60s", ">60s", "unknown"]


def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def source_dataset(video_id: str) -> str:
    return video_id.split("_", 1)[0] if "_" in video_id else "unknown"


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


def load_annotations(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_per_entry(qid: str, shards_root: Path) -> dict[str, Any] | None:
    for p in shards_root.glob(f"shard_*/per_entry/{qid}.json"):
        if p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("entry") or data
    return None


def entry_from_shard(qid: str, split: str) -> dict[str, Any] | None:
    shards = PATHS["sub5b_shards"] if split == "val" else PATHS["sub7b_shards"]
    return find_per_entry(qid, shards)


def video_path(split: str, video_id: str) -> Path:
    root = PATHS["val_videos"] if split == "val" else PATHS["test_videos"]
    return root / video_id


def probe_opencv(path: Path) -> dict[str, Any]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"error": "opencv_open_failed"}
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    cap.release()
    duration = (frame_count / fps) if fps > 0 and frame_count > 0 else None
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_s": round(duration, 6) if duration is not None else None,
    }


def probe_ffprobe(path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=avg_frame_rate,nb_frames,r_frame_rate",
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
    frame_count_raw = stream.get("nb_frames")
    frame_count = (
        int(frame_count_raw) if frame_count_raw not in (None, "N/A") else None
    )
    duration = float(fmt["duration"]) if fmt.get("duration") not in (None, "N/A") else None
    if duration is None and fps and frame_count:
        duration = frame_count / fps
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_s": round(duration, 6) if duration is not None else None,
    }


def probe_video(path: Path, backend: str = "auto") -> dict[str, Any]:
    use_ffprobe = backend == "ffprobe" or (backend == "auto" and ffprobe_available())
    if use_ffprobe:
        result = probe_ffprobe(path)
        if "error" not in result:
            result["probe_backend"] = "ffprobe"
            return result
    result = probe_opencv(path)
    result["probe_backend"] = "opencv" if "error" not in result else result.get("probe_backend", "opencv")
    return result


def length_bucket(duration_s: float | None) -> str:
    return duration_bucket(duration_s)


def foi_window_from_entry(entry: dict[str, Any] | None) -> list[float] | None:
    if not entry:
        return None
    foi = entry.get("frames_of_interest")
    fps = (entry.get("metadata") or {}).get("fps")
    if not valid_foi(foi) or not fps:
        return None
    start_s = round(float(foi[0]) / float(fps), 3)
    end_s = round(float(foi[1]) / float(fps), 3)
    return [start_s, end_s]


def load_duration_cache(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = f"{row['split']}:{row['qid']}"
            out[key] = row
    return out


def duration_cache_key(split: str, qid: str) -> str:
    return f"{split}:{qid}"


def load_enriched_manifest(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def our_answer_for_split(qid: str, split: str, sub5b: dict[str, str], sub7b: dict[str, str]) -> str:
    return sub5b.get(qid) if split == "val" else sub7b.get(qid, "")


def vanilla_answer_for_split(
    qid: str, split: str, sub1: dict[str, str], baseline_test: dict[str, str]
) -> str:
    return sub1.get(qid) if split == "val" else baseline_test.get(qid, "")


def evenly_spaced_frames(frame_count: int, n: int) -> list[int]:
    if frame_count <= 0:
        return []
    if n >= frame_count:
        return list(range(frame_count))
    if n <= 1:
        return [0]
    return sorted({round(i * (frame_count - 1) / (n - 1)) for i in range(n)})
