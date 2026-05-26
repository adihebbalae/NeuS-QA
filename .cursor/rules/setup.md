# TimeLogic / NeuS-QA — Server Bootstrap

What actually exists on the host `ece-859525`. Update when paths, mounts, or pinned versions change.

**Where this lives**: `.cursor/rules/setup.md` in `adihebbalae/NeuS-QA` fork. Soft convention: the **server** is the source of truth for this file (host facts live where the host is); the laptop side just reads it.

Last updated: 2026-05-26.

## Host facts

| Property | Value |
| --- | --- |
| Hostname | `ece-859525` |
| User | `ah66742@austin.utexas.edu` |
| Home disk | `/dev/mapper/ubuntu--vg-lv--0` — 3.5 TB total, ~560 GB free |
| Big local disk | `/mnt/Data` — 1.8 TB total, ~1.7 TB free, writable by us |
| GPUs | 8 × NVIDIA RTX A5000 (24 GB each), driver 590.48.01, CUDA 13.1 |
| System Python | `/usr/bin/python3.10` (3.10.12) |
| `ffmpeg` / `ffprobe` | System **`/usr/bin/ffmpeg`** after 2026-05-26 driver reboot; fallback **`imageio-ffmpeg`** in `.venv` via `nsvqa/utils/ffmpeg_path.py`. Container probe fallback: OpenCV in `.venv`. |
| Compilers | gcc/g++ 11.4, cmake 3.22, GNU Make 4.3 |
| `OPENAI_API_KEY` | set in `~/.env` (loaded explicitly by `run_timelogic.py --env-file`) |
| Fork clone | `/home/ah66742/NeuS-QA` (origin: `git@github.com:adihebbalae/NeuS-QA.git`, working branch: `timelogic-adapt`) |
| Upstream TimeLogic clone | `/home/ah66742/TimeLogic-Specs/upstream/` (kept out of the fork; do not mix) |
| tmux | 3.2a — used for any task > 10 min per `.cursor/rules/workflow.md` |
| SSH key | `~/.ssh/id_ed25519.pub` registered with GitHub; `ssh git@github.com` authenticates as `adihebbalae` |

## Storage layout (chosen 2026-05-19)

NAS at `/nas` is configured in `/etc/fstab` as a CIFS share to `//swarmcluster6.ece.utexas.edu/sambashare` with credentials at `/home/lab-admin/.smbcredentials`, but **not currently mounted** on this host — the mountpoint is empty and unwritable to our account. Requires lab-admin to mount it. Lab-admin has OK'd staying on `/mnt/Data` indefinitely.

```
/mnt/Data/ah66742/
├── timelogic/
│   ├── raw/              # downloaded zips (val_videos.zip, test_videos.zip)
│   ├── annotations/      # mirrored JSON from Swetha5/TimeLogic@challenge
│   ├── videos/
│   │   ├── val/          # unzipped val mp4s (combined_2k_videos/)
│   │   └── test/         # unzipped test mp4s (staged 2026-05-22)
│   ├── outputs/          # NeuS-QA per-run output dirs (smoke_v0..v4 so far)
│   ├── models/           # optional override HF cache (currently using ~/.cache/huggingface)
│   └── logs/             # download logs, sweep logs
└── hf_cache/             # reserved, not currently used
```

Symlink for convenience: `~/timelogic-data → /mnt/Data/ah66742/timelogic`.

`~/.cache/huggingface` (default) is used for model weights — home has enough room for InternVL2.5-8B (~16 GB) and Qwen2.5-VL-7B (~14 GB).

## Repo bootstrap (already done)

```bash
# NeuS-QA fork already cloned at /home/ah66742/NeuS-QA (origin: adihebbalae/NeuS-QA)
cd /home/ah66742/NeuS-QA

# uv installed via official script -> ~/.local/bin/uv (v0.11.15)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# pyproject.toml originally requires Python >=3.13. We relaxed to >=3.12
# because tokenizers==0.20.3 (forced by transformers<4.47) has no cp313
# wheel, and its sdist's pyproject.toml is malformed for modern uv.
# Pin Python 3.12 and sync:
uv python pin 3.12         # writes .python-version
uv sync                    # ~1 min, pulls torch 2.9, stormpy 1.11.3, transformers 4.46.3, ...

# build_dependency.sh is NOT needed for this server's smoke path.
# The prebuilt stormpy==1.11.3 wheel ships with Storm bundled; we verified
# `stormpy.build_model(prism_program)` works without a system Storm install.
# Only re-run build_dependency.sh if a future feature needs a custom Storm.
```

To re-enter the environment in a fresh shell:

```bash
export PATH="$HOME/.local/bin:$PATH"
cd /home/ah66742/NeuS-QA
source .venv/bin/activate              # or: uv run python ...
```

## TimeLogic data

```bash
# Val annotations (small, cloned)
cd /home/ah66742/TimeLogic-Specs
git clone --branch challenge --depth 1 https://github.com/Swetha5/TimeLogic.git upstream
# Source of truth: upstream/data/val/timelogic_val_data.json (2000 entries, 697 KB)

# Val videos zip — 23.4 GB, downloaded to /mnt/Data/ah66742/timelogic/raw/
cd /mnt/Data/ah66742/timelogic/raw
nohup curl -L --fail --retry 5 --retry-delay 10 --continue-at - \
  -o val_videos.zip \
  "https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/val_videos.zip" \
  > /mnt/Data/ah66742/timelogic/logs/val_videos_download.log 2>&1 &

# After it finishes, unzip into videos/val/
cd /mnt/Data/ah66742/timelogic
unzip -q raw/val_videos.zip -d videos/val/
# 2032 files unzipped; 17/2000 questions reference videos missing from the zip (0.85%)

# Test set (staged 2026-05-22)
cd /mnt/Data/ah66742/timelogic/raw
curl -L --fail -o test_videos.zip \
  "https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/test_videos.zip"
curl -L --fail -o timelogic_test_data.json \
  "https://www.crcv.ucf.edu/cvpr2026-vidllms-workshop/challenge/data/timelogicqa/test/timelogic_test_data.json"
```

## Environment file (recommended)

Create `~/.timelogic_env` and source from `.bashrc` for every shell:

```bash
export TIMELOGIC_ROOT=/mnt/Data/ah66742/timelogic
export TIMELOGIC_VAL_VIDEOS=$TIMELOGIC_ROOT/videos/val/combined_2k_videos
export TIMELOGIC_TEST_VIDEOS=$TIMELOGIC_ROOT/videos/test
export TIMELOGIC_VAL_ANN=/home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json
export TIMELOGIC_OUT=$TIMELOGIC_ROOT/outputs
export NSVQA_LLM_HISTORY_DIR=$TIMELOGIC_OUT/_llm_history_default
export PATH="$HOME/.local/bin:$PATH"
```

`run_timelogic.py` reads `--env-file ~/.env` for the OpenAI key explicitly; the OpenAI client doesn't auto-load dotenv files.

## Git hooks (once per clone)

Strip Cursor co-author attribution from all commits:

```bash
cd /home/ah66742/NeuS-QA
./scripts/install-git-hooks.sh
```

Sets `core.hooksPath=.githooks` (repo-local). Also disable **Cursor Settings → Agent → Attribution** in the IDE on each machine.

## Running the smoke

```bash
cd /home/ah66742/NeuS-QA
source .venv/bin/activate
python3 scripts/run_timelogic.py \
  --video-root /mnt/Data/ah66742/timelogic/videos/val/combined_2k_videos \
  --ann-path /home/ah66742/TimeLogic-Specs/upstream/data/val/timelogic_val_data.json \
  --output-dir /mnt/Data/ah66742/timelogic/outputs/smoke_v5 \
  --device 0 \
  --limit 20 \
  --seed 0 \
  --proposition-model InternVL2-2B
```

For runs > 10 minutes, wrap in tmux per `.cursor/rules/workflow.md`:

```bash
tmux new-session -d -s smoke_v5 \
  "cd /home/ah66742/NeuS-QA && source .venv/bin/activate && \
   python3 scripts/run_timelogic.py ... > /mnt/Data/ah66742/timelogic/outputs/smoke_v5/run.log 2>&1"
# Then: detach immediately (already detached due to -d), tail the log when ready
tmux ls
tmux attach -t smoke_v5    # attach to monitor
# Ctrl-b d                  # detach again
```

## Open env items

- **NAS**: pending lab-admin to mount `/nas` on this host so we can mirror artifacts to the shared NAS for the rest of the lab. Until then, local `/mnt/Data` only.
- **Future tests on other lab machines**: any artifact we want shared with Minkyu / Harsh has to go to NAS once mounted.
- **InternVL2-8B**: lever B fixed — device-map + model reuse verified (`smoke_v8_8b_reuse`, Sub #5B val/test).
