#!/usr/bin/env python3
"""Helpers for Sub9 val shard sizing and NSVS coverage checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_ann_entries(ann_path: Path, video_root: Path | None) -> list[dict]:
    """Load entries with real video_present flags (matches run_timelogic / TimeLogic)."""
    if video_root is not None:
        import os
        import sys

        repo = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo))
        from nsvqa.datamanager.timelogic import TimeLogic

        loader = TimeLogic(
            split="val",
            video_root=str(video_root),
            ann_path=str(ann_path),
            verbose=False,
        )
        return loader.load_data()
    return json.loads(ann_path.read_text(encoding="utf-8"))


def val_pool(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e["metadata"].get("video_present", True)]


def shard_bounds(n_pool: int, total_splits: int, shard_1idx: int) -> tuple[int, int]:
    cs = max(1, min(shard_1idx, total_splits))
    start = (n_pool * (cs - 1)) // total_splits
    end = (n_pool * cs) // total_splits
    return start, end


def expected_shard_size(n_pool: int, total_splits: int, shard_1idx: int) -> int:
    start, end = shard_bounds(n_pool, total_splits, shard_1idx)
    return end - start


def qid_to_shard(qid: str, entries: list[dict], total_splits: int) -> int:
    pool = val_pool(entries)
    by_qid = {str(e["metadata"]["question_id"]): i for i, e in enumerate(pool)}
    idx = by_qid[str(qid)]
    for cs in range(1, total_splits + 1):
        start, end = shard_bounds(len(pool), total_splits, cs)
        if start <= idx < end:
            return cs
    raise ValueError(f"qid {qid} index {idx} outside shards")


def load_seen_qids(base: Path, total_splits: int) -> dict[str, int]:
    seen: dict[str, int] = {}
    for i in range(1, total_splits + 1):
        path = base / f"shard_{i}" / "entries.json"
        if not path.is_file():
            continue
        for entry in json.loads(path.read_text(encoding="utf-8")):
            seen[str(entry["metadata"]["question_id"])] = i
    return seen


def missing_by_shard(
    base: Path,
    entries: list[dict],
    total_splits: int,
) -> dict[int, list[str]]:
    pool_qids = {str(e["metadata"]["question_id"]) for e in val_pool(entries)}
    seen = load_seen_qids(base, total_splits)
    missing = sorted(pool_qids - set(seen), key=int)
    out: dict[int, list[str]] = {i: [] for i in range(1, total_splits + 1)}
    for q in missing:
        out[qid_to_shard(q, entries, total_splits)].append(q)
    return out


def shard_complete(
    base: Path,
    entries: list[dict],
    total_splits: int,
    shard_1idx: int,
) -> bool:
    n_pool = len(val_pool(entries))
    expected = expected_shard_size(n_pool, total_splits, shard_1idx)
    path = base / f"shard_{shard_1idx}" / "entries.json"
    if not path.is_file():
        return False
    n = len(json.loads(path.read_text(encoding="utf-8")))
    return n >= expected


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--ann", required=True)
    p.add_argument(
        "--video-root",
        default=None,
        help="Val video dir (required for accurate video_present / coverage)",
    )
    p.add_argument("--total", type=int, default=6)
    p.add_argument("--check", action="store_true", help="Exit 0 iff all val qids covered")
    p.add_argument("--shard", type=int, default=0, help="Exit 0 iff shard has expected entry count")
    p.add_argument(
        "--shard-ready",
        type=int,
        default=0,
        help="Exit 0 iff shard has entries.json and no missing qids in its slice",
    )
    p.add_argument("--print-missing", action="store_true")
    p.add_argument("--write-gap-plan", metavar="PATH")
    args = p.parse_args()

    base = Path(args.base)
    ann_path = Path(args.ann)
    video_root = Path(args.video_root) if args.video_root else None
    entries = load_ann_entries(ann_path, video_root)
    pool = val_pool(entries)
    n_pool = len(pool)
    seen = load_seen_qids(base, args.total)
    pool_qids = {str(e["metadata"]["question_id"]) for e in pool}
    seen_in_pool = {q for q in seen if q in pool_qids}
    missing_global = sorted(pool_qids - seen_in_pool, key=int)
    missing = {i: [] for i in range(1, args.total + 1)}
    for q in missing_global:
        missing[qid_to_shard(q, entries, args.total)].append(q)

    if args.write_gap_plan:
        plan = {
            "n_pool": n_pool,
            "n_seen_in_pool": len(seen_in_pool),
            "n_missing": len(missing_global),
            "by_shard": {str(k): v for k, v in missing.items() if v},
        }
        Path(args.write_gap_plan).write_text(json.dumps(plan, indent=2), encoding="utf-8")

    if args.print_missing:
        for shard, qids in sorted(missing.items()):
            if qids:
                print(f"shard_{shard}: {len(qids)} missing -> {qids}")

    quiet = bool(args.shard or args.shard_ready or args.check)
    if not quiet:
        incomplete = [
            i
            for i in range(1, args.total + 1)
            if not shard_complete(base, entries, args.total, i)
        ]
        if incomplete:
            print(f"incomplete shards (entry count < expected): {incomplete}")

    if args.shard:
        return 0 if shard_complete(base, entries, args.total, args.shard) else 1

    if args.shard_ready:
        path = base / f"shard_{args.shard_ready}" / "entries.json"
        if not path.is_file():
            return 1
        gaps = missing_by_shard(base, entries, args.total)[args.shard_ready]
        return 0 if not gaps else 1

    if args.check:
        return 0 if len(seen_in_pool) >= n_pool else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
