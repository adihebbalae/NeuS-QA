"""Resolve ffmpeg executable: system PATH, then imageio-ffmpeg bundle in .venv."""

from __future__ import annotations

import os
import shutil


def get_ffmpeg_exe() -> str:
    override = os.environ.get("FFMPEG")
    if override:
        if not os.path.isfile(override) or not os.access(override, os.X_OK):
            raise RuntimeError(f"FFMPEG={override!r} is not an executable file")
        return override

    exe = shutil.which("ffmpeg")
    if exe:
        return exe

    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError(
            "ffmpeg not found on PATH and imageio-ffmpeg is not installed. "
            "Run: uv pip install imageio-ffmpeg"
        ) from exc

    bundled = imageio_ffmpeg.get_ffmpeg_exe()
    if not bundled or not os.path.isfile(bundled):
        raise RuntimeError("imageio-ffmpeg installed but bundled ffmpeg binary is missing")
    return bundled
