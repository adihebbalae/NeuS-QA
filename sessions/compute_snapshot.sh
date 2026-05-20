#!/usr/bin/env bash
# Print a single-shot compute footprint snapshot.
# Append the output into the day's session log under `## Compute footprint`.
#
# Usage:
#   ./compute_snapshot.sh                 # to stdout
#   ./compute_snapshot.sh >> 2026-05-19.md
set -euo pipefail

echo "### snapshot $(date -Iseconds)"
echo

echo "**GPUs (index, name, mem.used, util.gpu):**"
echo
echo '```'
nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader 2>/dev/null \
    || echo "nvidia-smi unavailable"
echo '```'
echo

echo "**Disk:**"
echo
echo '```'
df -h /mnt/Data /home 2>/dev/null
echo
echo "/mnt/Data/ah66742 total:"
du -sh /mnt/Data/ah66742 2>/dev/null
echo "/mnt/Data/ah66742/timelogic/* breakdown:"
du -sh /mnt/Data/ah66742/timelogic/* 2>/dev/null
echo
echo "~/.cache/huggingface (model weights cache):"
du -sh "$HOME/.cache/huggingface" 2>/dev/null || echo "(none)"
echo '```'
echo

echo "**Load + RAM:**"
echo
echo '```'
uptime
echo
free -h | head -3
echo '```'
