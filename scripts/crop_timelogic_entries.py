#!/usr/bin/env python3
"""Crop TimeLogic videos from NSVS frames_of_interest using NeuS-QA postprocess."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", required=True, help="Merged NSVS entries.json")
    p.add_argument("--output-dir", required=True, help="Directory for cropped videos and postprocess_entries.json")
    p.add_argument(
        "--video-root",
        default="/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos",
        help="TimeLogic video root, only needed to instantiate the loader.",
    )
    p.add_argument(
        "--ann-path",
        default="/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json",
        help="TimeLogic annotation path, only needed to instantiate the loader.",
    )
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from nsvqa.datamanager.timelogic import TimeLogic

    out_dir = Path(args.output_dir)
    cropped_dir = out_dir / "cropped_videos"
    cropped_dir.mkdir(parents=True, exist_ok=True)

    entries = load_json(args.entries)
    loader = TimeLogic(video_root=args.video_root, ann_path=args.ann_path, verbose=False)

    out_entries = []
    failures: list[dict[str, str]] = []
    for entry in tqdm(entries, desc="crop/sub5b"):
        qid = str(entry.get("metadata", {}).get("question_id") or entry.get("question_id"))
        cropped_path = cropped_dir / f"{qid}.mp4"
        entry.setdefault("paths", {})
        entry["paths"]["cropped_path"] = str(cropped_path)

        if not entry.get("metadata", {}).get("video_present", True):
            entry["metadata"]["crop_error"] = "source video missing on disk"
            entry["paths"]["cropped_path"] = entry["paths"].get("video_path", "")
        else:
            try:
                loader.crop_video(entry, save_path=str(cropped_path), ground_truth=False)
            except Exception as exc:  # noqa: BLE001 - keep the full run moving.
                entry.setdefault("metadata", {})
                entry["metadata"]["crop_error"] = repr(exc)
                entry["paths"]["cropped_path"] = entry["paths"].get("video_path", "")
                failures.append({"question_id": qid, "error": repr(exc)})

        out_entries.append(entry)

    with (out_dir / "postprocess_entries.json").open("w", encoding="utf-8") as f:
        json.dump(out_entries, f, indent=2, default=str)
    with (out_dir / "crop_summary.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "entries": len(out_entries),
                "crop_failures": len(failures),
                "failures": failures[:200],
                "cropped_dir": str(cropped_dir),
            },
            f,
            indent=2,
        )

    print(f"[crop] wrote {out_dir / 'postprocess_entries.json'}")
    print(f"[crop] crop_failures={len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
