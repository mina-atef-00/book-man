#!/usr/bin/env python3
"""Static pre-flight for a book-man HTML page. Layout checks are done in a browser.

Usage:  python3 check_html_page.py /home/mina/wiki/<book>/pages/<page>.html
Exit 1 on any FAIL.
"""
import pathlib
import re
import sys

BLOCK = [
    "section", "div", "svg", "table", "thead", "tbody", "details", "figure",
    "nav", "main", "header", "footer", "ul", "ol", "tr", "td", "th",
    "h1", "h2", "h3", "p",
]


def main(path: str) -> int:
    src = pathlib.Path(path).read_text(encoding="utf-8")
    fails: list[str] = []
    warns: list[str] = []

    if not src.lstrip().lower().startswith("<!doctype html"):
        fails.append("missing <!doctype html>")
    if re.search(r"<script", src, re.I):
        fails.append("script tag present - pages must be CSS-only")
    if 'name="viewport"' not in src:
        fails.append("missing viewport meta")

    for tag in BLOCK:
        opened = len(re.findall(rf"<{tag}[\s>]", src))
        closed = len(re.findall(rf"</{tag}>", src))
        if opened != closed:
            fails.append(f"unbalanced <{tag}>: {opened} open / {closed} close")

    ids = set(re.findall(r'id="([^"]+)"', src))
    missing = sorted({h for h in re.findall(r'href="#([^"]+)"', src) if h not in ids})
    if missing:
        fails.append("nav targets with no matching id: " + ", ".join(missing))

    if re.search(r"<svg[\s\S]*?var\(--", src):
        fails.append("CSS variable inside SVG - renders as black fill")

    sizes = [int(v) for v in re.findall(r'font-size="(\d+)"', src)]
    if sizes and min(sizes) < 26:
        warns.append(
            f"smallest SVG font-size {min(sizes)} viewBox units "
            "- confirm measured height >= 17px in the browser"
        )

    print(f"{path}\n  {len(src):,} bytes")
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    if fails:
        print(f"\n{len(fails)} failure(s). Fix, then run the browser layout pass.")
        return 1
    print("\nStatic checks pass. Next: 390px scroll tie, SVG label height, no text past the viewBox.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
