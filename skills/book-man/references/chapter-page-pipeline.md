# Chapter-page pipeline — many HTML pages from one wiki

For a book with 8+ chapters the reader-facing layer is one HTML page per chapter, plus a single compiled
guide that links them all. This is the build order. It assumes `wiki/chapters/ch-NN/summary.md` already
exists with printed-page citations (see the fan-out section of SKILL.md).

## 1. Write the template before writing any page

Create `_meta/chapter-page-template.html`: the full theme CSS, the eight section ids, and a **pre-drawn
SVG with real coordinates**. Place every piece of text as a `{{TOKEN}}`. Subagents then fill tokens and
touch nothing else, which is what keeps seventeen independently written pages looking like one document.

Lock these section ids: `answer`, `p1`, `p2`, `p3`, `p4`, `numbers`, `check`, `sources` — nav anchors are
built from them, so a renamed id becomes a dead link.

## 2. Diagram geometry — fixed, not freehand

A four-box horizontal chain for a 980×300 canvas:

| Box | x | width | y | height | label x |
|---|---|---|---|---|---|
| 1 | 25 | 210 | 50 | 120 | 130 |
| 2 | 265 | 210 | 50 | 120 | 370 |
| 3 | 505 | 210 | 50 | 120 | 610 |
| 4 | 745 | 210 | 50 | 120 | 850 |

- Box number baseline `y=86`, bold label `y=118`, detail line `y=148`.
- Arrows between boxes at `y=110`; caption lines at `y=232` and `y=262`.
- **Box labels: 13 characters maximum.** At font-size 21 in a 210px box, roughly 13 chars is where text
  starts touching the border. Caption lines may run to ~80 characters.
- Give the last box the amber fill to mark the outcome; leave the rest white.
- The four boxes must be the four sections, numbered to match. A diagram whose numbers do not line up with
  the sections is worse than no diagram.

## 3. Fan out

One subagent per 4–5 chapters. Each task must carry:

- the chapter's `summary.md` path as the only source of truth, with "do not invent a number, do not use the web";
- the template path and the instruction that CSS, class names, section ids and SVG coordinates are frozen;
- the exact placeholder token list and the character limits from §2;
- the output path (`pages/ch-NN.html`);
- a self-check list: no leftover `{{`, no `<script>`, every anchor resolves, labels ≤13 chars.

Real values only in the goal text — `delegate_task` rejects goals containing angle-bracket placeholders.

**Give every child an exclusive scratch directory.** Children run in parallel and share the same temp tree;
two of them writing `scratch/body.html`, or one cleaning `_build/` at the end of its run, will delete a
sibling's work mid-write. Put the chapter number in every intermediate path (`scratch/ch-07/body.html`) and
tell each child to clean only its own subdirectory. A child reporting "I deleted the shared `_build/`" is a
real loss, not a quirk.

**Print the expected artifact sizes in the task.** A child that believes it succeeded will say so; the file on
disk is the only evidence. After a batch lands, check each file for word count, figure count, citation count
and dead anchors before assembling anything. One child's "0 failing" can describe an earlier draft of a
neighbour's file, or a file it never wrote.

**When the brief says do not compress, the word ceiling loses.** Ask for 6,000-9,000 words *and* "keep every
quotation complete", and quotation-dense chapters will land at 11,000-16,000. Say in the task that fidelity
beats the ceiling and that the child should report the overshoot rather than cut the author's words —
otherwise it silently drops quotations to hit the number, which is the one failure the owner will notice.

## 4. Verify in three passes, in this order

**Pass 1 — static.** `scripts/check_html_page.py`, plus a per-chapter sweep for: unfilled `{{`,
`<script`, viewport meta, the eight section ids, dead anchors, diagram label length, citation count, word count.

**Pass 2 — layout, in a browser.** For every page: `scrollWidth > clientWidth` at 390px and at desktop,
SVG `getBBox()` of every `<text>` inside the viewBox, smallest rendered label ≥17px, zero scripts. Assert on
all of them at once and print the failing chapter numbers; fixing one page at a time from a prose description
wastes rounds.

**Pass 3 — no invented numbers.** Extract every figure-with-unit from the page text
(`\$?\d[\d,\.]*\s?(billion|million|per cent|%)`), then check each numeric core appears in the chapter's
`summary.md`. Any miss is either a fabrication or a transcription slip; both need a human look before shipping.
This pass is cheap and catches the failure that matters most in a study aid.

## Pitfall — suspect your checker before you suspect seventeen pages

A checker that reports every single file as broken is usually broken itself. Two false positives seen in
practice: `}}` is **legal CSS** (a nested rule closing twice), so a naive "unfilled placeholder" test fires on
the theme block of every page — strip `<style>` before searching. And a regex keyed on `font-size="21"`
matches both the short box labels and the long caption lines; key it on the `y="118"` baseline instead.
Fix the checker, re-run, and only then decide the pages are wrong.

## 5. Compile the guide

A script (`_meta/build_guide.py`) that reads every `summary.md` and emits one page with:

- a sticky sidebar (300px) grouped by part, at `max-width:900px` turning into a horizontal chip row;
- each chapter as `<section id="ch-NN">` with a link to `ch-NN.html` for the diagrammed version;
- a small markdown converter handling h1–h4, ordered and unordered lists, tables, blockquotes,
  `**bold**` and `[[wikilink|alias]]`. Keep it in the vault so a later edit is one command, not a rewrite.

Embed the font instead of linking Google Fonts: fetch the woff2 files with a desktop user-agent, base64 them
into `@font-face` blocks, and drop the `<link>` tags. Two weights is ~18KB and makes the page render
identically with no network. Verify with `document.fonts.check('20px "Atkinson Hyperlegible"')` and by
confirming zero remaining `fonts.googleapis`/`fonts.gstatic` references.

## 6. Deploy and check the deployed copy

Copy the guide and every page into one Windows folder, then verify **from that folder**: parse the guide's
`href` targets and confirm each file exists beside it. A relative link that resolves in the vault and breaks
on the desktop is the most common shipping bug here. Open the deployed file itself over `file://` and confirm
it navigates, not just that it renders.

## 7. One file instead of a folder of pages

A folder of seventeen pages is a filing cabinet; the owner wants a book. Assemble every chapter into a
single HTML file with `scripts/assemble_book.py`, which lifts each page's `<main>` content, prefixes every
`id` and `#href` with the chapter number (`p1` → `c7-p1`), and wraps it in `<article class="chapter" id="ch-07">`.

Chapter switching without JavaScript:

```css
.chapter{display:none}
.chapter.default{display:block}
.chapter:target{display:block}
body:has(.chapter:target) .chapter.default:not(:target){display:none}
```

A chip row of chapter numbers plus prev/next links at each chapter's foot. Emit a placeholder `<article>` for
any chapter not built yet, so the file always opens and visibly grows. Re-running the assembler after each
batch is idempotent — do that rather than hand-editing the merged file, or the next batch wipes your edits.

### Four failures that only appear in the merged file

1. **Dropping `<main>` kills the density switch.** `#density:checked ~ main .prose` is a sibling combinator;
   if chapters sit directly in `<body>` the rule matches nothing and the toggle silently does nothing. Wrap
   the article list in `<main>`.

2. **Tables need wrapping centrally.** A chapter page that emits `<table>` without `.tablewrap` is fine alone
   and overflows the page once merged, because `table{min-width:560px}` exceeds a 390px screen. Normalise in
   the assembler: strip any existing `tablewrap` div, then wrap every `<table>` uniformly.

3. **Never set `.tablewrap{overflow-x:visible}` in a mobile media query.** It looks like a fix for cramped
   tables and it does the opposite — it removes the scroll container and the table pushes the whole document
   sideways. Leave the wrapper scrolling and let `min-width` do its job.

4. **A hidden chapter cannot reveal its own overflow.** The mobile sweep must `location.hash` into each
   chapter in turn and measure `scrollWidth - clientWidth` after the switch settles. Checking only the default
   chapter reports "no overflow" while sixteen chapters are broken.

Verify the merged output before shipping: no duplicate `id`, every `href="#..."` resolves, zero placeholders
left, and one browser sweep at 390px, 1000px and 1400px. Duplicate ids and dead targets are silent until a
reader clicks.
