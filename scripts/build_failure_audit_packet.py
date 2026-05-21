#!/usr/bin/env python3
"""Build a human-readable Sub #1/Sub #2 disagreement audit packet.

EvalAI does not expose row-level labels locally. The 244/208 split in planning
docs is inferred from aggregate score math, not known per-row correctness, so
this packet samples from the full Sub #1/Sub #2 disagreement set.
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


DEFAULT_DIAG = Path("/home/ah66742/timelogic-data/outputs/diagnostics/sub1_vs_sub2")
DEFAULT_SUB2 = Path("/mnt/Data/ah66742/timelogic/outputs/nsvs_sub2_v2")
DEFAULT_OUT = DEFAULT_DIAG / "failure_audit_packet.md"
DEFAULT_FRAME_DESC_CACHE = DEFAULT_DIAG / "failure_audit_frame_descriptions.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diag-dir", type=Path, default=DEFAULT_DIAG)
    p.add_argument("--sub2-dir", type=Path, default=DEFAULT_SUB2)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--n", type=int, default=25)
    p.add_argument("--frame-desc-cache", type=Path, default=DEFAULT_FRAME_DESC_CACHE)
    p.add_argument("--vision-model", default="gpt-4o-mini")
    p.add_argument("--env-file", default=os.path.expanduser("~/.env"))
    p.add_argument("--force-frame-desc", action="store_true")
    p.add_argument("--skip-api", action="store_true", help="Do not call OpenAI; use only cached frame descriptions")
    return p.parse_args()


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


def frame_description_points(entry: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = entry.get("metadata", {})
    frame_count = int(metadata.get("frame_count") or 0)
    fps = float(metadata.get("fps") or 0.0)
    if frame_count <= 0:
        return []

    raw = entry.get("nsvs", {}).get("output")
    foi = entry.get("frames_of_interest")
    points: list[tuple[str, int]] = [
        ("0% of video", 0),
        ("25% of video", round((frame_count - 1) * 0.25)),
        ("50% of video", round((frame_count - 1) * 0.50)),
        ("75% of video", round((frame_count - 1) * 0.75)),
        ("100% of video", frame_count - 1),
    ]

    if valid_interval(foi):
        points.append(("FOI midpoint", (int(foi[0]) + int(foi[1])) // 2))
    else:
        points.append(("FOI fallback midpoint/full-video midpoint", (frame_count - 1) // 2))

    if valid_interval(raw):
        points.append(("reference moment from raw Storm midpoint", (int(raw[0]) + int(raw[1])) // 2))

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for label, idx in points:
        frame = clamp_frame(int(idx), frame_count)
        key = (label, frame)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(
            {
                "label": label,
                "frame": frame,
                "seconds": round(frame / fps, 3) if fps else None,
            }
        )
    return deduped


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
        max_tokens=1200,
        temperature=0.0,
    )
    text = response.choices[0].message.content or ""
    parsed = parse_json_object(text)
    parsed["status"] = "ok"
    return parsed


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


def frame_desc_html(cache_row: dict[str, Any] | None) -> str:
    if not cache_row:
        return "<p><i>No cached frame descriptions available.</i></p>"
    desc = cache_row.get("description", {})
    frames = desc.get("frames") if isinstance(desc, dict) else None
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


def select_rows(rows: list[dict[str, str]], entries: dict[str, dict[str, Any]], n: int) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for row in rows:
        qid = row["question_id"]
        if qid not in entries:
            continue
        row = dict(row)
        row["length_bucket"] = duration_bucket(float(row["duration_seconds"]))
        row["operator_family"] = operator_family(row.get("operator_guess", ""))
        candidates.append(row)

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
    return selected[:n]


def build_packet(args: argparse.Namespace) -> None:
    entries_list = load_json(args.sub2_dir / "merged" / "entries.json")
    entries = {qid_from_entry(entry): entry for entry in entries_list}
    answers = answer_diag_by_qid(args.sub2_dir / "answers_gpt52" / "answers_diag.json")

    with (args.diag_dir / "disagreements.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    selected = select_rows(rows, entries, args.n)
    frame_desc_cache = ensure_frame_descriptions(args, selected, entries)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    len_counts = Counter(r["length_bucket"] for r in selected)
    source_counts = Counter(r["source_dataset"] for r in selected)
    op_counts = Counter(r["operator_family"] for r in selected)

    lines: list[str] = []
    lines.extend(
        [
            "# Sub #1/Sub #2 Disagreement Audit Packet",
            "",
            "Purpose: a 25-row, human-flippable slice of the full 452-question set where Sub #1 and Sub #2 disagreed.",
            "",
            "> Important label caveat: EvalAI does not expose row-level ground truth locally. The 244/208 split in the planning doc is inferred from aggregate score math: 452 disagreements and Sub #1's aggregate +35 net advantage imply ~243.5 vs ~208.5 if every disagreement has exactly one correct answer. It is not a row-level label, so this packet does not condition on who won.",
            "",
            "## Slice Balance",
            "",
            f"- Rows: {len(selected)}",
            f"- Video length: {dict(len_counts)}",
            f"- Source dataset: {dict(source_counts)}",
            f"- Operator family: {dict(op_counts)}",
            f"- Frame-description cache: `{args.frame_desc_cache}`",
            "",
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
    )

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
            else "<i>not persisted: Sub #2's historical answerer prompted the VLM to emit only the final answer.</i>"
        )

        lines.extend(
            [
                f"## {idx}. QID {qid} - {metadata.get('source_dataset')} / {row['length_bucket']} / {row['operator_family']}",
                "",
                "**Tagging block**",
                "",
                "- PULS_ok: [ ]",
                "- NSVS_detect_ok: [ ]",
                "- Storm_interval_ok: [ ]",
                "- VQA_ok: [ ]",
                "- Notes:",
                "",
                "<table>",
                "<tr><th>Question and Answers</th><th>PULS Output</th><th>NSVS Trace</th><th>VQA Output</th></tr>",
                "<tr>",
                "<td>",
                f"<b>Question:</b> {safe_text(entry.get('question'))}<br><br>",
                f"<b>Candidates:</b><br>{options_html}<br><br>",
                f"<b>Sub #1 answer:</b> {safe_text(row.get('sub1_baseline_answer'))}<br>",
                f"<b>Sub #2 answer:</b> {safe_text(row.get('sub2_nsvs_answer'))}<br>",
                "<b>Ground truth:</b> <i>not available locally</i><br>",
                f"<b>Video:</b> {safe_text(metadata.get('video_id'))}<br>",
                f"<b>Duration:</b> {float(row['duration_seconds']):.1f}s",
                "</td>",
                "<td>",
                f"<b>Propositions:</b><br>{fmt_json(puls.get('proposition'))}<br><br>",
                f"<b>TL spec:</b><br><code>{safe_text(puls.get('specification'))}</code><br><br>",
                f"<b>Does this spec encode the question?</b><br>{safe_text(puls_sanity_stub(entry))}",
                "</td>",
                "<td>",
                f"<b>Full detection arrays per proposition:</b>{fmt_pre_json(nsvs.get('indices'))}",
                f"<b>Raw Storm interval:</b> {fmt_json(nsvs_output)}<br>",
                f"<b>Target-ID window:</b> <code>{safe_text(target.get('frame_window'))}</code><br>",
                f"<b>Target-ID explanation:</b> {safe_text(target.get('explanation'))}<br>",
                f"<b>Final FOI:</b> {fmt_json(foi)}",
                "</td>",
                "<td>",
                f"<b>Answer text:</b> {safe_text(answer.get('answer') or row.get('sub2_nsvs_answer'))}<br>",
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

    args.out.write_text("\n".join(lines) + "\n")
    print(f"Wrote {args.out}")
    print(f"Frame descriptions cached at {args.frame_desc_cache}")
    print(f"Length buckets: {dict(len_counts)}")
    print(f"Sources: {dict(source_counts)}")
    print(f"Operators: {dict(op_counts)}")


def main() -> None:
    build_packet(parse_args())


if __name__ == "__main__":
    main()
