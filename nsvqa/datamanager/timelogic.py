"""TimeLogic dataset loader for the CVPR 2026 VidLLMs workshop challenge #2690.

Annotation schema (per `Swetha5/TimeLogic@challenge/data/val/timelogic_val_data.json`):
    [{"question_id": str, "video_id": str, "mode": "mc"|"bool", "question": str}, ...]

The schema has no `candidates` field (for `mc`, the four options are baked into the
question string), no ground-truth field (cannot score locally; submit to EvalAI), and
no per-question operator label.

This loader produces entries in the dict shape that NeuS-QA's `evaluate.py` pipeline
already expects (`question`, `candidates`, `paths.video_path`, `metadata.*`).
"""

from nsvqa.datamanager.manager import Manager

import json
import os
import re
from tqdm import tqdm


_MC_PATTERN = re.compile(
    r"Option\s*A\s*:\s*(.+?)\s*,\s*"
    r"Option\s*B\s*:\s*(.+?)\s*,\s*"
    r"Option\s*C\s*:\s*(.+?)\s*,\s*"
    r"Option\s*D\s*:\s*(.+?)\s*(?:\.|\?)?\s*(?:Reply|$)",
    re.IGNORECASE | re.DOTALL,
)

_MC_PREAMBLE = re.compile(
    r"^\s*The following is a multiple choice question[^.]*?answer choices?\s*:\s*A\s*,\s*B\s*,\s*C\s*,\s*D\s*\.\s*",
    re.IGNORECASE,
)

_MC_CHOICE_BLOCK = re.compile(
    r"\s*Is it\s*Option\s*A\s*:.*?(?:Reply[^.]*\.|$)",
    re.IGNORECASE | re.DOTALL,
)

_OPERATOR_PROBES = [
    ("immediately_before", r"\bimmediately\s+before\b"),
    ("immediately_after", r"\bimmediately\s+after\b"),
    ("always_before", r"\balways\s+(?:occurs\s+)?before\b"),
    ("always_after", r"\balways\s+(?:occurs\s+)?after\b"),
    ("in_turn_occurs", r"\bin\s+turn\s+occurs\b"),
    ("between", r"\bbetween\b"),
    ("starts_doing", r"\bstart(?:s|ed)?\s+(?:doing|to)\b"),
    ("stops_doing", r"\bstop(?:s|ped)?\s+(?:doing|to)\b"),
    ("since", r"\bsince\b"),
    ("until", r"\buntil\b"),
    ("while", r"\bwhile\b"),
    ("during", r"\bduring\b"),
    ("when", r"\bwhen\b"),
    ("before", r"\bbefore\b"),
    ("after", r"\bafter\b"),
]


def parse_mc_choices(question: str) -> list[str]:
    """Extract the four MC choice texts from a TimeLogic MC question.

    Returns ['A', 'B', 'C', 'D'] as a degenerate fallback if the pattern does not match,
    so the downstream pipeline still sees a 4-element list.
    """
    m = _MC_PATTERN.search(question)
    if not m:
        return ["A", "B", "C", "D"]
    return [m.group(i).strip().rstrip(",.").strip() for i in range(1, 5)]


def infer_operator(question: str) -> str:
    """Best-effort operator family guess from question text (diagnostics only)."""
    q = question.lower()
    for tag, pat in _OPERATOR_PROBES:
        if re.search(pat, q):
            return tag
    return "unknown"


def strip_mc_scaffolding(question: str) -> str:
    """Strip the MC boilerplate so LQ2TL sees a clean natural-language question.

    Removes (1) the 'The following is a multiple choice question ... A, B, C, D.'
    preamble, (2) the 'Is it Option A: ..., Option B: ..., Option C: ..., Option D: ...
    Reply with ...' tail. The remaining text is the temporal question itself, which is
    what PULS needs in order to extract propositions and the TL spec.
    """
    q = _MC_PREAMBLE.sub("", question)
    q = _MC_CHOICE_BLOCK.sub("", q)
    return q.strip()


class TimeLogic(Manager):
    """Loader for the TimeLogic challenge."""

    def __init__(
        self,
        split: str = "val",
        video_root: str | None = None,
        ann_path: str | None = None,
        postprocess_dir: str | None = None,
        current_split: int | None = None,
        verbose: bool = True,
    ):
        self.split = split
        self.video_root = video_root or os.environ.get("TIMELOGIC_VAL_VIDEOS")
        self.ann_path = ann_path or os.environ.get(
            "TIMELOGIC_VAL_ANN" if split == "val" else "TIMELOGIC_TEST_ANN"
        )
        self.postprocess_dir = postprocess_dir
        self.current_split = current_split
        self.verbose = verbose

        if not self.video_root or not self.ann_path:
            raise ValueError(
                "TimeLogic loader needs both video_root and ann_path "
                "(or env vars TIMELOGIC_VAL_VIDEOS / TIMELOGIC_VAL_ANN)."
            )

    def load_data(self) -> list:
        with open(self.ann_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        entries: list[dict] = []
        missing_files: list[str] = []
        on_disk = set(os.listdir(self.video_root))

        for item in raw:
            mode = item["mode"]
            question = item["question"]
            video_id = item["video_id"]

            if mode == "mc":
                candidates = parse_mc_choices(question)
            elif mode == "bool":
                candidates = ["Yes", "No"]
            else:
                raise ValueError(f"unknown mode {mode!r} for question_id={item['question_id']}")

            video_path = os.path.join(self.video_root, video_id)
            video_present = video_id in on_disk
            if not video_present:
                missing_files.append(video_id)

            entries.append({
                "question": question,
                "candidates": candidates,
                "paths": {"video_path": video_path},
                "metadata": {
                    "question_id": item["question_id"],
                    "video_id": video_id,
                    "id": item["question_id"],
                    "mode": mode,
                    "source_dataset": video_id.split("_", 1)[0],
                    "operator_guess": infer_operator(question),
                    "video_present": video_present,
                    "cleaned_question": strip_mc_scaffolding(question) if mode == "mc" else question,
                },
            })

        if self.verbose:
            print(f"[TimeLogic] loaded {len(entries)} entries from {self.ann_path}")
            print(f"[TimeLogic] missing videos: {len(missing_files)} "
                  f"({len(missing_files) / max(1, len(entries)):.1%}); they will be answered with a default fallback")
            mc = sum(1 for e in entries if e['metadata']['mode'] == 'mc')
            bo = sum(1 for e in entries if e['metadata']['mode'] == 'bool')
            print(f"[TimeLogic] modes: {mc} mc, {bo} bool")

        return entries

    def postprocess_data(self, nsvqa_dir: str) -> None:
        """Crop the satisfying interval out of each video using the upstream
        ffmpeg-based `crop_video`, and persist a postprocess JSON that the
        downstream VQA step consumes.

        The submission JSON itself is written by `write_submission` after VQA runs.
        """
        if self.postprocess_dir is None or self.current_split is None:
            raise ValueError("postprocess_dir and current_split must be set on the loader")

        os.makedirs(self.postprocess_dir, exist_ok=True)
        cropped_dir = os.path.join(self.postprocess_dir, "cropped_videos")
        os.makedirs(cropped_dir, exist_ok=True)

        nsvs_file = os.path.join(nsvqa_dir, f"nsvqa_output_{self.current_split}.json")
        with open(nsvs_file, "r") as f:
            nsvs_data = json.load(f)

        out_entries = []
        for entry in tqdm(nsvs_data, desc="postprocess/crop"):
            qid = entry["metadata"]["question_id"]
            cropped_path = os.path.join(cropped_dir, f"{qid}.mp4")
            entry["paths"]["cropped_path"] = cropped_path

            if not entry["metadata"].get("video_present", True):
                entry["metadata"]["crop_error"] = "source video missing on disk"
                entry["paths"]["cropped_path"] = entry["paths"]["video_path"]
            else:
                try:
                    self.crop_video(entry, save_path=cropped_path, ground_truth=False)
                except Exception as e:
                    entry["metadata"]["crop_error"] = repr(e)
                    entry["paths"]["cropped_path"] = entry["paths"]["video_path"]

            out_entries.append(entry)

        out_file = os.path.join(self.postprocess_dir, f"postprocess_output_{self.current_split}.json")
        with open(out_file, "w") as f:
            json.dump(out_entries, f, indent=4)

    @staticmethod
    def write_submission(answers: list[dict], submission_path: str) -> None:
        """Write the EvalAI-format submission JSON.

        `answers` must be a list of {"question_id": str, "answer_choice": "A"|"B"|"C"|"D"|"Yes"|"No"}.
        """
        os.makedirs(os.path.dirname(submission_path), exist_ok=True)
        with open(submission_path, "w") as f:
            json.dump(answers, f, indent=2)
