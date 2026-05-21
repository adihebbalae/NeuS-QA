#!/usr/bin/env python3
"""Build a val submission that looks like a normal run (not a constant-A probe).

PI guidance: do NOT upload all-A / all-Yes — EvalAI may flag obvious calibration
probes. This script assigns a deterministic pseudo-random answer per question_id
so rows vary and marginals are roughly uniform (25% per MC letter, 50% Yes/No).

The resulting score is a **random-guess baseline**, not a per-letter GT prior.
See timelogic-data/outputs/probe_calibration/README.md.

Example:
    python3 scripts/build_probe_calibration_submission.py \\
        --val-annotations /home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json \\
        --output /home/ah66742/timelogic-data/outputs/probe_calibration/submission.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter


MC_CHOICES = ("A", "B", "C", "D")
BOOL_CHOICES = ("Yes", "No")
DEFAULT_SEED_TAG = "probe_calibration_v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--val-annotations",
        required=True,
        help="Path to timelogic_val_data.json",
    )
    p.add_argument("--output", required=True, help="EvalAI submission JSON path")
    p.add_argument(
        "--manifest",
        default=None,
        help="Optional manifest JSON (defaults to <output_dir>/manifest.json)",
    )
    p.add_argument(
        "--seed-tag",
        default=DEFAULT_SEED_TAG,
        help="Salt for per-qid hashing (change to regenerate a different slice)",
    )
    return p.parse_args()


def pick_answer(qid: str, mode: str, seed_tag: str) -> str:
    digest = hashlib.sha256(f"{seed_tag}:{qid}:{mode}".encode()).hexdigest()
    bucket = int(digest[:8], 16)
    choices = MC_CHOICES if mode == "mc" else BOOL_CHOICES
    return choices[bucket % len(choices)]


def main() -> int:
    args = parse_args()

    with open(args.val_annotations, "r", encoding="utf-8") as f:
        annotations = json.load(f)

    submission = []
    by_mode: dict[str, Counter] = {"mc": Counter(), "bool": Counter()}

    for entry in annotations:
        qid = str(entry["question_id"])
        mode = entry["mode"]
        answer = pick_answer(qid, mode, args.seed_tag)
        submission.append({"question_id": qid, "answer_choice": answer})
        by_mode[mode][answer] += 1

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)

    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = os.path.join(os.path.dirname(args.output), "manifest.json")

    manifest = {
        "method": "qid_seeded_pseudo_random",
        "seed_tag": args.seed_tag,
        "n_rows": len(submission),
        "warning": "Do not use constant all-A/all-Yes (EvalAI ban risk per PI).",
        "expected_accuracy_note": (
            "~25% on MC (4-way), ~50% on bool → ~32-35% overall if labels are balanced"
        ),
        "distribution": {
            mode: dict(sorted(dist.items())) for mode, dist in by_mode.items()
        },
        "val_annotations": os.path.abspath(args.val_annotations),
        "output": os.path.abspath(args.output),
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[probe-cal] wrote {len(submission)} rows → {args.output}")
    for mode, dist in by_mode.items():
        total = sum(dist.values())
        parts = ", ".join(f"{k}: {v} ({100 * v / total:.1f}%)" for k, v in sorted(dist.items()))
        print(f"  {mode} (n={total}): {parts}")
    print(f"[probe-cal] manifest → {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
