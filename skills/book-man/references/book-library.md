# Where the book files live

The wiki is derived. The actual ebook files are the source of truth for "what books do I have",
and they live outside the vault.

## Locations

| Path (WSL) | Windows path | Contents |
|---|---|---|
| `/mnt/d/Documents/Books/` | `D:\Documents\Books` | **The economics library** — one folder per author |
| `/mnt/d/Documents/PERSONAL/Books/` | — | Fiction / personal reading |
| `/mnt/d/Documents/Learning/` | — | Investing + course material (Martin Shkreli course, Excel, SEC filings) |
| `/home/mina/wiki/{book}/sources/` | — | The extracted EPUB/PDF a wiki was built from |
| `/home/mina/Documents/books/` | — | Exists but is empty; do not assume books are here |

`D:\Documents\Obsidian\Main\.trash` holds Arabic university material (محاسبة، نقود وبنوك،
إحصاء) — course handouts and exam reviews, not library books.

## The economics library — shape

It is a coherent **heterodox / political-economy** collection, not a general economics shelf:
Michael Hudson, Richard D. Wolff, Resnick & Wolff, Yanis Varoufakis, V. I. Lenin,
Clara E. Mattei, Gibson-Graham, Parenti, Gaddafi. Expect the financialization /
capital-as-social-relation lineage when the user asks an economics question.

Snapshot (verify with the commands below before quoting counts — the folder grows):
Varoufakis 7 · Hudson 9 (2 duplicate pairs) · Lenin 7 · Wolff 5 · Resnick & Wolff 1 ·
Wolff & Barsamian 1 · Mattei 1 · Gibson-Graham 1 · Gaddafi 1 · Parenti 1 (Roman history,
not economics) · Miscellaneous 1 (Egyptian left history).

Only two have wikis so far: Varoufakis *Foundations of Economics* (85 pages) and
Parenti *The Assassination of Julius Caesar*.

## Enumerating it reliably on /mnt/d

Start with the native tool: `search_files(target="files", pattern="*.epub", path="/mnt/d/Documents/Books")`
and again with `*.pdf`. It gives a fast flat listing, but it truncates at the limit and loses the
author folder context — use the shell loop below when you need a complete per-author roster.

Recursive `find` over `/mnt/d` can return `Permission denied` for directories that `ls` reads
fine — Windows-created folders carry ACL-style bits DrvFs surfaces as `d--x--x--x` while
`stat` reports 777. **Do not conclude the files are unreadable.** Enumerate from the top:

```bash
cd /mnt/d/Documents/Books && for d in */; do echo "### ${d%/}"; ls -1 "$d"; echo; done
```

For sizes (and to sort by bulk), per-directory `find` with a max depth and no recursion upward:

```bash
cd /mnt/d/Documents/Books && find . -maxdepth 2 -type f \
  \( -iname '*.pdf' -o -iname '*.epub' -o -iname '*.mobi' -o -iname '*.azw3' \) \
  -printf '%s\t%p\n' | sort -k2
```

`powershell.exe -NoProfile -Command "Get-ChildItem -LiteralPath 'D:\Documents\Books'"` is the
fallback if a mount genuinely refuses.

## Identifying an unknown file without a PDF toolchain

`read_file` on a PDF/EPUB auto-extracts text. Read the first ~25 lines to get the title page,
page count and whether it is a book, a paper, or a student essay — no pymupdf install needed.
This is for **identification only**. Study content still comes from the compiled wiki.

## Presenting an inventory

Group by author, one blank line between groups, indent the file facts under each title:
format and size on their own line. Flag duplicates, flag what is not economics, and mark which
books already have a wiki. Close with 2–3 concrete next-build candidates tied to gaps in the
existing wikis, not a generic offer to help.
