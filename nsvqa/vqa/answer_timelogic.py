"""TimeLogic-specific downstream answerer (lever C).

For each entry (with optional `frames_of_interest` from NSVS), sample N frames
from the satisfying interval, send them to an OpenAI Vision-capable chat model
along with the question and candidates, and parse the model's reply into the
EvalAI submission format.

Handles both TimeLogic modes:
- `mc`   → returns "A" | "B" | "C" | "D"
- `bool` → returns "Yes" | "No"

EvalAI submission format (per the workshop spec):
    [{"question_id": "1", "answer_choice": "D"},
     {"question_id": "2", "answer_choice": "Yes"}, ...]

This deliberately bypasses the upstream `nsvqa/vqa/vqa.py`, which is:
1. MC-only (no Yes/No branch)
2. Tied to a cluster-specific localhost vLLM server pattern
3. Outputs a different per-entry diagnostic JSON, not EvalAI's submission format

For 17/2000 val entries the source video is missing from the zip; we default
to "A" / "Yes" rather than skipping so the submission still covers every
question_id (EvalAI may penalize omissions).
"""

from openai import OpenAI

import base64
import cv2
import json
import numpy as np
import os
import time


DEFAULT_NUM_FRAMES = 8
DEFAULT_JPEG_QUALITY = 85
DEFAULT_IMAGE_DETAIL = "low"  # "low" / "auto" / "high" — low is fine + cheap for 8 frames


def sample_frames(video_path: str, num_frames: int, frame_range: list | None = None) -> list:
    """Sample `num_frames` BGR frames evenly from `video_path`.

    If `frame_range` is `[start, end]` and not the `[-1]` sentinel, sample within
    that interval; otherwise sample across the full video.
    """
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total == 0:
        cap.release()
        return []

    if frame_range and frame_range != [-1] and len(frame_range) == 2:
        s, e = int(frame_range[0]), int(frame_range[1])
    else:
        s, e = 0, total - 1
    s = max(0, s)
    e = min(total - 1, e)
    if e <= s:
        s, e = 0, total - 1

    if (e - s + 1) <= num_frames:
        idxs = list(range(s, e + 1))
    else:
        idxs = np.linspace(s, e, num_frames, dtype=int).tolist()

    images = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok and frame is not None:
            images.append(frame)
    cap.release()
    return images


def encode_jpeg(frame_bgr, quality: int = DEFAULT_JPEG_QUALITY) -> str | None:
    ok, buf = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return None
    return base64.b64encode(buf).decode("utf-8")


def format_puls_hint(propositions: list[str] | None, specification: str | None) -> str:
    """Format the PULS output (proposition list + TL spec) as a structured
    hint to insert into the answerer's user prompt. The VLM gets atomic events
    to look for and the temporal pattern between them. Returns "" if either
    field is missing."""
    if not propositions or not specification:
        return ""
    pretty_props = ", ".join(p.replace("_", " ") for p in propositions)
    return (
        "\nTemporal-logic decomposition of the question:\n"
        f"  Atomic events to look for: {pretty_props}\n"
        f"  Temporal pattern (U = until, & = and, ! = not): {specification}\n"
        "Use this decomposition to focus on the right events in the right "
        "order; the answer should be consistent with the pattern.\n"
    )


def build_prompt(
    question: str,
    candidates: list[str],
    mode: str,
    puls_hint: str = "",
) -> tuple[str, str, list[str]]:
    """Returns (system_prompt, user_text, valid_answers).

    If `puls_hint` is non-empty, it is inserted between the question and the
    answer instruction so the VLM can use the temporal-logic decomposition.
    """
    if mode == "mc":
        letters = ["A", "B", "C", "D"]
        formatted = "\n".join(f"{lt}: {c}" for lt, c in zip(letters, candidates))
        sys_p = (
            "You are a careful video-understanding assistant for a temporal-reasoning "
            "benchmark (CVPR 2026 TimeLogic). Answer multiple-choice questions about "
            "video content by replying with ONE letter only: A, B, C, or D. No "
            "explanation, no punctuation, no other text."
        )
        user_t = (
            "The images above are a temporally-ordered sampling of frames from the "
            "relevant interval of the video.\n\n"
            f"Question: {question}\n"
            f"{puls_hint}\n"
            f"Options:\n{formatted}\n\n"
            "Reply with exactly one letter: A, B, C, or D."
        )
        return sys_p, user_t, letters

    if mode == "bool":
        sys_p = (
            "You are a careful video-understanding assistant for a temporal-reasoning "
            "benchmark (CVPR 2026 TimeLogic). Answer Yes/No questions about video "
            "content by replying with ONE word only: 'Yes' or 'No'. No explanation, "
            "no punctuation, no other text."
        )
        user_t = (
            "The images above are a temporally-ordered sampling of frames from the "
            "relevant interval of the video.\n\n"
            f"Question: {question}\n"
            f"{puls_hint}\n"
            "Reply with exactly one word: Yes or No."
        )
        return sys_p, user_t, ["Yes", "No"]

    raise ValueError(f"unknown mode {mode!r}")


def parse_answer(raw: str, valid_answers: list[str]) -> str:
    """Best-effort: find which valid answer the model meant. Falls back to
    the first valid answer (A / Yes) if nothing matches.

    Strategy:
    1. Exact match after stripping punctuation (common case: model emits "A").
    2. Word-boundary regex search across the whole string. If multiple valid
       answers match, prefer the LAST occurrence — the model's final answer
       is usually at the end ("I think B but actually D" → D). Word boundaries
       prevent "ANSWER" from false-matching 'A'.
    """
    import re

    s = (raw or "").strip()
    for ch in ['"', "'", ".", ",", ":", ";", "(", ")", "[", "]", "*", "`"]:
        s = s.replace(ch, "")
    s = s.strip()
    s_upper = s.upper()

    for v in valid_answers:
        if s_upper == v.upper():
            return v

    matches: list[tuple[int, str]] = []
    for v in valid_answers:
        pattern = rf"\b{re.escape(v)}\b"
        for m in re.finditer(pattern, s_upper, re.IGNORECASE):
            matches.append((m.start(), v))
    if matches:
        matches.sort()
        return matches[-1][1]

    return valid_answers[0]


def _is_reasoning_model(model: str) -> bool:
    """gpt-5.x and o-series are reasoning models that use max_completion_tokens,
    reject temperature=0.0, and accept reasoning_effort. Older gpt-4 / gpt-4o
    models use the legacy max_tokens + temperature API.
    """
    m = model.lower()
    return m.startswith("gpt-5") or m.startswith("o1") or m.startswith("o3") or m.startswith("o4")


def _build_completion_kwargs(model: str, max_output_tokens: int = 512) -> dict:
    """Return the model-appropriate keyword args for chat.completions.create.

    Reasoning models (gpt-5.x, o1/o3/o4): `max_completion_tokens` INCLUDES
    reasoning tokens. Empirically on the TimeLogic vision payload with
    reasoning_effort="low", gpt-5.2 consumed ~150-200 reasoning tokens
    before emitting the actual answer. cap=128 was being entirely eaten by
    reasoning (finish_reason=length, empty content); cap=512 leaves a
    comfortable buffer. Billing is on actual tokens used, so the cap is a
    free safety margin.

    Legacy models (gpt-4 / gpt-4o family): plain max_tokens + temperature=0.0
    for deterministic short outputs. 16 is enough for the single letter or
    Yes/No reply we ask for.
    """
    if _is_reasoning_model(model):
        return {
            "max_completion_tokens": max_output_tokens,
            "reasoning_effort": "low",
        }
    return {
        "max_tokens": 16,
        "temperature": 0.0,
    }


def answer_one(
    client: OpenAI,
    model: str,
    video_path: str,
    frame_range: list | None,
    question: str,
    candidates: list[str],
    mode: str,
    num_frames: int = DEFAULT_NUM_FRAMES,
    image_detail: str = DEFAULT_IMAGE_DETAIL,
    puls_hint: str = "",
) -> dict:
    frames = sample_frames(video_path, num_frames, frame_range)
    if not frames:
        return {
            "answer": "A" if mode == "mc" else "Yes",
            "error": "no_frames_sampled",
            "raw": None,
            "num_frames": 0,
        }

    encoded = [encode_jpeg(f) for f in frames]
    encoded = [e for e in encoded if e is not None]
    if not encoded:
        return {
            "answer": "A" if mode == "mc" else "Yes",
            "error": "all_frames_encoding_failed",
            "raw": None,
            "num_frames": 0,
        }

    sys_p, user_t, valid_ans = build_prompt(question, candidates, mode, puls_hint=puls_hint)
    user_content = []
    for e in encoded:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{e}", "detail": image_detail},
        })
    user_content.append({"type": "text", "text": user_t})

    completion_kwargs = _build_completion_kwargs(model)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_p},
            {"role": "user", "content": user_content},
        ],
        store=False,
        **completion_kwargs,
    )
    raw = resp.choices[0].message.content
    answer = parse_answer(raw, valid_ans)
    return {
        "answer": answer,
        "raw": raw,
        "num_frames": len(encoded),
    }


def answer_timelogic(
    entries: list[dict],
    model: str = "gpt-4o-mini",
    num_frames: int = DEFAULT_NUM_FRAMES,
    output_dir: str | None = None,
    image_detail: str = DEFAULT_IMAGE_DETAIL,
    verbose: bool = True,
) -> tuple[list[dict], list[dict]]:
    """Answer each entry's question via OpenAI Vision and write the submission JSON.

    Returns (submission_records, diag_records).
    """
    client = OpenAI()
    submission: list[dict] = []
    diag: list[dict] = []

    for i, entry in enumerate(entries):
        qid = entry["metadata"]["question_id"]
        mode = entry["metadata"]["mode"]
        video_path = entry["paths"]["video_path"]
        candidates = entry["candidates"]
        question = entry["metadata"].get("cleaned_question") or entry["question"]
        foi = entry.get("frames_of_interest")

        # Default-answer for missing videos so we still cover every question_id
        if not entry["metadata"].get("video_present", True) or not os.path.isfile(video_path):
            default = "A" if mode == "mc" else "Yes"
            submission.append({"question_id": qid, "answer_choice": default})
            diag.append({
                "qid": qid, "mode": mode, "answer": default,
                "error": "video_missing_on_disk", "seconds": 0.0,
            })
            if verbose:
                print(f"[answer {i+1}/{len(entries)}] qid={qid} mode={mode} → {default} (missing video)")
            continue

        puls_data = entry.get("puls") or {}
        puls_hint = format_puls_hint(
            puls_data.get("proposition"),
            puls_data.get("specification"),
        )

        t0 = time.time()
        try:
            result = answer_one(
                client, model, video_path, foi, question, candidates, mode,
                num_frames=num_frames, image_detail=image_detail,
                puls_hint=puls_hint,
            )
        except Exception as exc:
            result = {
                "answer": "A" if mode == "mc" else "Yes",
                "error": repr(exc),
                "raw": None,
                "num_frames": 0,
            }
        result["seconds"] = round(time.time() - t0, 2)

        submission.append({"question_id": qid, "answer_choice": result["answer"]})
        diag_entry = {
            "qid": qid, "mode": mode, "foi": foi,
            "candidates": candidates if mode == "mc" else None,
            **result,
        }
        diag.append(diag_entry)

        if verbose:
            err = f"  ERR: {result.get('error')!r}" if result.get("error") else ""
            print(
                f"[answer {i+1}/{len(entries)}] qid={qid} mode={mode} "
                f"foi={foi} frames={result.get('num_frames')} → "
                f"{result.get('answer')!r}  ({result.get('seconds')}s)  raw={result.get('raw')!r}{err}"
            )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        sub_path = os.path.join(output_dir, "submission.json")
        diag_path = os.path.join(output_dir, "answers_diag.json")
        with open(sub_path, "w") as f:
            json.dump(submission, f, indent=2)
        with open(diag_path, "w") as f:
            json.dump(diag, f, indent=2, default=str)
        if verbose:
            print(f"\n[answer] wrote {sub_path}")
            print(f"[answer] wrote {diag_path}")

    return submission, diag
