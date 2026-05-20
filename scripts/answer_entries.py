"""Run the TimeLogic downstream answerer against an existing entries.json.

Reuses the heavy upstream pipeline output (PULS + target_id + NSVS + merge
already computed by `run_timelogic.py`) so we don't burn another 10-60 min
of GPU + LLM calls just to test a different VQA model.

Example:
    # Run the answerer on smoke_v5 with gpt-4o-mini (cheap dev)
    python3 scripts/answer_entries.py \\
        --entries /mnt/Data/ah66742/timelogic/outputs/smoke_v5/entries.json \\
        --output-dir /mnt/Data/ah66742/timelogic/outputs/smoke_v5_answers_mini \\
        --model gpt-4o-mini \\
        --num-frames 8

    # Then promote to gpt-5.2 for a real submission attempt
    python3 scripts/answer_entries.py \\
        --entries /mnt/Data/ah66742/timelogic/outputs/smoke_v5/entries.json \\
        --output-dir /mnt/Data/ah66742/timelogic/outputs/smoke_v5_answers_52 \\
        --model gpt-5.2 \\
        --num-frames 12
"""

import argparse
import json
import os
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--entries", required=True,
                   help="Path to entries.json from a prior `run_timelogic.py` run")
    p.add_argument("--output-dir", required=True,
                   help="Where to write submission.json and answers_diag.json")
    p.add_argument("--model", default="gpt-4o-mini",
                   help="OpenAI model with vision support. See .cursor/rules/workflow.md "
                        "for tiering: 'gpt-4o-mini' (dev), 'gpt-5.2' (val/test), 'gpt-5' (backup).")
    p.add_argument("--num-frames", type=int, default=8,
                   help="Number of frames to sample from the frames_of_interest interval. "
                        "More frames = better recall, more tokens, more $.")
    p.add_argument("--image-detail", default="low", choices=["low", "auto", "high"],
                   help="OpenAI vision image-detail level. 'low' is cheap and usually enough for 8 frames.")
    p.add_argument("--limit", type=int, default=None,
                   help="Process only the first N entries (smoke / debug)")
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"),
                   help="dotenv-style file with OPENAI_API_KEY (same format as run_timelogic.py)")
    p.add_argument("--quiet", action="store_true", help="Suppress per-entry progress lines")
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
    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[answer] WARNING: OPENAI_API_KEY not set and not found in {args.env_file}")

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from nsvqa.vqa.answer_timelogic import answer_timelogic

    with open(args.entries, "r") as f:
        entries = json.load(f)
    if args.limit is not None:
        entries = entries[:args.limit]

    print(f"[answer] loaded {len(entries)} entries from {args.entries}")
    print(f"[answer] model={args.model} num_frames={args.num_frames} image_detail={args.image_detail}")

    submission, diag = answer_timelogic(
        entries,
        model=args.model,
        num_frames=args.num_frames,
        output_dir=args.output_dir,
        image_detail=args.image_detail,
        verbose=not args.quiet,
    )

    mc_count = sum(1 for d in diag if d.get("mode") == "mc")
    bool_count = sum(1 for d in diag if d.get("mode") == "bool")
    errors = sum(1 for d in diag if d.get("error"))
    print(f"\n[answer] processed {len(diag)} entries ({mc_count} mc + {bool_count} bool); {errors} had errors")
    print(f"[answer] submission has {len(submission)} records")

    return 0


if __name__ == "__main__":
    sys.exit(main())
