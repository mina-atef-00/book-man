# Pitfalls that cost the most time

Each of these cost at least one rebuild. Read them before building.

## 1. Two book pages per PDF page

A scanned book often puts two printed pages on one PDF page. OCR the spread whole and the
two columns interleave into plausible-looking but wrong prose — the worst possible failure,
because it reads fine and cites nothing.

**Split the spread down the middle before OCR.** `book_info` detects it by page geometry;
`book_ocr` splits by default.

## 2. Checkers cry wolf — the browser is the truth

Three times a homemade checker reported every page broken when every page was fine:

- `}}` is legal CSS (closing a nested rule) and was flagged as a placeholder;
- an SVG width estimator guessed glyph widths and ignored `text-anchor="end"`;
- a regex measured SVG captions instead of box labels.

Static checks should **fail** only on unambiguous faults (placeholders, `<script>`, dead
anchors, figures absent from the source) and **warn** on anything estimated. Layout belongs
to `getBBox()` against `viewBox`, and `scrollWidth` against `clientWidth` — measured in a
real browser at 390px.

## 3. A generic element selector hits the section blocks

`details { border; background; max-width: 76ch }` written for self-check accordions also
matched every `<details class="part">`, capping whole sections at 76 characters and drawing
a box around each one. Write `details:not(.part)`.

## 4. The left rail

A 10px coloured border on each section reads as a broken border running the height of the
page, not as a colour code. Carry section colour on the heading's bottom border and the
number badge.

## 5. Centring, two ways

`max-width` + `margin:0 auto` on the text column, and a
`calc((100% - var(--colw))/2)` padding formula on the heading, do **not** agree — they land
several pixels apart. Put the heading inside the same `.wrap`/`.sumwrap` container as the
text.

## 6. Mobile overflow hides in three places

- **Tables** need an `overflow-x:auto` wrapper. A `min-width` table without one pushes the
  page sideways, silently.
- **A prev/next row** of three flex items with no `flex-wrap` overflows by exactly the width
  of the last link — and only on chapters that have both a previous and a next neighbour,
  which makes it look like a per-chapter bug.
- **A `white-space:nowrap` citation** inside a two-column grid forces the grid track wider
  than the screen.

Test at 390px, then again at 700, 1000 and 1400px.

## 7. Restructuring markup breaks selector contracts

Converting `<section class="part">` to `<details class="part">`, or dropping the `<main>`
wrapper during assembly, silently kills every `~ main .prose` rule. Re-run the browser
sweep after **any** structural change — a toggle that stops working is invisible until you
click it.

## 8. Never cite PDF pages

`book_pages` maps scan position to printed page. A citation to PDF page 37 is useless to
someone holding the book.

## 9. Subagent reports are self-reports

A builder that says "verified, no overflow" may have measured nothing. Check the artifact:
duplicate ids, dead anchors, figure counts, word counts, and the rendered page. One builder
in this project reported a passing file that had five dead anchors.

## 10. Do not compress the quotations

When a chapter runs long, the pressure is to trim. Trimming the author's sentences is how a
complete edition silently becomes a summary. Cut your own commentary, never the source.
