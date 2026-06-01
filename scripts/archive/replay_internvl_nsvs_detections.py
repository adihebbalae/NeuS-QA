#!/usr/bin/env python3
"""Replay InternVL2-8B NSVS detections on the same windows as a gpt5.2 run.

Writes per-qid internvl_detection_log JSON for head-to-head vote comparison.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", required=True, help="entries.json from gpt5.2 NSVS run")
    p.add_argument("--output-dir", required=True, help="Where to write internvl_detection_logs/")
    p.add_argument("--sample-rate", type=float, default=3.0)
    p.add_argument("--device", type=int, default=0)
    p.add_argument(
        "--cache-dir",
        default=None,
        help="Detection cache root (default: <output-dir>/nsvs_detection_cache)",
    )
    p.add_argument("--proposition-model", default="InternVL2-8B")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    return p.parse_args()


def load_json(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def replay_entry(entry: dict, vlm, sample_rate: float, device: int) -> list[dict]:
    from nsvqa.nsvs.nsvs import run_nsvs
    from nsvqa.nsvs.video.read_video import Mp4Reader

    puls = entry.get("puls") or {}
    propositions = puls.get("proposition") or []
    specification = puls.get("specification") or ""
    if not propositions:
        return []

    reader = Mp4Reader(path=entry["paths"]["video_path"], sample_rate=sample_rate)
    video_data = reader.read_video()
    vlm.detection_log = []
    run_nsvs(
        video_data,
        entry["paths"]["video_path"],
        propositions,
        specification,
        device=device,
        model=vlm.model_name,
        vlm=vlm,
    )
    return list(getattr(vlm, "detection_log", []))


def main() -> int:
    args = parse_args()
    from nsvqa.utils.env_loader import load_env_file

    load_env_file(args.env_file)

    from nsvqa.nsvs.vlm.detection_cache import DetectionCache
    from nsvqa.nsvs.vlm.internvl import InternVL

    entries = load_json(args.entries)
    if args.limit is not None:
        entries = entries[: args.limit]

    out_dir = Path(args.output_dir)
    log_dir = out_dir / "internvl_detection_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = args.cache_dir or str(out_dir / "nsvs_detection_cache")
    cache = DetectionCache(cache_dir, backend="internvl")

    print(f"[replay-internvl] loading InternVL2-8B on cuda:{args.device}")
    vlm = InternVL(model_name=args.proposition_model, device=args.device)
    vlm.backend = "internvl"
    vlm.cache = cache  # type: ignore[attr-defined]

    summary = []
    for i, entry in enumerate(entries):
        qid = str(entry["metadata"]["question_id"])
        print(f"[replay-internvl] [{i + 1}/{len(entries)}] qid={qid}")
        try:
            detection_log = replay_entry(entry, vlm, args.sample_rate, args.device)
            out_path = log_dir / f"{qid}.json"
            out_path.write_text(json.dumps(detection_log, indent=2) + "\n", encoding="utf-8")
            summary.append({"question_id": qid, "n_detections": len(detection_log), "status": "ok"})
        except Exception as exc:
            summary.append({"question_id": qid, "n_detections": 0, "status": f"error: {exc!r}"})

    summary_path = out_dir / "internvl_replay_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    ok = sum(1 for r in summary if r["status"] == "ok")
    print(f"[replay-internvl] completed {ok}/{len(summary)} -> {log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
