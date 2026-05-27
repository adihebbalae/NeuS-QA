"""Tests for build_submission distribution gate."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_submission import (  # noqa: E402
    check_submission_distribution,
    distribution_violations,
)


def test_distribution_violations_detects_skewed_mc():
    dist = {
        "mc": Counter({"A": 800, "B": 200, "C": 100, "D": 100}),
        "bool": Counter({"Yes": 400, "No": 400}),
    }
    v = distribution_violations(dist)
    assert len(v) == 1
    assert v[0][0] == "mc" and v[0][1] == "A"


def test_distribution_violations_ok_balanced():
    dist = {
        "mc": Counter({"A": 300, "B": 300, "C": 300, "D": 300}),
        "bool": Counter({"Yes": 400, "No": 400}),
    }
    assert distribution_violations(dist) == []


def test_check_submission_distribution_aborts_without_force(capsys):
    dist = {
        "mc": Counter({"A": 900, "B": 100, "C": 100, "D": 100}),
        "bool": Counter({"Yes": 400, "No": 400}),
    }
    assert check_submission_distribution(dist, force=False) is False
    out = capsys.readouterr().out
    assert "WARNING" in out
    assert "aborting" in out


def test_check_submission_distribution_allows_force(capsys):
    dist = {
        "mc": Counter({"A": 900, "B": 100, "C": 100, "D": 100}),
        "bool": Counter({"Yes": 400, "No": 400}),
    }
    assert check_submission_distribution(dist, force=True) is True
    assert "--force" in capsys.readouterr().out
