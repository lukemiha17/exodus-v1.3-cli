#!/usr/bin/env python3
"""
build-readme.py — generate README.md (GitHub-rendered) from the source edits.md.
GitHub renders relative-path images inline, so we convert the
`**Screenshot:** `screenshots/x.png`` code-spans into `![](screenshots/x.png)`
image embeds. Everything else passes through unchanged.
"""
import re
from pathlib import Path

DIR = Path(__file__).resolve().parent
SRC = DIR / "exodus-v1.3-cli-edits.md"
OUT = DIR / "README.md"

def main():
    lines = SRC.read_text().splitlines()
    out = []
    for line in lines:
        m = re.search(r'\*\*Screenshot:\*\*\s*`(screenshots/[^`]+)`', line)
        if m:
            path = m.group(1)
            out.append(f"**Screenshot:**")
            out.append("")
            out.append(f"![{Path(path).name}]({path})")
            out.append("")
        else:
            out.append(line)
    OUT.write_text("\n".join(out) + "\n")
    print(f"built: {OUT}")

if __name__ == "__main__":
    main()
