"""Render ../docs/*.md to PDF in this folder (Python-Markdown + headless Chrome).

Usage: python3 build_pdfs.py
"""
import html
import pathlib
import re
import subprocess
import tempfile

import markdown

HERE = pathlib.Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 18pt; border-bottom: 2px solid #0b6bcb; padding-bottom: 4px; }
h2 { font-size: 13.5pt; margin-top: 18px; color: #0b3d75; }
h3 { font-size: 11.5pt; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.5pt; }
th, td { border: 1px solid #c8d0da; padding: 4px 7px; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
tr, h2, h3 { break-inside: avoid; }
code { background: #f2f4f7; padding: 0 3px; border-radius: 3px; }
pre { background: #f2f4f7; padding: 8px; white-space: pre-wrap; }
blockquote { border-left: 3px solid #0b6bcb; margin: 8px 0; padding: 2px 10px; color: #444; }
.foot { margin-top: 24px; font-size: 8pt; color: #777; border-top: 1px solid #ddd; padding-top: 4px; }
"""


LIST_ITEM = re.compile(r"^\s*([-*]|\d+\.)\s")


def normalise(text: str) -> str:
    """Insert the blank line Python-Markdown needs before a list."""
    out = []
    for line in text.splitlines():
        if LIST_ITEM.match(line) and out and out[-1].strip() and not LIST_ITEM.match(out[-1]):
            out.append("")
        out.append(line)
    return "\n".join(out)


def build(md_path: pathlib.Path, tmp: pathlib.Path) -> pathlib.Path:
    body = markdown.markdown(normalise(md_path.read_text(encoding="utf-8")),
                             extensions=["tables", "fenced_code", "nl2br"])
    # keep codes such as F-217 or EC-KIT-217 on one line
    body = re.sub(r"\b([A-Z]{1,3}(?:-[A-Z0-9]+)+)\b", r'<span style="white-space:nowrap">\1</span>', body)
    page = (
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(md_path.stem)}</title>'
        f"<style>{CSS}</style></head><body>{body}"
        '<p class="foot">Fictional demo document (EPOWER Infrastructure Solutions).</p></body></html>'
    )
    html_file = tmp / f"{md_path.stem}.html"
    html_file.write_text(page, encoding="utf-8")
    pdf = HERE / f"{md_path.stem}.pdf"
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf}", html_file.as_uri()],
        check=True, capture_output=True,
    )
    return pdf


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as t:
        for md in sorted(DOCS.glob("*.md")):
            out = build(md, pathlib.Path(t))
            print(f"{out.name}: {out.stat().st_size // 1024} KB")
