#!/usr/bin/env python3
"""OCR a scanned PDF into markdown — handles two-page spreads, no Python deps.

Needs only poppler (pdfinfo/pdftoppm) and tesseract on PATH.

    ocr_scanned_pdf.py book.pdf sources/raw.md [--dpi 300] [--jobs 8] [--force-single]

What it does:
 1. asks pdfinfo for page count and page size
 2. decides whether each PDF page is one book page or a two-page spread
    (a spread renders wider than tall) and splits the spread down the middle
 3. renders each half directly from the PDF with pdftoppm crop flags
 4. OCRs with tesseract in parallel
 5. writes one block per half page, marked `<!-- PDF_PAGE n LEFT -->` / `RIGHT`

Spread OCR is the failure mode this exists to prevent: OCR'ing a whole spread
interleaves the two columns into text that still looks like prose.
"""
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pdf_info(path):
    out = sh(["pdfinfo", path]).stdout
    pages = int(re.search(r"^Pages:\s+(\d+)", out, re.M).group(1))
    size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", out, re.M)
    if not size:
        sys.exit("could not read page size from pdfinfo")
    return pages, float(size.group(1)), float(size.group(2))


def has_text_layer(path, pages):
    """True when the PDF already has a text layer and needs no OCR."""
    for n in range(1, min(5, pages) + 1):
        txt = sh(["pdftotext", "-f", str(n), "-l", str(n), path, "-"]).stdout
        if len(txt.strip()) > 200:
            return True
    return False


def ocr_side(args):
    pdf, n, side, dpi, crop, outdir = args
    out = os.path.join(outdir, f"{n:04d}{side}")
    if os.path.exists(out + ".txt") and os.path.getsize(out + ".txt") > 40:
        return out + ".txt"
    png = out + ".png"
    cmd = ["pdftoppm", "-r", str(dpi), "-f", str(n), "-l", str(n),
           "-png", "-singlefile"]
    if crop:
        x, y, w, h = crop
        cmd += ["-x", str(x), "-y", str(y), "-W", str(w), "-H", str(h)]
    cmd += [pdf, out]
    if sh(cmd).returncode != 0 or not os.path.exists(png):
        return None
    sh(["tesseract", png, out, "--psm", "3", "-l", "eng"])
    os.remove(png)
    return out + ".txt"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--force-single", action="store_true",
                    help="treat each PDF page as one book page even if it looks like a spread")
    ap.add_argument("--info-only", action="store_true",
                    help="report page count, size and spread detection, then stop")
    a = ap.parse_args()

    for tool in ("pdfinfo", "pdftoppm", "tesseract"):
        if sh(["which", tool]).returncode != 0:
            sys.exit(f"missing {tool}. Fedora: sudo dnf install poppler-utils tesseract")

    pages, w, h = pdf_info(a.pdf)
    spread = (w > h) and not a.force_single

    if has_text_layer(a.pdf, pages):
        print("NOTE: this PDF already has a text layer. Prefer pdftotext or pymupdf.")

    print(f"{pages} PDF pages, {w:.0f}x{h:.0f} pts -> "
          f"{'TWO-PAGE SPREADS (splitting)' if spread else 'single pages'}")
    if a.info_only:
        return

    outdir = os.path.splitext(a.out)[0] + "_ocrparts"
    os.makedirs(outdir, exist_ok=True)

    jobs = []
    for n in range(1, pages + 1):
        if spread:
            half_pts = w / 2
            half_px = int(half_pts * a.dpi / 72)
            full_px_h = int(h * a.dpi / 72)
            jobs.append((a.pdf, n, "L", a.dpi, (0, 0, half_px, full_px_h), outdir))
            jobs.append((a.pdf, n, "R", a.dpi, (half_px, 0, half_px, full_px_h), outdir))
        else:
            jobs.append((a.pdf, n, "", a.dpi, None, outdir))

    done = 0
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for res in ex.map(ocr_side, jobs):
            done += 1
            if done % 25 == 0:
                print(f"  ocr {done}/{len(jobs)}")

    head = ("# " + os.path.basename(a.pdf) + "\n\n"
            "**OCR note:** one block per page part. `<!-- PDF_PAGE n LEFT -->` gives the "
            "PDF page and the half; the running head at the top of each block gives the "
            "printed page number.\n\n---\n\n")
    blanks = []
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(head)
        for n in range(1, pages + 1):
            for side in (("L", "R") if spread else ("",)):
                p = os.path.join(outdir, f"{n:04d}{side}.txt")
                f.write(f"\n<!-- PDF_PAGE {n}{(' ' + side) if side else ''} -->\n\n")
                if os.path.exists(p):
                    body = open(p, encoding="utf-8", errors="replace").read()
                    if len(body.strip()) < 20:
                        blanks.append(f"{n}{side}")
                    f.write(body)
                else:
                    blanks.append(f"{n}{side}")

    size = os.path.getsize(a.out)
    print(f"wrote {a.out} ({size/1024:.0f} KB)")
    if blanks:
        print(f"WARNING: {len(blanks)} empty or unreadable parts: "
              f"{', '.join(blanks[:12])}{' ...' if len(blanks) > 12 else ''}")
    print("\nNext: confirm the printed-page mapping against the table of contents.")
    print("Every chapter opening must land where you predict, or the offset is wrong.")


if __name__ == "__main__":
    main()
