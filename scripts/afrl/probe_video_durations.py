#!/usr/bin/env python3
"""Probe video durations for all val+test TimeLogic qids (Task 1)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import (
    AFRL_ROOT,
    PATHS,
    length_bucket,
    load_annotations,
    probe_video,
    source_dataset,
    video_path,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "duration_cache.csv")
    p.add_argument(
        "--probe-backend",
        choices=("auto", "opencv", "ffprobe"),
        default="auto",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | float | None]] = []
    for split, ann_path in [("val", PATHS["val_ann"]), ("test", PATHS["test_ann"])]:
        annotations = load_annotations(ann_path)
        for i, ann in enumerate(annotations, start=1):
            qid = str(ann["question_id"])
            video_id = ann["video_id"]
            path = video_path(split, video_id)
            base = {
                "qid": qid,
                "split": split,
                "video_id": video_id,
                "source": source_dataset(video_id),
                "video_path": str(path),
            }
            if not path.is_file():
                rows.append(
                    {
                        **base,
                        "duration_s": "",
                        "length_bucket": "unknown",
                        "fps": "",
                        "frame_count": "",
                        "probe_backend": "",
                        "error": "missing_on_disk",
                    }
                )
                continue
            result = probe_video(path, backend=args.probe_backend)
            duration = result.get("duration_s")
            rows.append(
                {
                    **base,
                    "duration_s": duration if duration is not None else "",
                    "length_bucket": length_bucket(duration) if duration is not None else "unknown",
                    "fps": result.get("fps") or "",
                    "frame_count": result.get("frame_count") or "",
                    "probe_backend": result.get("probe_backend") or "",
                    "error": result.get("error") or "",
                }
            )
            if i % 500 == 0:
                print(f"[probe] {split}: {i}/{len(annotations)}", flush=True)

    fieldnames = [
        "qid",
        "split",
        "video_id",
        "source",
        "video_path",
        "duration_s",
        "length_bucket",
        "fps",
        "frame_count",
        "probe_backend",
        "error",
    ]
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    probed = sum(1 for r in rows if r.get("duration_s") not in ("", None))
    missing = sum(1 for r in rows if r.get("error") == "missing_on_disk")
    print(f"[probe] wrote {args.out} rows={len(rows)} probed={probed} missing={missing}")
    for qid in ("682", "1865"):
        match = next((r for r in rows if r["qid"] == qid), None)
        if match:
            print(f"[probe] spot-check qid={qid} duration_s={match.get('duration_s')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
