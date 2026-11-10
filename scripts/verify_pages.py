#!/usr/bin/env python3
"""Check a folder of generated study pages before you show them to anyone.

    verify_pages.py PAGES_DIR [--source-dir wiki/chapters] [--min-words 700]

Static checks per .html file:
  - leftover {{placeholders}} (}} alone is legal CSS, so only the double open counts)
  - <script> tags, missing viewport meta
  - every nav anchor resolves to a real id
  - SVG text that would fall outside its viewBox (estimated from label length)
  - citation density, prose length
  - numbers on the page that do not appear in the matching source markdown

Layout must still be checked in a browser; this script prints the JS to paste.
"""
import argparse
import os
import re
import sys

SKIP_IDS = set()


def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)


def check_file(path, source_text, min_words):
    s = open(path, encoding="utf-8").read()
    errs, warns = [], []

    no_style = re.sub(r"<style[\s\S]*?</style>", "", s)

    # a real placeholder is "{{"; "}}" appears in valid nested CSS
    if "{{" in s or re.search(r"\{\{[A-Z_]{3,}\}\}", no_style):
        errs.append("unfilled placeholder")
    if "<script" in s.lower():
        errs.append("script tag")
    if 'name="viewport"' not in s:
        errs.append("missing viewport meta")

    ids = set(re.findall(r'id="([^"]+)"', s))
    for nav in re.findall(r'<nav[^>]*class="[^"]*anchors[^"]*"[\s\S]*?</nav>', s):
        for h in re.findall(r'href="#([^"]+)"', nav):
            if h not in ids:
                errs.append(f"dead anchor #{h}")

    # SVG text overflow: a ROUGH estimate only. The browser is authoritative
    # (getBBox measures real glyphs); this exists to catch gross mistakes, so it
    # warns rather than fails.
    for m in re.finditer(r'<text x="([\d\.]+)" y="([\d\.]+)"([^>]*)>([^<]*)</text>', s):
        x, attrs, txt = float(m.group(1)), m.group(3), m.group(4)
        size_m = re.search(r'font-size="(\d+)"', attrs)
        size = int(size_m.group(1)) if size_m else 20
        anchor = "start"
        am = re.search(r'text-anchor="(\w+)"', attrs)
        if am:
            anchor = am.group(1)
        width = len(txt) * size * 0.5
        if anchor == "middle":
            left = x - width / 2
        elif anchor == "end":
            left = x - width
        else:
            left = x
        if left < -2 or left + width > 982:
            warns.append(f"check svg text near edge: {txt[:28]!r}")

    # accept both "(p. 42)" and a bare "p. 42" — bullet-first pages cite inline
    cites = len(re.findall(r"\bpp?\.\s*\d", s))
    if cites < 8:
        warns.append(f"only {cites} page citations")

    words = len(re.findall(r"\b\w+\b", strip_tags(no_style)))
    if words < min_words:
        warns.append(f"thin prose ({words} words)")

    if source_text:
        page_nums = set(re.findall(r"\$?\d[\d,\.]*\s?(?:billion|million|trillion|per cent|%)",
                                   strip_tags(no_style)))
        for c in page_nums:
            core = re.match(r"\$?([\d\.,]+)", c).group(1)
            if core not in source_text:
                warns.append(f"figure not in source: {c}")

    return errs, warns, words, cites


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--source-dir", default=None,
                    help="folder holding ch-NN/summary.md to cross-check figures against")
    ap.add_argument("--source-file", default=None,
                    help="single file (e.g. sources/raw.md) to cross-check figures against; "
                         "use this for coverage-preserving pages, whose figures may not be "
                         "in the condensed summary")
    ap.add_argument("--min-words", type=int, default=700)
    a = ap.parse_args()

    shared_source = ""
    if a.source_file:
        shared_source = open(a.source_file, encoding="utf-8", errors="replace").read()

    files = sorted(f for f in os.listdir(a.dir) if f.endswith(".html"))
    if not files:
        sys.exit("no html files found")

    bad = 0
    for f in files:
        src = shared_source
        if a.source_dir and not src:
            m = re.search(r"ch-(\d+)", f)
            if m:
                p = os.path.join(a.source_dir, f"ch-{int(m.group(1)):02d}", "summary.md")
                if os.path.exists(p):
                    src = open(p, encoding="utf-8").read()
        errs, warns, words, cites = check_file(os.path.join(a.dir, f), src, a.min_words)
        status = "FAIL" if errs else ("warn" if warns else "ok  ")
        if errs:
            bad += 1
        detail = "; ".join(errs + warns)
        print(f"{f:24} {status} {words:>5}w {cites:>3}cites  {detail}")

    print(f"\n{bad} failing out of {len(files)}")
    print("""
Layout still needs a browser pass. Paste this into browser_exec for each page:

  new_tab("file:///ABS/PATH.html"); wait_for_load()
  js("document.documentElement.scrollWidth>document.documentElement.clientWidth")
  js(\"\"\"(()=>{let b=[];document.querySelectorAll('svg').forEach(s=>{const vb=s.viewBox.baseVal;
    [...s.querySelectorAll('text')].forEach(t=>{const r=t.getBBox();
    if(r.x<vb.x-1||r.y<vb.y-1||r.x+r.width>vb.x+vb.width+1||r.y+r.height>vb.y+vb.height+1)
    b.push(t.textContent)})});return b})()\"\"\")
""")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
