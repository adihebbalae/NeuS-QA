"""Build a complete EvalAI submission from a partial answers file.

Reads the full TimeLogic val annotations to enumerate every required
`question_id`, merges in real predictions from one or more `submission.json`
files (output of `scripts/answer_entries.py`), and fills the gaps with safe
defaults: "A" for `mc`, "Yes" for `bool`. Writes a single 2000-entry
EvalAI-ready submission JSON.

Defaults rationale: "A" is the conventional first choice; "Yes" tends to be
the majority class for "Did X happen?"-style bool questions. Either deterministic
choice beats random on a skewed label distribution. We can sweep this once we
have a baseline number.

Example:
    python3 scripts/build_submission.py \\
        --val-annotations /mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json \\
        --partial /mnt/Data/ah66742/timelogic/outputs/smoke_v5_answers_mini/submission.json \\
        --output /mnt/Data/ah66742/timelogic/outputs/submissions/val_v01_smoke20_plus_defaults.json
"""

import argparse
import json
import os
import sys
from collections import Counter


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--val-annotations", required=True,
                   help="Path to timelogic_val_data.json (or test_data.json)")
    p.add_argument("--partial", action="append", default=[],
                   help="Path to a partial submission.json. Can be passed multiple "
                        "times; later partials override earlier ones for overlapping qids.")
    p.add_argument("--output", required=True,
                   help="Where to write the final merged submission.json")
    p.add_argument("--default-mc", default="A", choices=["A", "B", "C", "D"],
                   help="Default answer for mc questions not covered by a partial")
    p.add_argument("--default-bool", default="Yes", choices=["Yes", "No"],
                   help="Default answer for bool questions not covered by a partial")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    with open(args.val_annotations, "r") as f:
        annotations = json.load(f)
    print(f"[build] loaded {len(annotations)} val annotations")

    partial_predictions: dict[str, str] = {}
    for partial_path in args.partial:
        with open(partial_path, "r") as f:
            records = json.load(f)
        for r in records:
            partial_predictions[str(r["question_id"])] = r["answer_choice"]
        print(f"[build] merged {len(records)} records from {partial_path}")
    print(f"[build] total unique partial predictions: {len(partial_predictions)}")

    submission = []
    source_counter: Counter = Counter()
    answer_dist_by_mode: dict[str, Counter] = {"mc": Counter(), "bool": Counter()}

    for entry in annotations:
        qid = str(entry["question_id"])
        mode = entry["mode"]

        if qid in partial_predictions:
            answer = partial_predictions[qid]
            source_counter["real"] += 1
        else:
            answer = args.default_mc if mode == "mc" else args.default_bool
            source_counter["default"] += 1

        submission.append({"question_id": qid, "answer_choice": answer})
        answer_dist_by_mode[mode][answer] += 1

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(submission, f, indent=2)

    print(f"\n[build] wrote {len(submission)} records to {args.output}")
    print(f"[build] sources: {dict(source_counter)}")
    print(f"[build] answer distribution by mode:")
    for mode, dist in answer_dist_by_mode.items():
        total = sum(dist.values())
        breakdown = ", ".join(f"{k}: {v} ({v/total*100:.1f}%)" for k, v in sorted(dist.items()))
        print(f"    {mode:5s} (n={total:4d}): {breakdown}")

    # Sanity: every annotation got an answer
    if len(submission) != len(annotations):
        print(f"!! ERROR: submission has {len(submission)} but annotations has {len(annotations)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
