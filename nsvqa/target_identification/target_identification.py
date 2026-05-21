from nsvqa.puls.llm import LLM
import json


def clean_and_parse_json(raw_str):
    start = raw_str.find("{")
    end = raw_str.rfind("}") + 1
    json_str = raw_str[start:end]
    return json.loads(json_str)


def process_datapoint(
    llm,
    question,
    candidates,
    specification,
    nsvs_start_sec: float | None = None,
    nsvs_end_sec: float | None = None,
):
    """Predict second offsets to pad the NSVS satisfying interval before VQA.

    `target_frame_window` must be two signed integer second offsets applied to
    the NSVS interval start/end frame indices: "[+before_start_sec, +after_end_sec]".
    """
    if nsvs_start_sec is not None and nsvs_end_sec is not None:
        window_line = (
            f"Identified temporal window for the specification (from model checking): "
            f"[{nsvs_start_sec:.2f}, {nsvs_end_sec:.2f}] seconds in the video."
        )
        offset_instruction = (
            'Return target_frame_window as two signed integer second offsets in the form '
            '"[+before_start_sec, +after_end_sec]" to pad that interval. '
            'Example: "[+2, +8]" extends 2 seconds before the interval start and '
            '8 seconds after the interval end. Use 0 when no padding is needed on that side.'
        )
    else:
        window_line = (
            "Identified temporal window for the specification: unknown (not yet retrieved)."
        )
        offset_instruction = (
            'Return target_frame_window as "[+0, +0]" if you cannot infer useful padding.'
        )

    prompt = f"""The neuro-symbolic pipeline has already found a video interval where the temporal-logic specification is satisfied. Your job is to choose how many seconds to pad that interval before/after so the downstream VLM can answer the question.

{window_line}

Based on the temporal relationship in the question, choose padding relative to that interval:
1. For "after" questions: small padding before the interval end, larger padding after the interval end
2. For "before" questions: larger padding before the interval start, small padding after the interval start
3. For "during" questions: modest padding on both sides (about 2-3 seconds each)

{offset_instruction}

Inputs:
Question: {question}
Specification: {specification}
Possible answers (candidates):
{chr(10).join(f"- {candidate}" for candidate in candidates)}

Expected Output (only output the following JSON structure — nothing else):
{{
  "target_frame_window": "[+0, +0]",
  "explanation": "..."
}}
"""

    response = llm.prompt(prompt)
    response = clean_and_parse_json(response)
    target_frame_window = response["target_frame_window"]
    explanation = response["explanation"]

    history_path = llm.save_history("target")

    return {
        "frame_window": target_frame_window,
        "explanation": explanation,
        "saved_path": history_path,
    }


def identify_target(
    question,
    candidates,
    specification,
    conversation_history,
    model=None,
    nsvs_start_sec: float | None = None,
    nsvs_end_sec: float | None = None,
):
    with open(conversation_history, "r") as f:
        history = json.load(f)

    llm = LLM(history=history, model=model) if model else LLM(history=history)

    return process_datapoint(
        llm,
        question,
        candidates,
        specification,
        nsvs_start_sec=nsvs_start_sec,
        nsvs_end_sec=nsvs_end_sec,
    )
