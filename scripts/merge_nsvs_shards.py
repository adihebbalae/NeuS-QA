"""Merge per-shard entries.json from parallel run_timelogic.py jobs."""

from __future__ import annotations

import argparse
import json
import os


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shard-dirs", required=True,
                   help="Comma-separated directories each containing entries.json")
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    dirs = [d.strip() for d in args.shard_dirs.split(",") if d.strip()]
    merged: list[dict] = []
    for d in dirs:
        path = os.path.join(d, "entries.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            merged.extend(json.load(f))

    merged.sort(key=lambda e: int(e["metadata"]["question_id"]))
    seen = set()
    for e in merged:
        qid = e["metadata"]["question_id"]
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
        "foi_nonempty": sum(
            1 for e in merged
            if e.get("frames_of_interest") and e["frames_of_interest"] != [-1]
        ),
    }
    with open(os.path.join(args.out_dir, "merge_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[merge] {len(merged)} entries -> {out_entries}")
    print(f"[merge] foi_nonempty={summary['foi_nonempty']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
