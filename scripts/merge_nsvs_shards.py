"""Merge per-shard entries.json from parallel run_timelogic.py jobs."""

from __future__ import annotations

import argparse
import json
import os


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--shard-dirs",
        required=True,
        help="Comma-separated directories each containing entries.json",
    )
    p.add_argument("--out-dir", required=True)
    p.add_argument(
        "--into-entries",
        default=None,
        help="Optional existing entries.json; shard rows overwrite matching question_ids",
    )
    return p.parse_args()


def _qid(entry: dict) -> str:
    return str(entry["metadata"]["question_id"])


def main() -> int:
    args = parse_args()
    dirs = [d.strip() for d in args.shard_dirs.split(",") if d.strip()]

    by_qid: dict[str, dict] = {}
    n_base = 0
    if args.into_entries:
        with open(args.into_entries, "r", encoding="utf-8") as f:
            for entry in json.load(f):
                by_qid[_qid(entry)] = entry
        n_base = len(by_qid)

    n_from_shards = 0
    for d in dirs:
        path = os.path.join(d, "entries.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            shard_entries = json.load(f)
        for entry in shard_entries:
            by_qid[_qid(entry)] = entry
            n_from_shards += 1

    merged = sorted(by_qid.values(), key=lambda e: int(_qid(e)))

    if not args.into_entries:
        seen: set[str] = set()
        for entry in merged:
            qid = _qid(entry)
            if qid in seen:
                raise ValueError(f"duplicate question_id {qid}")
            seen.add(qid)

    os.makedirs(args.out_dir, exist_ok=True)
    out_entries = os.path.join(args.out_dir, "entries.json")
    with open(out_entries, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, default=str)

    summary = {
        "n_shards": len(dirs),
        "n_entries": len(merged),
        "shard_dirs": dirs,
        "into_entries": args.into_entries,
        "n_base_entries": n_base,
        "n_shard_rows_read": n_from_shards,
        "n_overwritten": n_from_shards if args.into_entries else 0,
        "foi_nonempty": sum(
            1 for e in merged
            if e.get("frames_of_interest") and e["frames_of_interest"] != [-1]
        ),
    }
    with open(os.path.join(args.out_dir, "merge_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if args.into_entries:
        print(
            f"[merge] {n_from_shards} shard rows into {n_base} base -> "
            f"{len(merged)} entries -> {out_entries}"
        )
    else:
        print(f"[merge] {len(merged)} entries -> {out_entries}")
    print(f"[merge] foi_nonempty={summary['foi_nonempty']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
