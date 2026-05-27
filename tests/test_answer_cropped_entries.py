"""Tests for scripts/answer_cropped_entries.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from answer_cropped_entries import prepare_entries  # noqa: E402


def _entry(*, qid: str, video_path: str, cropped_path: str, foi: list) -> dict:
    return {
        "metadata": {"question_id": qid},
        "paths": {"video_path": video_path, "cropped_path": cropped_path},
        "frames_of_interest": foi,
    }


def test_prepare_entries_foi_cleared_only_on_real_crop():
    real_crop = _entry(
        qid="real",
        video_path="/src/full.mp4",
        cropped_path="/crop/clip.mp4",
        foi=[100, 200],
    )
    fallback = _entry(
        qid="fallback",
        video_path="/src/full.mp4",
        cropped_path="/src/full.mp4",
        foi=[-1],
    )
    prepared = prepare_entries([real_crop, fallback], allow_crop_fallback=True)

    by_qid = {e["metadata"]["question_id"]: e for e in prepared}
    assert by_qid["real"]["frames_of_interest"] is None
    assert by_qid["real"]["paths"]["video_path"] == "/crop/clip.mp4"
    assert by_qid["fallback"]["frames_of_interest"] == [-1]
    assert by_qid["fallback"]["paths"]["video_path"] == "/src/full.mp4"
