#!/usr/bin/env python3
"""Print a printed-page range of Super Imperialism's OCR text, labelled by printed page.

Usage:  python3 range.py 41 60        # printed pages 41-60
        python3 range.py 41 60 --pdf  # pdf page markers instead

Mapping (verified against every chapter opening):
    printed = 2*pdf - 22   (left half)     printed = 2*pdf - 21   (right half)
so pdf for a printed page p is:  p even -> (p+22)/2 L,  p odd -> (p+21)/2 R
"""
import re, sys

PATH = "/home/mina/wiki/super-imperialism/sources/raw.md"
text = open(PATH).read()
parts = re.split(r"<!-- PDF_PAGE (\d+) (L|R) -->", text)
blocks = [{"pdf": int(parts[i]), "side": parts[i + 1], "body": parts[i + 2]}
          for i in range(1, len(parts), 3)]


def pnum(b):
    return 2 * b["pdf"] - (22 if b["side"] == "L" else 21)


def main():
    a, z = int(sys.argv[1]), int(sys.argv[2])
    sel = [b for b in blocks if a <= pnum(b) <= z]
    for b in sel:
        print(f"\n===== printed page {pnum(b)}   (pdf {b['pdf']}{b['side']}) =====")
        print(b["body"].strip())


if __name__ == "__main__":
    main()
