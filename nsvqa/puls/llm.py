from openai import OpenAI
import datetime
import json
import os

from nsvqa.utils.api_cost import cost_from_usage, estimate_text_call, usage_dict


DEFAULT_SAVE_DIR = os.environ.get(
    "NSVQA_LLM_HISTORY_DIR",
    "/nas/mars/experiment_result/nsvqa/9_post_submission/llm_conversation_history/",
)


class LLM:
    def __init__(self, model="gpt-4o", history=None, save_dir=None):
        """Initialize LLM. save_dir defaults to NSVQA_LLM_HISTORY_DIR env var."""
        self.client = OpenAI()
        self.model = model
        if history:
            self.history = history
        else:
            self.history = []
        if save_dir is None:
            save_dir = os.environ.get(
                "NSVQA_LLM_HISTORY_DIR",
                "/nas/mars/experiment_result/nsvqa/9_post_submission/llm_conversation_history/",
            )
        self.save_dir = save_dir
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        self.last_usage = None
        self.last_cost_usd: float | None = None

    def prompt(self, p):
        """Send a prompt to the LM and update conversation history"""
        user_message = {"role": "user", "content": [{"type": "text", "text": p}]}
        self.history.append(user_message)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            store=False,
        )
        self.last_usage = getattr(response, "usage", None)
        self.last_cost_usd = cost_from_usage(self.model, self.last_usage)
        if self.last_cost_usd is None:
            self.last_cost_usd = estimate_text_call(self.model)
        assistant_response = response.choices[0].message.content
        assistant_message = {"role": "assistant", "content": [{"type": "text", "text": assistant_response}]}
        self.history.append(assistant_message)

        return assistant_response

    def save_history(self, suffix=""):
        """Save conversation history to a JSON file and return the save path"""
        if not self.save_dir:
            return None
        if suffix:
            filename = f"conversation_history_target_{suffix}.json"
        else:
            filename = "conversation_history_target.json"

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, extension = os.path.splitext(filename)
        timestamped_filename = f"{base_name}_{timestamp}{extension}"

        save_path = os.path.join(self.save_dir, timestamped_filename)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)
        return save_path

