# book-man

**A dyslexia-friendly way to read a whole book.**

book-man turns a scanned academic book into a complete, navigable HTML edition — not a
summary. It runs in Hermes as a plugin: a skill that holds the writing method, and an MCP
server that holds the deterministic pipeline.

The reader this was built for has dyslexia and cannot read the raw source. The page is their
only access to the book, so the rule throughout is:

> **Distil for readability, never by deletion.**

**Status.** The pipeline is exercised, not sketched: the MCP server answers `initialize`,
`tools/list`, `book_pages` and `book_verify`; the OCR tool has run against a 249-page
two-up scan; the verifier checks every figure on a page against the source text. The
reference build is 17 chapters, ~187,000 words and 122 inline SVG figures in one file.

Everything is kept — every claim, number, name, quotation, metaphor and judgement — and the
*form* is what changes: claim-first containers, diagrams, timelines, glossaries, colour-coded
voices, and a density switch.

## Why not a summary

A summary is a lossy operation performed once, by someone who already understands the
argument. A reader who is lost does not need fewer words; they need the same words arranged
so the structure is visible.

This project was rebuilt after a summarised edition failed exactly that way: the reader came
back saying *"I'm reading chapter 2 and I'm just lost. There's no context."* The fix was not
more compression. It was completeness delivered in a readable shape.

## The pipeline

```
PDF ──► book_info ──► book_ocr ──► book_pages ──► [write the chapter page]
                                                        │
                                        book_verify ◄───┤
                                        browser sweep ◄─┤
                                        book_assemble ◄─┤
                                        book_publish ◄──┘
```

| Stage | Tool | What it removes |
|---|---|---|
| 1 | `book_info` | surprises: page count, and whether the scan is two-up |
| 2 | `book_ocr` | interleaved columns — splits spreads before OCR |
| 3 | `book_pages` | PDF-page confusion — prints **printed** page numbers |
| 4 | *the agent* | the writing. Judgement, not automation |
| 5 | `book_verify` | figures that don't exist in the book |
| 6 | *browser* | layout that overflows or clips |
| 7 | `book_assemble` | seventeen files becoming one |
| 8 | `book_publish` | dead relative links, missing fonts |

## What a chapter page contains

- One-paragraph summary, then the chapter in the book's own section order
- **Mixed containers**, chosen per job: two-panel contrasts, stat tiles, step rails, quote
  cards, verdict bars, tables. Bullets only for genuine lists
- **5-8 inline SVG figures**, each doing a different analytical job — never decoration
- **Voices tinted** by speaker, because a chapter of quotations is otherwise a puzzle
- A glossary of every technical term, in plain words, with page references
- Self-check questions, and the author's own sources

Every claim carries its printed page. No JavaScript anywhere — the file reads with scripts
blocked.

## Reading features

| Feature | What it does |
|---|---|
| **Density switch** | hides running explanations and page numbers; keeps quotes, charts and tables |
| **Wide layout** | 1060px column, or 1560px on a large screen |
| **Collapsible sections** | the page never presents 8,000 words at the door |
| **Sticky heading** | the current section title pins while you read it |
| **Section colours** | you know where you are without reading a heading |

## Install

```bash
git clone https://github.com/mina-atef-00/book-man
ln -s "$PWD/book-man" ~/.hermes/plugins/book-man
```

Restart Hermes. The `book-man` tools appear in the tool list, and the `book-man` skill loads
when a book task comes up.

Requires `tesseract` and `poppler-utils` (`pdftoppm`, `pdfinfo`) for the OCR stage. Nothing
else — the MCP server is standard library only.

## Quickstart

```
book_info("/books/Hudson - Super Imperialism.pdf")
# → 249 pages, 2410x1736 pts -> TWO-PAGE SPREADS (splitting)

book_ocr("/books/Hudson - Super Imperialism.pdf", "sources/raw.md")
book_pages("sources/raw.md", 41, 60)      # read chapter 1 at printed page numbers
# … write pages/ch-01.html …
book_verify("pages", source_file="sources/raw.md")
book_assemble("/home/mina/wiki/super-imperialism")
book_publish("pages", dest="/mnt/c/Users/mina/Desktop/Super Imperialism", fonts=True)
```

## Repository layout

```
plugin.json                     plugin manifest
mcp.json                        MCP server declaration
server/book_man_mcp.py          stdio JSON-RPC server, stdlib only
scripts/
  ocr_scanned_pdf.py            spread detection, splitting, parallel OCR
  verify_pages.py               citations, figures vs source, layout warnings
  assemble_book.py              many chapters -> one file
  publish.py                    deploy and check relative links
  check_html_page.py            single-page tag balance
  range.py                      printed-page helper
skills/book-man/
  SKILL.md                      the writing method
  references/page-contract.md   component vocabulary
  references/pitfalls.md        the ten failures that cost the most time
  templates/page-shell.html     the approved page shell
```

## Design rules that are not negotiable

1. **Cite printed pages.** A citation to PDF page 37 is useless to someone holding the book.
2. **Split two-up spreads before OCR.** Whole-spread OCR produces plausible, wrong prose —
   the worst failure mode, because it reads fine.
3. **Verify against the book, never against a summary** — the summary is the artifact that
   lost the detail.
4. **The browser is the only authority on layout.** Static checkers have cried wolf three
   times on this project.
5. **No JavaScript.** A reading aid that needs a script is not a reading aid.

## Honest limitations

- OCR quality bounds the result. Rotated tables and shredded columns are reported, never
  invented around — every chapter page lists the passages it could not read.
- The writing step is judgement and is not automated. A pipeline can guarantee completeness
  of *input*; only reading the source can guarantee completeness of *output*.
- Long chapters run 10,000-18,000 words. That is deliberate: the alternative was dropping
  the author's quotations.

## Legacy: the OpenCode plugin

The first version of this project was an OpenCode plugin (`AGENT.md`, `.opencode/`,
`package.json`). Those files are still in the repository and still work for OpenCode users,
but Hermes is now the supported target and the pipeline above is where development happens.

## Licence

MIT.
