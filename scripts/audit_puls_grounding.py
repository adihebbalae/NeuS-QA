#!/usr/bin/env python3
"""Audit whether PULS propositions are visually groundable in one frame."""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from openai import OpenAI


DEFAULT_BASELINE_PATH = Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/per_entry")
DEFAULT_NSVS_PATH = Path("/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2/per_entry")
DEFAULT_OUTPUT_DIR = Path("/mnt/Data/ah66742/timelogic/outputs/puls_grounding_audit")

FALLBACK_PATHS = {
    "baseline_cpu_v01": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/entries.json"),
    "nsvs_sub2": Path("/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2/merged/entries.json"),
}

PROMPT_TEMPLATE = (
    "Is this proposition assessable as a binary Yes/No on a single\n"
    "static video frame by a vision-language model? Score:\n"
    "1 = clearly yes (concrete visual state like 'person sits')\n"
    "2 = ambiguous (needs context, e.g., 'person looks tired')\n"
    "3 = no (requires temporal continuity, e.g., 'person is leaving')\n"
    "Proposition: {proposition}\n"
    "Return: <score>|<one-sentence justification>"
)

CSV_FIELDS = [
    "run",
    "question_id",
    "prop_index",
    "proposition",
    "score",
    "justification",
    "raw_response",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH))
    p.add_argument("--nsvs-path", default=str(DEFAULT_NSVS_PATH))
    p.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    p.add_argument("--sample-size", type=int, default=200, help="Number of PULS outputs to sample.")
    p.add_argument("--seed", type=int, default=20260521)
    p.add_argument("--model", default="gpt-5.2")
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--max-output-tokens", type=int, default=256)
    p.add_argument("--sleep-seconds", type=float, default=0.0)
    p.add_argument("--overwrite", action="store_true", help="Ignore existing CSV checkpoint.")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_env_file(path: str) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from nsvqa.utils.env_loader import load_env_file as _load_env_file

    _load_env_file(path)


def _fallback_for(label: str, requested: Path) -> Path | None:
    if requested.exists():
        return requested
    fallback = FALLBACK_PATHS.get(label)
    if fallback and fallback.exists():
        print(f"[audit] {requested} not found; using fallback {fallback}")
        return fallback
    return None


def _entry_from_payload(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict) and isinstance(payload.get("entry"), dict):
        return payload["entry"]
    if isinstance(payload, dict):
        return payload
    return None


def iter_entries(label: str, requested_path: str) -> list[dict[str, Any]]:
    path = _fallback_for(label, Path(requested_path))
    if path is None:
        raise FileNotFoundError(f"No usable artifact found for {label}: {requested_path}")

    entries: list[dict[str, Any]] = []
    if path.is_file():
        payload = load_json(path)
        if isinstance(payload, list):
            entries = [entry for item in payload if (entry := _entry_from_payload(item))]
        else:
            entry = _entry_from_payload(payload)
            entries = [entry] if entry else []
    elif path.is_dir():
        json_paths = sorted(path.rglob("*.json"))
        for json_path in json_paths:
            payload = load_json(json_path)
            if isinstance(payload, list):
                entries.extend(entry for item in payload if (entry := _entry_from_payload(item)))
            else:
                entry = _entry_from_payload(payload)
                if entry:
                    entries.append(entry)
    else:
        raise FileNotFoundError(f"Path is neither file nor directory: {path}")

    return [entry for entry in entries if extract_propositions(entry)]


def extract_propositions(entry: dict[str, Any]) -> list[str]:
    propositions = entry.get("puls", {}).get("proposition")
    if isinstance(propositions, list):
        return [str(p).strip() for p in propositions if str(p).strip()]
    if isinstance(propositions, str) and propositions.strip():
        return [propositions.strip()]
    return []


def question_id(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    return str(metadata.get("question_id") or entry.get("question_id") or metadata.get("id") or "")


def sample_outputs(runs: dict[str, list[dict[str, Any]]], sample_size: int, seed: int) -> list[dict[str, Any]]:
    population: list[dict[str, Any]] = []
    for label, entries in runs.items():
        for entry in entries:
            population.append({"run": label, "entry": entry})
    if sample_size > len(population):
        raise ValueError(f"sample-size={sample_size} exceeds available PULS outputs ({len(population)})")
    rng = random.Random(seed)
    return rng.sample(population, sample_size)


def build_prop_rows(sampled: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in sampled:
        entry = item["entry"]
        for idx, proposition in enumerate(extract_propositions(entry)):
            rows.append(
                {
                    "run": item["run"],
                    "question_id": question_id(entry),
                    "prop_index": str(idx),
                    "proposition": proposition,
                    "score": "",
                    "justification": "",
                    "raw_response": "",
                }
            )
    return rows


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["run"], row["question_id"], row["prop_index"], row["proposition"])


def load_completed(csv_path: Path) -> dict[tuple[str, str, str, str], dict[str, str]]:
    if not csv_path.exists():
        return {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {row_key(row): row for row in reader if row.get("score")}


def _is_reasoning_model(model: str) -> bool:
    return model.startswith(("gpt-5", "o1", "o3", "o4"))


def completion_kwargs(model: str, max_output_tokens: int) -> dict[str, Any]:
    if _is_reasoning_model(model):
        return {"max_completion_tokens": max_output_tokens, "reasoning_effort": "low"}
    return {"max_tokens": max_output_tokens, "temperature": 0.0}


def parse_judgment(raw: str | None) -> tuple[str, str]:
    text = (raw or "").strip()
    match = re.match(r"^\s*([123])\s*\|\s*(.+?)\s*$", text, flags=re.DOTALL)
    if match:
        return match.group(1), " ".join(match.group(2).split())
    match = re.search(r"\b([123])\b", text)
    if match:
        cleaned = re.sub(r"^\s*(score\s*[:=]?\s*)?[123]\s*(\||-|:)?\s*", "", text, flags=re.IGNORECASE)
        return match.group(1), " ".join(cleaned.split())
    return "", text


def judge_proposition(
    client: OpenAI,
    model: str,
    proposition: str,
    max_output_tokens: int,
    attempts: int = 3,
) -> tuple[str, str, str]:
    prompt = PROMPT_TEMPLATE.format(proposition=proposition)
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You classify whether atomic video propositions are visible as single-frame "
                            "binary visual predicates. Reply only as '<score>|<one-sentence justification>'."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                store=False,
                **completion_kwargs(model, max_output_tokens),
            )
            raw = resp.choices[0].message.content or ""
            score, justification = parse_judgment(raw)
            if score in {"1", "2", "3"}:
                return score, justification, raw
            last_error = f"unparseable response: {raw!r}"
        except Exception as exc:  # noqa: BLE001 - keep long audit resilient to transient API issues.
            last_error = repr(exc)
        if attempt < attempts:
            time.sleep(2**attempt)
    return "", last_error, last_error


def write_csv(csv_path: Path, rows: list[dict[str, str]]) -> None:
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(summary_path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    judged = [row for row in rows if row["score"] in {"1", "2", "3"}]
    counts = Counter(row["score"] for row in judged)
    total = len(judged)
    parse_errors = sum(1 for row in rows if not row["score"])
    lines = [
        "PULS Grounding Audit",
        "",
        f"model: {args.model}",
        f"seed: {args.seed}",
        f"sampled_puls_outputs: {args.sample_size}",
        f"total_propositions: {len(rows)}",
        f"judged_propositions: {total}",
        f"parse_or_api_errors: {parse_errors}",
        "",
        "Score buckets:",
    ]
    for score in ("1", "2", "3"):
        pct = (counts[score] / total * 100.0) if total else 0.0
        lines.append(f"{score}: {counts[score]} ({pct:.1f}%)")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "puls_grounding_audit.csv"
    summary_path = output_dir / "summary.txt"

    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(f"OPENAI_API_KEY not set and not found in {args.env_file}")

    runs = {
        "baseline_cpu_v01": iter_entries("baseline_cpu_v01", args.baseline_path),
        "nsvs_sub2": iter_entries("nsvs_sub2", args.nsvs_path),
    }
    print("[audit] loaded entries with PULS:", {label: len(entries) for label, entries in runs.items()})

    sampled = sample_outputs(runs, args.sample_size, args.seed)
    rows = build_prop_rows(sampled)

    completed = {} if args.overwrite else load_completed(csv_path)
    for idx, row in enumerate(rows):
        if row_key(row) in completed:
            rows[idx] = completed[row_key(row)]

    client = OpenAI()
    for i, row in enumerate(rows, start=1):
        if row["score"]:
            continue
        score, justification, raw = judge_proposition(
            client=client,
            model=args.model,
            proposition=row["proposition"],
            max_output_tokens=args.max_output_tokens,
        )
        row["score"] = score
        row["justification"] = justification
        row["raw_response"] = raw
        write_csv(csv_path, rows)
        print(f"[audit] {i}/{len(rows)} score={score or 'ERR'} proposition={row['proposition']}")
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    write_csv(csv_path, rows)
    write_summary(summary_path, rows, args)
    print(f"[audit] wrote {csv_path}")
    print(f"[audit] wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
