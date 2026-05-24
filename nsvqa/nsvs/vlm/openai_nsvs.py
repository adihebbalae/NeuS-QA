"""OpenAI gpt-5.2 NSVS proposition detector with CoT logging."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from openai import OpenAI

from nsvqa.nsvs.vlm.detection_cache import (
    NSVS_DETECT_PROMPT_VERSION,
    DetectionCache,
    hash_window_frames,
)
from nsvqa.nsvs.vlm.obj import DetectedObject
from nsvqa.utils.api_cost import RunMeter
from nsvqa.utils.sigmoid import calibrate_sigmoid
from nsvqa.vqa.answer_timelogic import (
    DEFAULT_IMAGE_DETAIL,
    _extract_message_text_from_response,
    _extract_reasoning_summary_from_response,
    _usage_for_cost,
    encode_jpeg,
    vision_completion,
)

DEFAULT_MODEL = "gpt-5.2"
DEFAULT_REASONING_EFFORT = "medium"


def _build_detect_prompt(scene_description: str) -> tuple[str, str]:
    if "subtitle" in scene_description:
        label = scene_description.replace("subtitle_", "").replace("_", " ")
        question = (
            f"Does the video have the subtitle '{label}' present in the sequence of images?"
        )
    else:
        label = scene_description.replace("_", " ")
        question = f"Is there a '{label}' present in the sequence of images?"

    system = (
        "You are a precise video proposition detector for temporal-logic verification. "
        "You receive a short sequence of video frames (Frame1, Frame2, ...). "
        "Decide whether the described event or object is present in ANY frame of the sequence.\n\n"
        "Respond in two parts:\n"
        "1. REASONING: 1-3 sentences citing which frame number(s) support your judgment.\n"
        "2. Final line exactly: ANSWER: Yes  OR  ANSWER: No\n\n"
        "Do not output anything after the ANSWER line."
    )
    user_text = question
    return system, user_text


def _parse_yes_no(raw: str | None) -> tuple[bool, str]:
    if not raw:
        return False, ""
    text = raw.strip()
    m = re.search(r"ANSWER:\s*(Yes|No)\b", text, flags=re.IGNORECASE)
    if m:
        ans = m.group(1).lower()
        return ans == "yes", text
    lower = text.lower()
    if "answer: yes" in lower or lower.endswith("yes"):
        return True, text
    if "answer: no" in lower or lower.endswith("no"):
        return False, text
    return "yes" in lower.split()[-3:], text


class OpenAINsvsVLM:
    """gpt-5.2 vision backend for NSVS proposition detection."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        cache: DetectionCache | None = None,
        meter: RunMeter | None = None,
        image_detail: str = DEFAULT_IMAGE_DETAIL,
        client: OpenAI | None = None,
    ) -> None:
        self.model_name = model
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.cache = cache
        self.meter = meter
        self.image_detail = image_detail
        self.client = client or OpenAI()
        self.detection_log: list[dict[str, Any]] = []
        self.backend = "gpt5.2"

    def _vision_call_with_effort(
        self,
        system_prompt: str,
        user_content: list,
    ) -> dict[str, Any]:
        """Responses API call with configurable reasoning effort."""
        from nsvqa.vqa.answer_timelogic import _is_reasoning_model, _user_content_for_responses

        if _is_reasoning_model(self.model):
            resp = self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=[{"role": "user", "content": _user_content_for_responses(user_content)}],
                reasoning={"effort": self.reasoning_effort, "summary": "auto"},
                max_output_tokens=512,
                store=False,
            )
            raw = _extract_message_text_from_response(resp)
            reasoning_summary = _extract_reasoning_summary_from_response(resp)
            return {
                "raw": raw,
                "reasoning_summary": reasoning_summary,
                "usage": _usage_for_cost(getattr(resp, "usage", None)),
            }

        return vision_completion(
            self.client,
            self.model,
            system_prompt,
            user_content,
            max_output_tokens=512,
            capture_reasoning_summary=True,
        )

    def detect(
        self,
        seq_of_frames: list[np.ndarray],
        scene_description: str,
        threshold: float,
        *,
        window_idx: int | None = None,
    ) -> DetectedObject:
        frames_hash = hash_window_frames(seq_of_frames)
        cache_hit = False
        reasoning = ""
        reasoning_summary = None
        raw = None
        usage = None

        if self.cache is not None:
            cached = self.cache.get(frames_hash, scene_description, NSVS_DETECT_PROMPT_VERSION)
            if cached is not None:
                cache_hit = True
                detected = bool(cached.get("is_detected"))
                confidence = float(cached.get("confidence", 0.0))
                probability = float(cached.get("probability", 0.0))
                reasoning = cached.get("reasoning") or cached.get("raw") or ""
                reasoning_summary = cached.get("reasoning_summary")
                raw = cached.get("raw")
                obj = DetectedObject(
                    name=scene_description,
                    is_detected=detected,
                    confidence=round(confidence, 3),
                    probability=round(probability, 3),
                    model_name=self.model,
                )
                self._log_detection(
                    window_idx=window_idx,
                    scene_description=scene_description,
                    obj=obj,
                    reasoning=reasoning,
                    reasoning_summary=reasoning_summary,
                    raw=raw,
                    cache_hit=True,
                    frames_hash=frames_hash,
                )
                return obj

        system, user_text = _build_detect_prompt(scene_description)
        user_content: list[dict[str, Any]] = [{"type": "text", "text": user_text}]
        for i, frame in enumerate(seq_of_frames, start=1):
            encoded = encode_jpeg(frame)
            if encoded:
                user_content.append(
                    {
                        "type": "text",
                        "text": f"Frame{i}:",
                    }
                )
                user_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": self.image_detail},
                    }
                )

        completion = self._vision_call_with_effort(system, user_content)
        raw = completion.get("raw")
        reasoning_summary = completion.get("reasoning_summary")
        usage = completion.get("usage")
        detected, reasoning = _parse_yes_no(raw)
        confidence = 1.0 if detected else 0.0
        probability = calibrate_sigmoid(confidence, false_threshold=threshold)

        if self.meter is not None:
            self.meter.add_vision(
                "nsvs_detect",
                self.model,
                usage,
                num_frames=len(seq_of_frames),
                image_detail=self.image_detail,
            )

        obj = DetectedObject(
            name=scene_description,
            is_detected=detected,
            confidence=round(confidence, 3),
            probability=round(probability, 3),
            model_name=self.model,
        )

        record = {
            "is_detected": detected,
            "confidence": obj.confidence,
            "probability": obj.probability,
            "raw": raw,
            "reasoning": reasoning,
            "reasoning_summary": reasoning_summary,
            "usage": usage,
        }
        if self.cache is not None:
            self.cache.put(frames_hash, scene_description, record, NSVS_DETECT_PROMPT_VERSION)

        self._log_detection(
            window_idx=window_idx,
            scene_description=scene_description,
            obj=obj,
            reasoning=reasoning,
            reasoning_summary=reasoning_summary,
            raw=raw,
            cache_hit=cache_hit,
            frames_hash=frames_hash,
        )
        return obj

    def _log_detection(
        self,
        *,
        window_idx: int | None,
        scene_description: str,
        obj: DetectedObject,
        reasoning: str,
        reasoning_summary: str | None,
        raw: str | None,
        cache_hit: bool,
        frames_hash: str,
    ) -> None:
        self.detection_log.append(
            {
                "window_idx": window_idx,
                "proposition": scene_description,
                "is_detected": obj.is_detected,
                "confidence": obj.confidence,
                "probability": obj.probability,
                "backend": self.backend,
                "model": self.model,
                "reasoning": reasoning,
                "reasoning_summary": reasoning_summary,
                "raw": raw,
                "cache_hit": cache_hit,
                "window_frames_hash": frames_hash,
                "prompt_version": NSVS_DETECT_PROMPT_VERSION,
            }
        )
