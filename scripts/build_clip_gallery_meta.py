#!/usr/bin/env python3
"""Enrich v1_clips/manifest.json and write QUERIES.md for the tech report."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "reports" / "tech_report" / "v1_clips"
MANIFEST = ROOT / "manifest.json"
QUERIES_MD = REPO / "docs/timelogic/tech_report/QUERIES.md"
SELECTED_CSV = REPO / "diagnostics/sub5b_failure_audit_v3/selected_rows.csv"

PATHS = {
    "val_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json"),
    "test_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json"),
    "sub1": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json"),
    "sub5b": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/submission_sub5b_paper_faithful_gpt52.json"
    ),
    "sub7b": Path("/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/submission_sub7b.json"),
    "sub9": Path("/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_test/submission_sub9_pulsv2_test.json"),
    "sub5b_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2"),
    "sub9_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub9_pulsv2_test"),
}


def load_submission(path: Path) -> dict[str, str]:
    rows = json.loads(path.read_text())
    return {str(r["question_id"]): r["answer_choice"] for r in rows}


def load_annotations(path: Path) -> dict[str, dict]:
    return {str(r["question_id"]): r for r in json.loads(path.read_text())}


def load_selected_rows() -> dict[str, dict[str, str]]:
    if not SELECTED_CSV.is_file():
        return {}
    out: dict[str, dict[str, str]] = {}
    with SELECTED_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            out[row["question_id"]] = row
    return out


def find_per_entry(qid: str, shards_root: Path) -> dict | None:
    for p in shards_root.glob(f"shard_*/per_entry/{qid}.json"):
        if p.is_file():
            data = json.loads(p.read_text())
            return data.get("entry") or data
    return None


def format_mc_choices(candidates: list[str]) -> str:
    labels = "ABCD"
    lines = []
    for i, c in enumerate(candidates):
        lab = labels[i] if i < len(labels) else "?"
        lines.append(f"- **{lab}:** {c}")
    return "\n".join(lines)


def render_queries_md(manifest: list[dict]) -> str:
    lines = [
        "# Tech report — queries (v1 clips)",
        "",
        "14 benchmark questions tied to the clip gallery (`v1_clips/gallery.html`).",
        "Regenerate: `python3 scripts/build_clip_gallery_meta.py`.",
        "",
        "**Note:** EvalAI val **ground truth** is not stored locally. Val rows show Sub #1 vs Sub #5B;",
        "test rows show Sub #7b (and Sub #9 where noted). Step 3 (worked/failed vs GT) needs label export.",
        "",
    ]
    for m in manifest:
        slot = m["slot"]
        qid = m["qid"]
        split = m["split"]
        lines.append(f"## #{slot:02d} — {split} qid {qid} ({m['source_dataset']}, {m.get('operator_guess', m.get('operator', '?'))})")
        lines.append("")
        cleaned = m.get("cleaned_question") or m.get("question", "")
        if cleaned and cleaned != m.get("question"):
            lines.append(f"**Cleaned:** {cleaned}")
            lines.append("")
        lines.append(f"**Question:** {m.get('question', '')}")
        lines.append("")
        if m.get("mode") == "bool":
            lines.append("**Choices:** Yes / No")
        elif m.get("candidates"):
            lines.append("**Choices:**")
            lines.append(format_mc_choices(m["candidates"]))
        lines.append("")
        if m.get("puls_specification"):
            lines.append(f"**PULS spec:** `{m['puls_specification']}`")
            lines.append("")
        ans_lines = []
        if split == "val":
            ans_lines.append(f"| Sub #1 | {m.get('sub1_answer') or '—'} |")
            ans_lines.append(f"| Sub #5B (val pipeline) | {m.get('sub5b_answer') or '—'} |")
            if m.get("sub1_sub5b_agree") is not None:
                agree = "same" if m["sub1_sub5b_agree"] else "**disagree**"
                ans_lines.append(f"| Sub1 vs 5B | {agree} |")
        else:
            ans_lines.append(f"| Sub #7b (test) | {m.get('sub7b_answer') or '—'} |")
            ans_lines.append(f"| Sub #9 PULS v2 (test) | {m.get('sub9_answer') or '—'} |")
        lines.append("| Run | Answer |")
        lines.append("| --- | --- |")
        lines.extend(ans_lines)
        lines.append("")
        meta_bits = [f"FOI: `{m.get('foi_status', '?')}`", f"`{m['video_id']}`"]
        lines.append(" · ".join(meta_bits))
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    val_ann = load_annotations(PATHS["val_ann"])
    test_ann = load_annotations(PATHS["test_ann"])
    sub1 = load_submission(PATHS["sub1"])
    sub5b = load_submission(PATHS["sub5b"])
    sub7b = load_submission(PATHS["sub7b"])
    sub9 = load_submission(PATHS["sub9"])
    selected = load_selected_rows()

    for m in manifest:
        qid = str(m["qid"])
        split = m["split"]
        ann = val_ann.get(qid) if split == "val" else test_ann.get(qid)
        shards = PATHS["sub5b_shards"] if split == "val" else PATHS["sub9_shards"]
        ent = find_per_entry(qid, shards)
        meta = (ent or {}).get("metadata") or {}
        puls = (ent or {}).get("puls") or {}

        m["question"] = (ent or {}).get("question") or (ann or {}).get("question") or ""
        m["cleaned_question"] = meta.get("cleaned_question") or ""
        m["candidates"] = (ent or {}).get("candidates") or []
        m["mode"] = meta.get("mode") or (ann or {}).get("mode") or ""
        m["operator_guess"] = meta.get("operator_guess") or m.get("operator", "")
        m["puls_specification"] = puls.get("specification") or ""
        m["puls_propositions"] = puls.get("proposition") or []
        m["foi_status"] = m.get("foi_status") or (
            str((ent or {}).get("frames_of_interest")) if ent else "?"
        )

        m["sub1_answer"] = sub1.get(qid) if split == "val" else None
        m["sub5b_answer"] = sub5b.get(qid) if split == "val" else None
        m["sub7b_answer"] = sub7b.get(qid) if split == "test" else None
        m["sub9_answer"] = sub9.get(qid) if split == "test" else None

        if split == "val" and qid in selected:
            row = selected[qid]
            m["sub1_sub5b_agree"] = row.get("same_answer") == "True"
        else:
            m["sub1_sub5b_agree"] = None

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    QUERIES_MD.parent.mkdir(parents=True, exist_ok=True)
    QUERIES_MD.write_text(render_queries_md(manifest))
    print(f"Wrote {MANIFEST}")
    print(f"Wrote {QUERIES_MD}")


if __name__ == "__main__":
    main()
