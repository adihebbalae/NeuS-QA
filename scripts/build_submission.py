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

DISTRIBUTION_MAX_FRACTION = 0.60


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
    p.add_argument(
        "--parse-failures",
        default=None,
        help="Optional parse_failures.jsonl from answer_cropped_entries (also auto-detected "
             "beside each --partial path)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Write submission even if any MC/Bool label exceeds 60%% (EvalAI ban risk)",
    )
    return p.parse_args()


def _count_parse_failures(path: str) -> int:
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def _resolve_parse_failures_path(args) -> str | None:
    if args.parse_failures and os.path.isfile(args.parse_failures):
        return args.parse_failures
    for partial_path in args.partial:
        candidate = os.path.join(os.path.dirname(partial_path), "parse_failures.jsonl")
        if os.path.isfile(candidate):
            return candidate
    return None


def _format_distribution_breakdown(dist: Counter, total: int) -> str:
    return ", ".join(f"{k}: {dist[k]} ({dist[k] / total * 100:.1f}%)" for k in sorted(dist))


def distribution_violations(
    answer_dist_by_mode: dict[str, Counter],
    max_fraction: float = DISTRIBUTION_MAX_FRACTION,
) -> list[tuple[str, str, int, int, float]]:
    """Return (mode, label, count, total, fraction) for labels above the cap."""
    violations: list[tuple[str, str, int, int, float]] = []
    for mode in ("mc", "bool"):
        dist = answer_dist_by_mode.get(mode, Counter())
        total = sum(dist.values())
        if total == 0:
            continue
        for label, count in dist.items():
            frac = count / total
            if frac > max_fraction:
                violations.append((mode, label, count, total, frac))
    return violations


def check_submission_distribution(
    answer_dist_by_mode: dict[str, Counter],
    *,
    force: bool,
) -> bool:
    """Print distribution breakdown; abort if any label exceeds 60% unless force."""
    violations = distribution_violations(answer_dist_by_mode)
    if not violations:
        return True

    print("\nWARNING: submission label distribution exceeds 60% cap (EvalAI auto-reject risk):")
    for mode in ("mc", "bool"):
        dist = answer_dist_by_mode.get(mode, Counter())
        total = sum(dist.values())
        if total == 0:
            continue
        print(f"  {mode} (n={total}): {_format_distribution_breakdown(dist, total)}")
    for mode, label, count, total, frac in violations:
        print(f"  >>> {mode} label {label!r}: {count}/{total} ({frac * 100:.1f}%)")

    if force:
        print("[build] --force passed; writing submission anyway")
        return True

    print("[build] aborting without writing output (pass --force to override)")
    return False


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

    if not check_submission_distribution(answer_dist_by_mode, force=args.force):
        return 1

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(submission, f, indent=2)

    print(f"\n[build] wrote {len(submission)} records to {args.output}")
    print(f"[build] sources: {dict(source_counter)}")

    parse_failures_path = _resolve_parse_failures_path(args)
    if parse_failures_path:
        pf_count = _count_parse_failures(parse_failures_path)
        print(f"[build] parse_failures: {pf_count} (from {parse_failures_path})")
    else:
        summary_candidates = []
        for partial_path in args.partial:
            summary_candidates.append(
                os.path.join(os.path.dirname(partial_path), "parse_failure_summary.json")
            )
        for summary_path in summary_candidates:
            if os.path.isfile(summary_path):
                with open(summary_path, encoding="utf-8") as f:
                    pf_count = json.load(f).get("parse_failure_count", 0)
                print(f"[build] parse_failures: {pf_count} (from {summary_path})")
                break

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
