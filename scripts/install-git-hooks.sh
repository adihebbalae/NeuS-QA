#!/usr/bin/env bash
# Point this repo at synced hooks that strip Cursor co-author attribution.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
chmod +x .githooks/prepare-commit-msg
git config core.hooksPath .githooks
echo "core.hooksPath=.githooks (Cursor attribution will be stripped from commits)"
