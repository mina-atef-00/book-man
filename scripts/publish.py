#!/usr/bin/env python3
"""Make a set of study pages readable on the owner's Windows desktop.

    publish.py PAGES_DIR --dest "/mnt/c/Users/mina/Desktop/My Book" \
               --guide guide-20261108.html [--fonts] [--dry-run]

Does three things that always go together:
 1. optionally embeds Atkinson Hyperlegible into the guide as woff2 data URIs,
    so it renders identically with no network
 2. copies every .html in the folder to the destination
 3. verifies that every relative link between the copied pages resolves

Run with --dry-run to see the copy list without touching anything.
"""
import argparse
import base64
import os
import re
import shutil
import subprocess
import sys

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CSS_URL = ("https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible"
           ":wght@400;700&display=swap")


def embed_fonts(html):
    css = subprocess.run(["curl", "-sS", "-A", UA, CSS_URL],
                         capture_output=True, text=True).stdout
    faces = re.findall(r"font-weight:\s*(\d+);.*?src:\s*url\((https://[^)]+\.woff2)\)",
                       css, re.S)
    if not faces:
        print("  ! could not fetch font CSS, leaving the page as-is")
        return html, 0
    style, seen, total = [], set(), 0
    for weight, url in faces:
        if weight in seen:
            continue
        seen.add(weight)
        data = subprocess.run(["curl", "-sS", "-A", UA, url],
                              capture_output=True).stdout
        total += len(data)
        style.append(
            "@font-face{font-family:'Atkinson Hyperlegible';font-style:normal;"
            f"font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) "
            "format('woff2');}")
    html = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", html)
    html = re.sub(r'<link href="https://fonts\.googleapis\.com[^"]*"[^>]*>\s*', "", html)
    html = html.replace("</head>", "<style>\n" + "\n".join(style) + "\n</style>\n</head>", 1)
    return html, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages_dir")
    ap.add_argument("--dest", required=True)
    ap.add_argument("--guide", default=None, help="html file to receive embedded fonts")
    ap.add_argument("--fonts", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.pages_dir) if f.endswith(".html"))
    print(f"{len(files)} pages -> {a.dest}")
    if a.dry_run:
        for f in files:
            print("  would copy", f)
        return 0

    os.makedirs(a.dest, exist_ok=True)

    if a.fonts and a.guide and a.guide in files:
        src = os.path.join(a.pages_dir, a.guide)
        html = open(src, encoding="utf-8").read()
        if "data:font/woff2" in html:
            print("  fonts already embedded, skipping")
        else:
            html, size = embed_fonts(html)
            open(src, "w", encoding="utf-8").write(html)
            print(f"  embedded {size/1024:.0f} KB of font into {a.guide}")

    for f in files:
        shutil.copy2(os.path.join(a.pages_dir, f), os.path.join(a.dest, f))
    print(f"  copied {len(files)} files")

    # every relative html link must land on a copied file
    missing = []
    for f in files:
        s = open(os.path.join(a.dest, f), encoding="utf-8").read()
        for href in re.findall(r'href="([a-z0-9_\-]+\.html)"', s):
            if not os.path.exists(os.path.join(a.dest, href)):
                missing.append(f"{f} -> {href}")
    if missing:
        print("  BROKEN LINKS:")
        for m in missing:
            print("   ", m)
        return 1
    print("  all relative links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
