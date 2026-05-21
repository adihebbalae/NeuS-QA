"""Summarize FOI and NSVS-index quality for a TimeLogic smoke output.

Reads either final `entries.json` or incremental `per_entry/*.json` artifacts
from `scripts/run_timelogic.py`.
"""

import argparse
import glob
import json
import math
import os
from collections import Counter
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        required=True,
        nargs="+",
        help="One or more smoke output directories",
    )
    parser.add_argument(
        "--write-json",
        default=None,
        help="Optional path for a machine-readable summary JSON",
    )
    return parser.parse_args()


def load_entries(output_dir: str) -> list[dict[str, Any]]:
    entries_path = os.path.join(output_dir, "entries.json")
    if os.path.exists(entries_path):
        with open(entries_path) as f:
            return json.load(f)

    rows: list[dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(output_dir, "per_entry", "*.json"))):
        with open(path) as f:
            payload = json.load(f)
        entry = payload.get("entry")
        if entry:
            rows.append(entry)
    return rows


def load_all_entries(output_dirs: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_qids: set[str] = set()
    for output_dir in output_dirs:
        for entry in load_entries(output_dir):
            qid = str(entry.get("metadata", {}).get("question_id"))
            if qid in seen_qids:
                continue
            seen_qids.add(qid)
            rows.append(entry)
    return rows


def is_valid_interval(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and value != [-1]
        and value[0] is not None
        and value[1] is not None
        and int(value[0]) <= int(value[1])
    )


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * pct
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def summarize_distribution(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p90": None,
            "max": None,
            "mean": None,
        }
    return {
        "count": len(values),
        "min": min(values),
        "p10": percentile(values, 0.10),
        "p25": percentile(values, 0.25),
        "median": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def pct(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else 100.0 * numerator / denominator


def summarize(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(entries)
    raw_nsvs_valid = 0
    raw_nsvs_minus_one = 0
    raw_nsvs_invalid_bounds = 0
    final_foi_valid = 0
    final_foi_minus_one = 0
    final_foi_invalid_bounds = 0
    final_minus_one_with_raw_valid = 0
    merged_not_superset_raw = 0

    foi_lengths_frames: list[float] = []
    foi_lengths_seconds: list[float] = []
    nsvs_lengths_frames: list[float] = []
    nsvs_lengths_seconds: list[float] = []
    modes = Counter()
    sources = Counter()

    indices_rows = 0
    indices_any_empty = 0
    indices_all_empty = 0
    empty_arrays = 0
    total_arrays = 0
    empty_by_position: Counter[int] = Counter()

    red_flags: list[dict[str, Any]] = []

    for entry in entries:
        metadata = entry.get("metadata", {})
        modes[str(metadata.get("mode"))] += 1
        sources[str(metadata.get("source_dataset"))] += 1
        fps = float(metadata.get("fps") or 1.0)
        qid = metadata.get("question_id")

        nsvs = entry.get("nsvs") or {}
        raw = nsvs.get("output")
        foi = entry.get("frames_of_interest")

        if raw == [-1] or not raw:
            raw_nsvs_minus_one += 1
            raw_valid = False
        elif is_valid_interval(raw):
            raw_nsvs_valid += 1
            raw_valid = True
            raw_len = int(raw[1]) - int(raw[0]) + 1
            nsvs_lengths_frames.append(raw_len)
            nsvs_lengths_seconds.append(raw_len / fps)
        else:
            raw_nsvs_invalid_bounds += 1
            raw_valid = False
            red_flags.append({"question_id": qid, "issue": "raw_nsvs_invalid_bounds", "raw_nsvs": raw})

        if foi == [-1] or not foi:
            final_foi_minus_one += 1
            if raw_valid:
                final_minus_one_with_raw_valid += 1
                red_flags.append({"question_id": qid, "issue": "foi_minus_one_with_raw_nsvs_valid", "raw_nsvs": raw})
        elif is_valid_interval(foi):
            final_foi_valid += 1
            foi_len = int(foi[1]) - int(foi[0]) + 1
            foi_lengths_frames.append(foi_len)
            foi_lengths_seconds.append(foi_len / fps)
            if raw_valid and (int(foi[0]) > int(raw[0]) or int(foi[1]) < int(raw[1])):
                merged_not_superset_raw += 1
                red_flags.append(
                    {
                        "question_id": qid,
                        "issue": "merged_foi_not_superset_raw_nsvs",
                        "raw_nsvs": raw,
                        "frames_of_interest": foi,
                    }
                )
        else:
            final_foi_invalid_bounds += 1
            red_flags.append({"question_id": qid, "issue": "final_foi_invalid_bounds", "frames_of_interest": foi})

        indices = nsvs.get("indices")
        if isinstance(indices, list) and indices:
            indices_rows += 1
            row_empty_arrays = 0
            for pos, arr in enumerate(indices):
                total_arrays += 1
                if not arr:
                    empty_arrays += 1
                    row_empty_arrays += 1
                    empty_by_position[pos] += 1
            if row_empty_arrays:
                indices_any_empty += 1
            if row_empty_arrays == len(indices):
                indices_all_empty += 1

    short_le_1s = sum(1 for value in foi_lengths_seconds if value <= 1.0)
    short_le_2s = sum(1 for value in foi_lengths_seconds if value <= 2.0)
    short_le_5s = sum(1 for value in foi_lengths_seconds if value <= 5.0)

    return {
        "total_entries": total,
        "mix": {
            "mode": dict(modes),
            "source_dataset": dict(sources),
        },
        "foi": {
            "non_empty": final_foi_valid,
            "non_empty_pct": pct(final_foi_valid, total),
            "minus_one": final_foi_minus_one,
            "minus_one_pct": pct(final_foi_minus_one, total),
            "invalid_bounds_non_minus_one": final_foi_invalid_bounds,
            "length_frames": summarize_distribution(foi_lengths_frames),
            "length_seconds": summarize_distribution(foi_lengths_seconds),
            "short_windows": {
                "le_1s": short_le_1s,
                "le_1s_pct_of_valid_foi": pct(short_le_1s, final_foi_valid),
                "le_2s": short_le_2s,
                "le_2s_pct_of_valid_foi": pct(short_le_2s, final_foi_valid),
                "le_5s": short_le_5s,
                "le_5s_pct_of_valid_foi": pct(short_le_5s, final_foi_valid),
            },
        },
        "raw_nsvs": {
            "valid_bounds": raw_nsvs_valid,
            "valid_bounds_pct": pct(raw_nsvs_valid, total),
            "minus_one": raw_nsvs_minus_one,
            "minus_one_pct": pct(raw_nsvs_minus_one, total),
            "invalid_bounds": raw_nsvs_invalid_bounds,
            "length_frames": summarize_distribution(nsvs_lengths_frames),
            "length_seconds": summarize_distribution(nsvs_lengths_seconds),
        },
        "merge_padding_red_flags": {
            "foi_minus_one_with_raw_nsvs_valid": final_minus_one_with_raw_valid,
            "foi_minus_one_with_raw_nsvs_valid_pct_of_raw_valid": pct(final_minus_one_with_raw_valid, raw_nsvs_valid),
            "merged_foi_not_superset_raw_nsvs": merged_not_superset_raw,
            "merged_foi_not_superset_raw_nsvs_pct_of_raw_valid": pct(merged_not_superset_raw, raw_nsvs_valid),
        },
        "nsvs_indices_probe": {
            "rows_with_indices": indices_rows,
            "rows_with_any_empty_prop_array": indices_any_empty,
            "rows_with_any_empty_prop_array_pct": pct(indices_any_empty, indices_rows),
            "rows_with_all_empty_prop_arrays": indices_all_empty,
            "rows_with_all_empty_prop_arrays_pct": pct(indices_all_empty, indices_rows),
            "empty_prop_arrays": empty_arrays,
            "total_prop_arrays": total_arrays,
            "empty_prop_arrays_pct": pct(empty_arrays, total_arrays),
            "empty_by_position": dict(empty_by_position),
        },
        "red_flags_sample": red_flags[:25],
    }


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def main() -> int:
    args = parse_args()
    entries = load_all_entries(args.output_dir)
    summary = summarize(entries)

    if args.write_json:
        with open(args.write_json, "w") as f:
            json.dump(summary, f, indent=2)

    foi = summary["foi"]
    raw = summary["raw_nsvs"]
    merge = summary["merge_padding_red_flags"]
    probe = summary["nsvs_indices_probe"]

    print(f"entries: {summary['total_entries']}")
    print(f"mix mode: {summary['mix']['mode']}")
    print(f"mix source_dataset: {summary['mix']['source_dataset']}")
    print(f"non-empty FOI: {foi['non_empty']}/{summary['total_entries']} ({foi['non_empty_pct']:.2f}%)")
    print(f"final FOI [-1]: {foi['minus_one']}/{summary['total_entries']} ({foi['minus_one_pct']:.2f}%)")
    print(f"raw NSVS valid: {raw['valid_bounds']}/{summary['total_entries']} ({raw['valid_bounds_pct']:.2f}%)")
    print(f"raw NSVS [-1]: {raw['minus_one']}/{summary['total_entries']} ({raw['minus_one_pct']:.2f}%)")
    print(
        "FOI [-1] despite raw NSVS valid: "
        f"{merge['foi_minus_one_with_raw_nsvs_valid']} "
        f"({merge['foi_minus_one_with_raw_nsvs_valid_pct_of_raw_valid']:.2f}% of raw-valid)"
    )
    print(
        "merged FOI not superset of raw NSVS: "
        f"{merge['merged_foi_not_superset_raw_nsvs']} "
        f"({merge['merged_foi_not_superset_raw_nsvs_pct_of_raw_valid']:.2f}% of raw-valid)"
    )
    length_seconds = foi["length_seconds"]
    print(
        "FOI length seconds: "
        f"min={fmt(length_seconds['min'])}, p25={fmt(length_seconds['p25'])}, "
        f"median={fmt(length_seconds['median'])}, p75={fmt(length_seconds['p75'])}, "
        f"p90={fmt(length_seconds['p90'])}, max={fmt(length_seconds['max'])}"
    )
    short = foi["short_windows"]
    print(
        "short FOI windows: "
        f"<=1s {short['le_1s']} ({short['le_1s_pct_of_valid_foi']:.2f}% of valid), "
        f"<=2s {short['le_2s']} ({short['le_2s_pct_of_valid_foi']:.2f}% of valid), "
        f"<=5s {short['le_5s']} ({short['le_5s_pct_of_valid_foi']:.2f}% of valid)"
    )
    print(
        "NSVS indices rows with any empty proposition array: "
        f"{probe['rows_with_any_empty_prop_array']}/{probe['rows_with_indices']} "
        f"({probe['rows_with_any_empty_prop_array_pct']:.2f}%)"
    )
    print(
        "NSVS empty proposition arrays: "
        f"{probe['empty_prop_arrays']}/{probe['total_prop_arrays']} "
        f"({probe['empty_prop_arrays_pct']:.2f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
