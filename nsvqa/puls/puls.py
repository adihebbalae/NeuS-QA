from nsvqa.puls.llm import *
from nsvqa.puls.prompts import *
import json
import os
import re

def clean_and_parse_json(raw_str):
    start = raw_str.find('{')
    end = raw_str.rfind('}') + 1
    json_str = raw_str[start:end]
    return json.loads(json_str)

def process_specification(specification, propositions):
    new_propositions = []
    for prop in propositions:
        prop_cleaned = re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", prop)
        prop_cleaned = re.sub(r"\s+", "_", prop_cleaned)
        prop_cleaned = prop_cleaned.replace("'", "").replace("-", "_").lower()
        prop_cleaned = re.sub(r'[^a-zA-Z0-9_]', '', prop_cleaned)
        new_propositions.append(prop_cleaned)

    replacements = sorted(
        list(zip(propositions, new_propositions)),
        key=lambda x: len(x[0]),
        reverse=True
    )
    for original, new in replacements:
        # Replace every occurrence; the descending length sort above prevents a
        # shorter proposition from corrupting a longer one that contains it as
        # a substring (e.g. 'fall' vs 'person falls').
        if specification.count(original) >= 1:
            specification = specification.replace(original, f'"{new}"')

    replacements = {
        "AND": "&",
        "OR": "|",
        "UNTIL": "U",
        "ALWAYS": "G",
        "EVENTUALLY": "F",
        "NOT": "!"
    }
    for word, symbol in replacements.items():
        specification = specification.replace(word, symbol)

    # specification = specification.replace("U", "& F")
    # if 'G "' in specification:
    #     specification = specification.replace('G "', 'F "')

    return new_propositions, specification

def PULS(prompt, openai_key=None, model=None):
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

    llm = LLM(model=model) if model else LLM()

    full_prompt = find_prompt(prompt)
    llm_output = llm.prompt(full_prompt)
    parsed = clean_and_parse_json(llm_output)

    final_output = {}

    cleaned_props, processed_spec = process_specification(parsed["specification"], parsed["proposition"])
    final_output["proposition"] = cleaned_props
    final_output["specification"] = processed_spec

    saved_path = llm.save_history()
    final_output["saved_path"] = saved_path
    final_output["api_cost_usd"] = llm.last_cost_usd
    final_output["api_usage"] = usage_dict(llm.last_usage)

    return final_output


def PULS_atemporal_mc(question: str, choices: list[dict], openai_key=None, model=None) -> dict:
    """
    Run the atemporal-MC PULS mode. Returns:
    {
      "propositions": [<one per choice>],
      "specifications": [<one per choice>],
      "choice_letters": ["A", "B", "C", "D"],
      "saved_path": ...,
      "api_cost_usd": ...,
      "api_usage": ...
    }
    On guardrail reject, includes "error" and omits proposition/spec lists.
    """
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

    llm = LLM(model=model) if model else LLM()

    full_prompt = find_prompt_atemporal_mc(question, choices)
    llm_output = llm.prompt(full_prompt)
    parsed = clean_and_parse_json(llm_output)

    saved_path = llm.save_history()
    api_cost_usd = llm.last_cost_usd
    api_usage = usage_dict(llm.last_usage)

    if parsed.get("error"):
        return {
            "error": parsed["error"],
            "saved_path": saved_path,
            "api_cost_usd": api_cost_usd,
            "api_usage": api_usage,
        }

    raw_props = parsed["propositions"]
    raw_specs = parsed["specifications"]
    raw_letters = parsed["choice_letters"]
    if not (len(raw_props) == len(raw_specs) == len(raw_letters) == len(choices)):
        raise ValueError(
            f"atemporal_mc output length mismatch: "
            f"propositions={len(raw_props)} specifications={len(raw_specs)} "
            f"choice_letters={len(raw_letters)} choices={len(choices)}"
        )

    by_letter = {}
    for letter, prop, spec in zip(raw_letters, raw_props, raw_specs):
        by_letter[str(letter).strip()] = (prop, spec)

    cleaned_props = []
    cleaned_specs = []
    out_letters = []
    for c in choices:
        letter = str(c.get("letter", "")).strip()
        if letter not in by_letter:
            raise ValueError(f"atemporal_mc missing choice letter {letter!r} in model output")
        prop, spec = by_letter[letter]
        props_one, spec_one = process_specification(spec, [prop])
        cleaned_props.append(props_one[0])
        cleaned_specs.append(spec_one)
        out_letters.append(letter)

    return {
        "propositions": cleaned_props,
        "specifications": cleaned_specs,
        "choice_letters": out_letters,
        "saved_path": saved_path,
        "api_cost_usd": api_cost_usd,
        "api_usage": api_usage,
    }
