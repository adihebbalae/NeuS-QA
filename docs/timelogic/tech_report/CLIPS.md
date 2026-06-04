# Tech report — video clips (v1)

Curated **source benchmark** MP4s for the CVPR TimeLogic write-up. Queries and pass/fail labels come in a later pass.

## Where the files live

| Item | Path |
| --- | --- |
| Clip symlinks + manifest | `reports/tech_report/v1_clips/` (in NeuS-QA repo) |
| HTML gallery (inline players) | `reports/tech_report/v1_clips/gallery.html` |
| Machine-readable index | `v1_clips/manifest.json` |

### Viewing from your laptop (Remote SSH)

**Do not click `vscode-remote://` links in Chrome/Edge** — Windows has no handler; those links only work inside Cursor/VS Code.

**Option A — play MP4s in Cursor (easiest)**

1. In the file tree, open `v1_clips/source/` on the server path above.
2. Click an `.mp4` — Cursor’s built-in preview should play it (same as any remote file).

**Option B — gallery in Cursor Simple Browser**

1. `Ctrl+Shift+P` → **Simple Browser: Show**.
2. Paste this path (server path; Simple Browser resolves it over SSH):

   `/home/ah66742/NeuS-QA/reports/tech_report/v1_clips/gallery.html`

   If that fails, use Option C.

**Option C — cached clip gallery (recommended)**

Use the dedicated script (serves **only** `v1_clips/`, not the NeuS-QA repo):

```bash
fuser -k 8765/tcp   # if an old http.server is still bound
cd /home/ah66742/NeuS-QA
python3 scripts/serve_clip_gallery.py --port 8765
```

Forward port **8765**, then open:

`http://127.0.0.1:8765/gallery.html`

1. Page loads **without downloading anything** (fixes reload hang).
2. Cached clips restore from IndexedDB automatically.
3. Click **Download missing clips** only when you want local smooth playback, or **Stream all** to play immediately over the tunnel.
4. **Clear browser cache** if stuck; close the old tab before reopening.

Do **not** run `python3 -m http.server` from `~/NeuS-QA` — that serves the repo and breaks clip URLs.

**Option D — copy clips to your PC**

```bash
scp -r ah66742@ece-859525:/home/ah66742/NeuS-QA/reports/tech_report/v1_clips ~/Downloads/timelogic-clips
```

Then double-click `gallery.html` under `~/Downloads/timelogic-clips` in Explorer.

## What’s in the set (14 clips)

| # | Split | QID | Source | ~Duration | Notes |
| ---: | --- | ---: | --- | ---: | --- |
| 01 | val | 1809 | star | 0.56s | Sub-1s; audit disagreement row |
| 02 | val | 1014 | star | 0.72s | `since` operator |
| 03 | val | 1215 | agqa | 1.0s | Valid FOI (non −1) |
| 04 | val | 1252 | agqa | 1.04s | FOI = −1 |
| 05 | val | 107 | bf | 39s | Natural-length breakfast |
| 06 | val | 808 | bf | 45s | `unknown` operator |
| 07 | val | 1911 | ct | 72s | Charades |
| 08 | val | 738 | ct | 77s | Clean FOI window |
| 09 | val | 1525 | bf | 137s | Long kitchen clip |
| 10 | val | 1590 | ct | 181s | Long Charades |
| 11 | test | 1 | star | 0.6s | Sub #9; cropped twin in `cropped_sub9/` |
| 12 | test | 2 | agqa | 1.4s | Sub #9 |
| 13 | test | 500 | bf | 30s | Sub #9 |
| 14 | test | 1500 | ct | 201s | Sub #9 |

Val rows **01–10** are drawn from the Sub #5B failure-audit slice (`diagnostics/sub5b_failure_audit_v3/selected_rows.csv`). Test rows **11–14** are from Sub #9 PULS v2 test; `cropped_sub9/` holds the ffmpeg crops the VLM actually saw.

## Playback note (STAR / AGQA)

Roughly half of val STAR/AGQA videos are **under 2 seconds** (often time-compressed). For temporal ordering questions, use **0.25× speed** when reviewing — same guidance as the failure-audit packet.

## Step 2 — queries

| Artifact | Path |
| --- | --- |
| Markdown report (all 14) | `docs/timelogic/tech_report/QUERIES.md` |
| Gallery (inline under each clip) | `gallery.html` + `manifest.json` |

Regenerate after clip set changes:

```bash
python3 scripts/build_clip_gallery_meta.py
```

Each clip includes: full question, A–D or Yes/No choices, **PULS spec**, Sub #1 / Sub #5B (val) or Sub #7b (test), and Sub1↔5B **disagree** flag on val audit rows.

## Step 3 — what worked / failed (next)

Needs EvalAI val label export (or PI-provided GT) to mark correct vs wrong. Until then, use Sub1 vs Sub5B disagreement as a proxy on val clips.
