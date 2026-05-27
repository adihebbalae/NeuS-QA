"""Answer TimeLogic entries on ffmpeg-cropped clips via OpenAI Vision.

Reuses `nsvqa.vqa.answer_timelogic.answer_timelogic` (same prompts, parsing,
and gpt-5.x reasoning-model handling as Sub #1) but reads
`postprocess/postprocess_entries.json` from the paper-faithful Sub #5B pipeline.

Each entry's `paths.cropped_path` becomes the video source (V'). When the crop
is real (`cropped_path != video_path`), `frames_of_interest` is cleared so VQA
samples uniformly over V' — original FOI indices are in source-video coordinates
and must not be applied to the cropped file. Crop fallbacks that re-encode the
full source video leave FOI unchanged.

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
import random
import sys
import time

PARSE_RETRY_SUFFIX = "\n\nRespond with only the letter (A/B/C/D) or Yes/No."
PROMPT_TRUNCATE_CHARS = 500


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
        if cropped != video:
            # VQA runs on V'; source-frame FOI indices are invalid on the crop.
            e["frames_of_interest"] = None
        prepared.append(e)
    if fallback_count:
        print(f"[answer-cropped] WARNING: {fallback_count} entries used crop fallback (source video)")
    return prepared


def _truncate_prompt(prompt: str, max_chars: int = PROMPT_TRUNCATE_CHARS) -> str:
    if len(prompt) <= max_chars:
        return prompt
    return prompt[: max_chars - 3] + "..."


def _default_max_output_tokens(model: str) -> int:
    from nsvqa.vqa.answer_timelogic import _is_reasoning_model

    return 512 if _is_reasoning_model(model) else 16


def _log_parse_failure(fp, qid: str, raw, prompt: str) -> None:
    record = {
        "qid": str(qid),
        "raw": raw,
        "prompt_truncated": _truncate_prompt(prompt),
    }
    fp.write(json.dumps(record, default=str) + "\n")
    fp.flush()


def answer_cropped_timelogic(
    entries: list[dict],
    *,
    model: str,
    num_frames: int,
    output_dir: str,
    image_detail: str,
    verbose: bool,
    write_entries_path: str | None,
    entries_for_merge: list[dict] | None,
) -> tuple[list[dict], list[dict], int]:
    """Run VQA on cropped clips with parse-retry and unbiased parse-failure fallback."""
    from openai import OpenAI

    from nsvqa.utils.api_cost import RunMeter
    from nsvqa.vqa.answer_timelogic import (
        answer_one,
        format_puls_hint,
        merge_vqa_into_entries,
    )

    os.makedirs(output_dir, exist_ok=True)
    parse_failures_path = os.path.join(output_dir, "parse_failures.jsonl")
    client = OpenAI()
    run_meter = RunMeter(output_dir, label="answer_cropped")
    submission: list[dict] = []
    diag: list[dict] = []
    parse_failure_count = 0
    base_max_tokens = _default_max_output_tokens(model)

    with open(parse_failures_path, "w", encoding="utf-8") as parse_failures_fp:
        for i, entry in enumerate(entries):
            qid = entry["metadata"]["question_id"]
            mode = entry["metadata"]["mode"]
            video_path = entry["paths"]["video_path"]
            candidates = entry["candidates"]
            question = entry["metadata"].get("cleaned_question") or entry["question"]
            foi = entry.get("frames_of_interest")

            if not entry["metadata"].get("video_present", True) or not os.path.isfile(video_path):
                default = "A" if mode == "mc" else "Yes"
                submission.append({"question_id": qid, "answer_choice": default})
                diag.append({
                    "qid": qid,
                    "mode": mode,
                    "answer": default,
                    "error": "video_missing_on_disk",
                    "seconds": 0.0,
                })
                if verbose:
                    print(f"[answer {i + 1}/{len(entries)}] qid={qid} mode={mode} → {default} (missing video)")
                continue

            puls_data = entry.get("puls") or {}
            puls_hint = format_puls_hint(
                puls_data.get("proposition"),
                puls_data.get("specification"),
            )

            t0 = time.time()
            try:
                result = answer_one(
                    client,
                    model,
                    video_path,
                    foi,
                    question,
                    candidates,
                    mode,
                    num_frames=num_frames,
                    image_detail=image_detail,
                    puls_hint=puls_hint,
                    max_output_tokens=base_max_tokens,
                )
                if result.get("answer") is None and result.get("raw") is None and not result.get("error"):
                    result = answer_one(
                        client,
                        model,
                        video_path,
                        foi,
                        question,
                        candidates,
                        mode,
                        num_frames=num_frames,
                        image_detail=image_detail,
                        puls_hint=puls_hint,
                        max_output_tokens=base_max_tokens * 2,
                        prompt_suffix=PARSE_RETRY_SUFFIX,
                    )
                    result["parse_retried"] = True

                if result.get("answer") is None:
                    valid_answers = result.get("valid_answers") or (
                        ["A", "B", "C", "D"] if mode == "mc" else ["Yes", "No"]
                    )
                    _log_parse_failure(
                        parse_failures_fp,
                        qid,
                        result.get("raw"),
                        result.get("user_prompt") or question,
                    )
                    result["answer"] = random.Random(str(qid)).choice(valid_answers)
                    result["parse_failure"] = True
                    parse_failure_count += 1
            except Exception as exc:
                result = {
                    "answer": "A" if mode == "mc" else "Yes",
                    "error": repr(exc),
                    "raw": None,
                    "num_frames": 0,
                }

            result["seconds"] = round(time.time() - t0, 2)
            if run_meter and result.get("api_cost_usd") is not None:
                source = "metered" if result.get("api_usage") else "heuristic"
                run_meter.add(
                    "vision_answer",
                    float(result["api_cost_usd"]),
                    model=model,
                    source=source,
                )

            submission.append({"question_id": qid, "answer_choice": result["answer"]})
            diag.append({
                "qid": qid,
                "mode": mode,
                "foi": foi,
                "candidates": candidates if mode == "mc" else None,
                **result,
            })

            if verbose:
                err = f"  ERR: {result.get('error')!r}" if result.get("error") else ""
                pf = "  PARSE_FAILURE" if result.get("parse_failure") else ""
                print(
                    f"[answer {i + 1}/{len(entries)}] qid={qid} mode={mode} "
                    f"foi={foi} frames={result.get('num_frames')} → "
                    f"{result.get('answer')!r}  ({result.get('seconds')}s)  "
                    f"raw={result.get('raw')!r}{err}{pf}"
                )

    diag_path = os.path.join(output_dir, "answers_diag.json")
    with open(diag_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2, default=str)
    if verbose:
        print(f"\n[answer] wrote {diag_path}")

    summary_path = os.path.join(output_dir, "parse_failure_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"parse_failure_count": parse_failure_count}, f, indent=2)
    if verbose:
        print(f"[answer] parse_failures={parse_failure_count} -> {parse_failures_path}")

    if write_entries_path:
        source_entries = entries_for_merge if entries_for_merge is not None else entries
        enriched = merge_vqa_into_entries(source_entries, diag, model)
        with open(write_entries_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=2)
        if verbose:
            print(f"[answer] wrote {write_entries_path} (vqa + reasoning_summary merged)")

    run_meter.write({"vision_model": model, "num_frames": num_frames, "parse_failure_count": parse_failure_count})
    if verbose:
        print(run_meter.log_line("[answer]"))

    return submission, diag, parse_failure_count


def main() -> int:
    args = parse_args()
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"[answer-cropped] WARNING: OPENAI_API_KEY not set and not found in {args.env_file}")

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

    submission, diag, parse_failure_count = answer_cropped_timelogic(
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
        f"({mc_count} mc + {bool_count} bool); {errors} had errors; "
        f"{parse_failure_count} parse failures"
    )
    print(f"[answer-cropped] wrote {partial_path} ({len(submission)} records)")
    if not args.no_write_entries:
        print(f"[answer-cropped] merged vqa + reasoning_summary into {args.entries}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
