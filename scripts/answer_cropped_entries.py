"""Answer TimeLogic entries on ffmpeg-cropped clips via OpenAI Vision.

Reuses `nsvqa.vqa.answer_timelogic.answer_timelogic` (same prompts, parsing,
and gpt-5.x reasoning-model handling as Sub #1) but reads
`postprocess/postprocess_entries.json` from the paper-faithful Sub #5B pipeline.

Each entry's `paths.cropped_path` becomes the video source while preserving
`frames_of_interest` so the VQA sampler can use the FOI window when available.

Example:
    python3 scripts/answer_cropped_entries.py \\
        --entries /mnt/Data/.../postprocess/postprocess_entries.json \\
        --output-dir /mnt/Data/.../answers_gpt52 \\
        --model gpt-5.2 \\
        --num-frames 16
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entries", required=True, help="postprocess_entries.json with paths.cropped_path")
    p.add_argument("--output-dir", required=True)
    p.add_argument(
        "--model",
        default="gpt-5.2",
        help="OpenAI vision model. See .cursor/rules/workflow.md for tiering.",
    )
    p.add_argument("--num-frames", type=int, default=16)
    p.add_argument("--image-detail", default="low", choices=["low", "auto", "high"])
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--quiet", action="store_true")
    p.add_argument(
        "--no-write-entries",
        action="store_true",
        help="Do not merge vqa.reasoning_summary back into --entries",
    )
    p.add_argument(
        "--allow-crop-fallback",
        action="store_true",
        help="Allow cropped_path == video_path (source fallback); default is assert-and-fail",
    )
    return p.parse_args()


def load_env_file(path: str) -> None:
    from nsvqa.utils.env_loader import load_env_file as _load

    _load(path)


def prepare_entries(entries: list[dict], *, allow_crop_fallback: bool = False) -> list[dict]:
    prepared: list[dict] = []
    fallback_count = 0
    for entry in entries:
        e = copy.deepcopy(entry)
        cropped = e.get("paths", {}).get("cropped_path", "")
        video = e.get("paths", {}).get("video_path", "")
        if not cropped:
            raise AssertionError(
                f"qid {e.get('metadata', {}).get('question_id')}: cropped_path missing — "
                "crop step did not run cleanly"
            )
        if cropped == video:
            if allow_crop_fallback:
                fallback_count += 1
            else:
                raise AssertionError(
                    f"qid {e.get('metadata', {}).get('question_id')}: cropped_path == video_path — "
                    "crop fell back to source. ffmpeg preflight should have caught this."
                )
        e["paths"]["video_path"] = cropped
        prepared.append(e)
    if fallback_count:
        print(f"[answer-cropped] WARNING: {fallback_count} entries used crop fallback (source video)")
    return prepared


def main() -> int:
    args = parse_args()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[answer-cropped] WARNING: OPENAI_API_KEY not set and not found in {args.env_file}")

    from nsvqa.vqa.answer_timelogic import answer_timelogic

    with open(args.entries, "r", encoding="utf-8") as f:
        entries = json.load(f)
    if args.limit is not None:
        entries = entries[: args.limit]

    prepared = prepare_entries(entries, allow_crop_fallback=args.allow_crop_fallback)
    print(f"[answer-cropped] loaded {len(prepared)} entries from {args.entries}")
    print(
        f"[answer-cropped] model={args.model} num_frames={args.num_frames} "
        f"image_detail={args.image_detail}"
    )

    submission, diag = answer_timelogic(
        prepared,
        model=args.model,
        num_frames=args.num_frames,
        output_dir=args.output_dir,
        image_detail=args.image_detail,
        verbose=not args.quiet,
        write_entries_path=None if args.no_write_entries else args.entries,
        entries_for_merge=entries,
    )

    partial_path = os.path.join(args.output_dir, "submission_partial.json")
    with open(partial_path, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)

    mc_count = sum(1 for d in diag if d.get("mode") == "mc")
    bool_count = sum(1 for d in diag if d.get("mode") == "bool")
    errors = sum(1 for d in diag if d.get("error"))
    print(
        f"\n[answer-cropped] processed {len(diag)} entries "
        f"({mc_count} mc + {bool_count} bool); {errors} had errors"
    )
    print(f"[answer-cropped] wrote {partial_path} ({len(submission)} records)")
    if not args.no_write_entries:
        print(f"[answer-cropped] merged vqa + reasoning_summary into {args.entries}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
