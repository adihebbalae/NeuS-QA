#!/usr/bin/env python3
"""Build entries.json from NSVS rerun shard outputs.

Supports two sources:
  - per_entry: incremental per-qid JSON while rerun is in flight
  - shard_entries: complete shard_*/entries.json after rerun finishes
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rerun-root", required=True, help="nsvs_rerun directory")
    p.add_argument("--output", required=True, help="Output entries.json path")
    p.add_argument(
        "--source",
        choices=["per_entry", "shard_entries"],
        default="per_entry",
    )
    p.add_argument(
        "--qid-file",
        help="Optional JSON list of qids to keep (order preserved when limiting)",
    )
    p.add_argument("--limit", type=int, help="Max rows after filtering")
    p.add_argument(
        "--require-nsvs-ok",
        action="store_true",
        help="Drop rows whose status.step_status.nsvs != ok",
    )
    return p.parse_args()


def load_qid_filter(path: str | None) -> set[str] | None:
    if not path:
        return None
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(q) for q in raw}


def load_from_per_entry(rerun_root: Path) -> dict[str, dict]:
    by_qid: dict[str, dict] = {}
    for shard_dir in sorted(rerun_root.glob("shard_*")):
        per_dir = shard_dir / "per_entry"
        if not per_dir.is_dir():
            continue
        for path in sorted(per_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            entry = payload.get("entry")
            if not isinstance(entry, dict):
                raise ValueError(f"{path}: missing entry dict")
            qid = str(entry.get("metadata", {}).get("question_id") or path.stem)
            by_qid[qid] = entry
    return by_qid


def load_from_shard_entries(rerun_root: Path) -> dict[str, dict]:
    by_qid: dict[str, dict] = {}
    for shard_dir in sorted(rerun_root.glob("shard_*")):
        entries_path = shard_dir / "entries.json"
        if not entries_path.is_file():
            continue
        for entry in json.loads(entries_path.read_text(encoding="utf-8")):
            qid = str(entry["metadata"]["question_id"])
            by_qid[qid] = entry
    return by_qid


def load_status_map(rerun_root: Path) -> dict[str, dict]:
    status_by_qid: dict[str, dict] = {}
    for shard_dir in sorted(rerun_root.glob("shard_*")):
        per_dir = shard_dir / "per_entry"
        if not per_dir.is_dir():
            continue
        for path in per_dir.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            status = payload.get("status") or {}
            qid = str(status.get("question_id") or path.stem)
            status_by_qid[qid] = status
    return status_by_qid


def main() -> int:
    args = parse_args()
    rerun_root = Path(args.rerun_root)
    if not rerun_root.is_dir():
        print(f"FATAL: missing rerun root {rerun_root}", file=sys.stderr)
        return 1

    if args.source == "per_entry":
        by_qid = load_from_per_entry(rerun_root)
    else:
        by_qid = load_from_shard_entries(rerun_root)

    if not by_qid:
        print(f"FATAL: no entries found under {rerun_root} (source={args.source})", file=sys.stderr)
        return 1

    qid_filter = load_qid_filter(args.qid_file)
    if qid_filter is not None:
        by_qid = {q: by_qid[q] for q in qid_filter if q in by_qid}

    if args.require_nsvs_ok:
        status_map = load_status_map(rerun_root)
        kept: dict[str, dict] = {}
        for qid, entry in by_qid.items():
            st = status_map.get(qid, {}).get("step_status", {}).get("nsvs", "")
            if st == "ok":
                kept[qid] = entry
        by_qid = kept

    if args.qid_file and args.limit is None:
        order = [q for q in json.loads(Path(args.qid_file).read_text(encoding="utf-8")) if str(q) in by_qid]
        entries = [by_qid[str(q)] for q in order]
    else:
        entries = [by_qid[q] for q in sorted(by_qid.keys(), key=int)]

    if args.limit is not None:
        entries = entries[: args.limit]

    if not entries:
        print("FATAL: no entries after filtering", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, indent=2, default=str) + "\n", encoding="utf-8")

    foi_valid = sum(
        1
        for e in entries
        if e.get("frames_of_interest") and e["frames_of_interest"] != [-1]
    )
    print(
        f"[assemble] source={args.source} rows={len(entries)} "
        f"foi_valid={foi_valid}/{len(entries)} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
