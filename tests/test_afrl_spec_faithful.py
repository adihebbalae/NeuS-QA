"""Tests for PULS spec_faithful heuristics in scripts/afrl/_lib.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts" / "afrl"))

from _lib import spec_faithful  # noqa: E402


def test_co_occur_requires_and_not_u():
    q = "Is it true that person holding a bag always co-occur with sitting at a table ?"
    ok, _ = spec_faithful(
        "unknown",
        q,
        '("person_holds_a_bag" & "person_sits_at_a_table")',
        ["person_holds_a_bag", "person_sits_at_a_table"],
    )
    assert ok
    bad, reason = spec_faithful(
        "unknown",
        q,
        '"person_holds_a_bag" U "person_sits_at_a_table"',
        ["person_holds_a_bag", "person_sits_at_a_table"],
    )
    assert not bad
    assert "co_occur" in reason


def test_always_before_chain_not_plain_u():
    q = "Which action always occurs before A which in turn always occurs before C ?"
    ok, _ = spec_faithful(
        "always_before",
        q,
        '"a" U "b" U "c"',
        ["a", "b", "c"],
    )
    assert ok
    bad, reason = spec_faithful(
        "always_before",
        q,
        '"a" U "b"',
        ["a", "b", "c"],
    )
    assert not bad
    assert "plain_u" in reason


def test_empty_spec_not_faithful():
    ok, reason = spec_faithful("until", "What until X ?", "", [])
    assert not ok
    assert reason == "empty_spec_or_props"
