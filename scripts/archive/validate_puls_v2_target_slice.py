#!/usr/bin/env python3
"""Re-run PULS (v2 prompt) on the 148-row Diagnostic-2 target slice.

Target = 94 empty_puls_output + 54 operator_collapse_open_ended rows from
diagnostics/puls_unknown_analysis/details.csv (unknown-family NSVS-bypassed).

Compares baseline PULS (from Sub #5B entries) vs fresh PULS call using current
nsvqa/puls/prompts.py. PULS-only structural gates — no NSVS re-run.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_DETAILS = REPO_ROOT / "diagnostics/puls_unknown_analysis/details.csv"
DEFAULT_ENTRIES = Path(
    "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/merged/entries.json"
)
DEFAULT_OUT = Path("/mnt/Data/ah66742/timelogic/outputs/puls_v2_validation_148")
TARGET_REASONS = frozenset({"empty_puls_output", "operator_collapse_open_ended"})

def _load_analyze_module():
    import importlib.util

    path = REPO_ROOT / "scripts/analyze_puls_unknown_bypassed.py"
    spec = importlib.util.spec_from_file_location("analyze_puls_unknown_bypassed", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_analyze = _load_analyze_module()
OPEN_ENDED_Q = _analyze.OPEN_ENDED_Q
RELATION_Q = _analyze.RELATION_Q
TEMPORAL_Q = _analyze.TEMPORAL_Q
is_groundable_prop = _analyze.is_groundable_prop


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--details-csv", type=Path, default=DEFAULT_DETAILS)
    p.add_argument("--entries", type=Path, default=DEFAULT_ENTRIES)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument(
        "--reasons",
        default=",".join(sorted(TARGET_REASONS)),
        help="Comma-separated category_reason values to include",
    )
    p.add_argument("--puls-model", default="gpt-4o", help="Match Sub #5B production PULS model")
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--limit", type=int, default=None, help="Smoke: process first N rows only")
    p.add_argument("--sleep-seconds", type=float, default=0.25)
    p.add_argument("--resume", action="store_true", help="Skip QIDs already in results.jsonl")
    return p.parse_args()


def load_env(path: str) -> None:
    from nsvqa.utils.env_loader import load_env_file

    load_env_file(path)


def puls_structural_reason(question: str, props: list[str], spec: str) -> str | None:
    """Return Diagnostic-2-style failure reason, or None if structurally OK for PULS."""
    spec = (spec or "").strip()
    if not props or not spec:
        return "empty_puls_output"

    if not any(is_groundable_prop(p) for p in props):
        return "no_groundable_propositions"

    missing = [p for p in props if p not in spec.replace('"', "")]
    if len(missing) == len(props):
        return "propositions_not_in_spec"

    if OPEN_ENDED_Q.search(question) and TEMPORAL_Q.search(question):
        if " U " not in spec and len(props) == 1:
            return "operator_collapse_open_ended"

    if RELATION_Q.search(question):
        if len(props) < 2 or (" U " not in spec and "&" not in spec):
            return "relation_not_in_spec"

    return None


def load_target_rows(details_path: Path, reasons: set[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with details_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("category_reason") in reasons:
                rows.append(row)
    rows.sort(key=lambda r: int(r["question_id"]))
    return rows


def load_entries_by_qid(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for entry in data:
        qid = str(entry.get("metadata", {}).get("question_id") or entry.get("question_id"))
        out[qid] = entry
    return out


def load_done_qids(jsonl_path: Path) -> set[str]:
    if not jsonl_path.is_file():
        return set()
    done: set[str] = set()
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(str(json.loads(line)["question_id"]))
    return done


def run_puls(question: str, model: str, history_dir: Path) -> dict[str, Any]:
    os.environ["NSVQA_LLM_HISTORY_DIR"] = str(history_dir)
    from nsvqa.puls.puls import PULS

    t0 = time.time()
    out = PULS(question, model=model)
    return {
        "proposition": out.get("proposition") or [],
        "specification": out.get("specification") or "",
        "seconds": round(time.time() - t0, 2),
        "api_cost_usd": out.get("api_cost_usd"),
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    baseline = Counter(r["baseline_reason"] for r in records)
    v2_fail = Counter(r["v2_reason"] for r in records if r["v2_reason"])
    rescued = [r for r in records if r["rescued"]]
    still_fail = [r for r in records if not r["rescued"]]
    by_bucket: dict[str, dict[str, int]] = {}
    for bucket in ("empty_puls_output", "operator_collapse_open_ended"):
        sub = [r for r in records if r["baseline_reason"] == bucket]
        by_bucket[bucket] = {
            "n": len(sub),
            "rescued": sum(1 for r in sub if r["rescued"]),
            "still_fail": sum(1 for r in sub if not r["rescued"]),
        }
    return {
        "n": n,
        "baseline_reasons": dict(baseline),
        "v2_failure_reasons": dict(v2_fail),
        "rescued_n": len(rescued),
        "still_fail_n": len(still_fail),
        "rescued_pct": round(len(rescued) / n * 100, 1) if n else 0,
        "by_baseline_bucket": by_bucket,
        "total_api_usd": round(
            sum(float(r.get("api_cost_usd") or 0) for r in records), 4
        ),
    }


def write_report(out_dir: Path, summary: dict[str, Any], model: str) -> None:
    repo_report = REPO_ROOT / "diagnostics/puls_v2_prep/validation_148/report.md"
    repo_report.parent.mkdir(parents=True, exist_ok=True)
    bb = summary["by_baseline_bucket"]
    lines = [
        "# PULS v2 validation — 148-row target slice",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"PULS model: `{model}` · Prompt: current `nsvqa/puls/prompts.py` (Examples 13–16)",
        "",
        "## Target slice",
        "",
        "- **94** `empty_puls_output` + **54** `operator_collapse_open_ended`",
        "- Source: `diagnostics/puls_unknown_analysis/details.csv`",
        f"- Full per-row log: `{out_dir.resolve()}/results.jsonl`",
        "",
        "## Headline",
        "",
        f"| Metric | Count |",
        f"| --- | ---: |",
        f"| Total | {summary['n']} |",
        f"| **Structurally rescued** (v2 passes PULS gates) | **{summary['rescued_n']}** ({summary['rescued_pct']}%) |",
        f"| Still failing structural gate | {summary['still_fail_n']} |",
        f"| Est. API spend | ${summary['total_api_usd']:.4f} |",
        "",
        "### By baseline bucket",
        "",
        "| Baseline reason | n | Rescued | Still fail |",
        "| --- | ---: | ---: | ---: |",
    ]
    for bucket, stats in bb.items():
        lines.append(
            f"| `{bucket}` | {stats['n']} | {stats['rescued']} | {stats['still_fail']} |"
        )
    lines.extend(
        [
            "",
            "### v2 failure reasons (remaining)",
            "",
            "```json",
            json.dumps(summary["v2_failure_reasons"], indent=2),
            "```",
            "",
            "## Notes",
            "",
            "- **Rescued** = baseline had empty/collapse; v2 returns non-empty spec passing "
            "`relation_not_in_spec` / `operator_collapse` / `empty` gates (PULS-only).",
            "- Does **not** re-run NSVS or measure val accuracy.",
            "- Re-run: `python3 scripts/validate_puls_v2_target_slice.py --resume`",
        ]
    )
    text = "\n".join(lines) + "\n"
    (out_dir / "report.md").write_text(text, encoding="utf-8")
    repo_report.write_text(text.replace(str(out_dir), str(out_dir)), encoding="utf-8")


def main() -> int:
    args = parse_args()
    reasons = {r.strip() for r in args.reasons.split(",") if r.strip()}
    load_env(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        print("[validate-puls-v2] ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    target = load_target_rows(args.details_csv, reasons)
    if args.limit is not None:
        target = target[: args.limit]

    entries_by_qid = load_entries_by_qid(args.entries) if args.entries.is_file() else {}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = args.out_dir / "llm_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    os.environ["NSVQA_LLM_HISTORY_DIR"] = str(history_dir)
    jsonl_path = args.out_dir / "results.jsonl"
    done = load_done_qids(jsonl_path) if args.resume else set()

    print(f"[validate-puls-v2] target rows={len(target)} model={args.puls_model}")
    print(f"[validate-puls-v2] out={args.out_dir} resume={args.resume} already_done={len(done)}")

    records: list[dict[str, Any]] = []
    if done and jsonl_path.is_file():
        with jsonl_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    mode = "a" if args.resume and jsonl_path.exists() else "w"
    with jsonl_path.open(mode, encoding="utf-8") as out_f:
        for i, row in enumerate(target, 1):
            qid = str(row["question_id"])
            if qid in done:
                continue
            question = row["question_text"]
            baseline_reason = row["category_reason"]
            entry = entries_by_qid.get(qid, {})
            baseline_puls = entry.get("puls", {})
            baseline_props = baseline_puls.get("proposition") or []
            baseline_spec = baseline_puls.get("specification") or ""

            try:
                v2 = run_puls(question, args.puls_model, history_dir)
            except Exception as e:
                v2 = {
                    "proposition": [],
                    "specification": "",
                    "seconds": None,
                    "api_cost_usd": None,
                    "error": repr(e),
                }

            v2_props = v2.get("proposition") or []
            v2_spec = v2.get("specification") or ""
            v2_reason = puls_structural_reason(question, v2_props, v2_spec)
            if v2.get("error"):
                v2_reason = v2_reason or "puls_api_error"

            rec = {
                "question_id": qid,
                "baseline_reason": baseline_reason,
                "baseline_n_props": len(baseline_props),
                "baseline_spec": baseline_spec,
                "v2_n_props": len(v2_props),
                "v2_propositions": v2_props,
                "v2_specification": v2_spec,
                "v2_reason": v2_reason,
                "rescued": baseline_reason in TARGET_REASONS and v2_reason is None,
                "api_cost_usd": v2.get("api_cost_usd"),
                "seconds": v2.get("seconds"),
                "error": v2.get("error"),
                "question_mode": row.get("question_mode"),
                "source_dataset": row.get("source_dataset"),
            }
            out_f.write(json.dumps(rec, ensure_ascii=True) + "\n")
            out_f.flush()
            records.append(rec)
            status = "RESCUED" if rec["rescued"] else (v2_reason or "ok")
            print(
                f"[{i}/{len(target)}] qid={qid} baseline={baseline_reason} → v2={status} "
                f"props={len(v2_props)} spec_len={len(v2_spec)}"
            )
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)

    # Merge full record set for summary if resume appended only partial
    all_records = records
    if args.resume or len(all_records) != len(target):
        all_records = []
        with jsonl_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_records.append(json.loads(line))

    summary = summarize(all_records)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    write_report(args.out_dir, summary, args.puls_model)
    print(f"[validate-puls-v2] rescued {summary['rescued_n']}/{summary['n']} "
          f"({summary['rescued_pct']}%)")
    print(f"[validate-puls-v2] wrote {args.out_dir}/report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
