#!/usr/bin/env python3
"""Build taxonomy contact sheet montage (Task 5)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _lib import AFRL_ROOT


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--taxonomy", type=Path, default=AFRL_ROOT / "taxonomy.json")
    p.add_argument("--out", type=Path, default=AFRL_ROOT / "taxonomy_contact_sheet.png")
    p.add_argument("--thumb-width", type=int, default=320)
    return p.parse_args()


def pick_key_frame(record: dict) -> Path | None:
    frames = record.get("frames") or []
    if not frames:
        return None
    foi_frames = [f for f in frames if "_foi" in Path(f).name]
    if foi_frames:
        return Path(foi_frames[len(foi_frames) // 2])
    return Path(frames[len(frames) // 2])


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    args = parse_args()
    records = json.loads(args.taxonomy.read_text(encoding="utf-8"))
    if not records:
        raise SystemExit("empty taxonomy.json")

    cols = min(4, len(records))
    rows = (len(records) + cols - 1) // cols
    label_h = 48
    thumb_w = args.thumb_width
    thumb_h = int(thumb_w * 9 / 16)

    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), color=(24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = load_font(14)

    for i, rec in enumerate(records):
        r, c = divmod(i, cols)
        x0 = c * thumb_w
        y0 = r * (thumb_h + label_h)
        frame_path = pick_key_frame(rec)
        if frame_path and frame_path.is_file():
            img = Image.open(frame_path).convert("RGB")
            img.thumbnail((thumb_w, thumb_h))
            px = x0 + (thumb_w - img.width) // 2
            py = y0 + (thumb_h - img.height) // 2
            sheet.paste(img, (px, py))
        tag = rec.get("taxonomy_tag", "?")
        dur = rec.get("duration_s")
        dur_s = f"{float(dur):.1f}s" if dur is not None else "?"
        label = f"q{rec['qid']} | {tag} | {dur_s}"
        draw.text((x0 + 8, y0 + thumb_h + 8), label, fill=(230, 230, 230), font=font)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(f"[contact] wrote {args.out} ({cols}x{rows} grid)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
