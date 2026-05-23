#!/usr/bin/env python3
"""Estimate OpenAI API spend for TimeLogic output runs (retroactive + ledger).

Reads metered api_cost.json when present; otherwise heuristics from artifacts.
Writes per-run api_cost.json (if missing) and updates the project ledger.

Example:
    python3 scripts/estimate_api_spend.py
    python3 scripts/estimate_api_spend.py --run-dir /mnt/Data/.../baseline_cpu_v01
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nsvqa.utils.api_cost import (  # noqa: E402
    RunMeter,
    estimate_text_call,
    estimate_vision_call,
)

DEFAULT_OUTPUTS = "/mnt/Data/ah66742/timelogic/outputs"
DEFAULT_LEDGER = os.path.join(DEFAULT_OUTPUTS, "api_spend_ledger.json")

KNOWN_RUNS = [
    "baseline_cpu_v01",
    "baseline_cpu_test",
    "nsvs_sub2",
    "nsvs_sub2_v2",
    "sub4_tiebreak_gpt52",
    "sub5b_paper_faithful",
    "sub5b_paper_faithful_3fps",
    "sub5b_paper_faithful_3fps_fix",
    "sub5b_paper_faithful_3fps_fix2",
    "sub5b_paper_faithful_3fps_fix2_aborted_20260521_155924",
    "sub5b_test_3fps",
    "puls_grounding_audit",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outputs-root", default=DEFAULT_OUTPUTS)
    p.add_argument("--run-dir", action="append", default=[], help="Single run dir (repeatable)")
    p.add_argument("--ledger", default=DEFAULT_LEDGER)
    p.add_argument("--write-run-files", action="store_true", default=True)
    p.add_argument("--refresh", action="store_true", help="Recompute even if api_cost.json exists")
    p.add_argument("--quiet", action="store_true")
    return p.parse_args()


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_config(run_dir: str) -> dict[str, Any]:
    path = os.path.join(run_dir, "config.json")
    return load_json(path) if os.path.isfile(path) else {}


def count_entries(run_dir: str) -> int | None:
    for rel in ("merged/entries.json", "entries.json", "diag.json"):
        path = os.path.join(run_dir, rel)
        if os.path.isfile(path):
            rows = load_json(path)
            return len(rows)
    return None


def count_llm_history(run_dir: str) -> int:
    return len(glob.glob(os.path.join(run_dir, "**", "llm_history", "*.json"), recursive=True))


def infer_answer_model(run_dir: str, cfg: dict[str, Any]) -> str:
    downstream = str(cfg.get("downstream_vqa") or cfg.get("answer_model") or "")
    if "gpt" in downstream.lower():
        return downstream
    for path in glob.glob(os.path.join(run_dir, "answers_gpt*")) + glob.glob(
        os.path.join(run_dir, "answers_*")
    ):
        base = os.path.basename(path).lower()
        if "gpt_5_2" in base or "gpt52" in base or "gpt-5.2" in base:
            return "gpt-5.2"
        if "gpt_5" in base:
            return "gpt-5.2"
    return "gpt-5.2"


def infer_num_frames(cfg: dict[str, Any]) -> int:
    for key in ("num_frames", "downstream_vqa_frames"):
        if cfg.get(key) is not None:
            return int(cfg[key])
    return 8


def count_vision_answers(run_dir: str) -> int:
    total = 0
    for partial in glob.glob(os.path.join(run_dir, "**", "submission_partial.json"), recursive=True):
        total = max(total, len(load_json(partial)))
    diag_paths = glob.glob(os.path.join(run_dir, "**", "answers_diag.json"), recursive=True)
    for path in diag_paths:
        total = max(total, len(load_json(path)))
    sub = os.path.join(run_dir, "submission.json")
    if total == 0 and os.path.isfile(sub):
        rows = load_json(sub)
        if rows and "answer_choice" in rows[0]:
            total = len(rows)
    return total


def retroactive_estimate(run_dir: str, refresh: bool = False) -> dict[str, Any]:
    existing = os.path.join(run_dir, "api_cost.json")
    if os.path.isfile(existing) and not refresh:
        data = load_json(existing)
        if not data.get("retroactive"):
            data["source"] = "metered_file"
            return data

    name = os.path.basename(run_dir.rstrip("/"))
    cfg = read_config(run_dir)
    meter = RunMeter(run_dir, label=name)
    source = "retroactive_heuristic"

    puls_model = cfg.get("puls_model") or cfg.get("target_identification_model") or "gpt-5.2"
    answer_model = infer_answer_model(run_dir, cfg)
    num_frames = infer_num_frames(cfg)

    n_entries = count_entries(run_dir)
    llm_hist = count_llm_history(run_dir)
    n_vision = count_vision_answers(run_dir)

    if name == "sub4_tiebreak_gpt52":
        summary_path = os.path.join(run_dir, "summary.json")
        judged = 452
        if os.path.isfile(summary_path):
            judged = int(load_json(summary_path).get("counts", {}).get("judge_sub1", 0)) + int(
                load_json(summary_path).get("counts", {}).get("judge_sub2", 0)
            )
            judged += int(load_json(summary_path).get("counts", {}).get("judge_errors", 0))
        model = load_json(summary_path).get("model", "gpt-5.2") if os.path.isfile(summary_path) else "gpt-5.2"
        for _ in range(judged):
            meter.add("tiebreak_judge", estimate_vision_call(model, num_frames=12), model=model, source=source)
    elif name == "puls_grounding_audit":
        summary_txt = os.path.join(run_dir, "summary.txt")
        judged = 341
        if os.path.isfile(summary_txt):
            for line in open(summary_txt):
                if line.startswith("judged_propositions:"):
                    judged = int(line.split(":", 1)[1].strip())
        model = "gpt-5.2"
        for _ in range(judged):
            meter.add("puls_grounding_judge", estimate_text_call(model) * 0.7, model=model, source=source)
    else:
        if llm_hist:
            # Most runs save one history file per text API call (PULS and/or target_id).
            text_model = puls_model if "gpt" in str(puls_model) else "gpt-4o"
            per_call = estimate_text_call(str(text_model))
            for _ in range(llm_hist):
                stage = "text_api"
                meter.add(stage, per_call, model=str(text_model), source=source)
        elif n_entries:
            text_model = str(puls_model if "gpt" in str(puls_model) else "gpt-4o")
            for _ in range(n_entries * 2):
                meter.add("puls", estimate_text_call(text_model), model=text_model, source=source)

        if n_vision:
            vision_model = str(answer_model)
            for _ in range(n_vision):
                meter.add(
                    "vision_answer",
                    estimate_vision_call(vision_model, num_frames=num_frames),
                    model=vision_model,
                    source=source,
                )

    summary = meter.summary(
        {
            "source": source,
            "retroactive": True,
            "n_entries": n_entries,
            "llm_history_files": llm_hist,
            "vision_answers": n_vision,
            "config": cfg,
        }
    )
    return summary


def discover_run_dirs(outputs_root: str, explicit: list[str]) -> list[str]:
    if explicit:
        return [os.path.abspath(p) for p in explicit]
    dirs = []
    for name in KNOWN_RUNS:
        path = os.path.join(outputs_root, name)
        if os.path.isdir(path):
            dirs.append(path)
    return sorted(set(dirs))


def main() -> int:
    args = parse_args()
    run_dirs = discover_run_dirs(args.outputs_root, args.run_dir)
    rows = []
    total = 0.0

    for run_dir in run_dirs:
        summary = retroactive_estimate(run_dir, refresh=args.refresh)
        if args.write_run_files and (summary.get("source") != "metered_file" or args.refresh):
            json_path = os.path.join(run_dir, "api_cost.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            log_path = os.path.join(run_dir, "api_cost.log")
            line = f"{summary['generated_at']}  [api-cost] estimated ${summary['estimated_total_usd']:.2f} (retroactive)\n"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        usd = float(summary.get("estimated_total_usd") or 0)
        total += usd
        rows.append(
            {
                "run_dir": run_dir,
                "label": summary.get("label") or os.path.basename(run_dir),
                "estimated_usd": round(usd, 2),
                "source": summary.get("source"),
                "calls": summary.get("calls"),
            }
        )
        if not args.quiet:
            print(f"{summary.get('label')}: ${usd:.2f}  ({summary.get('source')})")

    ledger = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "note": "Estimated OpenAI API spend — not billing-grade.",
        "total_estimated_usd": round(total, 2),
        "runs": rows,
    }
    os.makedirs(os.path.dirname(args.ledger), exist_ok=True)
    with open(args.ledger, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    if not args.quiet:
        print(f"\nLedger: {args.ledger}")
        print(f"Total estimated API spend: ${total:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
