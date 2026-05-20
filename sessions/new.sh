#!/usr/bin/env bash
# Start a new daily session log from TEMPLATE.md.
# Usage: ./new.sh           # uses today's date
#        ./new.sh 2026-05-20  # uses the given date
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE="${1:-$(date +%F)}"
TARGET="$DIR/$DATE.md"

if [[ -f "$TARGET" ]]; then
    echo "$TARGET already exists; opening." >&2
else
    cp "$DIR/TEMPLATE.md" "$TARGET"
    # Replace the title placeholder with the actual date and an empty headline.
    sed -i "1s/.*/# $DATE \xe2\x80\x94 <one-line headline>/" "$TARGET"
    echo "created $TARGET" >&2
    echo "Don't forget to update sessions/INDEX.md with a one-liner." >&2
fi

if [[ -n "${EDITOR:-}" ]]; then
    "$EDITOR" "$TARGET"
else
    echo "set \$EDITOR to auto-open; created file at $TARGET" >&2
fi
