"""TimeLogic-specific driver for the NeuS-QA neuro-symbolic pipeline.

Runs PULS (LQ2TL) -> NSVS (proposition detection + Storm model checking) ->
target identification (padding relative to the NSVS interval) -> merge into
frames_of_interest, for each
question in the TimeLogic val annotations. Writes per-entry JSON plus a
diagnostic summary.

Does NOT invoke the downstream VQA (final-answer) step in this driver. That is
a separate concern: TimeLogic has Yes/No questions that the upstream vqa.py
does not support, and the upstream vLLM-server setup is its own task. Run
the answering step as a follow-on with the postprocess output this script
writes.

Hardcoded `/nas/mars/...` paths in puls/llm.py are bypassed via the
NSVQA_LLM_HISTORY_DIR env var, which this driver sets to <output_dir>/llm_history.

Example:
    python3 scripts/run_timelogic.py \\
        --video-root /mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos \\
        --ann-path /mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json \\
        --output-dir /mnt/Data/ah66742/timelogic/outputs/smoke_v0 \\
        --device 0 \\
        --limit 10 \\
        --seed 0
"""

import argparse
import collections
import json
import os
import random
import sys
import time
import traceback
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--video-root", required=True, help="Directory containing the video files")
    p.add_argument("--ann-path", required=True, help="Path to timelogic_val_data.json")
    p.add_argument("--output-dir", required=True, help="Where to write per-entry results and the diag summary")
    p.add_argument("--device", type=int, default=0, help="CUDA device for InternVL")
    p.add_argument("--limit", type=int, default=None,
                   help="Max entries to process. Default: 10 for smoke, unlimited for --full-val.")
    p.add_argument("--full-val", action="store_true",
                   help="Process the val shard (all entries with video_present), not a smoke subset.")
    p.add_argument("--total-splits", type=int, default=1,
                   help="Split val into N shards for parallel GPU workers (1-indexed --current-split).")
    p.add_argument("--current-split", type=int, default=1,
                   help="Which shard to run (1 .. total-splits).")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for the smoke subset selection")
    p.add_argument(
        "--proposition-model",
        default="InternVL2-8B",
        help="HuggingFace model name suffix for the proposition detector. The upstream class re-prepends 'OpenGVLab/'.",
    )
    p.add_argument(
        "--puls-model",
        default="gpt-4o-mini",
        help="OpenAI model for PULS (LQ2TL) and target_identification. "
             "Lab key constraint (2026-05-19): no gpt-5.4 / 5.5 access yet. "
             "Tiering per .cursor/rules/workflow.md: 'gpt-4o-mini' for dev "
             "($0.15/$0.60 per 1M), 'gpt-5.2' for val/test ($1.75/$14, PI's recc "
             "within constraint), 'gpt-5' as backup. Promote to 'gpt-5.4' / "
             "'gpt-5.4-mini' once the lab key gets 5.4 access.",
    )
    p.add_argument("--sample-rate", type=float, default=1.0, help="NeuS-QA frame sampling rate (fps-equivalent)")
    p.add_argument(
        "--smoke-strategy",
        choices=["mixed", "first"],
        default="mixed",
        help="'mixed' = sample to cover modes+source_datasets+operator families; 'first' = take the first N",
    )
    p.add_argument(
        "--env-file",
        default=os.path.expanduser("~/.env"),
        help="dotenv-style file from which to load OPENAI_API_KEY (etc.) if it is not already in the env",
    )
    p.add_argument(
        "--multi-gpus",
        action="store_true",
        help="Shard the proposition detector across visible GPUs (use with --gpus to cap the set).",
    )
    p.add_argument(
        "--gpus",
        default=None,
        help="Comma-separated CUDA device indices to expose (sets CUDA_VISIBLE_DEVICES). "
             "InternVL2-8B saturates a single 24 GB A5000; pass e.g. '0,1' with --multi-gpus.",
    )
    p.add_argument(
        "--qid-file",
        default=None,
        help="Optional JSON or newline-delimited question_id list. Overrides smoke/full-val selection.",
    )
    p.add_argument(
        "--qid-total-shards",
        type=int,
        default=1,
        help="Split --qid-file entries into N round-robin shards.",
    )
    p.add_argument(
        "--qid-current-shard",
        type=int,
        default=1,
        help="Which --qid-file shard to run (1 .. --qid-total-shards).",
    )
    p.add_argument(
        "--nsvs-backend",
        choices=["internvl", "gpt5.2"],
        default="internvl",
        help="NSVS proposition detector backend. gpt5.2 = OpenAI gpt-5.2 medium reasoning.",
    )
    p.add_argument(
        "--nsvs-cache-dir",
        default=None,
        help="Detection cache root (default: <output_dir>/nsvs_detection_cache)",
    )
    p.add_argument(
        "--reuse-from",
        default=None,
        help="Optional baseline entries.json — reuse puls/target_id to isolate NSVS swap",
    )
    return p.parse_args()


def load_env_file(path: str) -> None:
    from nsvqa.utils.env_loader import load_env_file as _load
    _load(path)


def pick_smoke_subset(entries: list[dict], limit: int, seed: int, strategy: str) -> list[dict]:
    """Build a small but diverse smoke subset for first runs."""
    entries = [e for e in entries if e["metadata"].get("video_present", True)]

    if strategy == "first":
        return entries[:limit]

    rng = random.Random(seed)

    by_bucket: dict[tuple, list[dict]] = collections.defaultdict(list)
    for e in entries:
        key = (e["metadata"]["mode"], e["metadata"]["source_dataset"])
        by_bucket[key].append(e)

    picked: list[dict] = []
    bucket_keys = list(by_bucket.keys())
    rng.shuffle(bucket_keys)
    i = 0
    while len(picked) < limit and any(by_bucket.values()):
        key = bucket_keys[i % len(bucket_keys)]
        bucket = by_bucket[key]
        if bucket:
            picked.append(bucket.pop(rng.randrange(len(bucket))))
        i += 1
    return picked


def load_qid_file(path: str) -> list[str]:
    with open(path) as f:
        raw = f.read().strip()
    if not raw:
        return []
    if raw[0] == "[":
        return [str(qid) for qid in json.loads(raw)]
    return [line.strip() for line in raw.splitlines() if line.strip()]


def load_baseline_entries(path: str) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    by_qid: dict[str, dict] = {}
    for entry in rows:
        qid = str(entry.get("metadata", {}).get("question_id") or entry.get("question_id"))
        by_qid[qid] = entry
    return by_qid


_PADDING_LOG_COUNT = 0
_PADDING_LOG_LIMIT = 10


def merge_frames_of_interest(entry: dict) -> list:
    """Combine NSVS frame indices with target-identification second offsets."""
    import re

    global _PADDING_LOG_COUNT

    nsvs_out = entry.get("nsvs", {}).get("output")
    if nsvs_out == [-1] or not nsvs_out:
        return [-1]

    fps = float(entry["metadata"].get("fps") or 1.0)
    frame_count = int(entry["metadata"].get("frame_count") or 0)
    start_f, end_f = int(nsvs_out[0]), int(nsvs_out[1])

    ti = entry.get("target_identification") or {}
    inner = str(ti.get("frame_window", "[+0, +0]")).strip()[1:-1]
    offsets = []
    for part in inner.split(","):
        part = part.strip()
        m = re.search(r"-?\d+", part)
        offsets.append(int(m.group(0)) if m else 0)
    while len(offsets) < 2:
        offsets.append(0)

    max_frame = max(0, frame_count - 1)
    before_start_sec = max(0, abs(offsets[0]))
    after_end_sec = max(0, offsets[1])
    if _PADDING_LOG_COUNT < _PADDING_LOG_LIMIT:
        qid = entry.get("metadata", {}).get("question_id", "?")
        print(
            f"[merge_foi] qid={qid} frame_window={ti.get('frame_window')} "
            f"parsed before={before_start_sec}s after={after_end_sec}s"
        )
        _PADDING_LOG_COUNT += 1
    merged_start = max(0, start_f - int(before_start_sec * fps))
    merged_end = min(max_frame, end_f + int(after_end_sec * fps))

    if merged_start > merged_end:
        return [-1]

    return [merged_start, merged_end]


_CUDA_NSVS_MARKERS = (
    "cudacachingallocator",
    "internal assert",
    "cuda launch failure",
    "cuda driver error: unknown",
)


def _is_cuda_nsvs_error(exc: BaseException) -> bool:
    text = f"{exc!r}\n{traceback.format_exc()}".lower()
    return any(marker in text for marker in _CUDA_NSVS_MARKERS)


def run_one(
    entry: dict,
    vlm,
    sample_rate: float,
    device: int,
    puls_model: str | None = None,
    baseline_entry: dict | None = None,
) -> dict:
    """Execute NeuS-QA steps for one entry: PULS -> video -> NSVS -> target pad -> merge.

    Target identification runs after NSVS so padding is relative to a real interval.
    When ``baseline_entry`` is set, reuse its puls and target_identification to isolate
    NSVS-backend changes.
    """
    from nsvqa.puls.puls import PULS
    from nsvqa.target_identification.target_identification import identify_target
    from nsvqa.nsvs.video.read_video import Mp4Reader

    status: dict[str, Any] = {
        "question_id": entry["metadata"]["question_id"],
        "mode": entry["metadata"]["mode"],
        "operator_guess": entry["metadata"]["operator_guess"],
        "source_dataset": entry["metadata"]["source_dataset"],
        "step_timings": {},
        "step_status": {},
    }

    question_for_puls = entry["metadata"].get("cleaned_question") or entry["question"]

    if baseline_entry and baseline_entry.get("puls"):
        entry["puls"] = dict(baseline_entry["puls"])
        status["step_status"]["puls"] = "reused_from_baseline"
    else:
        try:
            t0 = time.time()
            puls_out = PULS(question_for_puls, model=puls_model)
            status["step_timings"]["puls"] = round(time.time() - t0, 2)
            status["step_status"]["puls"] = "ok"
            entry["puls"] = {
                "proposition": puls_out["proposition"],
                "specification": puls_out["specification"],
                "conversation_history": os.path.join(os.getcwd(), puls_out["saved_path"]),
            }
        except Exception as e:
            status["step_status"]["puls"] = f"error: {e!r}"
            status["traceback"] = traceback.format_exc()
            return status

    try:
        t0 = time.time()
        reader = Mp4Reader(path=entry["paths"]["video_path"], sample_rate=sample_rate)
        video_data = reader.read_video()
        entry.setdefault("metadata", {})
        if video_data is None:
            entry["metadata"]["read_video_error"] = "VideoCapture failed to open"
            entry["frames_of_interest"] = [-1]
            status["step_status"]["read_video"] = "error: VideoCapture failed to open"
            status["foi"] = [-1]
            status["step_timings"]["read_video"] = round(time.time() - t0, 2)
            return status
        entry["metadata"]["fps"] = video_data["video_info"]["fps"]
        entry["metadata"]["frame_count"] = video_data["video_info"]["frame_count"]
        status["step_timings"]["read_video"] = round(time.time() - t0, 2)
    except Exception as e:
        status["step_status"]["read_video"] = f"error: {e!r}"
        status["traceback"] = traceback.format_exc()
        return status

    try:
        from nsvqa.nsvs.nsvs import run_nsvs

        model_name = getattr(vlm, "model_name", getattr(vlm, "model", "InternVL2-8B"))
        nsvs_exc: Exception | None = None
        for attempt in (1, 2):
            try:
                t0 = time.time()
                output, indices = run_nsvs(
                    video_data,
                    entry["paths"]["video_path"],
                    entry["puls"]["proposition"],
                    entry["puls"]["specification"],
                    device=device,
                    model=model_name,
                    vlm=vlm,
                )
                status["step_timings"]["nsvs"] = round(time.time() - t0, 2)
                status["step_status"]["nsvs"] = "ok"
                detection_log = getattr(vlm, "detection_log", [])
                entry["nsvs"] = {"output": output, "indices": indices, "detection_log": detection_log}
                nsvs_exc = None
                break
            except Exception as e:
                nsvs_exc = e
                if attempt == 1 and _is_cuda_nsvs_error(e):
                    import torch

                    qid = entry["metadata"]["question_id"]
                    print(f"[runner] qid={qid} CUDA NSVS error on attempt 1; empty_cache and retry once")
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    continue
        if nsvs_exc is not None:
            raise nsvs_exc
    except Exception as e:
        status["step_status"]["nsvs"] = f"error: {e!r}"
        status["traceback"] = traceback.format_exc()
        entry["nsvs"] = {"output": [-1], "indices": [], "detection_log": []}
        entry["frames_of_interest"] = [-1]
        status["foi"] = [-1]
        return status

    nsvs_start_sec = nsvs_end_sec = None
    if entry["nsvs"]["output"] != [-1]:
        fps = float(entry["metadata"]["fps"] or 1.0)
        nsvs_start_sec = entry["nsvs"]["output"][0] / fps
        nsvs_end_sec = entry["nsvs"]["output"][1] / fps

    if baseline_entry and baseline_entry.get("target_identification"):
        entry["target_identification"] = dict(baseline_entry["target_identification"])
        status["step_status"]["target_identification"] = "reused_from_baseline"
    else:
        question_for_ti = entry["metadata"].get("cleaned_question") or entry["question"]
        try:
            t0 = time.time()
            ti_out = identify_target(
                question_for_ti,
                entry["candidates"],
                entry["puls"]["specification"],
                entry["puls"]["conversation_history"],
                model=puls_model,
                nsvs_start_sec=nsvs_start_sec,
                nsvs_end_sec=nsvs_end_sec,
            )
            status["step_timings"]["target_identification"] = round(time.time() - t0, 2)
            status["step_status"]["target_identification"] = "ok"
            entry["target_identification"] = {
                "frame_window": ti_out["frame_window"],
                "explanation": ti_out["explanation"],
                "conversation_history": os.path.join(os.getcwd(), ti_out["saved_path"]),
                "nsvs_start_sec": nsvs_start_sec,
                "nsvs_end_sec": nsvs_end_sec,
            }
        except Exception as e:
            status["step_status"]["target_identification"] = f"error: {e!r}"
            entry["target_identification"] = {"frame_window": "[+0, +0]", "explanation": repr(e)}
            status["step_status"]["merge"] = "fallback: raw_nsvs_no_target_id"

    try:
        entry["frames_of_interest"] = merge_frames_of_interest(entry)
        status["step_status"]["merge"] = status["step_status"].get("merge", "ok")
    except Exception as e:
        status["step_status"]["merge"] = f"error: {e!r}"
        entry["frames_of_interest"] = (
            entry["nsvs"]["output"] if entry["nsvs"]["output"] != [-1] else [-1]
        )

    status["foi"] = entry.get("frames_of_interest")
    status["fps"] = entry["metadata"].get("fps")
    status["frame_count"] = entry["metadata"].get("frame_count")
    status["proposition"] = entry["puls"]["proposition"]
    status["specification"] = entry["puls"]["specification"]
    status["target_window"] = entry["target_identification"]["frame_window"]
    return status


def main() -> int:
    args = parse_args()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "per_entry"), exist_ok=True)

    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[runner] WARNING: OPENAI_API_KEY not set and not found in {args.env_file}; "
              "PULS and target_identification will fail")

    if args.gpus:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus

    history_dir = os.path.join(args.output_dir, "llm_history")
    os.makedirs(history_dir, exist_ok=True)
    os.environ["NSVQA_LLM_HISTORY_DIR"] = history_dir

    from nsvqa.datamanager.timelogic import TimeLogic

    baseline_by_qid: dict[str, dict] = {}
    if args.reuse_from:
        baseline_by_qid = load_baseline_entries(args.reuse_from)
        print(f"[runner] reuse-from: {len(baseline_by_qid)} baseline entries at {args.reuse_from}")

    loader = TimeLogic(
        split="val",
        video_root=args.video_root,
        ann_path=args.ann_path,
    )
    all_entries = loader.load_data()
    if args.qid_file:
        qids = load_qid_file(args.qid_file)
        total_shards = max(1, args.qid_total_shards)
        current_shard = max(1, min(args.qid_current_shard, total_shards))
        qids = [qid for idx, qid in enumerate(qids) if idx % total_shards == current_shard - 1]
        by_qid = {str(e["metadata"]["question_id"]): e for e in all_entries}
        subset = [
            by_qid[qid]
            for qid in qids
            if qid in by_qid and by_qid[qid]["metadata"].get("video_present", True)
        ]
        print(
            f"[runner] qid-file mode: shard {current_shard}/{total_shards}, "
            f"{len(subset)} entries from {args.qid_file}"
        )
    elif args.full_val:
        pool = [e for e in all_entries if e["metadata"].get("video_present", True)]
        if args.total_splits > 1:
            cs = max(1, min(args.current_split, args.total_splits))
            start = (len(pool) * (cs - 1)) // args.total_splits
            end = (len(pool) * cs) // args.total_splits
            pool = pool[start:end]
            print(f"[runner] shard {cs}/{args.total_splits}: indices [{start}, {end}) -> {len(pool)} entries")
        if args.limit is not None:
            pool = pool[: args.limit]
        subset = pool
        print(f"[runner] full-val mode: {len(subset)} entries")
    else:
        smoke_limit = args.limit if args.limit is not None else 10
        subset = pick_smoke_subset(all_entries, smoke_limit, args.seed, args.smoke_strategy)
        print(f"[runner] smoke: {len(subset)} entries (strategy={args.smoke_strategy}, seed={args.seed})")

    import torch
    visible = torch.cuda.device_count()
    print(f"[runner] CUDA_VISIBLE_DEVICES sees {visible} GPUs; multi_gpus={args.multi_gpus}")
    print(f"[runner] NSVS backend: {args.nsvs_backend}")
    print(f"[runner] PULS / target_identification model: {args.puls_model}")

    cache_dir = args.nsvs_cache_dir or os.path.join(args.output_dir, "nsvs_detection_cache")
    meter = None
    vlm = None

    if args.nsvs_backend == "gpt5.2":
        from nsvqa.nsvs.vlm.detection_cache import DetectionCache
        from nsvqa.nsvs.vlm.openai_nsvs import OpenAINsvsVLM
        from nsvqa.utils.api_cost import RunMeter

        meter = RunMeter(args.output_dir, label=os.path.basename(args.output_dir.rstrip("/")))
        cache = DetectionCache(cache_dir, backend="gpt5.2")
        vlm = OpenAINsvsVLM(cache=cache, meter=meter)
        print(f"[runner] gpt-5.2 NSVS detector (reasoning=medium), cache={cache_dir}")
    else:
        from nsvqa.nsvs.vlm.internvl import InternVL

        print(f"[runner] proposition detector: OpenGVLab/{args.proposition_model} "
              f"({'sharded' if args.multi_gpus else f'cuda:{args.device}'})")
        t0 = time.time()
        vlm = InternVL(model_name=args.proposition_model, device=args.device, multi_gpus=args.multi_gpus)
        print(f"[runner] proposition detector ready in {time.time() - t0:.1f}s")

    diag = []
    for i, entry in enumerate(subset):
        qid = entry["metadata"]["question_id"]
        print("\n" + "=" * 90)
        print(f"[{i + 1}/{len(subset)}] qid={qid} mode={entry['metadata']['mode']} "
              f"src={entry['metadata']['source_dataset']} op={entry['metadata']['operator_guess']}")
        print(f"   Q: {entry['question'][:160]}{'...' if len(entry['question']) > 160 else ''}")

        t0 = time.time()
        try:
            status = run_one(
                entry,
                vlm,
                args.sample_rate,
                args.device,
                puls_model=args.puls_model,
                baseline_entry=baseline_by_qid.get(str(qid)),
            )
        except Exception as e:
            status = {
                "question_id": qid,
                "fatal_error": repr(e),
                "traceback": traceback.format_exc(),
            }
        status["total_seconds"] = round(time.time() - t0, 2)
        diag.append(status)

        with open(os.path.join(args.output_dir, "per_entry", f"{qid}.json"), "w") as f:
            json.dump({"entry": entry, "status": status}, f, indent=2, default=str)

        print(f"   propositions={status.get('proposition')}")
        print(f"   spec        ={status.get('specification')}")
        print(f"   target_win  ={status.get('target_window')}")
        print(f"   nsvs_foi    ={status.get('foi')}  (fps={status.get('fps')}, frames={status.get('frame_count')})")
        print(f"   step times  ={status.get('step_timings')}")
        print(f"   step status ={status.get('step_status')}")

    with open(os.path.join(args.output_dir, "diag.json"), "w") as f:
        json.dump(diag, f, indent=2, default=str)
    with open(os.path.join(args.output_dir, "entries.json"), "w") as f:
        json.dump(subset, f, indent=2, default=str)

    if meter is not None:
        meter.write(
            {
                "nsvs_backend": args.nsvs_backend,
                "sample_rate": args.sample_rate,
                "entries": len(subset),
            }
        )
        print(meter.log_line(prefix="[runner]"))

    completed = sum(
        1 for d in diag if d.get("step_status", {}).get("nsvs") == "ok"
    )
    foi_found = sum(
        1 for d in diag
        if d.get("foi") and isinstance(d["foi"], list) and len(d["foi"]) == 2 and d["foi"] != [-1]
    )
    print("\n" + "=" * 90)
    print(f"completed nsvs : {completed}/{len(diag)}")
    print(f"non-empty foi  : {foi_found}/{len(diag)}")
    print(f"wrote results  : {args.output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
