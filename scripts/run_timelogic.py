"""TimeLogic-specific driver for the NeuS-QA neuro-symbolic pipeline.

Runs PULS (LQ2TL via gpt-4o) -> target identification -> NSVS (proposition
detection + Storm model checking) -> merge into frames_of_interest, for each
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
    p.add_argument("--limit", type=int, default=10, help="Maximum number of entries to process")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for the smoke subset selection")
    p.add_argument(
        "--proposition-model",
        default="InternVL2-8B",
        help="HuggingFace model name suffix for the proposition detector. The upstream class re-prepends 'OpenGVLab/'.",
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
    return p.parse_args()


def load_env_file(path: str) -> None:
    """Set os.environ from a simple KEY=VALUE file. Skips comments and blanks.
    Existing env vars take precedence.
    """
    if not path or not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw in f.read().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


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


def run_one(entry: dict, vlm, sample_rate: float, device: int) -> dict:
    """Execute the four NeuS-QA steps for a single entry, in-place on the dict.

    Returns a per-step status dict for diagnostics. The entry itself accretes
    the puls/target_identification/metadata/nsvs/frames_of_interest fields the
    upstream pipeline already uses.
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

    try:
        t0 = time.time()
        puls_out = PULS(question_for_puls)
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
        ti_out = identify_target(
            entry["question"],
            entry["candidates"],
            entry["puls"]["specification"],
            entry["puls"]["conversation_history"],
        )
        status["step_timings"]["target_identification"] = round(time.time() - t0, 2)
        status["step_status"]["target_identification"] = "ok"
        entry["target_identification"] = {
            "frame_window": ti_out["frame_window"],
            "explanation": ti_out["explanation"],
            "conversation_history": os.path.join(os.getcwd(), ti_out["saved_path"]),
        }
    except Exception as e:
        status["step_status"]["target_identification"] = f"error: {e!r}"
        status["traceback"] = traceback.format_exc()
        return status

    try:
        t0 = time.time()
        reader = Mp4Reader(path=entry["paths"]["video_path"], sample_rate=sample_rate)
        video_data = reader.read_video()
        entry.setdefault("metadata", {})
        entry["metadata"]["fps"] = video_data["video_info"]["fps"]
        entry["metadata"]["frame_count"] = video_data["video_info"]["frame_count"]
        status["step_timings"]["read_video"] = round(time.time() - t0, 2)
    except Exception as e:
        status["step_status"]["read_video"] = f"error: {e!r}"
        status["traceback"] = traceback.format_exc()
        return status

    try:
        t0 = time.time()
        from nsvqa.nsvs.nsvs import run_nsvs
        output, indices = run_nsvs(
            video_data,
            entry["paths"]["video_path"],
            entry["puls"]["proposition"],
            entry["puls"]["specification"],
            device=device,
            model=vlm.model_name,
        )
        status["step_timings"]["nsvs"] = round(time.time() - t0, 2)
        status["step_status"]["nsvs"] = "ok"
        entry["nsvs"] = {"output": output, "indices": indices}
    except Exception as e:
        status["step_status"]["nsvs"] = f"error: {e!r}"
        status["traceback"] = traceback.format_exc()
        entry["nsvs"] = {"output": [-1], "indices": []}
        return status

    import re
    try:
        inner = entry["target_identification"]["frame_window"].strip()[1:-1]
        parts = inner.split(",")
        result = []
        for part in parts:
            part = part.strip()
            m = re.search(r"([+-])\s*(\d+)", part)
            result.append(int(m.group(1) + m.group(2)) if m else 0)

        if entry["nsvs"]["output"] != [-1]:
            entry["frames_of_interest"] = [
                max(0, int(entry["nsvs"]["output"][0] + result[0] * entry["metadata"]["fps"])),
                min(entry["metadata"]["frame_count"] - 1,
                    int(entry["nsvs"]["output"][1] + result[1] * entry["metadata"]["fps"])),
            ]
        else:
            entry["frames_of_interest"] = [-1]
        status["step_status"]["merge"] = "ok"
    except Exception as e:
        status["step_status"]["merge"] = f"error: {e!r}"

    status["foi"] = entry.get("frames_of_interest")
    status["fps"] = entry["metadata"].get("fps")
    status["frame_count"] = entry["metadata"].get("frame_count")
    status["proposition"] = entry["puls"]["proposition"]
    status["specification"] = entry["puls"]["specification"]
    status["target_window"] = entry["target_identification"]["frame_window"]
    return status


def main() -> int:
    args = parse_args()
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

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from nsvqa.datamanager.timelogic import TimeLogic
    from nsvqa.nsvs.vlm.internvl import InternVL

    loader = TimeLogic(
        split="val",
        video_root=args.video_root,
        ann_path=args.ann_path,
    )
    all_entries = loader.load_data()
    subset = pick_smoke_subset(all_entries, args.limit, args.seed, args.smoke_strategy)
    print(f"[runner] selected {len(subset)} entries (strategy={args.smoke_strategy}, seed={args.seed})")

    import torch
    visible = torch.cuda.device_count()
    print(f"[runner] CUDA_VISIBLE_DEVICES sees {visible} GPUs; multi_gpus={args.multi_gpus}")
    print(f"[runner] loading proposition detector: OpenGVLab/{args.proposition_model} "
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
            status = run_one(entry, vlm, args.sample_rate, args.device)
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
