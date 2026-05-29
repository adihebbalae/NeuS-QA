"""Tests for Sub7 vs Sub1 stratification script."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from stratify_sub7_vs_sub1 import (  # noqa: E402
    aggregate_buckets,
    build_rows,
    foi_cleanliness,
    run_stratification,
    strat_duration_bucket,
)


def _make_fixture(n: int = 50) -> tuple[dict, dict, list, dict, dict, dict]:
    sub1: dict[str, str] = {}
    sub7: dict[str, str] = {}
    labels: dict[str, str] = {}
    annotations: list[dict] = []
    duration_by_video: dict[str, float] = {}
    entries: dict[str, dict] = {}

    durations = [1.0, 5.0, 30.0, 90.0, 200.0]
    sources = ["agqa", "star", "ct", "bf"]
    operators = ["until", "since", "always_before", "before", "after", "unknown"]
    foi_states = ["clean", "foi_minus1"]

    for i in range(1, n + 1):
        qid = str(i)
        dur = durations[i % len(durations)]
        source = sources[i % len(sources)]
        op = operators[i % len(operators)]
        foi_state = foi_states[i % len(foi_states)]
        video_id = f"{source}_VID{i}.mp4"

        ans1 = "A" if i % 2 else "B"
        ans7 = "A" if i % 3 else "C"
        label = "A" if i % 4 else "No"

        sub1[qid] = ans1
        sub7[qid] = ans7
        labels[qid] = label
        annotations.append(
            {
                "question_id": qid,
                "video_id": video_id,
                "mode": "mc" if i % 2 else "bool",
                "question": f"Did something happen {op} something else?",
            }
        )
        duration_by_video[video_id] = dur
        foi = [10, 50] if foi_state == "clean" else [-1]
        entries[qid] = {
            "metadata": {
                "question_id": qid,
                "video_id": video_id,
                "operator_guess": op,
                "source_dataset": source,
            },
            "frames_of_interest": foi,
        }

    return sub1, sub7, annotations, duration_by_video, entries, labels


def test_strat_duration_bucket_boundaries():
    assert strat_duration_bucket(1.9) == "<2s"
    assert strat_duration_bucket(2.0) == "2-10s"
    assert strat_duration_bucket(9.99) == "2-10s"
    assert strat_duration_bucket(10.0) == "10-60s"
    assert strat_duration_bucket(59.9) == "10-60s"
    assert strat_duration_bucket(60.0) == "60-180s"
    assert strat_duration_bucket(180.0) == ">180s"
    assert strat_duration_bucket(500.0) == ">180s"


def test_foi_cleanliness():
    assert foi_cleanliness({"frames_of_interest": [0, 10]}) == "clean"
    assert foi_cleanliness({"frames_of_interest": [-1]}) == "foi_minus1"
    assert foi_cleanliness(None) == "missing"


def test_bucket_counts_sum_to_n():
    sub1, sub7, annotations, duration_by_video, entries, labels = _make_fixture(50)
    rows, aggregates = run_stratification(
        sub1=sub1,
        sub7=sub7,
        annotations=annotations,
        duration_by_video=duration_by_video,
        entries=entries,
        labels=labels,
    )
    assert len(rows) == 50
    assert sum(row["n"] for row in aggregates) == 50


def test_labeled_accuracy_columns_present():
    sub1, sub7, annotations, duration_by_video, entries, labels = _make_fixture(50)
    rows = build_rows(
        sub1=sub1,
        sub7=sub7,
        annotations=annotations,
        duration_by_video=duration_by_video,
        entries=entries,
        labels=labels,
    )
    aggregates = aggregate_buckets(rows, has_labels=True)
    assert all("acc_delta_sub7_minus_sub1_pct" in row for row in aggregates)
    assert all(row["labeled_n"] == row["n"] for row in aggregates)


def test_each_row_assigned_exactly_one_bucket():
    sub1, sub7, annotations, duration_by_video, entries, labels = _make_fixture(50)
    rows = build_rows(
        sub1=sub1,
        sub7=sub7,
        annotations=annotations,
        duration_by_video=duration_by_video,
        entries=entries,
        labels=labels,
    )
    keys = {
        (r["duration_bucket"], r["operator_family"], r["source"], r["foi_status"]) for r in rows
    }
    assert len(keys) <= 50
    grouped = aggregate_buckets(rows, has_labels=True)
    assert sum(g["n"] for g in grouped) == len(rows)
