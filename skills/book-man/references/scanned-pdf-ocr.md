# Scanned PDFs and two-up spreads → citable text

No text layer, no citations until you OCR. The whole job is getting page numbers right, because every
wiki claim downstream will quote one.

## Step 1 — confirm there is no text layer

```python
import pymupdf
d = pymupdf.open(pdf)
print(d.page_count, len(d[0].get_text()), [round(v) for v in d[0].rect])
```

Zero characters on several pages = image-only. Stop shopping for a better extractor and go to OCR.

## Step 2 — check the geometry BEFORE splitting (the expensive mistake)

A **landscape page with one image covering the full page** is usually two book pages scanned side by side.
The rect ratio gives it away: a normal portrait page is taller than wide, a spread is wider than tall
(e.g. 2410 × 1736 points).

Confirm from the OCR you already have:

- Two running heads inside one page's text (`INTRODUCTION` … `INTRODUCTION 3`).
- Lines that alternate between unrelated sentences, or words cut mid-line (`al first chapter into what now are`).

Why this matters: an unsplit two-up scan OCRs into text that **reads plausibly and is wrong** — two pages
interleaved line by line. Every quotation and figure location taken from it will be off. Split first, always.

## Step 3 — split, downscale, OCR

```bash
pdftoppm -r 300 -f 1 -l 249 -png book.pdf pages/page     # render once, cache the PNGs
```

```python
from PIL import Image
im = Image.open(png).convert("L")
w, h = im.size
for side, box in (("L", (0, 0, w // 2, h)), ("R", (w // 2, 0, w, h))):
    c = im.crop(box)
    c = c.resize((2600, int(c.height * 2600 / c.width)), Image.LANCZOS)
    c.save(f"half/{n:03d}{side}.png")
```

Grayscale + ~2600 px wide is the sweet spot for printed text. Wider only costs time.

Missing tesseract: `sudo dnf install -y tesseract poppler-utils` (Fedora) or
`sudo apt-get install -y tesseract-ocr poppler-utils` (Debian/Ubuntu).

## Step 4 — parallelise the OCR

`tesseract half.png out --psm 3 -l eng` costs roughly 8 s per half page at 300 dpi. Five hundred half-pages
serially is over an hour; a process pool of 8 finishes in about five minutes.

```python
with ProcessPoolExecutor(max_workers=8) as ex:
    list(ex.map(ocr_one, keys, chunksize=4))
```

Keep the per-page `.txt` files on disk. Assembly is then free and re-runs after a fix cost nothing.

Launch long pipelines with the terminal tool's own background mode and no trailing `&`. A script started
with `cmd &` inside a foreground call keeps running after the tracked session reports `exited`, leaving you
with an orphan you must hunt down. Stop a tracked job with `process_manage(action="kill", session_id=...)`.

## Step 5 — derive the mapping, then PROVE it

Assemble the blocks in reading order (page n left, then page n right) with a marker per block, then find
the linear relation `printed = a × pdf + b` from two known points. Front matter uses roman numerals and
usually breaks the relation — fit on the body only.

Then assert it: for every chapter opener in the table of contents, compute the page and check that the
block's first lines contain that chapter's number and title. All seventeen matching means the offset is
right; one mismatch means it is not, and nothing downstream may be written until it is fixed.

```
printed 41 -> pdf 31R: 1 / Origins of Inter-Governmental Debt, 1917-1921
printed 61 -> pdf 41R: 2 / Breakdown of World Balance, 1921-1932
```

Treat any solved pair as a worked example, never a constant: derive it per book.

## Step 6 — ship a range reader

Write `_meta/range.py` in the book folder exposing `python3 range.py FIRST LAST`, printing each block
labelled `===== printed page N =====`. Every later read — yours and every subagent's — goes through it, so
citations are printed pages by construction rather than by care. 400 pages then cost one command per chapter.

## Step 7 — record the defect

Some spreads defeat splitting (tight gutter, bleed-through, two columns). Name them in `log.md` and treat
those passages as uncitable. A gap in the wiki is recoverable; an invented figure is not.
