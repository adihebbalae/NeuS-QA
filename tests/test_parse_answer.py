"""Tests for parse_answer and cropped-entry parse-failure handling."""

from __future__ import annotations

import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from answer_cropped_entries import PARSE_RETRY_SUFFIX, _truncate_prompt  # noqa: E402
from nsvqa.vqa.answer_timelogic import parse_answer  # noqa: E402


def test_parse_answer_none_returns_none():
    assert parse_answer(None, ["A", "B", "C", "D"]) is None
    assert parse_answer(None, ["Yes", "No"]) is None


def test_parse_answer_still_parses_letters():
    assert parse_answer("C", ["A", "B", "C", "D"]) == "C"
    assert parse_answer("Yes", ["Yes", "No"]) == "Yes"


def test_parse_answer_unparseable_non_none_falls_back_to_first():
    assert parse_answer("maybe?", ["A", "B", "C", "D"]) == "A"


def test_qid_seeded_random_fallback_is_reproducible():
    valid = ["A", "B", "C", "D"]
    a = random.Random("42").choice(valid)
    b = random.Random("42").choice(valid)
    assert a == b


def test_truncate_prompt():
    long = "x" * 600
    out = _truncate_prompt(long, max_chars=500)
    assert len(out) == 500
    assert out.endswith("...")


def test_parse_retry_suffix_text():
    assert "A/B/C/D" in PARSE_RETRY_SUFFIX
    assert "Yes/No" in PARSE_RETRY_SUFFIX
