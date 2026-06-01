#!/usr/bin/env python3
"""Run atemporal-MC prototype: PULS_atemporal_mc + per-choice InternVL NSVS.

Reads diagnostics/atemporal_mc_prototype/manifest.json. No VQA — measures whether
NSVS alone differentiates MC options via per-choice single-prop specs.

Outputs:
  diagnostics/atemporal_mc_prototype/runs/qid_<QID>.json
  diagnostics/atemporal_mc_prototype/runs/all_rows.jsonl
  diagnostics/atemporal_mc_prototype/runs/nsvs/qid_<QID>_<LETTER>.json  (raw dumps)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_MANIFEST = REPO_ROOT / "diagnostics/atemporal_mc_prototype/manifest.json"
DEFAULT_OUT = REPO_ROOT / "diagnostics/atemporal_mc_prototype/runs"
DEFAULT_VIDEO_ROOT = Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos")

# Sub #5B paper-faithful NSVS settings (run_sub5b_test.sh / run_nsvs defaults)
DEFAULT_SAMPLE_RATE = 3.0
DEFAULT_PROP_MODEL = "InternVL2-8B"
DEFAULT_PULS_MODEL = "gpt-4o"
NUM_OF_FRAME_IN_SEQUENCE = 3
TL_SATISFACTION_THRESHOLD = 0.6
DETECTION_THRESHOLD = 0.5
VLM_DETECTION_THRESHOLD = 0.349


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--video-root", type=Path, default=DEFAULT_VIDEO_ROOT)
    p.add_argument("--device", type=int, default=0)
    p.add_argument("--sample-rate", type=float, default=DEFAULT_SAMPLE_RATE)
    p.add_argument("--proposition-model", default=DEFAULT_PROP_MODEL)
    p.add_argument("--puls-model", default=DEFAULT_PULS_MODEL)
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--resume", action="store_true", help="Skip QIDs with existing qid_*.json")
    p.add_argument("--qid", type=int, default=None, help="Run a single QID from manifest")
    return p.parse_args()


def load_env(path: str) -> None:
    from nsvqa.utils.env_loader import load_env_file

    load_env_file(path)


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def video_path_for_row(row: dict[str, Any], video_root: Path) -> Path:
    vid = row["video_id"]
    p = video_root / vid
    if not p.is_file() and not str(vid).endswith(".mp4"):
        p = video_root / f"{vid}.mp4"
    return p


def summarize_detection_scores(detection_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate VLM scores surfaced in NSVS detection_log."""
    if not detection_log:
        return {
            "per_window": [],
            "max_probability": None,
            "max_confidence": None,
            "mean_probability": None,
            "n_windows_scored": 0,
        }
    probs = [float(d["probability"]) for d in detection_log if d.get("probability") is not None]
    confs = [float(d["confidence"]) for d in detection_log if d.get("confidence") is not None]
    per_window = [
        {
            "window_idx": d.get("window_idx"),
            "is_detected": d.get("is_detected"),
            "confidence": d.get("confidence"),
            "probability": d.get("probability"),
        }
        for d in detection_log
    ]
    return {
        "per_window": per_window,
        "max_probability": max(probs) if probs else None,
        "max_confidence": max(confs) if confs else None,
        "mean_probability": round(sum(probs) / len(probs), 4) if probs else None,
        "n_windows_scored": len(detection_log),
    }


def count_grounded_windows(detection_log: list[dict[str, Any]]) -> int:
    return sum(1 for d in detection_log if d.get("is_detected"))


def count_supporting_frames(
    foi: list[int],
    all_detections: list[list[int]],
    num_of_frame_in_sequence: int,
    frame_step: int,
) -> int:
    """Native-frame count implied by NSVS windows / merged FOI."""
    if foi and foi != [-1]:
        if len(foi) == 1:
            return 1
        return int(foi[1]) - int(foi[0]) + 1
    native: set[int] = set()
    scale = num_of_frame_in_sequence * frame_step
    for split in all_detections or []:
        for win_idx in split or []:
            start = int(win_idx) * scale
            end = start + scale - 1
            native.update(range(start, end + 1))
    return len(native)


def run_nsvs_for_choice(
    video_data: dict,
    video_path: str,
    proposition: list[str],
    specification: str,
    vlm: Any,
    device: int,
    model_name: str,
) -> tuple[list[int], list[list[int]], list[dict[str, Any]]]:
    from nsvqa.nsvs.nsvs import run_nsvs

    vlm.detection_log = []
    foi, indices = run_nsvs(
        video_data,
        video_path,
        proposition,
        specification,
        device=device,
        model=model_name,
        vlm=vlm,
        num_of_frame_in_sequence=NUM_OF_FRAME_IN_SEQUENCE,
        tl_satisfaction_threshold=TL_SATISFACTION_THRESHOLD,
        detection_threshold=DETECTION_THRESHOLD,
        vlm_detection_threshold=VLM_DETECTION_THRESHOLD,
    )
    detection_log = list(getattr(vlm, "detection_log", []))
    return foi, indices, detection_log


def build_choice_record(
    row: dict[str, Any],
    letter: str,
    proposition: str,
    specification: str,
    foi: list[int],
    indices: list[list[int]],
    detection_log: list[dict[str, Any]],
    video_data: dict,
    raw_path: Path,
) -> dict[str, Any]:
    fps = float(video_data["video_info"]["fps"] or 1.0)
    frame_step = max(1, int(round(fps / video_data["sample_rate"])))

    raw_payload = {
        "qid": row["qid"],
        "choice_letter": letter,
        "video_id": row["video_id"],
        "proposition": proposition,
        "specification": specification,
        "foi": foi,
        "indices": indices,
        "detection_log": detection_log,
        "nsvs_params": {
            "sample_rate": video_data["sample_rate"],
            "num_of_frame_in_sequence": NUM_OF_FRAME_IN_SEQUENCE,
            "tl_satisfaction_threshold": TL_SATISFACTION_THRESHOLD,
            "detection_threshold": DETECTION_THRESHOLD,
            "vlm_detection_threshold": VLM_DETECTION_THRESHOLD,
            "frame_step": frame_step,
        },
    }
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(raw_payload, indent=2) + "\n", encoding="utf-8")

    tl_satisfaction = foi != [-1]
    return {
        "choice_letter": letter,
        "option_text": next(
            (o["text"] for o in row["options"] if o["letter"] == letter),
            "",
        ),
        "proposition": proposition,
        "specification": specification,
        "tl_satisfaction": tl_satisfaction,
        "foi": foi,
        "nsvs_indices": indices,
        "detection_score": summarize_detection_scores(detection_log),
        "n_grounded_windows": count_grounded_windows(detection_log),
        "n_supporting_frames": count_supporting_frames(
            foi, indices, NUM_OF_FRAME_IN_SEQUENCE, frame_step
        ),
        "raw_nsvs_output_path": str(raw_path),
    }


def process_row(
    row: dict[str, Any],
    args: argparse.Namespace,
    vlm: Any,
    out_dir: Path,
    llm_history_dir: Path,
) -> dict[str, Any]:
    from nsvqa.nsvs.video.read_video import Mp4Reader
    from nsvqa.puls.puls import PULS_atemporal_mc

    qid = row["qid"]
    t0 = time.time()
    record: dict[str, Any] = {
        "qid": qid,
        "video_id": row["video_id"],
        "stratum": row.get("stratum"),
        "source_dataset": row.get("source_dataset"),
        "video_duration_sec": row.get("video_duration_sec"),
        "stem": row["stem"],
        "status": "pending",
    }

    os.environ["NSVQA_LLM_HISTORY_DIR"] = str(llm_history_dir)
    puls_t0 = time.time()
    try:
        puls_out = PULS_atemporal_mc(
            question=row["stem"],
            choices=row["options"],
            model=args.puls_model,
        )
    except Exception as exc:
        record["status"] = "puls_error"
        record["error"] = repr(exc)
        record["traceback"] = traceback.format_exc()
        record["seconds"] = round(time.time() - t0, 2)
        return record

    record["puls_atemporal_mc"] = puls_out
    record["puls_seconds"] = round(time.time() - puls_t0, 2)
    record["puls_api_cost_usd"] = puls_out.get("api_cost_usd")
    record["puls_api_usage"] = puls_out.get("api_usage")

    if puls_out.get("error"):
        record["status"] = "puls_guardrail"
        record["seconds"] = round(time.time() - t0, 2)
        return record

    props = puls_out.get("propositions") or []
    specs = puls_out.get("specifications") or []
    letters = puls_out.get("choice_letters") or []
    if not (len(props) == len(specs) == len(letters)):
        record["status"] = "puls_format_error"
        record["error"] = "propositions/specifications/choice_letters length mismatch"
        record["seconds"] = round(time.time() - t0, 2)
        return record

    vpath = video_path_for_row(row, args.video_root)
    if not vpath.is_file():
        record["status"] = "video_missing"
        record["error"] = f"video not found: {vpath}"
        record["seconds"] = round(time.time() - t0, 2)
        return record

    try:
        reader = Mp4Reader(path=str(vpath), sample_rate=args.sample_rate)
        video_data = reader.read_video()
        if video_data is None:
            raise RuntimeError("Mp4Reader returned None")
        video_data["sample_rate"] = args.sample_rate
    except Exception as exc:
        record["status"] = "read_video_error"
        record["error"] = repr(exc)
        record["traceback"] = traceback.format_exc()
        record["seconds"] = round(time.time() - t0, 2)
        return record

    nsvs_dir = out_dir / "nsvs"
    choice_records: list[dict[str, Any]] = []
    model_name = getattr(vlm, "model_name", args.proposition_model)

    for letter, prop, spec in zip(letters, props, specs, strict=True):
        raw_path = nsvs_dir / f"qid_{qid}_{letter}.json"
        try:
            foi, indices, detection_log = run_nsvs_for_choice(
                video_data,
                str(vpath),
                [prop],
                spec,
                vlm,
                args.device,
                model_name,
            )
            choice_records.append(
                build_choice_record(
                    row,
                    letter,
                    prop,
                    spec,
                    foi,
                    indices,
                    detection_log,
                    video_data,
                    raw_path,
                )
            )
        except Exception as exc:
            choice_records.append(
                {
                    "choice_letter": letter,
                    "proposition": prop,
                    "specification": spec,
                    "status": "nsvs_error",
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                    "raw_nsvs_output_path": str(raw_path),
                }
            )

    record["choices"] = choice_records
    record["choice_summary"] = {
        c["choice_letter"]: {
            "tl_satisfaction": c.get("tl_satisfaction"),
            "max_probability": (c.get("detection_score") or {}).get("max_probability"),
            "n_grounded_windows": c.get("n_grounded_windows"),
            "n_supporting_frames": c.get("n_supporting_frames"),
        }
        for c in choice_records
        if c.get("choice_letter")
    }
    n_ok = sum(1 for c in choice_records if c.get("tl_satisfaction") is not None)
    n_sat = sum(1 for c in choice_records if c.get("tl_satisfaction"))
    record["differentiation"] = {
        "n_choices": len(choice_records),
        "n_tl_satisfied": n_sat,
        "satisfied_letters": [c["choice_letter"] for c in choice_records if c.get("tl_satisfaction")],
        "max_prob_by_letter": {
            c["choice_letter"]: (c.get("detection_score") or {}).get("max_probability")
            for c in choice_records
            if c.get("choice_letter")
        },
    }
    record["status"] = "ok" if n_ok == len(choice_records) else "partial"
    record["seconds"] = round(time.time() - t0, 2)
    return record


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def rebuild_all_rows_jsonl(out_dir: Path) -> None:
    """Rewrite all_rows.jsonl from per-qid files (idempotent)."""
    jsonl_path = out_dir / "all_rows.jsonl"
    qid_files = sorted(out_dir.glob("qid_*.json"))
    lines = []
    for p in qid_files:
        if p.name == "qid_template.json":
            continue
        lines.append(json.loads(p.read_text(encoding="utf-8")))
    jsonl_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    load_env(args.env_file)

    manifest = load_manifest(args.manifest)
    rows = manifest["rows"]
    if args.qid is not None:
        rows = [r for r in rows if r["qid"] == args.qid]
        if not rows:
            print(f"QID {args.qid} not in manifest", file=sys.stderr)
            return 1
    if args.limit is not None:
        rows = rows[: args.limit]

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    llm_history_dir = out_dir / "llm_history"
    llm_history_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "manifest": str(args.manifest),
        "puls_model": args.puls_model,
        "proposition_model": args.proposition_model,
        "sample_rate": args.sample_rate,
        "device": args.device,
        "nsvs": {
            "num_of_frame_in_sequence": NUM_OF_FRAME_IN_SEQUENCE,
            "tl_satisfaction_threshold": TL_SATISFACTION_THRESHOLD,
            "detection_threshold": DETECTION_THRESHOLD,
            "vlm_detection_threshold": VLM_DETECTION_THRESHOLD,
        },
        "n_rows": len(rows),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    from nsvqa.nsvs.vlm.detection_cache import DetectionCache
    from nsvqa.nsvs.vlm.internvl import InternVL

    cache_dir = out_dir / "nsvs_detection_cache"
    cache = DetectionCache(str(cache_dir), backend="internvl")
    print(f"[prototype] loading {args.proposition_model} on cuda:{args.device}")
    vlm = InternVL(model_name=args.proposition_model, device=args.device)
    vlm.backend = "internvl"
    vlm.cache = cache  # type: ignore[attr-defined]

    jsonl_path = out_dir / "all_rows.jsonl"
    if not args.resume and jsonl_path.is_file():
        jsonl_path.unlink()

    done = 0
    skipped = 0
    for i, row in enumerate(rows):
        qid = row["qid"]
        qid_path = out_dir / f"qid_{qid}.json"
        if args.resume and qid_path.is_file():
            existing = json.loads(qid_path.read_text(encoding="utf-8"))
            if existing.get("status") in ("ok", "partial", "puls_guardrail"):
                skipped += 1
                print(f"[prototype] [{i + 1}/{len(rows)}] qid={qid} resume skip")
                continue

        print(f"[prototype] [{i + 1}/{len(rows)}] qid={qid} stratum={row.get('stratum')}")
        record = process_row(row, args, vlm, out_dir, llm_history_dir)
        qid_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        append_jsonl(jsonl_path, record)
        done += 1
        print(
            f"  status={record.get('status')} "
            f"puls_cost={record.get('puls_api_cost_usd')} "
            f"diff={record.get('differentiation')}"
        )

    rebuild_all_rows_jsonl(out_dir)
    print(f"[prototype] done processed={done} skipped={skipped} -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
