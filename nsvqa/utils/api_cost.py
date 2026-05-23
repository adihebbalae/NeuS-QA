"""Estimated OpenAI API spend tracking (not billing-grade).

Uses response.usage when available; otherwise heuristics calibrated on TimeLogic
runs. Prices are USD per 1M tokens — see .cursor/rules/workflow.md.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any


# input_usd_per_1m, output_usd_per_1m
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-5.2": (1.75, 14.0),
    "gpt-5": (1.75, 14.0),
    "gpt-4o": (2.50, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o-2024-08-06": (2.50, 10.0),
    "o3": (2.0, 8.0),
}

# Fallback when usage is missing (USD per call).
HEURISTIC_TEXT_USD: dict[str, float] = {
    "gpt-5.2": 0.003,
    "gpt-5": 0.003,
    "gpt-4o": 0.0045,
    "gpt-4o-mini": 0.0003,
}

HEURISTIC_VISION_USD: dict[str, float] = {
    "gpt-5.2": 0.007,
    "gpt-5": 0.007,
    "gpt-4o": 0.006,
    "gpt-4o-mini": 0.001,
}

# Extra per frame above 8 (low detail), approximate.
VISION_FRAME_SURCHARGE_USD = 0.00035


def normalize_model(model: str) -> str:
    return (model or "").strip().lower()


def pricing_for(model: str) -> tuple[float, float]:
    key = normalize_model(model)
    if key in MODEL_PRICING:
        return MODEL_PRICING[key]
    for prefix, rates in MODEL_PRICING.items():
        if key.startswith(prefix):
            return rates
    return MODEL_PRICING["gpt-4o-mini"]


def cost_from_tokens(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    in_rate, out_rate = pricing_for(model)
    return (prompt_tokens * in_rate + completion_tokens * out_rate) / 1_000_000.0


def cost_from_usage(model: str, usage: Any) -> float | None:
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_tokens", None)
    completion = getattr(usage, "completion_tokens", None)
    if prompt is None and isinstance(usage, dict):
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
    if prompt is None or completion is None:
        return None
    return cost_from_tokens(model, int(prompt), int(completion))


def estimate_text_call(model: str) -> float:
    key = normalize_model(model)
    for prefix, cost in HEURISTIC_TEXT_USD.items():
        if key.startswith(prefix):
            return cost
    return HEURISTIC_TEXT_USD["gpt-4o-mini"]


def estimate_vision_call(model: str, num_frames: int = 8, image_detail: str = "low") -> float:
    key = normalize_model(model)
    base = HEURISTIC_VISION_USD.get("gpt-4o-mini")
    for prefix, cost in HEURISTIC_VISION_USD.items():
        if key.startswith(prefix):
            base = cost
            break
    extra_frames = max(0, int(num_frames) - 8)
    detail_mult = 1.5 if image_detail == "high" else 1.0
    return (base + extra_frames * VISION_FRAME_SURCHARGE_USD) * detail_mult


def usage_dict(usage: Any) -> dict[str, int] | None:
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_tokens", None)
    completion = getattr(usage, "completion_tokens", None)
    total = getattr(usage, "total_tokens", None)
    if prompt is None and isinstance(usage, dict):
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
        total = usage.get("total_tokens")
    if prompt is None:
        return None
    out = {"prompt_tokens": int(prompt), "completion_tokens": int(completion or 0)}
    if total is not None:
        out["total_tokens"] = int(total)
    return out


class RunMeter:
    """Accumulates estimated spend for one pipeline run."""

    def __init__(self, output_dir: str, label: str = "") -> None:
        self.output_dir = output_dir
        self.label = label or os.path.basename(output_dir.rstrip("/"))
        self.total_usd = 0.0
        self.calls = 0
        self.by_stage: Counter[str] = Counter()
        self.by_model: Counter[str] = Counter()
        self.metered_calls = 0
        self.heuristic_calls = 0

    def add(
        self,
        stage: str,
        cost_usd: float,
        *,
        model: str = "",
        source: str = "metered",
    ) -> None:
        cost = float(cost_usd or 0.0)
        self.total_usd += cost
        self.calls += 1
        self.by_stage[stage] += cost
        if model:
            self.by_model[model] += cost
        if source == "metered":
            self.metered_calls += 1
        else:
            self.heuristic_calls += 1

    def add_text(self, stage: str, model: str, usage: Any = None) -> float:
        cost = cost_from_usage(model, usage)
        source = "metered"
        if cost is None:
            cost = estimate_text_call(model)
            source = "heuristic"
        self.add(stage, cost, model=model, source=source)
        return cost

    def add_vision(
        self,
        stage: str,
        model: str,
        usage: Any = None,
        *,
        num_frames: int = 8,
        image_detail: str = "low",
    ) -> float:
        cost = cost_from_usage(model, usage)
        source = "metered"
        if cost is None:
            cost = estimate_vision_call(model, num_frames=num_frames, image_detail=image_detail)
            source = "heuristic"
        self.add(stage, cost, model=model, source=source)
        return cost

    def summary(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "label": self.label,
            "output_dir": self.output_dir,
            "estimated_total_usd": round(self.total_usd, 4),
            "calls": self.calls,
            "metered_calls": self.metered_calls,
            "heuristic_calls": self.heuristic_calls,
            "by_stage_usd": {k: round(v, 4) for k, v in sorted(self.by_stage.items())},
            "by_model_usd": {k: round(v, 4) for k, v in sorted(self.by_model.items())},
            "note": "Estimate only — verify against OpenAI usage dashboard.",
        }
        if extra:
            payload.update(extra)
        return payload

    def log_line(self, prefix: str = "") -> str:
        p = f"{prefix} " if prefix else ""
        return (
            f"{p}[api-cost] estimated ${self.total_usd:.2f} "
            f"({self.calls} calls, {self.metered_calls} metered / {self.heuristic_calls} heuristic)"
        )

    def write(self, extra: dict[str, Any] | None = None) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        summary = self.summary(extra)
        json_path = os.path.join(self.output_dir, "api_cost.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        log_path = os.path.join(self.output_dir, "api_cost.log")
        line = self.log_line() + "\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{summary['generated_at']}  {line}")
        return json_path
