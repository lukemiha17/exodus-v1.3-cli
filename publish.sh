#!/usr/bin/env bash
# publish.sh — regenerate README + HTML from edits.md and push to GitHub.
# Run after adding new findings/screenshots so Brad's link stays current.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
python3 build-readme.py
python3 build-report.py
git add -A
git -c user.email="lukemiha@gmail.com" -c user.name="lukemiha17" \
    commit -qm "${1:-Update dashboard audit}" || { echo "nothing to commit"; exit 0; }
git push -q origin main
echo "published: https://github.com/lukemiha17/exodus-v1.3-cli"