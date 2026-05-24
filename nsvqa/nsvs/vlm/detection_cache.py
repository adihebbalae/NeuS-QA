"""Disk cache for NSVS proposition-detection calls.

Cache key: (backend, window_frames_hash, action_label, prompt_version)
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import numpy as np

from nsvqa.vqa.answer_timelogic import DEFAULT_JPEG_QUALITY, encode_jpeg

NSVS_DETECT_PROMPT_VERSION = "nsvs_detect_cot_v1"


def hash_window_frames(seq_of_frames: list[np.ndarray], quality: int = DEFAULT_JPEG_QUALITY) -> str:
    """SHA-256 over JPEG bytes of each frame in order."""
    h = hashlib.sha256()
    for frame in seq_of_frames:
        encoded = encode_jpeg(frame, quality=quality)
        if encoded is None:
            h.update(b"\x00")
        else:
            h.update(encoded.encode("utf-8"))
    return h.hexdigest()


def cache_key(
    backend: str,
    window_frames_hash: str,
    action_label: str,
    prompt_version: str = NSVS_DETECT_PROMPT_VERSION,
) -> str:
    payload = f"{backend}\0{window_frames_hash}\0{action_label}\0{prompt_version}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DetectionCache:
    """JSON file cache keyed by hash of (backend, frames, action, prompt_version)."""

    def __init__(self, root_dir: str, backend: str) -> None:
        self.root_dir = os.path.join(root_dir, backend)
        os.makedirs(self.root_dir, exist_ok=True)
        self.backend = backend

    def _path(self, key: str) -> str:
        return os.path.join(self.root_dir, f"{key}.json")

    def get(
        self,
        window_frames_hash: str,
        action_label: str,
        prompt_version: str = NSVS_DETECT_PROMPT_VERSION,
    ) -> dict[str, Any] | None:
        key = cache_key(self.backend, window_frames_hash, action_label, prompt_version)
        path = self._path(key)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def put(
        self,
        window_frames_hash: str,
        action_label: str,
        record: dict[str, Any],
        prompt_version: str = NSVS_DETECT_PROMPT_VERSION,
    ) -> str:
        key = cache_key(self.backend, window_frames_hash, action_label, prompt_version)
        record = dict(record)
        record.setdefault("cache_key", key)
        record.setdefault("backend", self.backend)
        record.setdefault("window_frames_hash", window_frames_hash)
        record.setdefault("action_label", action_label)
        record.setdefault("prompt_version", prompt_version)
        path = self._path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=True)
        return key
