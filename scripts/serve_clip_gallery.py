#!/usr/bin/env python3
"""Serve TimeLogic report clips from v1_clips only (not the NeuS-QA repo).

On startup, copies symlinked benchmark MP4s into ``_serve_cache/`` and loads
them into RAM (~80 MB for the current set). The browser gallery prefetches each
clip once over the port-forward, then plays from an in-memory blob URL (smooth
seek/scrub) instead of re-streaming from the server.

Usage (remote terminal, then forward port in Cursor):

    python3 scripts/serve_clip_gallery.py --port 8765

On laptop:

    http://127.0.0.1:8765/gallery.html
"""

from __future__ import annotations

import argparse
import http.server
import os
import shutil
import socketserver
import urllib.parse
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "reports" / "tech_report" / "v1_clips"
CLIP_PREFIXES = ("/source/", "/cropped_sub9/")

# URL path -> raw mp4 bytes (filled at startup)
MEM_CACHE: dict[str, bytes] = {}


class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def materialize_clips(root: Path) -> Path:
    """Copy real MP4 bytes into _serve_cache (follow symlinks to benchmark videos)."""
    cache_root = root / "_serve_cache"
    total = 0
    for sub in ("source", "cropped_sub9"):
        src_dir = root / sub
        if not src_dir.is_dir():
            continue
        dst_dir = cache_root / sub
        dst_dir.mkdir(parents=True, exist_ok=True)
        for link in sorted(src_dir.glob("*.mp4")):
            dst = dst_dir / link.name
            real = link.resolve()
            if not real.is_file():
                raise SystemExit(f"Broken clip symlink: {link} -> {real}")
            if not dst.exists() or dst.stat().st_size != real.stat().st_size:
                shutil.copy2(real, dst)
            total += 1
    if total == 0:
        raise SystemExit(f"No .mp4 files under {root}/source — wrong --root?")
    return cache_root


def load_mem_cache(root: Path) -> int:
    cache_root = materialize_clips(root)
    MEM_CACHE.clear()
    nbytes = 0
    for sub in ("source", "cropped_sub9"):
        subdir = cache_root / sub
        if not subdir.is_dir():
            continue
        for mp4 in sorted(subdir.glob("*.mp4")):
            key = f"/{sub}/{mp4.name}"
            data = mp4.read_bytes()
            MEM_CACHE[key] = data
            nbytes += len(data)
    return nbytes


class GalleryHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static gallery; MP4s from RAM cache with long browser cache headers."""

    def clip_cache_key(self) -> str | None:
        clean = urllib.parse.unquote(self.path.split("?", 1)[0])
        for prefix in CLIP_PREFIXES:
            if clean.startswith(prefix) and clean.endswith(".mp4"):
                return clean
        return None

    def do_GET(self) -> None:
        key = self.clip_cache_key()
        if key and key in MEM_CACHE:
            data = MEM_CACHE[key]
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400, immutable")
            self.send_header("Accept-Ranges", "none")
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path in ("", "/"):
            self.send_response(302)
            self.send_header("Location", "/gallery.html")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self) -> None:
        if self.path.endswith((".html", "json")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def guess_type(self, path: str) -> str:
        if path.endswith(".mp4"):
            return "video/mp4"
        return super().guess_type(path)

    def log_message(self, format: str, *args) -> None:
        # Quieter logs for large clip payloads during prefetch
        if args and isinstance(args[0], str) and ".mp4" in args[0] and args[1].startswith("2"):
            return
        super().log_message(format, *args)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="v1_clips directory only")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--no-mem-cache", action="store_true", help="Disk _serve_cache only, no RAM preload")
    args = p.parse_args()
    root = args.root.resolve()
    if not (root / "gallery.html").is_file():
        raise SystemExit(f"Not a clip folder (missing gallery.html): {root}")

    if args.no_mem_cache:
        materialize_clips(root)
        print(f"Warmed disk cache under {root / '_serve_cache'} (no RAM preload)")
    else:
        nbytes = load_mem_cache(root)
        print(f"Loaded {len(MEM_CACHE)} clips into RAM ({nbytes / (1024 * 1024):.1f} MB)")

    os.chdir(root)
    try:
        httpd = ReuseTCPServer((args.bind, args.port), GalleryHandler)
    except OSError as e:
        if e.errno == 98:
            raise SystemExit(
                f"Port {args.port} is already in use.\n"
                f"  fuser -k {args.port}/tcp\n"
                f"  Or: python3 scripts/serve_clip_gallery.py --port 8766"
            ) from e
        raise

    with httpd:
        print(f"Serving clips only: {root}")
        print(f"  Open: http://{args.bind}:{args.port}/gallery.html")
        print("  (Page loads instantly; use buttons to stream or download clips.)")
        print("Forward port {0} in Cursor → laptop opens http://127.0.0.1:{0}/gallery.html".format(args.port))
        print("Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
