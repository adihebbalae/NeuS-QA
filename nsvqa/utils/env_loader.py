"""Load dotenv-style files; map OPENAI_API_KEY1/2 to OPENAI_API_KEY when needed."""

import os


def load_env_file(path: str) -> None:
    if not path or not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
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
