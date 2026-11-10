# Component kit — mixed-format chapter pages

Copy from here instead of re-deriving. Every rule below was verified in a real browser at 390, 600, 900,
1400 and 1920px. All interactivity is CSS-only; no JavaScript, ever.

Method and page shell: `references/output-formats/asdiagram-html.md`.
Theme tokens: `references/dyslexia-html-template.md`.

## Skeleton — order matters

```html
<body>
<input type="checkbox" id="density" hidden>
<input type="checkbox" id="wide" hidden>

<div class="ui">
  <label for="density"><span class="dot"></span>Argument only</label>
  <label for="wide" class="wide"><span class="dot"></span>Wide layout</label>
  <span class="hint">Hides the running explanations and page numbers.</span>
</div>

<header class="top">…</header>
<nav class="anchors">…</nav>

<main>
  <details class="part" id="p1" open>
    <summary><div class="sumwrap"><h2><span class="num">1</span>Section title</h2></div></summary>
    <div class="wrap">
      <p class="orient">What this section does: …</p>
      …containers…
      <div class="verdict"><b>Carry this forward:</b> …</div>
    </div>
  </details>
</main>
```

The two checkboxes are siblings of `.ui` and `main` because the toggle rules use `~`. Put them anywhere
else and the switches render but do nothing.

## Tokens and column

```css
:root{--ground:#FAF7F0;--ink:#1B1B1B;--muted:#4A4640;--accent:#0B5C8A;--amber:#FFE9A8;
      --card:#FFFFFF;--line:#E2DBCC;--warn:#A8342A;
      --colw:1060px;--gutter:1.6rem;--measure:66ch;}
body:has(#wide:checked){--colw:1560px;--measure:78ch;}      /* the width switch */

.wrap{width:100%;max-width:var(--colw);margin:0 auto;padding:0 var(--gutter);}
p,li{max-width:var(--measure);}
.prose{max-width:var(--measure);}
```

`--colw:1060px` is chosen so a 980-wide SVG fits flush inside it (1060 − 2×32 gutter = 996).

## Sections: collapsible + sticky heading

```css
.part{padding:0;border-bottom:2px solid var(--line);}
.part>summary{padding:0;cursor:pointer;list-style:none;background:var(--ground);
    border-bottom:2px solid transparent;}
.part>summary .sumwrap{max-width:var(--colw);margin:0 auto;width:100%;
    padding:1.35rem var(--gutter) 1.1rem;display:flex;align-items:center;gap:.7rem;}
.part>summary .sumwrap::after{content:"+";margin-left:auto;font-size:1.6rem;color:var(--muted);}
.part[open]>summary .sumwrap::after{content:"\2212";}
.part[open]>summary{position:sticky;top:0;z-index:12;border-bottom:3px solid var(--accent);}
.part>summary h2{margin:0;font-size:1.45rem;max-width:none;}
.part>summary::-webkit-details-marker{display:none;}

#p1{--accent:#0B5C8A;} #p2{--accent:#1F6F4A;} #p3{--accent:#8A4B0B;}
#p4{--accent:#7A2E5E;} #p5{--accent:#4F3F8C;}
```

The `.sumwrap` is a real box with the same max-width and gutter as `.wrap`. Do **not** try to reproduce
that alignment with `padding-left:calc((100% - var(--colw))/2 + var(--gutter))` on the summary — the two
formulas disagree by a few pixels at every width and the heading visibly misses the text edge.

Open the first section only (`open` on `#p1`); reference sections (numbers, glossary, self-check,
sources) stay closed.

## Switches

```css
#density:checked ~ main .prose,
#density:checked ~ main .gloss,
#density:checked ~ main .pg,
#density:checked ~ main .steps p{display:none;}

.ui label{cursor:pointer;display:inline-flex;align-items:center;gap:.55rem;font-weight:700;
    border:2px solid var(--line);border-radius:999px;padding:.35rem .9rem;background:var(--card);}
.ui label .dot{width:1.05rem;height:1.05rem;border-radius:50%;background:#C9BFA8;border:2px solid #8E8676;}
#density:checked ~ .ui label .dot{background:#1F6F4A;border-color:#1F6F4A;}
#wide:checked ~ .ui label.wide .dot{background:#0B5C8A;border-color:#0B5C8A;}
```

## Containers

| Class | Markup | Use |
|---|---|---|
| `.compare` | `<div class="compare"><div><h4>A</h4>…</div><div class="hi"><h4>B</h4>…</div></div>` | two things set against each other; `.hi` tints the second |
| `.stats` | `<div class="stats"><div class="stat"><span class="n">$88bn</span><span class="l">label</span><span class="p">p. 42</span></div>…` | a handful of quantities |
| `.steps` | `<ul class="steps"><li><span class="st">Event</span><p>detail</p></li></ul>` | a real sequence, on a rail |
| `.cards3` | `<div class="cards3"><div><h4>T</h4><p>…</p></div>…` | parallel claims about different actors |
| `.pullq` | `<div class="pullq"><p>"…"</p><p class="who">source</p></div>` | the author's own judgement |
| `.qcard` | `<div class="qcard v-us"><p>"…"</p><p class="who"><span class="vtag">Washington</span>…</p><p class="gloss">why it matters</p></div>` | a document, letter or speech |
| `.verdict` | `<div class="verdict"><b>Carry this forward:</b> …</div>` | the one line to remember |
| `.chain` | `<div class="chain"><span>$3.5bn</span><b>+</b><span>…</span><b>=</b><span>…</span></div>` | a small arithmetic chain |
| `.onepara` | `<div class="onepara"><h3>The chapter in one paragraph</h3><p>…</p></div>` | the whole chapter before any detail |
| `.legend` | swatches explaining amber / panel / voice tints | the page's visual grammar |
| `.gloss-grid` / `.gterm` | term, plain definition, page refs | scaffolding the book does not provide |

```css
.compare{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.4rem 0;}
.compare>div{background:var(--card);border:2px solid var(--line);border-radius:14px;
    padding:1rem 1.15rem;min-width:0;}
.compare>div.hi{background:#FFF7E0;border-color:#C9A227;}
@media (max-width:680px){.compare{grid-template-columns:1fr;}}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:.9rem;}
.stat{background:var(--card);border:2px solid var(--line);border-radius:14px;padding:.9rem 1rem;min-width:0;}
.stat .n{display:block;font-size:1.75rem;font-weight:700;color:var(--accent);line-height:1.15;}
.stat .l{display:block;font-size:.96rem;color:var(--muted);margin-top:.3rem;}

.steps{list-style:none;margin:1.3rem 0 1.3rem .5rem;padding:0 0 0 1.7rem;border-left:3px solid #C9BFA8;}
.steps>li{position:relative;padding-bottom:1.25rem;}
.steps>li::before{content:"";position:absolute;left:-2.13rem;top:.55rem;width:.85rem;height:.85rem;
    border-radius:50%;background:var(--accent);}

.cards3{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.9rem;}
.cards3>div{background:var(--card);border:2px solid var(--line);border-radius:14px;
    padding:.95rem 1.05rem;min-width:0;}

.verdict{background:var(--amber);border-radius:12px;padding:1rem 1.2rem;font-size:1.05rem;max-width:74ch;}
.pullq{background:var(--card);border-left:8px solid var(--accent);border-radius:0 14px 14px 0;
    padding:1.1rem 1.3rem;max-width:74ch;}
.qcard{background:var(--card);border:2px solid var(--line);border-radius:14px;
    padding:1rem 1.15rem;max-width:74ch;}
.qcard .gloss{border-top:2px solid var(--line);padding-top:.5rem;margin:.5rem 0 0;color:var(--muted);}

/* voices */
.qcard.v-us,.pullq.v-us{border-left-color:#0B5C8A;background:#F3F7FB;}
.qcard.v-allies,.pullq.v-allies{border-left-color:#8A4B0B;background:#FBF6F0;}
.qcard.v-observer,.pullq.v-observer{border-left-color:#4F3F8C;background:#F8F6FC;}
.vtag{font-size:.82rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);display:block;}
```

`min-width:0` on grid children is not optional. Without it a single unbreakable line inside a tile or
panel sets the track's min-content width and blows the layout past the viewport.

## Accordions vs sections — the selector trap

```css
details:not(.part){background:var(--card);border:2px solid var(--line);border-radius:12px;
    padding:.9rem 1.1rem;margin:.9rem 0;max-width:76ch;}
details.part{max-width:none;background:transparent;border:0;border-bottom:2px solid var(--line);}
```

A bare `details{…}` written for the self-check accordions also matches every `<details class="part">`,
which gives whole sections a 2px box, a white background and a 76ch width cap. The symptom the owner
reports is "the content only fills half the page" and "there is a line down the left side". Scope it.

## Verification (browser is the only authority)

```js
// every label inside its canvas
Array.from(document.querySelectorAll('svg')).map(s=>{const vb=s.viewBox.baseVal,n=[];
  s.querySelectorAll('text').forEach(t=>{const r=t.getBBox();
    if(r.x<vb.x-1||r.y<vb.y-1||r.x+r.width>vb.x+vb.width+1||r.y+r.height>vb.y+vb.height+1)
      n.push(t.textContent.slice(0,20));});return n.length;})

// page overflow, at 390/600/900/1400/1920
document.documentElement.scrollWidth > document.documentElement.clientWidth + 1

// heading must align with the text column
Math.abs(h2.getBoundingClientRect().left - p.getBoundingClientRect().left) < 2

// no full-height rail anywhere
[...document.querySelectorAll('*')].filter(e=>parseFloat(getComputedStyle(e).borderLeftWidth)>=4
  && e.getBoundingClientRect().height>1000)
```

Centring check: compare the column's left gap against `document.documentElement.clientWidth`, not
`window.innerWidth` — the scrollbar makes a correctly centred column look off by ~15px otherwise.
