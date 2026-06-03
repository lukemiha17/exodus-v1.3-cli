#!/usr/bin/env bash
# paste.sh <NN-slug> [N]
# Files images you PASTED INTO THE CLAUDE CODE CHAT into screenshots/<NN-slug>.png
# (BYTE-IDENTICAL copy; sources are left intact).
#
# WHY THIS EXISTS / IMPORTANT: pasted images are EPHEMERAL. Claude Code writes
# them to ~/.claude/image-cache/<id>/<n>.png, and macOS also stashes the
# original under /var/folders/.../TemporaryItems/. BOTH self-clean within
# ~1-2 minutes. So FILE EACH PASTE IMMEDIATELY (same turn it arrives) — do not
# batch several pastes and grab later, or the bytes will be gone.
#
# This grabs the newest N PNGs across BOTH sources by mtime, so whichever
# source still holds the bytes wins. N>1 -> -a,-b,-c suffixes, oldest-first.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHOTS="$DIR/screenshots"
mkdir -p "$SHOTS"

name="${1:?usage: paste.sh <NN-slug> [count]}"
count="${2:-1}"

# Candidate sources (newest first). TemporaryItems tends to outlive image-cache.
mapfile -t files < <(
  { ls -t "$HOME/.claude/image-cache/"*/*.png 2>/dev/null
    find /var/folders/*/*/T/TemporaryItems -type f -iname '*.png' 2>/dev/null \
      | while read -r f; do printf '%s\t%s\n' "$(stat -f '%m' "$f")" "$f"; done \
      | sort -rn | cut -f2-
  } | awk '!seen[$0]++' | head -n "$count"
)
if [ "${#files[@]}" -eq 0 ]; then
  echo "No pasted image found in image-cache or TemporaryItems — it may have already rotated. Re-paste and grab immediately." >&2
  exit 1
fi

if [ "$count" -eq 1 ]; then
  cp "${files[0]}" "$SHOTS/$name.png"
  echo "saved: screenshots/$name.png  (from: ${files[0]})"
else
  letters=({a..z})
  for ((i=count-1, j=0; i>=0; i--, j++)); do
    cp "${files[i]}" "$SHOTS/$name-${letters[j]}.png"
    echo "saved: screenshots/$name-${letters[j]}.png  (from: ${files[i]})"
  done
fi
