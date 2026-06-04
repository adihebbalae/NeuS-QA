"""Shared helpers for AFRL taxonomy / test pipeline-stage reports.

Pipeline stages (test taxonomy):
  - cropped_foi: PULS valid + valid FOI + real crop (cropped_path != video_path)
  - full_video_hinted: PULS valid but NSVS/crop did not yield a FOI clip
  - full_video_no_hint: PULS failed (empty spec or propositions)

Operator complexity levels (1–5) are heuristic rollups aligned with
docs/timelogic-dataset-breakdown.md section 7 (TimeLogic paper Table 1).
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from compare_submissions import (  # noqa: E402
    duration_bucket,
    load_submission,
    normalize_answer,
    valid_foi,
)

AFRL_ROOT = Path("/mnt/Data/ah66742/timelogic/reports/afrl")

PATHS = {
    "val_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_val_data.json"),
    "test_ann": Path("/mnt/Data/ah66742/timelogic/annotations/timelogic_test_data.json"),
    "val_videos": Path("/mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos"),
    "test_videos": Path("/mnt/Data/ah66742/timelogic/videos/test/benchmark_test_videos_json"),
    "sub1": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_v01/submission.json"),
    "sub5b": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2/"
        "submission_sub5b_paper_faithful_gpt52.json"
    ),
    "sub7b": Path("/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/submission_sub7b.json"),
    "baseline_test": Path("/mnt/Data/ah66742/timelogic/outputs/baseline_cpu_test/submission.json"),
    "sub5b_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2"),
    "sub7b_shards": Path("/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful"),
    "sub5b_test": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub5b_test_3fps/submission_sub5b_test_gpt52.json"
    ),
    "sub7b_postprocess_entries": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/"
        "postprocess/postprocess_entries.json"
    ),
    "sub7b_rerun_postprocess_entries": Path(
        "/mnt/Data/ah66742/timelogic/outputs/sub7_neusqa_paper_faithful/"
        "sub7b_rerun_vqa/postprocess/postprocess_entries.json"
    ),
}

_TEST_ENTRY_BY_QID: dict[str, dict[str, Any]] | None = None

LENGTH_BUCKET_ORDER = ["<2s", "2-10s", "10-60s", ">60s", "unknown"]

PIPELINE_STAGES = ("cropped_foi", "full_video_hinted", "full_video_no_hint")
SOURCE_ORDER = ("star", "agqa", "ct", "bf", "unknown")


def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def source_dataset(video_id: str) -> str:
    return video_id.split("_", 1)[0] if "_" in video_id else "unknown"


def operator_family(operator: str) -> str:
    op = (operator or "unknown").lower()
    if op in {"always_before", "always_after"}:
        return op
    if "until" in op:
        return "until"
    if "since" in op:
        return "since"
    if "while" in op or "during" in op:
        return "during"
    if "before" in op:
        return "before"
    if "after" in op:
        return "after"
    return op


def operator_complexity_level(operator_guess: str) -> str:
    """Heuristic rollup to TimeLogic paper complexity levels 1–5."""
    op = (operator_guess or "unknown").lower()
    if op == "unknown":
        return "unknown"
    if op in {"in_turn_occurs", "between"}:
        return "5"
    if op in {
        "immediately_after",
        "immediately_before",
        "always_before",
        "always_after",
    }:
        return "4"
    if op in {"until", "since", "before", "after"}:
        return "3"
    if op in {"when", "while", "during"}:
        return "2"
    if op in {"starts_doing", "stops_doing"}:
        return "1"
    return "unknown"


def puls_valid(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    puls = entry.get("puls") or {}
    spec = (puls.get("specification") or "").strip()
    props = puls.get("proposition") or []
    return bool(spec and props)


def real_crop(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    paths = entry.get("paths") or {}
    cropped = paths.get("cropped_path") or ""
    video = paths.get("video_path") or ""
    return bool(cropped and video and cropped != video)


def classify_pipeline_stage(entry: dict[str, Any] | None) -> str:
    if not puls_valid(entry):
        return "full_video_no_hint"
    if valid_foi((entry or {}).get("frames_of_interest")) and real_crop(entry):
        return "cropped_foi"
    return "full_video_hinted"


def nsvs_outcome_label(entry: dict[str, Any] | None) -> str:
    window = foi_window_from_entry(entry)
    if window is not None:
        return f"foi=[{window[0]},{window[1]}]s"
    return "bypassed"


def spec_for_row(entry: dict[str, Any] | None) -> str:
    if not entry:
        return "empty"
    spec = ((entry.get("puls") or {}).get("specification") or "").strip()
    return spec if spec else "empty"


_CO_OCCUR_Q = re.compile(r"\bco-occur|\boverlap\b", re.I)
_NON_OVERLAP_Q = re.compile(r"does not overlap|non-overlap|not overlap with", re.I)
_TEMPORAL_Q = re.compile(
    r"\b(before|after|until|since|when|while|always|in turn|during)\b",
    re.I,
)


def foi_is_minus_one(foi: Any) -> bool:
    return foi == [-1] or (isinstance(foi, list) and len(foi) >= 1 and foi[0] == -1)


def spec_operator_flags(spec: str) -> dict[str, Any]:
    """Storm TL operator presence in an emitted PULS spec string."""
    text = (spec or "").strip()
    upper = f" {text.upper()} "
    return {
        "has_and": "&" in text or " AND " in upper,
        "has_u": " U " in upper,
        "has_not": "!" in text or " NOT " in upper,
        "has_g": " G " in upper,
        "n_u": text.upper().count(" U "),
        "empty": not text,
    }


def spec_faithful(
    operator_guess: str,
    question: str,
    spec: str,
    props: list[str] | None,
) -> tuple[bool, str]:
    """Does the emitted TL spec match the question's operator family?

    Rules (diagnostic):
    - Non-empty spec + propositions required.
    - Co-occur / overlap: ``&`` required, ``U`` forbidden.
    - Non-overlap: ``NOT`` + ``&`` (e.g. ``! (A & B)``).
    - ``until`` / ``since``: need ``U`` or ``G``.
    - ``always_*`` / ``in_turn_occurs``: chained ``U`` for 3+ props; no plain
      single-prop collapse; ``always_*`` must not be only ``&`` without ``U``.
    - Pairwise ordering ops: 2+ props and ``U`` or ``&``.
    """
    propositions = props or []
    flags = spec_operator_flags(spec)
    if flags["empty"] or not propositions:
        return False, "empty_spec_or_props"

    q = question or ""
    op = (operator_guess or "unknown").lower()
    has_and = flags["has_and"]
    has_u = flags["has_u"]
    has_not = flags["has_not"]
    has_g = flags["has_g"]
    n_u = flags["n_u"]
    n_props = len(propositions)

    if _CO_OCCUR_Q.search(q) and not _NON_OVERLAP_Q.search(q):
        ok = has_and and not has_u and n_props >= 2
        return ok, "co_occur" if ok else "co_occur_wrong_op"

    if _NON_OVERLAP_Q.search(q):
        ok = has_not and has_and
        return ok, "non_overlap" if ok else "non_overlap_wrong_op"

    if op in {"until", "since"}:
        ok = has_u or has_g
        return ok, op if ok else f"{op}_missing_u_or_g"

    if op in {"always_before", "always_after", "in_turn_occurs"}:
        if n_props < 2:
            return False, f"{op}_collapsed"
        if not has_u:
            return False, f"{op}_no_u"
        if n_props >= 3 and n_u < n_props - 1:
            return False, f"{op}_plain_u_not_chained"
        return True, f"{op}_ok"

    if op in {"before", "after", "immediately_before", "immediately_after"}:
        if n_props < 2:
            return False, f"{op}_collapsed"
        ok = has_u or has_and
        return ok, op if ok else f"{op}_missing_structure"

    if op in {"when", "while", "during"}:
        ok = has_u or has_g or (has_and and n_props >= 2)
        return ok, op if ok else f"{op}_missing_structure"

    if op == "between":
        ok = n_props >= 3 and has_u
        return ok, "between" if ok else "between_wrong_shape"

    if op == "unknown":
        if _CO_OCCUR_Q.search(q):
            ok = has_and and not has_u and n_props >= 2
            return ok, "unknown_co_occur" if ok else "unknown_co_occur_wrong"
        if _TEMPORAL_Q.search(q):
            if n_props < 2:
                return False, "unknown_temporal_collapse"
            ok = has_u or has_and
            return ok, "unknown_temporal" if ok else "unknown_temporal_wrong"
        return True, "unknown_atemporal"

    return True, "default_pass"


def crosstab_2x2(
    rows: list[dict[str, Any]],
    row_key: str,
    col_key: str,
    row_true_label: str = "true",
    col_true_label: str = "true",
) -> dict[str, Any]:
    """2×2 counts + row/column/total rates for boolean row_key × col_key."""
    cells = {(True, True): 0, (True, False): 0, (False, True): 0, (False, False): 0}
    for row in rows:
        cells[(bool(row[row_key]), bool(row[col_key]))] += 1

    n = len(rows) or 1
    out_cells: dict[str, dict[str, Any]] = {}
    for r_val, r_name in [(True, row_true_label), (False, f"not_{row_true_label}")]:
        r_true = cells[(r_val, True)]
        r_false = cells[(r_val, False)]
        r_total = r_true + r_false
        out_cells[r_name] = {
            col_true_label: r_true,
            f"not_{col_true_label}": r_false,
            "row_n": r_total,
            f"rate_{col_true_label}_within_row": round(r_true / r_total, 4) if r_total else None,
        }

    col_true_total = cells[(True, True)] + cells[(False, True)]
    col_false_total = cells[(True, False)] + cells[(False, False)]
    row_true_total = cells[(True, True)] + cells[(True, False)]
    row_false_total = cells[(False, True)] + cells[(False, False)]

    p_col_given_row_true = (
        cells[(True, True)] / row_true_total if row_true_total else None
    )
    p_col_given_row_false = (
        cells[(False, True)] / row_false_total if row_false_total else None
    )

    return {
        "row_key": row_key,
        "col_key": col_key,
        "n": len(rows),
        "cells": {
            f"{row_true_label}_x_{col_true_label}": cells[(True, True)],
            f"{row_true_label}_x_not_{col_true_label}": cells[(True, False)],
            f"not_{row_true_label}_x_{col_true_label}": cells[(False, True)],
            f"not_{row_true_label}_x_not_{col_true_label}": cells[(False, False)],
        },
        "rows": out_cells,
        "marginals": {
            f"rate_{row_true_label}": round(row_true_total / n, 4),
            f"rate_{col_true_label}": round(col_true_total / n, 4),
        },
        "conditional_rates": {
            f"p_{col_key}_given_{row_key}": {
                "faithful": round(p_col_given_row_true, 4)
                if p_col_given_row_true is not None
                else None,
                "not_faithful": round(p_col_given_row_false, 4)
                if p_col_given_row_false is not None
                else None,
            },
            "lift_unfaithful_over_faithful": round(
                p_col_given_row_false / p_col_given_row_true, 3
            )
            if p_col_given_row_true and p_col_given_row_false
            else None,
        },
    }


def iter_test_shard_entries(shards_root: Path | None = None) -> list[tuple[str, dict[str, Any]]]:
    """All (qid, entry) pairs from sub7b test per_entry shards."""
    root = shards_root or PATHS["sub7b_shards"]
    out: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(root.glob("shard_*/per_entry/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        entry = payload.get("entry") or payload
        meta = entry.get("metadata") or {}
        qid = str(meta.get("question_id") or path.stem)
        out.append((qid, entry))
    return out


def build_puls_shard_row(
    qid: str,
    entry: dict[str, Any],
    sub7b: dict[str, str],
    baseline_test: dict[str, str],
) -> dict[str, Any]:
    """One joined row: shard metadata + PULS/NSVS fields + faithfulness flags."""
    meta = entry.get("metadata") or {}
    puls = entry.get("puls") or {}
    nsvs = entry.get("nsvs") or {}
    spec = (puls.get("specification") or "").strip()
    props = puls.get("proposition") or []
    operator_guess = meta.get("operator_guess") or "unknown"
    foi = entry.get("frames_of_interest")
    faithful, faithful_reason = spec_faithful(
        operator_guess, entry.get("question") or "", spec, props
    )
    sub7b_ans = sub7b.get(qid, "")
    baseline_ans = baseline_test.get(qid, "")

    return {
        "qid": qid,
        "operator_guess": operator_guess,
        "operator_family": operator_family(operator_guess),
        "puls_spec": spec if spec else "empty",
        "propositions": props,
        "foi_raw": foi,
        "foi_minus1": foi_is_minus_one(foi),
        "nsvs_indices": nsvs.get("indices"),
        "spec_faithful": faithful,
        "spec_faithful_reason": faithful_reason,
        "sub7b_answer": sub7b_ans,
        "baseline_answer": baseline_ans,
        "ours_ne_vanilla": sub7b_ans != baseline_ans if sub7b_ans and baseline_ans else None,
    }


def load_annotations(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_per_entry(qid: str, shards_root: Path) -> dict[str, Any] | None:
    for p in shards_root.glob(f"shard_*/per_entry/{qid}.json"):
        if p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("entry") or data
    return None


def entry_from_shard(qid: str, split: str) -> dict[str, Any] | None:
    shards = PATHS["sub5b_shards"] if split == "val" else PATHS["sub7b_shards"]
    return find_per_entry(qid, shards)


def load_test_entries_by_qid() -> dict[str, dict[str, Any]]:
    """Postprocess entries (crop paths + FOI); rerun rows overlay main."""
    global _TEST_ENTRY_BY_QID
    if _TEST_ENTRY_BY_QID is not None:
        return _TEST_ENTRY_BY_QID
    out: dict[str, dict[str, Any]] = {}
    for path in (PATHS["sub7b_postprocess_entries"], PATHS["sub7b_rerun_postprocess_entries"]):
        if not path.is_file():
            continue
        for entry in json.loads(path.read_text(encoding="utf-8")):
            meta = entry.get("metadata") or {}
            qid = str(meta.get("question_id") or "")
            if qid:
                out[qid] = entry
    _TEST_ENTRY_BY_QID = out
    return out


def entry_for_test(qid: str) -> dict[str, Any] | None:
    return load_test_entries_by_qid().get(qid) or entry_from_shard(qid, "test")


def video_path(split: str, video_id: str) -> Path:
    root = PATHS["val_videos"] if split == "val" else PATHS["test_videos"]
    return root / video_id


def probe_opencv(path: Path) -> dict[str, Any]:
    import cv2

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"error": "opencv_open_failed"}
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    cap.release()
    duration = (frame_count / fps) if fps > 0 and frame_count > 0 else None
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_s": round(duration, 6) if duration is not None else None,
    }


def probe_ffprobe(path: Path) -> dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=avg_frame_rate,nb_frames,r_frame_rate",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"error": f"ffprobe_failed: {proc.stderr.strip()[:200]}"}
    data = json.loads(proc.stdout or "{}")
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    def parse_rate(value: str | None) -> float | None:
        if not value or value in {"0/0", "N/A"}:
            return None
        if "/" in value:
            num, den = value.split("/", 1)
            den_f = float(den)
            return float(num) / den_f if den_f else None
        return float(value)

    fps = parse_rate(stream.get("avg_frame_rate")) or parse_rate(stream.get("r_frame_rate"))
    frame_count_raw = stream.get("nb_frames")
    frame_count = (
        int(frame_count_raw) if frame_count_raw not in (None, "N/A") else None
    )
    duration = float(fmt["duration"]) if fmt.get("duration") not in (None, "N/A") else None
    if duration is None and fps and frame_count:
        duration = frame_count / fps
    return {
        "frame_count": frame_count,
        "fps": round(fps, 6) if fps else None,
        "duration_s": round(duration, 6) if duration is not None else None,
    }


def probe_video(path: Path, backend: str = "auto") -> dict[str, Any]:
    use_ffprobe = backend == "ffprobe" or (backend == "auto" and ffprobe_available())
    if use_ffprobe:
        result = probe_ffprobe(path)
        if "error" not in result:
            result["probe_backend"] = "ffprobe"
            return result
    result = probe_opencv(path)
    result["probe_backend"] = "opencv" if "error" not in result else result.get("probe_backend", "opencv")
    return result


def length_bucket(duration_s: float | None) -> str:
    return duration_bucket(duration_s)


def foi_window_from_entry(entry: dict[str, Any] | None) -> list[float] | None:
    if not entry:
        return None
    foi = entry.get("frames_of_interest")
    fps = (entry.get("metadata") or {}).get("fps")
    if not valid_foi(foi) or not fps:
        return None
    start_s = round(float(foi[0]) / float(fps), 3)
    end_s = round(float(foi[1]) / float(fps), 3)
    return [start_s, end_s]


def load_duration_cache(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = f"{row['split']}:{row['qid']}"
            out[key] = row
    return out


def duration_cache_key(split: str, qid: str) -> str:
    return f"{split}:{qid}"


def load_enriched_manifest(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def our_answer_for_split(qid: str, split: str, sub5b: dict[str, str], sub7b: dict[str, str]) -> str:
    return sub5b.get(qid) if split == "val" else sub7b.get(qid, "")


def vanilla_answer_for_split(
    qid: str, split: str, sub1: dict[str, str], baseline_test: dict[str, str]
) -> str:
    return sub1.get(qid) if split == "val" else baseline_test.get(qid, "")


def evenly_spaced_frames(frame_count: int, n: int) -> list[int]:
    if frame_count <= 0:
        return []
    if n >= frame_count:
        return list(range(frame_count))
    if n <= 1:
        return [0]
    return sorted({round(i * (frame_count - 1) / (n - 1)) for i in range(n)})


def build_test_row(
    ann: dict[str, Any],
    entry: dict[str, Any] | None,
    sub7b: dict[str, str],
    baseline_test: dict[str, str],
    sub5b_test: dict[str, str],
) -> dict[str, Any]:
    """One test-split manifest/taxonomy row."""
    qid = str(ann["question_id"])
    video_id = ann["video_id"]
    meta = (entry or {}).get("metadata") or {}
    puls = (entry or {}).get("puls") or {}
    operator_guess = meta.get("operator_guess") or "unknown"
    foi = (entry or {}).get("frames_of_interest")
    sub7b_ans = sub7b.get(qid, "")
    baseline_ans = baseline_test.get(qid, "")
    sub5b_ans = sub5b_test.get(qid, "")

    return {
        "qid": qid,
        "split": "test",
        "source": source_dataset(video_id),
        "video_id": video_id,
        "mode": meta.get("mode") or ann.get("mode") or "",
        "operator_guess": operator_guess,
        "operator_family": operator_family(operator_guess),
        "complexity_level": operator_complexity_level(operator_guess),
        "question": (entry or {}).get("question") or ann.get("question") or "",
        "candidates": (entry or {}).get("candidates") or [],
        "our_spec": spec_for_row(entry),
        "pipeline_stage": classify_pipeline_stage(entry),
        "nsvs_outcome": nsvs_outcome_label(entry),
        "foi_window": foi_window_from_entry(entry),
        "foi_success": valid_foi(foi) if entry else False,
        "foi_raw": foi,
        "sub7b_answer": sub7b_ans,
        "baseline_answer": baseline_ans,
        "sub5b_test_answer": sub5b_ans,
        "answers_agree_sub7b_baseline": (
            sub7b_ans == baseline_ans if sub7b_ans and baseline_ans else None
        ),
        "answers_agree_sub7b_sub5b": (
            sub7b_ans == sub5b_ans if sub7b_ans and sub5b_ans else None
        ),
        # Legacy aliases for older afrl scripts
        "our_answer": sub7b_ans,
        "vanilla_vlm_answer": baseline_ans,
        "answers_agree": sub7b_ans == baseline_ans if sub7b_ans and baseline_ans else None,
        "gt": None,
        "gt_available": False,
    }
