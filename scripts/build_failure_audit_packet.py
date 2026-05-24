#!/usr/bin/env python3
"""Build a human-readable Sub #1 vs challenger disagreement audit packet.

EvalAI does not expose row-level labels locally, so this packet samples from
the disagreement CSV and records both answers without conditioning on who won.
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
from openai import OpenAI


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIAG = Path("/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2")
DEFAULT_ENTRIES = Path("/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2")
DEFAULT_OUT = DEFAULT_DIAG / "failure_audit_packet.md"
DEFAULT_FRAME_DESC_CACHE = DEFAULT_DIAG / "failure_audit_frame_descriptions.json"
V2_AUDIT_DIR = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v2"
V3_AUDIT_DIR = REPO_ROOT / "diagnostics" / "sub5b_failure_audit_v3"

_PROP_KEYWORD_STOPWORDS = frozenset(
    {"person", "something", "somewhere", "from", "with", "into", "onto", "the", "and", "for"}
)

AUDIT_DURATION_BUCKETS: list[tuple[str, float | None, float | None]] = [
    ("<10s", None, 10.0),
    ("10-30s", 10.0, 30.0),
    ("30-60s", 30.0, 60.0),
    ("60-180s", 60.0, 180.0),
    (">180s", 180.0, None),
]

# Frame-audit sampling tiers (by frame_count, not wall-clock alone).
MAX_AUDIT_FRAMES = 20
DENSE_FRAME_COUNT = 30  # include every frame
MEDIUM_FRAME_COUNT = 120  # ~1 fps spacing
PERCENTILE_PCTS = (10, 25, 50, 75, 90)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diag-dir", type=Path, default=DEFAULT_DIAG)
    p.add_argument(
        "--entries-dir",
        type=Path,
        default=None,
        help="Pipeline output dir containing merged/entries.json (default: --sub2-dir or DEFAULT_ENTRIES)",
    )
    p.add_argument(
        "--sub2-dir",
        type=Path,
        default=DEFAULT_ENTRIES,
        help="Deprecated alias for --entries-dir",
    )
    p.add_argument("--answers-diag", type=Path, default=None, help="answers_diag.json path (auto-detected if omitted)")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--n", type=int, default=25)
    p.add_argument("--frame-desc-cache", type=Path, default=DEFAULT_FRAME_DESC_CACHE)
    p.add_argument("--vision-model", default="gpt-4o-mini")
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--force-frame-desc", action="store_true")
    p.add_argument("--skip-api", action="store_true", help="Do not call OpenAI; use only cached frame descriptions")
    p.add_argument(
        "--stratify-duration-buckets",
        action="store_true",
        help="Pick --per-bucket rows from each audit duration bucket (<10s, 10-30s, 30-60s, 60-180s, >180s)",
    )
    p.add_argument("--per-bucket", type=int, default=5, help="Rows per audit duration bucket when stratifying")
    p.add_argument("--sub-b-label", default="Sub #2", help="Display label for the challenger submission")
    p.add_argument(
        "--sub-b-answer-col",
        default="sub2_nsvs_answer",
        help="CSV column for the challenger answer in disagreements.csv",
    )
    p.add_argument("--packet-title", default=None, help="Markdown H1 title (auto if omitted)")
    p.add_argument("--packet-purpose", default=None, help="Intro paragraph (auto if omitted)")
    p.add_argument(
        "--selected-csv",
        type=Path,
        default=None,
        help="Reuse exact QIDs (in order) from a prior selected_rows.csv",
    )
    p.add_argument(
        "--version",
        choices=("v2", "v3"),
        default="v2",
        help="Packet format version (v3 adds auto triage fields and two-tier tally)",
    )
    p.add_argument(
        "--cot-traces",
        type=Path,
        default=None,
        help="CoT diagnostic cot_traces.json to inline per-row (v3 only)",
    )
    args = p.parse_args()
    if args.entries_dir is None:
        args.entries_dir = args.sub2_dir
    apply_version_defaults(args)
    return args


def apply_version_defaults(args: argparse.Namespace) -> None:
    if args.version != "v3":
        return
    if args.sub_b_label == "Sub #2":
        args.sub_b_label = "Sub #5B"
    if args.sub_b_answer_col == "sub2_nsvs_answer":
        args.sub_b_answer_col = "sub5b_paper_faithful_fix2_answer"
    if args.diag_dir == DEFAULT_DIAG:
        args.diag_dir = Path("/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub5b_fix2")
    if args.entries_dir == DEFAULT_ENTRIES:
        args.entries_dir = Path("/mnt/Data/ah66742/timelogic/outputs/sub5b_paper_faithful_3fps_fix2")
    if args.selected_csv is None:
        args.selected_csv = V2_AUDIT_DIR / "selected_rows.csv"
    if args.frame_desc_cache == DEFAULT_FRAME_DESC_CACHE:
        args.frame_desc_cache = V2_AUDIT_DIR / "failure_audit_frame_descriptions.json"
    if args.out == DEFAULT_OUT:
        args.out = V3_AUDIT_DIR / "failure_audit_packet.md"
    if args.packet_title is None:
        args.packet_title = f"Sub #1/{args.sub_b_label} Disagreement Audit Packet (v3)"
    if args.packet_purpose is None:
        args.packet_purpose = (
            f"Purpose: a human-flippable disagreement slice where Sub #1 and {args.sub_b_label} "
            "gave different answers. v3 pre-fills triage signals (PULS_preliminary, Watch_for, "
            "Caption_coverage, Caption_question_mismatch, NSVS_bypassed) to speed tagging."
        )
    if args.cot_traces is None:
        args.cot_traces = V3_AUDIT_DIR / "cot_traces.json"
    args.skip_api = True


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def load_env_file(path: str) -> None:
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for raw in f.read().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    if not os.environ.get("OPENAI_API_KEY"):
        for alt in ("OPENAI_API_KEY1", "OPENAI_API_KEY2"):
            if os.environ.get(alt):
                os.environ["OPENAI_API_KEY"] = os.environ[alt]
                break


def qid_from_entry(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    return str(metadata.get("question_id") or entry.get("question_id") or entry.get("qid"))


def duration_bucket(seconds: float | None) -> str:
    if seconds is None or math.isnan(seconds):
        return "unknown"
    if seconds < 30:
        return "short"
    if seconds <= 120:
        return "medium"
    return "long"


def audit_duration_bucket(seconds: float | None) -> str:
    if seconds is None or math.isnan(seconds):
        return "unknown"
    for label, low, high in AUDIT_DURATION_BUCKETS:
        if low is not None and seconds < low:
            continue
        if high is not None and seconds >= high:
            continue
        return label
    return ">180s"


def audit_bucket_midpoint(label: str) -> float:
    for bucket_label, low, high in AUDIT_DURATION_BUCKETS:
        if bucket_label != label:
            continue
        if low is None:
            return (high or 10.0) / 2.0
        if high is None:
            return low + 60.0
        return (low + high) / 2.0
    return 0.0


def resolve_answers_diag(entries_dir: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    candidates = [
        entries_dir / "answers_gpt52" / "answers_diag.json",
        entries_dir / "answers_gpt_5_2" / "answers_diag.json",
        entries_dir / "answers_gpt52_smoke" / "answers_diag.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


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


def extract_options(question: str, candidates: list[str] | None) -> list[str]:
    if candidates:
        if candidates == ["Yes", "No"]:
            return ["Yes", "No"]
        return [f"{chr(65 + i)}. {c}" for i, c in enumerate(candidates)]

    matches = re.findall(r"Option ([A-D]): ([^.,?]+)", question)
    if matches:
        return [f"{letter}. {text.strip()}" for letter, text in matches]
    return []


def fmt_json(value: Any) -> str:
    return "<code>" + html.escape(json.dumps(value, ensure_ascii=True)) + "</code>"


def fmt_pre_json(value: Any) -> str:
    body = html.escape(json.dumps(value, ensure_ascii=True, indent=2))
    return f"<pre><code>{body}</code></pre>"


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def answer_diag_by_qid(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows = load_json(path)
    return {str(row.get("qid")): row for row in rows}


def load_cot_traces_by_qid(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_json(path)
    rows = payload.get("rows") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return {}
    return {str(row.get("question_id")): row for row in rows if row.get("question_id") is not None}


def load_cot_traces_order(path: Path) -> dict[str, int]:
    """Preserve cot_summary.md / cot_traces.json row order for within-tier sorting."""
    if not path.exists():
        return {}
    payload = load_json(path)
    rows = payload.get("rows") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return {}
    return {str(row.get("question_id")): idx for idx, row in enumerate(rows) if row.get("question_id") is not None}


COT_PRIORITY_RANK = {"A": 0, "B": 1, "Boring": 2, "unknown": 3}


def cot_priority_label(cot_row: dict[str, Any] | None) -> str:
    """Classify a row for human review ordering.

    Priority A: CoT self-agrees but both runs disagree with Sub #5B.
    Priority B: CoT flaky (two runs disagree with each other).
    Boring: CoT stable and matches Sub #5B on both runs.
    """
    if not cot_row:
        return "unknown"
    if cot_row.get("self_agreement") is False:
        return "B"
    if cot_row.get("agrees_with_sub5b_both") is False:
        return "A"
    return "Boring"


def sort_selected_by_cot_priority(
    selected: list[dict[str, str]],
    cot_by_qid: dict[str, dict[str, Any]],
    cot_order: dict[str, int],
) -> list[dict[str, str]]:
    def sort_key(row: dict[str, str]) -> tuple[int, int, int]:
        qid = row["question_id"]
        label = cot_priority_label(cot_by_qid.get(qid))
        return (COT_PRIORITY_RANK[label], cot_order.get(qid, 9999), int(qid))

    return sorted(selected, key=sort_key)


def render_cot_priority_section(
    selected: list[dict[str, str]],
    cot_by_qid: dict[str, dict[str, Any]],
    cot_order: dict[str, int],
) -> list[str]:
    tiers: dict[str, list[str]] = {"A": [], "B": [], "Boring": [], "unknown": []}
    for row in selected:
        qid = row["question_id"]
        tiers[cot_priority_label(cot_by_qid.get(qid))].append(qid)
    for label in tiers:
        tiers[label].sort(key=lambda qid: (cot_order.get(qid, 9999), int(qid)))

    def fmt_qids(qids: list[str]) -> str:
        return ", ".join(qids) if qids else "_none_"

    return [
        "## CoT Review Priority",
        "",
        "Packet row order: **Priority A → Priority B → Boring** (lists match `cot_summary.md`).",
        "",
        f"- **Priority A** — CoT stable + disagrees Sub #5B ({len(tiers['A'])}): {fmt_qids(tiers['A'])}",
        f"- **Priority B** — CoT flaky ({len(tiers['B'])}): {fmt_qids(tiers['B'])}",
        f"- **Boring** — CoT stable + agrees Sub #5B ({len(tiers['Boring'])}): {fmt_qids(tiers['Boring'])}",
        "",
    ]


def format_bool_flag(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "n/a"


def render_cot_run_block(run: dict[str, Any]) -> list[str]:
    run_idx = run.get("run", "?")
    lines = [
        f"<h4>Run {safe_text(run_idx)}</h4>",
        f"<b>Answer:</b> <code>{safe_text(run.get('answer'))}</code><br>",
        f"<b>Sampled frame indices:</b> <code>{safe_text(run.get('sampled_frame_indices'))}</code><br>",
        f"<b>Frames used:</b> {safe_text(run.get('num_frames', '?'))}<br>",
    ]
    if run.get("error"):
        lines.append(f"<b>Error:</b> {safe_text(run.get('error'))}<br>")
    reasoning = run.get("reasoning") or run.get("raw")
    if reasoning:
        lines.extend(
            [
                "<b>Reasoning:</b>",
                f"<pre><code>{safe_text(reasoning)}</code></pre>",
            ]
        )
    reasoning_summary = run.get("reasoning_summary")
    if reasoning_summary:
        lines.extend(
            [
                "<b>Reasoning summary (API):</b>",
                f"<pre><code>{safe_text(reasoning_summary)}</code></pre>",
            ]
        )
    return lines


def render_cot_rerun_details(cot_row: dict[str, Any] | None) -> list[str]:
    if not cot_row:
        return [
            "<details>",
            "<summary><b>CoT Diagnostic Rerun</b> — <i>not available</i></summary>",
            "<p><i>No matching row in cot_traces.json.</i></p>",
            "</details>",
            "",
        ]

    summary_bits = [
        f"self-agree: {format_bool_flag(cot_row.get('self_agreement'))}",
        f"Sub #5B (both): {format_bool_flag(cot_row.get('agrees_with_sub5b_both'))}",
        f"Sub #5B run1: {format_bool_flag(cot_row.get('agrees_with_sub5b_run1'))}",
        f"Sub #5B run2: {format_bool_flag(cot_row.get('agrees_with_sub5b_run2'))}",
        f"Sub #5B (any): {format_bool_flag(cot_row.get('agrees_with_sub5b_any'))}",
    ]
    runs = cot_row.get("runs") or []
    lines = [
        "<details>",
        f"<summary><b>CoT Diagnostic Rerun</b> — {safe_text('; '.join(summary_bits))}</summary>",
        "",
        f"<b>Sub #5B baseline answer:</b> <code>{safe_text(cot_row.get('sub5b_answer'))}</code><br>",
        f"<b>Sub #1 answer:</b> <code>{safe_text(cot_row.get('sub1_answer'))}</code><br>",
        "<b>Agreement flags:</b> "
        f"self={format_bool_flag(cot_row.get('self_agreement'))}, "
        f"sub5b_both={format_bool_flag(cot_row.get('agrees_with_sub5b_both'))}, "
        f"sub5b_run1={format_bool_flag(cot_row.get('agrees_with_sub5b_run1'))}, "
        f"sub5b_run2={format_bool_flag(cot_row.get('agrees_with_sub5b_run2'))}, "
        f"sub5b_any={format_bool_flag(cot_row.get('agrees_with_sub5b_any'))}",
        "",
    ]
    for run in runs:
        lines.extend(render_cot_run_block(run))
        lines.append("")
    lines.extend(["</details>", ""])
    return lines


def valid_interval(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 2
        and value != [-1]
        and value[0] != -1
        and value[1] != -1
        and int(value[0]) <= int(value[1])
    )


def clamp_frame(idx: int, frame_count: int) -> int:
    if frame_count <= 0:
        return 0
    return max(0, min(idx, frame_count - 1))


def evenly_spaced_frames(frame_count: int, n: int) -> list[int]:
    if frame_count <= 0:
        return []
    if n >= frame_count:
        return list(range(frame_count))
    if n <= 1:
        return [0]
    return sorted({round(i * (frame_count - 1) / (n - 1)) for i in range(n)})


def nsvs_detection_anchors(entry: dict[str, Any]) -> list[tuple[str, int]]:
    props = entry.get("puls", {}).get("proposition") or []
    indices = entry.get("nsvs", {}).get("indices") or []
    anchors: list[tuple[str, int]] = []
    for prop, idxs in zip(props, indices):
        if not idxs:
            continue
        short = str(prop).replace("_", " ")[:36]
        for j, idx in enumerate(idxs[:5]):
            anchors.append((f"NSVS detect: {short} [{j}]", int(idx)))
    return anchors


def frame_description_points(entry: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = entry.get("metadata", {})
    frame_count = int(metadata.get("frame_count") or 0)
    fps = float(metadata.get("fps") or 0.0)
    if frame_count <= 0:
        return []

    foi = entry.get("frames_of_interest")
    anchors: list[tuple[str, int]] = []

    if frame_count <= DENSE_FRAME_COUNT:
        anchors.extend((f"frame {frame_idx}", frame_idx) for frame_idx in range(frame_count))
    elif frame_count <= MEDIUM_FRAME_COUNT:
        target = min(MAX_AUDIT_FRAMES - 4, max(8, int(math.ceil(frame_count / max(fps, 1.0)))))
        for frame_idx in evenly_spaced_frames(frame_count, target):
            sec = frame_idx / fps if fps else None
            label = f"~{sec:.2f}s" if sec is not None else f"frame {frame_idx}"
            anchors.append((label, frame_idx))
    else:
        for pct in PERCENTILE_PCTS:
            anchors.append((f"{pct}% of video", round((frame_count - 1) * (pct / 100.0))))

    if valid_interval(foi):
        start, end = int(foi[0]), int(foi[1])
        mid = (start + end) // 2
        anchors.extend(
            [
                ("FOI start", start),
                ("FOI midpoint", mid),
                ("FOI end", end),
            ]
        )
    elif frame_count > DENSE_FRAME_COUNT:
        anchors.append(("FOI midpoint (fallback full-video midpoint)", (frame_count - 1) // 2))

    anchors.extend(nsvs_detection_anchors(entry))

    deduped: list[dict[str, Any]] = []
    seen_frames: set[int] = set()
    for label, idx in anchors:
        frame = clamp_frame(int(idx), frame_count)
        if frame in seen_frames:
            continue
        seen_frames.add(frame)
        deduped.append(
            {
                "label": label,
                "frame": frame,
                "seconds": round(frame / fps, 3) if fps else None,
            }
        )
        if len(deduped) >= MAX_AUDIT_FRAMES:
            break

    deduped.sort(key=lambda point: int(point["frame"]))
    return deduped


def video_audit_links(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata", {})
    video_id = metadata.get("video_id") or "unknown"
    video_path = entry.get("paths", {}).get("video_path") or ""
    if not video_path:
        return f"<b>Video:</b> {safe_text(video_id)}<br>"
    file_uri = Path(video_path).resolve().as_uri()
    escaped_path = safe_text(video_path)
    return (
        f"<b>Video:</b> {safe_text(video_id)}<br>"
        f'<b>Open:</b> <a href="{safe_text(file_uri)}">{safe_text(video_id)}</a><br>'
        f"<b>Path:</b> <code>{escaped_path}</code><br>"
        f"<b>Play:</b> <code>ffplay -autoexit '{escaped_path}'</code><br>"
    )


def read_frame_bgr(video_path: str, frame_idx: int) -> Any | None:
    if not video_path or not os.path.exists(video_path):
        return None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_idx))
        ok, frame = cap.read()
    finally:
        cap.release()
    if not ok or frame is None:
        return None
    return frame


def encode_frame_data_url(frame_bgr: Any, quality: int = 80) -> str | None:
    ok, buf = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return None
    encoded = base64.b64encode(buf).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def parse_json_object(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {"raw_response": text, "frames": []}


def describe_frames_with_vision(
    client: OpenAI,
    model: str,
    entry: dict[str, Any],
    points: list[dict[str, Any]],
) -> dict[str, Any]:
    video_path = entry.get("paths", {}).get("video_path", "")
    images: list[tuple[dict[str, Any], str]] = []
    for point in points:
        frame = read_frame_bgr(video_path, int(point["frame"]))
        if frame is None:
            continue
        data_url = encode_frame_data_url(frame)
        if data_url:
            images.append((point, data_url))

    if not images:
        return {
            "status": "no_frames_read",
            "frames": [
                {
                    **point,
                    "description": "Frame could not be read from the source video.",
                }
                for point in points
            ],
        }

    label_block = "\n".join(
        f"{i + 1}. {point['label']} | frame {point['frame']} | {point.get('seconds')}s"
        for i, (point, _data_url) in enumerate(images)
    )
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "Describe each provided video frame in exactly two concise sentences. "
                "Focus on visible actions, objects, people, and temporal evidence relevant to the question. "
                "Do not answer the question. Return strict JSON with key 'frames', an array of objects "
                "with keys label, frame, seconds, description.\n\n"
                f"Question: {entry.get('question')}\n"
                f"PULS propositions: {entry.get('puls', {}).get('proposition')}\n"
                f"PULS temporal spec: {entry.get('puls', {}).get('specification')}\n\n"
                f"Frame labels, in image order:\n{label_block}"
            ),
        }
    ]
    for _point, data_url in images:
        content.append({"type": "image_url", "image_url": {"url": data_url, "detail": "low"}})

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You describe video frames for a temporal QA failure audit. Be literal and concise.",
            },
            {"role": "user", "content": content},
        ],
        max_tokens=2400,
        temperature=0.0,
    )
    text = response.choices[0].message.content or ""
    parsed = parse_json_object(text)
    parsed["status"] = "ok"
    parsed["frames"] = align_frame_descriptions(points, parsed.get("frames"))
    return parsed


def align_frame_descriptions(
    points: list[dict[str, Any]], model_frames: Any
) -> list[dict[str, Any]]:
    """Map vision-model output back onto requested points (stable labels/order)."""
    by_frame: dict[int, str] = {}
    if isinstance(model_frames, list):
        for item in model_frames:
            if not isinstance(item, dict):
                continue
            frame = item.get("frame")
            desc = item.get("description")
            if frame is None or not desc:
                continue
            by_frame[int(frame)] = str(desc)

    aligned: list[dict[str, Any]] = []
    for point in points:
        frame = int(point["frame"])
        aligned.append(
            {
                "label": point["label"],
                "frame": frame,
                "seconds": point.get("seconds"),
                "description": by_frame.get(frame, "No description returned for this frame."),
            }
        )
    return aligned


def load_frame_desc_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = load_json(path)
    return data if isinstance(data, dict) else {}


def write_frame_desc_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=True, indent=2) + "\n")


def ensure_frame_descriptions(
    args: argparse.Namespace,
    selected: list[dict[str, str]],
    entries: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    cache = load_frame_desc_cache(args.frame_desc_cache)
    if args.skip_api:
        return cache

    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(f"OPENAI_API_KEY not set and not found in {args.env_file}")

    client = OpenAI()
    changed = False
    for i, row in enumerate(selected, start=1):
        qid = row["question_id"]
        if qid in cache and not args.force_frame_desc:
            continue
        entry = entries[qid]
        points = frame_description_points(entry)
        print(f"Describing frames for QID {qid} ({i}/{len(selected)})")
        cache[qid] = {
            "qid": qid,
            "video_id": entry.get("metadata", {}).get("video_id"),
            "model": args.vision_model,
            "points": points,
            "description": describe_frames_with_vision(client, args.vision_model, entry, points),
        }
        write_frame_desc_cache(args.frame_desc_cache, cache)
        changed = True
    if changed:
        write_frame_desc_cache(args.frame_desc_cache, cache)
    return cache


def puls_sanity_stub(entry: dict[str, Any]) -> str:
    puls = entry.get("puls", {})
    props = puls.get("proposition") or []
    spec = puls.get("specification") or ""
    if not props or not spec:
        return "Stub: missing propositions or TL spec; likely not enough information to encode the question."
    if isinstance(props, list):
        concrete = all(isinstance(p, str) and len(p.replace("_", " ").split()) >= 2 for p in props)
        prop_text = ", ".join(str(p).replace("_", " ") for p in props)
    else:
        concrete = False
        prop_text = str(props)
    verdict = "concrete enough to audit visually" if concrete else "possibly too abstract for frame-level detection"
    return f"Stub: check whether `{spec}` captures the temporal relation; propositions ({prop_text}) look {verdict}."


def proposition_keywords(proposition: str) -> set[str]:
    text = humanize_proposition(proposition).lower()
    keywords = {
        token
        for token in re.findall(r"[a-z]{3,}", text)
        if token not in _PROP_KEYWORD_STOPWORDS
    }
    for part in str(proposition).lower().split("_"):
        if len(part) >= 4 and part not in _PROP_KEYWORD_STOPWORDS:
            keywords.add(part)
    return keywords


def proposition_mentioned_in_captions(proposition: str, captions: str) -> bool:
    keywords = proposition_keywords(proposition)
    if any(keyword in captions for keyword in keywords):
        return True
    prop_text = humanize_proposition(proposition).lower().replace(" ", "")
    for word in re.findall(r"[a-z]{4,}", captions):
        if word in prop_text:
            return True
    return False


def ordered_propositions(entry: dict[str, Any]) -> list[str]:
    props = [str(p) for p in entry.get("puls", {}).get("proposition") or []]
    if len(props) < 2:
        return props
    spec = str(entry.get("puls", {}).get("specification") or "")
    match = re.search(r'"([^"]+)"\s*U\s*"([^"]+)"', spec)
    if match:
        first, second = match.group(1), match.group(2)
        if first in props and second in props:
            remainder = [p for p in props if p not in {first, second}]
            return [first, second, *remainder]
    return props


def humanize_proposition(proposition: str) -> str:
    return str(proposition).replace("_", " ")


def compute_puls_preliminary(entry: dict[str, Any], row: dict[str, str]) -> str:
    puls = entry.get("puls", {})
    props = puls.get("proposition") or []
    spec = str(puls.get("specification") or "")
    operator = row.get("operator_guess") or "unknown"
    issues: list[str] = []

    if not props:
        issues.append("missing propositions")
    if not spec:
        issues.append("missing TL spec")
    if issues:
        return f"fail: {'; '.join(issues)}"

    for prop in props:
        if len(humanize_proposition(prop).split()) < 2:
            issues.append(f"abstract proposition `{prop}`")

    spec_upper = spec.upper()
    if operator == "immediately_after" and " U " in spec_upper:
        issues.append("spec uses U (until); question asks immediately_after (ordering may be under-specified)")
    if operator == "always_before" and len(props) >= 2 and spec.count(" U ") < len(props) - 1:
        issues.append("always_before may need chained U ordering across all propositions")
    if operator in {"since", "until"} and " U " not in spec_upper and " G " not in spec_upper:
        issues.append(f"{operator} question but spec has neither U nor G operator")

    if issues:
        return "flag: " + "; ".join(issues)
    return "pass"


def compute_watch_for(entry: dict[str, Any], row: dict[str, str]) -> str:
    labels = [humanize_proposition(p) for p in ordered_propositions(entry)]
    a = labels[0] if labels else "event A"
    b = labels[1] if len(labels) > 1 else "event B"
    chain = " → ".join(labels) if len(labels) > 2 else ""
    operator = row.get("operator_guess") or row.get("operator_family") or "unknown"
    source = row.get("source_dataset") or entry.get("metadata", {}).get("source_dataset") or "unknown"
    playback = " Use 0.25× playback for star/agqa sub-10s clips." if source in {"star", "agqa"} else ""

    hints: dict[str, str] = {
        "immediately_after": f"Check whether `{b}` begins within 1–2 frames after `{a}` ends.{playback}",
        "after": f"Confirm `{b}` occurs only after `{a}` completes.{playback}",
        "before": f"Confirm `{a}` completes before `{b}` begins.{playback}",
        "since": f"Confirm `{b}` holds continuously from the anchor/start of `{a}` through the clip end.{playback}",
        "until": f"Confirm `{b}` holds until `{a}` occurs (then may stop).{playback}",
        "during": f"Confirm `{b}` overlaps the interval while `{a}` is happening.{playback}",
        "always_before": (
            f"Verify global ordering across the chain ({chain or f'{a} before {b}'}); earlier actions must precede later ones."
        ),
        "always_after": (
            f"Verify global ordering across the chain ({chain or f'{a} before {b}'}); later actions must follow earlier ones."
        ),
    }
    return hints.get(operator, f"Inspect whether frame captions support the `{operator}` relation among {labels or ['pipeline events']}.{playback}")


def caption_frames_from_cache(cache_row: dict[str, Any] | None) -> set[int]:
    if not cache_row:
        return set()
    desc = cache_row.get("description", {})
    frames = desc.get("frames") if isinstance(desc, dict) else None
    if not isinstance(frames, list):
        return set()
    return {int(item["frame"]) for item in frames if isinstance(item, dict) and item.get("frame") is not None}


def caption_text_from_cache(cache_row: dict[str, Any] | None) -> str:
    if not cache_row:
        return ""
    desc = cache_row.get("description", {})
    frames = desc.get("frames") if isinstance(desc, dict) else None
    if not isinstance(frames, list):
        return ""
    return " ".join(str(item.get("description") or "") for item in frames if isinstance(item, dict)).lower()


def compute_caption_coverage(entry: dict[str, Any], cache_row: dict[str, Any] | None) -> str:
    caption_frames = caption_frames_from_cache(cache_row)
    if not caption_frames:
        return "unknown: no cached captions"

    detection_frames: set[int] = set()
    for idxs in entry.get("nsvs", {}).get("indices") or []:
        for idx in idxs or []:
            detection_frames.add(int(idx))

    target_frames: set[int] = set(detection_frames)
    foi = entry.get("frames_of_interest")
    if valid_interval(foi):
        start, end = int(foi[0]), int(foi[1])
        target_frames.update(range(start, end + 1))

    if not target_frames:
        return f"n/a: {len(caption_frames)} caption frames; no FOI interval or NSVS detections to cover"

    missing = sorted(target_frames - caption_frames)
    if not missing:
        return f"full: {len(caption_frames)} caption frames cover all {len(target_frames)} target frames"
    return (
        f"partial: missing caption frames {missing} "
        f"({len(caption_frames)} captions vs {len(target_frames)} target frames)"
    )


def compute_caption_question_mismatch(entry: dict[str, Any], cache_row: dict[str, Any] | None) -> str:
    props = entry.get("puls", {}).get("proposition") or []
    if not props:
        return "unknown: no propositions"
    captions = caption_text_from_cache(cache_row)
    if not captions:
        return "unknown: no cached captions"

    missing_props: list[str] = []
    for prop in props:
        if not proposition_mentioned_in_captions(str(prop), captions):
            missing_props.append(str(prop))

    if missing_props:
        return f"flag: captions never mention keywords from {missing_props}"
    return "pass"


def compute_nsvs_bypassed(entry: dict[str, Any]) -> str:
    nsvs = entry.get("nsvs", {})
    output = nsvs.get("output")
    indices = nsvs.get("indices") or []
    foi = entry.get("frames_of_interest")

    if output == [-1] or foi == [-1]:
        return "yes: Storm/FOI returned [-1] (downstream VQA likely unconstrained)"

    if indices:
        empty_count = sum(1 for idxs in indices if not idxs)
        if empty_count == len(indices):
            return "yes: all proposition detection arrays empty"
        if empty_count:
            return f"partial: {empty_count}/{len(indices)} propositions have zero detections"
    return "no"


def benchmark_confound(row: dict[str, str]) -> str:
    source = row.get("source_dataset", "")
    duration = float(row.get("duration_seconds") or 0.0)
    if source in {"star", "agqa"} and duration < 10.0:
        return f"yes: {source} clip {duration:.1f}s (likely time-warped; use 0.25× playback)"
    return "no"


def compute_v3_triage(
    entry: dict[str, Any],
    row: dict[str, str],
    cache_row: dict[str, Any] | None,
) -> dict[str, str]:
    return {
        "PULS_preliminary": compute_puls_preliminary(entry, row),
        "Watch_for": compute_watch_for(entry, row),
        "Caption_coverage": compute_caption_coverage(entry, cache_row),
        "Caption_question_mismatch": compute_caption_question_mismatch(entry, cache_row),
        "NSVS_bypassed": compute_nsvs_bypassed(entry),
        "Benchmark_confound": benchmark_confound(row),
    }


def triage_flagged(field: str, value: str) -> bool:
    if field == "PULS_preliminary":
        return not value.startswith("pass")
    if field == "Caption_question_mismatch":
        return not value.startswith("pass")
    if field == "Caption_coverage":
        return value.startswith("partial") or value.startswith("unknown")
    if field == "NSVS_bypassed":
        return value.startswith("yes") or value.startswith("partial")
    if field == "Benchmark_confound":
        return value.startswith("yes")
    return False


def render_reader_tally_v2() -> list[str]:
    return [
        "## Reader Tally",
        "",
        "After reviewing, tally unchecked boxes here:",
        "",
        "- PULS_ok unchecked: ____ / 25",
        "- NSVS_detect_ok unchecked: ____ / 25",
        "- Storm_interval_ok unchecked: ____ / 25",
        "- VQA_ok unchecked: ____ / 25",
        "",
        "Use the tally as the decision signal: dominant `NSVS_detect_ok` failures point at visual grounding / InternVL; dominant `Storm_interval_ok` failures point at interval semantics / DAG-style logic.",
        "",
        "Tagging criteria:",
        "",
        "- PULS_ok: Does the spec encode the question's actual temporal relationship, and are propositions concrete enough to detect in frames?",
        "- NSVS_detect_ok: For each proposition, do the detection indices land where the frame descriptions say that action is happening? If a visible proposition has zero detections, mark broken.",
        "- Storm_interval_ok: Given the detection arrays, is the returned raw interval the right interval for the spec semantics?",
        "- VQA_ok: Given the final FOI and frame descriptions, does the answer follow from visible evidence?",
        "",
    ]


def render_reader_tally_v3(selected: list[dict[str, str]], triage_by_qid: dict[str, dict[str, str]]) -> list[str]:
    n = len(selected)
    tier1_fields = (
        "PULS_preliminary",
        "NSVS_bypassed",
        "Caption_coverage",
        "Caption_question_mismatch",
        "Benchmark_confound",
    )
    counts = {field: 0 for field in tier1_fields}
    for row in selected:
        triage = triage_by_qid[row["question_id"]]
        for field in tier1_fields:
            if triage_flagged(field, triage[field]):
                counts[field] += 1

    lines = [
        "## Reader Tally",
        "",
        "### Tier 1 — Pre-filled auto triage",
        "",
        "Builder-computed counts across the slice. Use these to prioritize human review.",
        "",
        "| Signal | Flagged rows | / 25 |",
        "| --- | ---: | ---: |",
    ]
    labels = {
        "PULS_preliminary": "PULS_preliminary ≠ pass",
        "NSVS_bypassed": "NSVS_bypassed starts with yes/partial",
        "Caption_coverage": "Caption_coverage partial or unknown",
        "Caption_question_mismatch": "Caption_question_mismatch ≠ pass",
        "Benchmark_confound": "Benchmark_confound = yes (star/agqa <10s)",
    }
    for field in tier1_fields:
        lines.append(f"| {labels[field]} | {counts[field]} | / {n} |")
    lines.extend(
        [
            "",
            "### Tier 2 — Human review (fill after tagging)",
            "",
            "After reviewing each row, tally unchecked boxes here:",
            "",
            f"- PULS_ok unchecked: ____ / {n}",
            f"- NSVS_detect_ok unchecked: ____ / {n}",
            f"- Storm_interval_ok unchecked: ____ / {n}",
            f"- VQA_ok unchecked: ____ / {n}",
            f"- Caption_ok unchecked: ____ / {n}",
            "",
            "Verdict tallies (fill after tagging):",
            "",
            f"- sub1: ____ / {n}",
            f"- sub5b: ____ / {n}",
            f"- both_wrong: ____ / {n}",
            f"- unanswerable: ____ / {n}",
            "",
            "Use Tier 2 as the decision signal: dominant `NSVS_detect_ok` failures point at visual grounding / InternVL; dominant `Storm_interval_ok` failures point at interval semantics / DAG-style logic.",
            "",
            "Tagging criteria:",
            "",
            "- Verdict: After reviewing evidence, which answer is correct? `sub1`, `sub5b`, `both_wrong`, or `unanswerable` (ambiguous / insufficient video).",
            "- PULS_preliminary / PULS_ok: Does the spec encode the question's actual temporal relationship, and are propositions concrete enough to detect in frames?",
            "- Watch_for: Use the per-row hint to know which temporal edge to inspect in captions/video.",
            "- Caption_coverage / Caption_ok: Do sampled captions cover NSVS detections and the final FOI window?",
            "- Caption_question_mismatch: Do captions mention proposition keywords at all?",
            "- NSVS_bypassed: Was Storm/FOI effectively unusable ([-1] or all-empty detections)?",
            "- NSVS_detect_ok: For each proposition, do detection indices land where captions say the action happens?",
            "- Storm_interval_ok: Given detection arrays, is the raw Storm interval correct for the spec semantics?",
            "- VQA_ok: Given final FOI and frame descriptions, does the answer follow from visible evidence?",
            "- Benchmark_confound: star/agqa sub-10s clips may be time-warped; do not over-penalize ordering at 1× playback.",
            "",
        ]
    )
    return lines


def render_tagging_block_v2() -> list[str]:
    return [
        "**Tagging block**",
        "",
        "- PULS_ok: [ ]",
        "- NSVS_detect_ok: [ ]",
        "- Storm_interval_ok: [ ]",
        "- VQA_ok: [ ]",
        "- Notes:",
        "",
    ]


def render_tagging_block_v3(triage: dict[str, str]) -> list[str]:
    return [
        "**Tagging block (v3)**",
        "",
        f"- PULS_preliminary: {safe_text(triage['PULS_preliminary'])}",
        f"- Watch_for: {safe_text(triage['Watch_for'])}",
        f"- Caption_coverage: {safe_text(triage['Caption_coverage'])}",
        f"- Caption_question_mismatch: {safe_text(triage['Caption_question_mismatch'])}",
        f"- NSVS_bypassed: {safe_text(triage['NSVS_bypassed'])}",
        f"- Benchmark_confound: {safe_text(triage['Benchmark_confound'])}",
        "",
        "Human confirmation:",
        "",
        "- Verdict: "
        '<select>'
        '<option value="">— choose —</option>'
        '<option value="sub1">sub1</option>'
        '<option value="sub5b">sub5b</option>'
        '<option value="both_wrong">both_wrong</option>'
        '<option value="unanswerable">unanswerable</option>'
        "</select>",
        "- PULS_ok: [ ]",
        "- NSVS_detect_ok: [ ]",
        "- Storm_interval_ok: [ ]",
        "- VQA_ok: [ ]",
        "- Caption_ok: [ ]",
        "- Notes:",
        "",
    ]


def frame_desc_html(cache_row: dict[str, Any] | None) -> str:
    if not cache_row:
        return "<p><i>No cached frame descriptions available.</i></p>"
    desc = cache_row.get("description", {})
    points = cache_row.get("points")
    frames = desc.get("frames") if isinstance(desc, dict) else None
    if isinstance(points, list) and points:
        if isinstance(frames, list):
            frames = align_frame_descriptions(points, frames)
    if not isinstance(frames, list) or not frames:
        raw = desc.get("raw_response") if isinstance(desc, dict) else None
        if raw:
            return f"<pre><code>{safe_text(raw)}</code></pre>"
        return "<p><i>No frame descriptions returned.</i></p>"
    lines = ["<ul>"]
    for item in frames:
        label = item.get("label", "frame")
        frame = item.get("frame", "?")
        seconds = item.get("seconds", "?")
        description = item.get("description", "")
        lines.append(
            f"<li><b>{safe_text(label)}</b> "
            f"(frame {safe_text(frame)}, {safe_text(seconds)}s): {safe_text(description)}</li>"
        )
    lines.append("</ul>")
    return "\n".join(lines)


def prepare_candidates(rows: list[dict[str, str]], entries: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for row in rows:
        qid = row["question_id"]
        if qid not in entries:
            continue
        enriched = dict(row)
        duration = float(row["duration_seconds"]) if row.get("duration_seconds") else None
        enriched["length_bucket"] = duration_bucket(duration)
        enriched["audit_duration_bucket"] = audit_duration_bucket(duration)
        enriched["operator_family"] = operator_family(row.get("operator_guess", ""))
        candidates.append(enriched)
    return candidates


def diversity_score(row: dict[str, str], selected: list[dict[str, str]]) -> tuple[float, float, str]:
    source_counts = Counter(r["source_dataset"] for r in selected)
    op_counts = Counter(r["operator_family"] for r in selected)
    quality_counts = Counter(r.get("retrieval_quality_bucket", "") for r in selected)
    s = 0.0
    s += max(0, 2 - source_counts[row["source_dataset"]]) * 3
    s += max(0, 2 - op_counts[row["operator_family"]]) * 4
    bucket = row.get("retrieval_quality_bucket", "")
    if bucket:
        s += max(0, 3 - quality_counts[bucket]) * 2
    if row.get("nsvs_indices_any_empty") == "True":
        s += 2
    if row.get("foi_status") == "-1":
        s += 1
    return (-s, float(row["duration_seconds"]), row["question_id"])


def select_rows_stratified(
    candidates: list[dict[str, str]],
    per_bucket: int,
    *,
    allow_nearest_midpoint_fallback: bool = True,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    selected_qids: set[str] = set()

    for bucket_label, _low, _high in AUDIT_DURATION_BUCKETS:
        pool = [
            r
            for r in candidates
            if r["audit_duration_bucket"] == bucket_label and r["question_id"] not in selected_qids
        ]
        bucket_selected: list[dict[str, str]] = []
        while len(bucket_selected) < per_bucket and pool:
            pool.sort(key=lambda r: diversity_score(r, selected + bucket_selected))
            pick = dict(pool.pop(0))
            pick["selection_bucket"] = bucket_label
            pick.setdefault("selection_note", "")
            bucket_selected.append(pick)
            selected_qids.add(pick["question_id"])

        if len(bucket_selected) < per_bucket and allow_nearest_midpoint_fallback:
            midpoint = audit_bucket_midpoint(bucket_label)
            fallback_pool = [
                r for r in candidates if r["question_id"] not in selected_qids and r not in pool
            ]
            fallback_pool = [r for r in fallback_pool if r["question_id"] not in selected_qids]
            fallback_pool.sort(key=lambda r: (abs(float(r["duration_seconds"]) - midpoint), int(r["question_id"])))
            for pick in fallback_pool:
                if len(bucket_selected) >= per_bucket:
                    break
                enriched = dict(pick)
                enriched["selection_bucket"] = bucket_label
                enriched["selection_note"] = "proxy_nearest_midpoint"
                bucket_selected.append(enriched)
                selected_qids.add(enriched["question_id"])

        selected.extend(bucket_selected)

    bucket_order = {label: i for i, (label, _, _) in enumerate(AUDIT_DURATION_BUCKETS)}
    selected.sort(
        key=lambda r: (
            bucket_order.get(r.get("selection_bucket", r["audit_duration_bucket"]), 99),
            float(r["duration_seconds"]),
            int(r["question_id"]),
        )
    )
    return selected


def select_rows(rows: list[dict[str, str]], entries: dict[str, dict[str, Any]], n: int) -> list[dict[str, str]]:
    candidates = prepare_candidates(rows, entries)

    selected: list[dict[str, str]] = []
    selected_qids: set[str] = set()

    # Force coverage for rare/high-risk operator families first.
    must_cover = [
        "since",
        "since",
        "until",
        "until",
        "during",
        "always_before",
        "always_after",
        "before",
        "after",
    ]
    for family in must_cover:
        pool = [r for r in candidates if r["operator_family"] == family and r["question_id"] not in selected_qids]
        if not pool:
            continue
        pool.sort(key=lambda r: (r["source_dataset"], -float(r["duration_seconds"])))
        pick = pool[0]
        selected.append(pick)
        selected_qids.add(pick["question_id"])

    target_len = {"short": 8, "medium": 8, "long": 9}
    target_source = {"agqa": 6, "bf": 7, "ct": 6, "star": 6}
    target_ops = {
        "since": 3,
        "until": 4,
        "during": 1,
        "before": 2,
        "after": 2,
        "always_before": 5,
        "always_after": 2,
    }

    def score(row: dict[str, str]) -> tuple[float, float, str]:
        len_counts = Counter(r["length_bucket"] for r in selected)
        source_counts = Counter(r["source_dataset"] for r in selected)
        op_counts = Counter(r["operator_family"] for r in selected)
        length = row["length_bucket"]
        source = row["source_dataset"]
        op = row["operator_family"]
        s = 0.0
        s += max(0, target_len.get(length, 0) - len_counts[length]) * 6
        s += max(0, target_source.get(source, 0) - source_counts[source]) * 4
        s += max(0, target_ops.get(op, 0) - op_counts[op]) * 5
        if op in {"until", "since"}:
            s += 2
        if row.get("foi_status") == "-1":
            s += 1
        # Prefer deterministic stable IDs after coverage scoring.
        return (-s, float(row["duration_seconds"]), row["question_id"])

    while len(selected) < n:
        remaining = [r for r in candidates if r["question_id"] not in selected_qids]
        if not remaining:
            break
        remaining.sort(key=score)
        pick = remaining[0]
        selected.append(pick)
        selected_qids.add(pick["question_id"])

    # Group the packet by length, then source/operator for easier human scanning.
    selected.sort(
        key=lambda r: (
            {"short": 0, "medium": 1, "long": 2}.get(r["length_bucket"], 9),
            r["source_dataset"],
            r["operator_family"],
            int(r["question_id"]),
        )
    )
    for row in selected:
        row.setdefault("selection_bucket", row["audit_duration_bucket"])
    return selected[:n]


def build_packet(args: argparse.Namespace) -> None:
    entries_list = load_json(args.entries_dir / "merged" / "entries.json")
    entries = {qid_from_entry(entry): entry for entry in entries_list}
    answers_path = resolve_answers_diag(args.entries_dir, args.answers_diag)
    answers = answer_diag_by_qid(answers_path) if answers_path.exists() else {}

    with (args.diag_dir / "disagreements.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))

    candidates = prepare_candidates(rows, entries)
    if args.selected_csv:
        row_by_qid = {row["question_id"]: row for row in candidates}
        selected = []
        with args.selected_csv.open(newline="") as f:
            for picked in csv.DictReader(f):
                qid = picked["question_id"]
                if qid in row_by_qid:
                    selected.append(row_by_qid[qid])
        if not selected:
            raise RuntimeError(f"No matching QIDs found for --selected-csv {args.selected_csv}")
    elif args.stratify_duration_buckets:
        selected = select_rows_stratified(candidates, args.per_bucket)
    else:
        selected = select_rows(rows, entries, args.n)

    frame_desc_cache = ensure_frame_descriptions(args, selected, entries)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    len_counts = Counter(r["length_bucket"] for r in selected)
    audit_counts = Counter(r.get("selection_bucket", r["audit_duration_bucket"]) for r in selected)
    source_counts = Counter(r["source_dataset"] for r in selected)
    op_counts = Counter(r["operator_family"] for r in selected)
    proxy_count = sum(1 for r in selected if r.get("selection_note") == "proxy_nearest_midpoint")

    title = args.packet_title or f"Sub #1/{args.sub_b_label} Disagreement Audit Packet"
    purpose = args.packet_purpose or (
        f"Purpose: a {len(selected)}-row, human-flippable slice of the disagreement set where "
        f"Sub #1 and {args.sub_b_label} gave different answers."
    )

    selected_csv = args.selected_csv if args.version == "v3" and args.selected_csv else args.out.parent / "selected_rows.csv"
    if selected and not (args.version == "v3" and args.selected_csv):
        with selected_csv.open("w", newline="") as f:
            fieldnames = list(selected[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(selected)

    triage_by_qid: dict[str, dict[str, str]] = {}
    cot_by_qid: dict[str, dict[str, Any]] = {}
    cot_order: dict[str, int] = {}
    if args.version == "v3":
        cot_by_qid = load_cot_traces_by_qid(args.cot_traces)
        cot_order = load_cot_traces_order(args.cot_traces)
        for row in selected:
            qid = row["question_id"]
            triage_by_qid[qid] = compute_v3_triage(
                entries[qid],
                row,
                frame_desc_cache.get(qid),
            )
        selected = sort_selected_by_cot_priority(selected, cot_by_qid, cot_order)

    lines: list[str] = []
    lines.extend(
        [
            f"# {title}",
            "",
            purpose,
            "",
            "> Important label caveat: EvalAI does not expose row-level ground truth locally. "
            "Disagreement rows are not conditioned on who was correct.",
            "",
            "## Slice Balance",
            "",
            f"- Rows: {len(selected)}",
            f"- Audit duration buckets: {dict(audit_counts)}",
            f"- Legacy length buckets: {dict(len_counts)}",
            f"- Source dataset: {dict(source_counts)}",
            f"- Operator family: {dict(op_counts)}",
            f"- Nearest-midpoint proxy fills: {proxy_count}",
            f"- Frame-description cache: `{args.frame_desc_cache}`",
            f"- Selected rows CSV: `{selected_csv}`",
            "",
        ]
    )
    if args.version == "v3":
        cot_matched = sum(1 for row in selected if row["question_id"] in cot_by_qid)
        lines.extend(
            [
                f"- CoT traces: `{args.cot_traces}` ({cot_matched}/{len(selected)} rows matched)",
                "",
            ]
        )
        lines.extend(render_cot_priority_section(selected, cot_by_qid, cot_order))
        lines.extend(render_reader_tally_v3(selected, triage_by_qid))
    else:
        lines.extend(render_reader_tally_v2())

    for idx, row in enumerate(selected, start=1):
        qid = row["question_id"]
        entry = entries[qid]
        metadata = entry.get("metadata", {})
        puls = entry.get("puls", {})
        nsvs = entry.get("nsvs", {})
        target = entry.get("target_identification", {})
        answer = answers.get(qid, {})
        foi = entry.get("frames_of_interest")
        nsvs_output = nsvs.get("output")

        options = extract_options(entry.get("question", ""), entry.get("candidates"))
        options_html = "<br>".join(safe_text(option) for option in options) if options else "_not available_"
        reasoning = answer.get("reasoning") or answer.get("explanation")
        reasoning_text = (
            safe_text(reasoning)
            if reasoning
            else f"<i>not persisted: {safe_text(args.sub_b_label)} answerer emits final answer only.</i>"
        )
        sub_b_answer = row.get(args.sub_b_answer_col, "")
        selection_bucket = row.get("selection_bucket", row.get("audit_duration_bucket", "unknown"))
        selection_note = row.get("selection_note", "")
        proxy_note = (
            f"<br><b>Selection note:</b> <i>proxy fill for empty {safe_text(selection_bucket)} bucket "
            f"(actual duration {float(row['duration_seconds']):.1f}s)</i>"
            if selection_note == "proxy_nearest_midpoint"
            else ""
        )
        padding_bits = [
            f"frame_window={target.get('frame_window')}",
            f"nsvs_start_sec={target.get('nsvs_start_sec')}",
            f"nsvs_end_sec={target.get('nsvs_end_sec')}",
        ]
        padding_text = "; ".join(str(bit) for bit in padding_bits if "None" not in str(bit))
        priority_suffix = ""
        if args.version == "v3":
            priority_label = cot_priority_label(cot_by_qid.get(qid))
            priority_suffix = f" / Priority {priority_label}"

        lines.extend(
            [
                f"## {idx}. QID {qid}{priority_suffix} - {metadata.get('source_dataset')} / {selection_bucket} / {row['operator_family']}",
                "",
            ]
        )
        if args.version == "v3":
            lines.extend(render_tagging_block_v3(triage_by_qid[qid]))
        else:
            lines.extend(render_tagging_block_v2())
        lines.extend(
            [
                "<table>",
                "<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>",
                "<tr>",
                "<td>",
                f"<b>Question:</b> {safe_text(entry.get('question'))}<br><br>",
                f"<b>Candidates:</b><br>{options_html}<br><br>",
                f"<b>Sub #1 answer:</b> {safe_text(row.get('sub1_baseline_answer'))}<br>",
                f"<b>{safe_text(args.sub_b_label)} answer:</b> {safe_text(sub_b_answer)}<br>",
                "<b>Ground truth:</b> <i>not available locally</i><br>",
                video_audit_links(entry),
                f"<b>Duration:</b> {float(row['duration_seconds']):.1f}s{proxy_note}",
                "</td>",
                "<td>",
                f"<b>Propositions:</b><br>{fmt_json(puls.get('proposition'))}<br><br>",
                f"<b>TL spec:</b><br><code>{safe_text(puls.get('specification'))}</code><br><br>",
                f"<b>Does this spec encode the question?</b><br>{safe_text(puls_sanity_stub(entry))}",
                "</td>",
                "<td>",
                f"<b>Raw nsvs.indices (per proposition):</b>{fmt_pre_json(nsvs.get('indices'))}",
                f"<b>Raw Storm interval:</b> {fmt_json(nsvs_output)}<br>",
                f"<b>Target-ID padding:</b> <code>{safe_text(padding_text)}</code><br>",
                f"<b>Target-ID explanation:</b> {safe_text(target.get('explanation'))}<br>",
                f"<b>Final FOI:</b> {fmt_json(foi)}",
                "</td>",
                "<td>",
                f"<b>Answer text:</b> {safe_text(answer.get('answer') or sub_b_answer)}<br>",
                f"<b>Raw answer:</b> <code>{safe_text(answer.get('raw'))}</code><br>",
                f"<b>Reasoning:</b> {reasoning_text}<br>",
                f"<b>Frames sampled by answerer:</b> {safe_text(answer.get('num_frames', 'unknown'))}",
                "</td>",
                "</tr>",
                "</table>",
                "",
                "<details open>",
                "<summary><b>Frame Description Block</b></summary>",
                frame_desc_html(frame_desc_cache.get(qid)),
                "</details>",
                "",
            ]
        )
        if args.version == "v3":
            lines.extend(render_cot_rerun_details(cot_by_qid.get(qid)))

    args.out.write_text("\n".join(lines) + "\n")
    print(f"Wrote {args.out}")
    print(f"Frame descriptions cached at {args.frame_desc_cache}")
    print(f"Audit duration buckets: {dict(audit_counts)}")
    print(f"Length buckets: {dict(len_counts)}")
    print(f"Sources: {dict(source_counts)}")
    print(f"Operators: {dict(op_counts)}")
    print(f"Proxy fills: {proxy_count}")
    print(f"Selected rows: {selected_csv}")


def main() -> None:
    build_packet(parse_args())


if __name__ == "__main__":
    main()
