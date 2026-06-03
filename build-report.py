#!/usr/bin/env python3
"""
build-report.py — turn exodus-v1.3-cli-edits.md into a single self-contained
HTML report with screenshots base64-embedded inline next to each finding.

Output: exodus-v1.3-cli-report.html (one file, share-with-Brad ready).

It scans the markdown for image references of the form:
    ![alt](screenshots/NN-slug.png)
  OR  - **Screenshot:** `screenshots/NN-slug.png`
and embeds the actual image bytes so the HTML has no external dependencies.
The markdown itself stays the machine/AI-readable source of truth.
"""
import base64, html, mimetypes, re, sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
MD = DIR / "exodus-v1.3-cli-edits.md"
OUT = DIR / "exodus-v1.3-cli-report.html"

def embed(rel: str) -> str:
    p = (DIR / rel).resolve()
    if not p.exists():
        return f'<div class="missing">⚠ missing image: {html.escape(rel)}</div>'
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return (f'<figure><img src="data:{mime};base64,{b64}" alt="{html.escape(rel)}">'
            f'<figcaption>{html.escape(rel)}</figcaption></figure>')

def md_to_html(text: str) -> str:
    out, in_code = [], False
    for line in text.splitlines():
        # fenced code
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append("<pre>" if in_code else "</pre>")
            continue
        if in_code:
            out.append(html.escape(line)); continue
        # ![alt](screenshots/..)
        m = re.search(r'!\[[^\]]*\]\((screenshots/[^)]+)\)', line)
        if m:
            out.append(embed(m.group(1))); continue
        # - **Screenshot:** `screenshots/..`
        m = re.search(r'\*\*Screenshot:\*\*\s*`(screenshots/[^`]+)`', line)
        if m:
            out.append("<p><strong>Screenshot:</strong></p>")
            out.append(embed(m.group(1))); continue
        # headings
        h = re.match(r'^(#{1,4})\s+(.*)', line)
        if h:
            lvl = len(h.group(1)); out.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>"); continue
        if re.match(r'^\s*---\s*$', line):
            out.append("<hr>"); continue
        if line.strip().startswith(("- ", "| ")) or line.strip() == "":
            out.append(f"<div class='ln'>{inline(line)}</div>"); continue
        out.append(f"<p>{inline(line)}</p>")
    return "\n".join(out)

def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

CSS = """
body{font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:2rem auto;padding:0 1.2rem;color:#1a1a1a}
h1,h2,h3,h4{line-height:1.2}h1{border-bottom:3px solid #e8674c}h3{color:#c44;margin-top:2rem}
code{background:#f4f4f4;padding:1px 5px;border-radius:4px;font-size:.9em}
pre{background:#1e1e1e;color:#eee;padding:1rem;border-radius:8px;overflow:auto;font-size:13px}
figure{margin:1rem 0;border:1px solid #ddd;border-radius:8px;overflow:hidden}
img{display:block;max-width:100%;height:auto}
figcaption{font-size:12px;color:#888;padding:6px 10px;background:#fafafa;border-top:1px solid #eee}
.missing{color:#b00;background:#fee;padding:8px;border-radius:6px}
.ln{white-space:pre-wrap}hr{border:0;border-top:1px solid #e3e3e3;margin:2rem 0}
"""

def main():
    if not MD.exists():
        sys.exit(f"missing {MD}")
    body = md_to_html(MD.read_text())
    OUT.write_text(f"<!doctype html><meta charset=utf-8><title>Exodus v1.3 CLI Audit</title>"
                   f"<style>{CSS}</style>\n{body}\n")
    print(f"built: {OUT}")

if __name__ == "__main__":
    main()
