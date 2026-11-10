#!/usr/bin/env python3
"""Assemble standalone chapter pages into one self-contained HTML file.

    python3 assemble_book.py --wiki /home/mina/wiki/super-imperialism \
        --out pages/super-imperialism-complete.html --count 17

Assumes:
  * pages/ch-NN.html all share one theme, taken from the first built chapter
    (`--model`, default pages/ch-01.html), and put their content inside <main>.
  * a not-yet-built chapter simply lacks the marker class (`--marker`).

What it does, and why each part matters:
  * prefixes every id and #href with the chapter number, because seventeen pages
    written independently will collide on p1, glossary, sources;
  * unwraps and re-wraps every <table> in .tablewrap, because a page that omitted
    the wrapper overflows the document on a 390px screen once merged;
  * wraps the articles in <main>, because the density toggle is a sibling
    combinator (#density:checked ~ main .prose) and silently dies without it;
  * emits a placeholder article for any chapter still being written, so the file
    always opens and visibly grows;
  * is idempotent — re-run it after each batch instead of hand-editing the output.
"""
import argparse, os, re, sys

SHELL_CSS = """
  /* ---------- chapter shell ---------- */
  .chapters{display:flex;flex-wrap:wrap;gap:.45rem;padding:.9rem 1.4rem;background:var(--card);
      border-bottom:2px solid var(--line);align-items:center;}
  .chapters .lab{font-size:.9rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-right:.3rem;}
  .chapters a{font-size:.95rem;text-decoration:none;border:2px solid var(--line);border-radius:999px;
      padding:.28rem .7rem;color:var(--ink);background:var(--ground);white-space:nowrap;}
  .chapters a:hover,.chapters a:focus{background:var(--amber);border-color:var(--amber);}
  .chapter{display:none;}
  .chapter.default{display:block;}
  .chapter:target{display:block;}
  body:has(.chapter:target) .chapter.default:not(:target){display:none;}
  .chapternav{display:flex;justify-content:space-between;gap:1rem;padding:1.6rem 1.4rem 3rem;
      border-top:2px solid var(--line);margin-top:1.2rem;}
  .chapternav a{font-size:1rem;text-decoration:none;border:2px solid var(--line);border-radius:999px;
      padding:.5rem 1rem;background:var(--card);color:var(--ink);}
  .chapternav a:hover{background:var(--amber);border-color:var(--amber);}
  .notyet{background:var(--card);border:2px dashed var(--line);border-radius:16px;padding:1.4rem;
      margin:1.4rem;max-width:70ch;}
  @media (max-width:680px){
    .chapters{flex-wrap:nowrap;overflow-x:auto;}
    .chapters .lab{display:none;}
  }
"""

TOPBAR = """<input type="checkbox" id="density" hidden>
<input type="checkbox" id="wide" hidden>

<div class="ui">
  <label for="density"><span class="dot"></span>Argument only</label>
  <label for="wide" class="wide"><span class="dot"></span>Wide layout</label>
  <span class="hint">Hides the running explanations and page numbers. The claims, quotes, charts and tables stay.</span>
</div>
"""


def chapter_title(wiki, n):
    """Title from the wiki summary frontmatter, falling back to 'Chapter N'."""
    p = os.path.join(wiki, "wiki", "chapters", f"ch-{n:02d}", "summary.md")
    if os.path.exists(p):
        m = re.search(r"^title:\s*(.+)$", open(p, encoding="utf-8").read(), re.M)
        if m:
            return re.sub(r"^Chapter\s+\d+\s*[-–—:]\s*", "", m.group(1).strip())
    return f"Chapter {n}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--count", type=int, default=17)
    ap.add_argument("--model", default=None, help="page whose <head> is reused (default pages/ch-01.html)")
    ap.add_argument("--marker", default='class="onepara"', help="how to recognise a rebuilt chapter page")
    ap.add_argument("--title", default="The complete study edition")
    ap.add_argument("--subtitle", default="Every claim carries its printed page.")
    a = ap.parse_args()

    pages = os.path.join(a.wiki, "pages")
    model_path = a.model or os.path.join(pages, "ch-01.html")
    if not os.path.exists(model_path):
        sys.exit(f"no model page at {model_path} — build chapter 1 first")
    model = open(model_path, encoding="utf-8").read()
    head = model[: model.index("<body>")]
    head = head.replace("</title>", f" — {a.title}</title>", 1)
    if "@media (max-width:680px){" not in head:
        sys.exit("model page has no mobile breakpoint to attach the shell CSS to")
    head = head.replace("  @media (max-width:680px){", SHELL_CSS + "\n  @media (max-width:680px){", 1)

    built, missing = [], []
    for n in range(1, a.count + 1):
        path = os.path.join(pages, f"ch-{n:02d}.html")
        if not os.path.exists(path):
            missing.append(n)
            continue
        src = open(path, encoding="utf-8").read()
        if a.marker not in src:
            missing.append(n)
            continue
        m = re.search(r"<main>(.*)</main>", src, re.S)
        if not m:
            missing.append(n)
            continue
        body = re.sub(r'<nav class="anchors">.*?</nav>', "", m.group(1), flags=re.S)
        # normalise tables: unwrap, then wrap uniformly
        body = re.sub(r'<div class="tablewrap">\s*(<table\b.*?</table>)\s*</div>', r"\1", body, flags=re.S)
        body = re.sub(r"(<table\b.*?</table>)", r'<div class="tablewrap">\1</div>', body, flags=re.S)
        # namespaced ids and links
        for i in sorted(set(re.findall(r'id="([^"]+)"', body)), key=len, reverse=True):
            body = body.replace(f'id="{i}"', f'id="c{n}-{i}"')
            body = body.replace(f'href="#{i}"', f'href="#c{n}-{i}"')
        built.append((n, body))

    parts = ['<div class="chapters"><span class="lab">Chapters</span>' +
             "".join(f'<a href="#ch-{n:02d}">{n}</a>' for n in range(1, a.count + 1)) +
             "</div>"]

    def nav(n):
        prev = f'<a href="#ch-{n-1:02d}">← Chapter {n-1}</a>' if n > 1 else "<span>&nbsp;</span>"
        nxt = f'<a href="#ch-{n+1:02d}">Chapter {n+1} →</a>' if n < a.count else "<span>&nbsp;</span>"
        return f'<div class="chapternav">{prev}<a href="#top">All chapters ↑</a>{nxt}</div>'

    for n, body in built:
        cls = "chapter default" if n == 1 else "chapter"
        parts.append(f'\n<article class="{cls}" id="ch-{n:02d}">\n{body}\n{nav(n)}\n</article>')
    for n in missing:
        parts.append(f'''\n<article class="chapter" id="ch-{n:02d}">
  <div class="notyet"><h2>Chapter {n} — {chapter_title(a.wiki, n)}</h2>
  <p>This chapter has not been rebuilt in the current format yet.</p></div>
  {nav(n)}
</article>''')

    doc = (head + '<body id="top">\n\n' + TOPBAR +
           f'\n<header class="top"><div class="wrap"><div class="kicker">{a.title}</div>'
           f'<h1>{a.title}</h1><p style="color:var(--muted);margin:0">{a.subtitle}</p></div></header>\n\n'
           + '<main>\n' + "\n".join(parts) + '\n</main>\n'
           + '\n<footer><div class="wrap">Assembled by book-man.</div></footer>\n</body>\n</html>\n')

    out = a.out if os.path.isabs(a.out) else os.path.join(a.wiki, a.out)
    open(out, "w", encoding="utf-8").write(doc)

    # ---- self-check the merged artifact, because ids and anchors fail silently
    ids = re.findall(r'id="([^"]+)"', doc)
    dup = {i for i in ids if ids.count(i) > 1}
    dead = {l for l in re.findall(r'href="#([^"]+)"', doc) if l not in set(ids)}
    print(f"built:     {[n for n, _ in built]}")
    print(f"pending:   {missing}")
    print(f"duplicate ids: {sorted(dup)[:5] or 'none'}")
    print(f"dead links:    {sorted(dead)[:5] or 'none'}")
    print(f"tables wrapped: {doc.count('<table') == doc.count('class=\"tablewrap\"')}")
    print(f"written: {out} ({len(doc.encode())/1048576:.1f} MB)")
    if dup or dead:
        sys.exit("merged file has id/link collisions — fix before shipping")


if __name__ == "__main__":
    main()
