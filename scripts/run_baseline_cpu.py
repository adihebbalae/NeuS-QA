"""Run the NeuS-QA pipeline WITHOUT the GPU stages (no NSVS, no InternVL).

Stages per entry, all OpenAI API:
1. PULS  (LQ2TL: natural-language question → propositions + TL specification)
2. Answerer (vision call: sample N frames from full video + question + PULS
   spec/propositions injected as a structured hint → letter or Yes/No)

Skipped vs the full pipeline:
- target_identification (only useful when combined with NSVS frame indices)
- read_video / NSVS / merge (the GPU half — InternVL proposition detection
  and Storm model checking)

Why this exists:
- First EvalAI submission needs to land tonight without burning GPU hours
- PULS still gives the answerer structured priors (atomic events + temporal
  pattern), so this is strictly stronger than a naked VLM baseline
- Establishes a clean reference for "what does symbolic-prefix + VLM achieve",
  vs the full pipeline (next submission) which adds NSVS narrowing on GPU

Example (full val, gpt-5.2, in tmux):
    python3 scripts/run_baseline_cpu.py \\
        --video-root /mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos \\
        --ann-path /mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json \\
        --output-dir /mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01 \\
        --puls-model gpt-5.2 \\
        --answer-model gpt-5.2 \\
        --num-frames 8

Expected wall-clock (sequential): ~2-3 h for full val. Expected OpenAI spend
with gpt-5.2: ~$15-20 for the full 2000 entries. Cost knob: --puls-model and
--answer-model independently; gpt-4o-mini for either halves cost ~10x.
"""

import argparse
import json
import os
import sys
import time
import traceback


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--video-root", required=True)
    p.add_argument("--ann-path", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--limit", type=int, default=None,
                   help="Process only the first N entries (smoke / debug). Default: all 2000.")
    p.add_argument("--puls-model", default="gpt-4o-mini",
                   help="OpenAI model for PULS. Tiering per workflow.md: gpt-4o-mini "
                        "(dev), gpt-5.2 (val/test), gpt-5 (backup).")
    p.add_argument("--answer-model", default="gpt-4o-mini",
                   help="OpenAI vision-capable model for the answerer. Same tiering.")
    p.add_argument("--num-frames", type=int, default=8,
                   help="Frames to sample from each video for the answerer.")
    p.add_argument("--image-detail", default="low", choices=["low", "auto", "high"])
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--puls-only", action="store_true",
                   help="Run only the PULS stage (skip the answerer). Useful when "
                        "you want to compute specs for all entries and answer later.")
    return p.parse_args()


def load_env_file(path: str) -> None:
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


def main() -> int:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[runner] FATAL: OPENAI_API_KEY not set and not in {args.env_file}")
        return 2

    history_dir = os.path.join(args.output_dir, "llm_history")
    os.makedirs(history_dir, exist_ok=True)
    os.environ["NSVQA_LLM_HISTORY_DIR"] = history_dir

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from nsvqa.datamanager.timelogic import TimeLogic
    from nsvqa.puls.puls import PULS
    from openai import OpenAI

    loader = TimeLogic(split="val", video_root=args.video_root, ann_path=args.ann_path)
    all_entries = loader.load_data()
    if args.limit is not None:
        entries = all_entries[:args.limit]
    else:
        entries = all_entries
    print(f"[runner] loaded {len(all_entries)} val entries; processing {len(entries)}")
    print(f"[runner] PULS model: {args.puls_model}")
    print(f"[runner] answerer model: {args.answer_model}  (num_frames={args.num_frames}, detail={args.image_detail})")

    diag: list[dict] = []
    submission: list[dict] = []
    client = OpenAI() if not args.puls_only else None
    t_start = time.time()

    for i, entry in enumerate(entries):
        qid = entry["metadata"]["question_id"]
        mode = entry["metadata"]["mode"]
        video_path = entry["paths"]["video_path"]
        candidates = entry["candidates"]
        question_for_puls = entry["metadata"].get("cleaned_question") or entry["question"]

        rec: dict = {"qid": qid, "mode": mode, "step_status": {}, "step_timings": {}}

        try:
            t0 = time.time()
            puls_out = PULS(question_for_puls, model=args.puls_model)
            rec["step_timings"]["puls"] = round(time.time() - t0, 2)
            rec["step_status"]["puls"] = "ok"
            entry["puls"] = {
                "proposition": puls_out["proposition"],
                "specification": puls_out["specification"],
                "conversation_history": os.path.join(os.getcwd(), puls_out["saved_path"]),
            }
            rec["proposition"] = puls_out["proposition"]
            rec["specification"] = puls_out["specification"]
        except Exception as e:
            rec["step_status"]["puls"] = f"error: {e!r}"
            rec["traceback"] = traceback.format_exc()
            entry["puls"] = {"proposition": [], "specification": ""}

        if args.puls_only:
            diag.append(rec)
            elapsed = time.time() - t_start
            avg = elapsed / (i + 1)
            eta_min = avg * (len(entries) - i - 1) / 60
            print(f"[{i+1}/{len(entries)}] qid={qid} {mode} PULS={rec['step_status'].get('puls')} "
                  f"spec={rec.get('specification','')[:60]}... avg={avg:.1f}s/Q eta={eta_min:.0f}m")
            continue

        if not entry["metadata"].get("video_present", True) or not os.path.isfile(video_path):
            default = "A" if mode == "mc" else "Yes"
            submission.append({"question_id": qid, "answer_choice": default})
            rec["step_status"]["answer"] = "default: missing_video"
            rec["answer"] = default
            diag.append(rec)
            continue

        from nsvqa.vqa.answer_timelogic import answer_one, format_puls_hint
        try:
            t0 = time.time()
            hint = format_puls_hint(entry["puls"].get("proposition"), entry["puls"].get("specification"))
            ans = answer_one(
                client, args.answer_model, video_path, [-1],
                entry["question"], candidates, mode,
                num_frames=args.num_frames, image_detail=args.image_detail,
                puls_hint=hint,
            )
            rec["step_timings"]["answer"] = round(time.time() - t0, 2)
            rec["step_status"]["answer"] = "ok" if not ans.get("error") else f"warn: {ans.get('error')}"
            rec["answer"] = ans.get("answer")
            rec["raw"] = ans.get("raw")
            rec["num_frames"] = ans.get("num_frames")
            submission.append({"question_id": qid, "answer_choice": ans.get("answer")})
        except Exception as e:
            default = "A" if mode == "mc" else "Yes"
            rec["step_status"]["answer"] = f"error: {e!r}"
            rec["traceback"] = traceback.format_exc()
            rec["answer"] = default
            submission.append({"question_id": qid, "answer_choice": default})

        diag.append(rec)

        elapsed = time.time() - t_start
        avg = elapsed / (i + 1)
        eta_min = avg * (len(entries) - i - 1) / 60
        if (i + 1) % 25 == 0 or i < 5 or (i + 1) == len(entries):
            print(f"[{i+1}/{len(entries)}] qid={qid} {mode} → {rec.get('answer')!r}  "
                  f"(PULS {rec['step_timings'].get('puls','-')}s, ans {rec['step_timings'].get('answer','-')}s)  "
                  f"avg={avg:.1f}s/Q  eta={eta_min:.0f}m")

        if (i + 1) % 100 == 0:
            with open(os.path.join(args.output_dir, "entries.json"), "w") as f:
                json.dump(entries[:i+1], f, indent=2, default=str)
            with open(os.path.join(args.output_dir, "diag.json"), "w") as f:
                json.dump(diag, f, indent=2, default=str)
            with open(os.path.join(args.output_dir, "submission.json"), "w") as f:
                json.dump(submission, f, indent=2)
            print(f"  [checkpoint] wrote intermediate files at i={i+1}")

    with open(os.path.join(args.output_dir, "entries.json"), "w") as f:
        json.dump(entries, f, indent=2, default=str)
    with open(os.path.join(args.output_dir, "diag.json"), "w") as f:
        json.dump(diag, f, indent=2, default=str)
    with open(os.path.join(args.output_dir, "submission.json"), "w") as f:
        json.dump(submission, f, indent=2)

    total_time = time.time() - t_start
    puls_ok = sum(1 for r in diag if r["step_status"].get("puls") == "ok")
    ans_ok = sum(1 for r in diag if r["step_status"].get("answer") == "ok")
    answers = [r.get("answer") for r in diag if r.get("answer")]
    print("\n" + "=" * 80)
    print(f"completed       : {len(diag)} entries in {total_time/60:.1f} min ({total_time/len(diag):.2f} s/Q)")
    print(f"PULS ok         : {puls_ok}/{len(diag)}")
    print(f"answer ok       : {ans_ok}/{len(diag)}")
    print(f"submission size : {len(submission)}")
    print(f"output dir      : {args.output_dir}")
    print(f"submission file : {args.output_dir}/submission.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
