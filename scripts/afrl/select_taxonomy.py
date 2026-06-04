#!/usr/bin/env python3
"""Select 8-10 taxonomy clips from enriched manifest (Task 3).

Deprecated for test slide cases: use select_pipeline_examples.py (pipeline-stage taxonomy).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT, load_enriched_manifest, write_json

# Manual audit hints (RESULTS.md 2026-05-24): priority-B CoT-split → ill-posed.
ILL_POSED_AUDIT_QIDS = {"1105", "489", "601", "262", "1525", "635", "1865", "796"}
# 1865 is ours win, not both_wrong — exclude from both_wrong pool.
OURS_WIN_AUDIT_QIDS = {"1865"}

SEED_VLM_ONLY = ["682", "489", "601"]
SEED_OURS_ONLY = ["1865"]

TAG_ORDER = ["vlm_only_correct", "ours_only_correct", "both_correct", "both_wrong"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=AFRL_ROOT / "enriched_manifest.json")
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "taxonomy.json")
    p.add_argument(
        "--split",
        choices=("val", "test", "both"),
        default="val",
        help="Select taxonomy clips from this split (default: val — audit-backed seeds)",
    )
    p.add_argument(
        "--override-qids",
        nargs="*",
        help="Optional qid:tag pairs, e.g. 682:vlm_only_correct",
    )
    p.add_argument("--min-clips", type=int, default=8)
    p.add_argument("--max-clips", type=int, default=10)
    return p.parse_args()


def val_rows(manifest: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    if split == "both":
        return manifest
    return [r for r in manifest if r["split"] == split]


def spec_collapse(row: dict[str, Any]) -> bool:
    op = (row.get("operator_guess") or "").lower()
    spec = (row.get("our_spec") or "").strip()
    return op == "unknown" or not spec or spec in {'""', "()"}


def short_clip(row: dict[str, Any]) -> bool:
    return row.get("length_bucket") in {"<2s", "2-10s"}


def long_clip(row: dict[str, Any]) -> bool:
    return row.get("length_bucket") == ">60s"


def score_vlm_only(row: dict[str, Any]) -> tuple:
    seed = 0 if row["qid"] in SEED_VLM_ONLY else 1
    short = 0 if short_clip(row) else 1
    collapse = 0 if spec_collapse(row) else 1
    disagree = 0 if row.get("answers_agree") is False else 1
    return (disagree, seed, short, collapse, -float(row.get("duration_s") or 0))


def score_ours_only(row: dict[str, Any]) -> tuple:
    seed = 0 if row["qid"] in SEED_OURS_ONLY else 1
    long_ok = 0 if long_clip(row) else 1
    foi = 0 if row.get("foi_success") else 1
    disagree = 0 if row.get("answers_agree") is False else 1
    bf_ct = 0 if row.get("source") in {"bf", "ct"} else 1
    return (disagree, seed, long_ok, foi, bf_ct, -float(row.get("duration_s") or 0))


def score_both_correct(row: dict[str, Any]) -> tuple:
    agree = 0 if row.get("answers_agree") else 1
    long_ok = 0 if long_clip(row) else 1
    bf_ct = 0 if row.get("source") in {"bf", "ct"} else 1
    ordering = 0 if row.get("operator_family") in {"always_before", "before"} else 1
    return (agree, long_ok, bf_ct, ordering, -float(row.get("duration_s") or 0))


def score_both_wrong(row: dict[str, Any]) -> tuple:
    audit = 0 if row["qid"] in ILL_POSED_AUDIT_QIDS and row["qid"] not in OURS_WIN_AUDIT_QIDS else 1
    short = 0 if short_clip(row) else 1
    star_agqa = 0 if row.get("source") in {"star", "agqa"} else 1
    disagree = 0 if row.get("answers_agree") is False else 1
    return (audit, disagree, short, star_agqa)


def pick_best(pool: list[dict[str, Any]], score_fn, used: set[str], n: int = 1) -> list[dict[str, Any]]:
    ranked = sorted(pool, key=score_fn)
    picked: list[dict[str, Any]] = []
    for row in ranked:
        if row["qid"] in used:
            continue
        picked.append(row)
        used.add(row["qid"])
        if len(picked) >= n:
            break
    return picked


def apply_overrides(
    rows_by_qid: dict[str, dict[str, Any]], overrides: list[str] | None
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not overrides:
        return mapping
    for item in overrides:
        if ":" not in item:
            continue
        qid, tag = item.split(":", 1)
        mapping[qid.strip()] = tag.strip()
    for qid, tag in mapping.items():
        if qid not in rows_by_qid:
            raise SystemExit(f"override qid {qid} not found in manifest")
        if tag not in TAG_ORDER:
            raise SystemExit(f"unknown tag {tag} for qid {qid}")
    return mapping


def ensure_coverage(
    selected: list[tuple[dict[str, Any], str]], pool: list[dict[str, Any]], used: set[str]
) -> list[tuple[dict[str, Any], str]]:
    """Swap or append rows until agqa/star/bf/ct and mc/bool are represented."""
    required_sources = {"agqa", "star", "bf", "ct"}
    required_modes = {"mc", "bool"}

    def sources_modes(items: list[tuple[dict[str, Any], str]]) -> tuple[set[str], set[str]]:
        return {r["source"] for r, _ in items}, {r["mode"] for r, _ in items}

    src, modes = sources_modes(selected)
    missing_src = required_sources - src
    missing_modes = required_modes - modes

    if not missing_src and not missing_modes:
        return selected

    # Prefer seed replacements for known gaps
    seed_by_source = {
        "bf": ("107", "ours_only_correct"),
        "star": ("682", "vlm_only_correct"),
        "agqa": ("489", "vlm_only_correct"),
        "ct": ("1865", "ours_only_correct"),
    }
    for src_name in list(missing_src):
        qid, preferred_tag = seed_by_source.get(src_name, ("", ""))
        if qid and qid in {r["qid"] for r in pool}:
            row = next(r for r in pool if r["qid"] == qid)
            if row["qid"] not in {r["qid"] for r, _ in selected}:
                # Replace last clip from an over-represented source if at capacity
                selected.append((row, preferred_tag))
                used.add(qid)
                missing_src.discard(src_name)

    src, modes = sources_modes(selected)
    missing_src = required_sources - src
    missing_modes = required_modes - modes

    score_by_tag = {
        "vlm_only_correct": score_vlm_only,
        "ours_only_correct": score_ours_only,
        "both_correct": score_both_correct,
        "both_wrong": score_both_wrong,
    }
    for src_name in missing_src:
        for tag in TAG_ORDER:
            candidates = [r for r in pool if r["source"] == src_name and r["qid"] not in used]
            if not candidates:
                continue
            row = pick_best(candidates, score_by_tag[tag], set(), 1)[0]
            selected.append((row, tag))
            used.add(row["qid"])
            break

    src, modes = sources_modes(selected)
    for mode in required_modes - modes:
        for tag in TAG_ORDER:
            candidates = [r for r in pool if r["mode"] == mode and r["qid"] not in used]
            if not candidates:
                continue
            row = pick_best(candidates, score_by_tag[tag], set(), 1)[0]
            selected.append((row, tag))
            used.add(row["qid"])
            break

    # Deduplicate by qid, keep first tag assignment
    seen: set[str] = set()
    deduped: list[tuple[dict[str, Any], str]] = []
    for row, tag in selected:
        if row["qid"] in seen:
            continue
        seen.add(row["qid"])
        deduped.append((row, tag))
    return deduped


def auto_select(
    pool: list[dict[str, Any]], min_clips: int, max_clips: int
) -> list[tuple[dict[str, Any], str]]:
    rows_by_qid = {r["qid"]: r for r in pool}
    used: set[str] = set()
    selected: list[tuple[dict[str, Any], str]] = []

    # Seed-first assignments from plan / manual audit
    seed_assignments = [
        ("682", "vlm_only_correct"),
        ("489", "vlm_only_correct"),
        ("1865", "ours_only_correct"),
        ("107", "ours_only_correct"),
        ("5", "both_correct"),
        ("1105", "both_wrong"),
        ("262", "both_wrong"),
        ("796", "both_wrong"),
    ]
    for qid, tag in seed_assignments:
        row = rows_by_qid.get(qid)
        if row and qid not in used:
            selected.append((row, tag))
            used.add(qid)

    tag_targets = {
        "vlm_only_correct": 2,
        "ours_only_correct": 2,
        "both_correct": 1,
        "both_wrong": 3,
    }
    tag_counts = {tag: sum(1 for _, t in selected if t == tag) for tag in TAG_ORDER}

    for tag in TAG_ORDER:
        need = tag_targets[tag] - tag_counts.get(tag, 0)
        if need <= 0:
            continue
        if tag == "vlm_only_correct":
            picks = pick_best(pool, score_vlm_only, used, need)
        elif tag == "ours_only_correct":
            picks = pick_best(pool, score_ours_only, used, need)
        elif tag == "both_correct":
            picks = pick_best(pool, score_both_correct, used, need)
        else:
            picks = pick_best(pool, score_both_wrong, used, need)
        for row in picks:
            selected.append((row, tag))

    selected = ensure_coverage(selected, pool, used)

    if len(selected) > max_clips:
        # Drop lowest-priority extras: keep one per tag minimum, then seeds
        priority_qids = set(SEED_VLM_ONLY + SEED_OURS_ONLY + ["107", "5", "1105", "262"])
        trimmed: list[tuple[dict[str, Any], str]] = []
        tags_seen: set[str] = set()
        for row, tag in selected:
            if row["qid"] in priority_qids or tag not in tags_seen:
                trimmed.append((row, tag))
                tags_seen.add(tag)
        for row, tag in selected:
            if len(trimmed) >= max_clips:
                break
            if (row, tag) not in trimmed:
                trimmed.append((row, tag))
        selected = trimmed[:max_clips]

    while len(selected) < min_clips:
        for tag in TAG_ORDER:
            score_fn = {
                "vlm_only_correct": score_vlm_only,
                "ours_only_correct": score_ours_only,
                "both_correct": score_both_correct,
                "both_wrong": score_both_wrong,
            }[tag]
            extra = pick_best(pool, score_fn, used, 1)
            if extra:
                selected.append((extra[0], tag))
                break
        else:
            break

    return selected[:max_clips]


def to_taxonomy_record(row: dict[str, Any], tag: str) -> dict[str, Any]:
    return {
        "qid": row["qid"],
        "split": row["split"],
        "source": row["source"],
        "video_id": row.get("video_id"),
        "duration_s": row["duration_s"],
        "length_bucket": row["length_bucket"],
        "mode": row["mode"],
        "operator_family": row["operator_family"],
        "question": row["question"],
        "candidates": row["candidates"],
        "gt": row["gt"],
        "expected_spec": row["expected_spec"],
        "our_spec": row["our_spec"],
        "our_answer": row["our_answer"],
        "vanilla_vlm_answer": row["vanilla_vlm_answer"],
        "taxonomy_tag": tag,
        "gt_available": False,
        "frames": [],
        "foi_window": row["foi_window"],
    }


def validate_selection(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    tags = {r["taxonomy_tag"] for r in records}
    for tag in TAG_ORDER:
        if tag not in tags:
            errors.append(f"missing tag: {tag}")
    sources = {r["source"] for r in records}
    for src in ("agqa", "star", "bf", "ct"):
        if src not in sources:
            errors.append(f"missing source: {src}")
    modes = {r["mode"] for r in records}
    if "mc" not in modes or "bool" not in modes:
        errors.append(f"missing mode coverage: {modes}")
    families = {r["operator_family"] for r in records}
    if len(families) < 3:
        errors.append(f"need >=3 operator families, got {families}")
    for r in records:
        if not r["our_answer"] or not r["vanilla_vlm_answer"]:
            errors.append(f"qid {r['qid']} missing answers")
    return errors


def main() -> int:
    args = parse_args()
    manifest = load_enriched_manifest(args.manifest)
    pool = val_rows(manifest, args.split)
    rows_by_qid = {r["qid"]: r for r in pool}

    override_map = apply_overrides(rows_by_qid, args.override_qids)
    if override_map:
        selected = [(rows_by_qid[qid], tag) for qid, tag in override_map.items()]
    else:
        selected = auto_select(pool, args.min_clips, args.max_clips)

    records = [to_taxonomy_record(row, tag) for row, tag in selected]
    errors = validate_selection(records)
    if errors:
        for err in errors:
            print(f"[select] WARNING: {err}", file=sys.stderr)

    write_json(args.out, records)

    print(f"[select] wrote {args.out} clips={len(records)}")
    print(f"{'qid':>6} {'tag':22} {'src':5} {'bucket':8} {'mode':5} ours  vanilla")
    for r in records:
        print(
            f"{r['qid']:>6} {r['taxonomy_tag']:22} {r['source']:5} "
            f"{r['length_bucket']:8} {r['mode']:5} {r['our_answer']:4}  {r['vanilla_vlm_answer']}"
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
