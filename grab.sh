#!/usr/bin/env bash
# grab.sh <NN-slug> [N]
# Moves the newest screenshot(s) from ~/Desktop into screenshots/<NN-slug>.png
# N (optional) = how many of the newest to grab (default 1). Multiple -> -a, -b, -c suffixes.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHOTS="$DIR/screenshots"
DESK="$HOME/Desktop"
mkdir -p "$SHOTS"

name="${1:?usage: grab.sh <NN-slug> [count]}"
count="${2:-1}"

# Newest <count> screenshot PNGs on the Desktop (macOS names them "Screenshot ...")
mapfile -t files < <(ls -t "$DESK"/Screenshot*.png 2>/dev/null | head -n "$count")
if [ "${#files[@]}" -eq 0 ]; then
  echo "No Screenshot*.png on Desktop. Take the shot (Cmd+Shift+4) first." >&2
  exit 1
fi

if [ "$count" -eq 1 ]; then
  mv "${files[0]}" "$SHOTS/$name.png"
  echo "saved: screenshots/$name.png  (from: $(basename "${files[0]}"))"
else
  letters=({a..z})
  # reverse so oldest-of-the-batch becomes -a (chronological order)
  for ((i=count-1, j=0; i>=0; i--, j++)); do
    mv "${files[i]}" "$SHOTS/$name-${letters[j]}.png"
    echo "saved: screenshots/$name-${letters[j]}.png  (from: $(basename "${files[i]}"))"
  done
fi
