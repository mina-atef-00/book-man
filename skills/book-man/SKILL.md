---
name: book-man
description: Use when building or querying a study edition of a book (PDF/EPUB). Produces a complete, dyslexia-friendly HTML edition, not a summary.
---

# book-man

Turn a book into a readable edition its owner can actually finish. The reader has
dyslexia and cannot read the raw source, so **the page you build is their only access to
the book**. Completeness is the product; readability is the delivery.

## The one rule

> Distil for *readability*, never by *deletion*.

Keep every substantive claim and the reasoning that connects it, every number, date and
name, quotations whole rather than trimmed, metaphors and worked examples, and the
author's own judgements — including harsh ones. Cut only true tangents and repetition.

A page that omits cannot be repaired by the reader. When in doubt, keep it and make it
easier to read.

## Pipeline

Deterministic steps run through the plugin's MCP tools (`book_info`, `book_ocr`,
`book_pages`, `book_verify`, `book_assemble`, `book_publish`). Judgement — the writing —
is yours.

```
1  book_info(pdf)                  page count, and whether the scan is two-up
2  book_ocr(pdf, sources/raw.md)   spread splitting + parallel tesseract
3  book_pages(raw.md, a, b)        read the chapter at PRINTED page numbers
4  build pages/ch-NN.html          the writing step (see the page contract)
5  book_verify(pages, source_file) figures must appear in the book text
6  browser sweep                   the only authority on layout
7  book_assemble(wiki_dir)         merge into one navigable file
8  book_publish(pages, dest)       copy to where the reader opens it
```

**Never cite PDF page numbers.** Map to printed pages at step 3 and cite those, so a
citation matches the copy in the reader's hands.

**Never read the raw PDF once OCR exists.** Read `sources/raw.md` through `book_pages`.

## The page contract

One page per chapter, following the book's own section order. 6,000-9,000 words for
~20 printed pages — roughly 400-450 words per printed page of source.

1. **One-paragraph summary** in a bordered box at the top. The whole chapter before any detail.
2. **Legend** explaining the visual grammar.
3. **Sections** as collapsible blocks, each opening with one orienting line
   ("What this section does: …") and closing with one carry-forward verdict.
4. **Mixed containers, chosen per job** — never one container for everything:

   | The material | The container |
   |---|---|
   | a contrast, or a charge and its answer | two-panel `.compare` |
   | a quantity, or several side by side | `.stats` tiles, or a bar chart |
   | a real sequence | `.steps` rail, or a vertical timeline |
   | parallel claims about different actors | `.cards3` |
   | the author's verdict | `.pullq`, or a `.verdict` bar |
   | a document, speech or letter | `.qcard` with a gloss line under the quote |
   | a small arithmetic chain | `.chain` strip |
   | terms compared on several axes | a table |

   Bullets are for genuine unordered lists only. A wall of fifty identical bullets is
   the same failure as a wall of paragraphs.
5. **Five to eight inline SVG figures**, each doing a *different* analytical job: two-panel
   contrast, scaled bars, vertical timeline, stacked or nested bars, gap chart,
   node-and-arrow loop, inversion diagram.
6. **Voices tinted** — national officials, foreign voices, outside observers, each labelled.
   In a chapter made of other people's words, "who is saying this" is the reader's hardest
   reconstruction.
7. **Glossary** of every technical term in plain words, with page references.
8. **Self-check** of six questions, and a sources section naming the author's own sources.

Every claim carries `<span class="pg">p. 94</span>`.

## Visual rules

- `viewBox="0 0 980 H"`, every colour an explicit hex, **no text below 19px**, labels
  inside their boxes, each figure in `<div class="svgwrap">` inside `<figure>`.
- Measure **58-66 characters**. Long lines are where dyslexic readers lose the line.
- Never a full-height rule down the left of a section — carry colour on the heading's
  bottom border and the number badge instead.
- Centre the column, and put headings inside the same container as the text so they align.

See `references/page-contract.md` for the component vocabulary and
`references/pitfalls.md` for the failures that cost the most time.

## Verification discipline

**Static checkers cry wolf; the browser is the only authority on layout.**

- `book_verify(pages, source_file=sources/raw.md)` — figures on the page must appear in the
  book text. Verify against the **book**, never against a condensed summary: the summary is
  the artifact that lost the detail.
- Then measure in a real browser: `getBBox()` of every `<text>` against the SVG `viewBox`,
  and `documentElement.scrollWidth > clientWidth` at **390px, 700px, 1000px and 1400px**.
- When a checker fails every page, suspect the checker first. Legal CSS (`}}`) and
  `text-anchor="end"` have both produced 100% false failures.

## Assembly

One self-contained file per book, not a folder of pages. `book_assemble` lifts each
chapter's `<main>` content, prefixes every id and anchor with the chapter number, and wraps
it in `<article class="chapter">`. Navigation is `:target` plus
`body:has(.chapter:target)` — **no JavaScript anywhere**, so the page reads with scripts
blocked.

Verify the merged file for duplicate ids and unresolvable internal links: both are silent
until clicked.

## Delegating chapter builds

For a long book, build chapter 1 by hand and use it as the approved model. Then dispatch one
subagent per chapter with: the printed page range, the model page path, the page contract,
the accuracy rule ("never invent a number, date, name or quotation to fill an OCR gap —
report it as unreadable"), and the verification command.

Verify every child mechanically and say plainly which chapters were machine-drafted and
which were hand-edited. **A child's report is a self-report, not evidence.**

## Delivery

The reader opens a file on their own machine: publish to
`/mnt/c/Users/<user>/Desktop/<Book Title>/` with fonts embedded, and tell them the absolute
path. Keep the vault copy under `pages/`.
