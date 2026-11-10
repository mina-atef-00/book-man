# The page contract — component vocabulary

Every chapter page borrows the stylesheet from `templates/page-shell.html`. These are the
classes it defines. Use the container that matches the material, not the one you used last.

## Summary and legend

```html
<div class="onepara">
  <h3>The chapter in one paragraph</h3>
  <p>…the whole argument, before any detail…</p>
</div>

<div class="legend">
  <div><span class="sw sw-amber"></span><span><b>Amber</b> marks the author's judgement.</span></div>
  <div><span class="sw sw-quote"></span><span><b>Blue quotes</b> are national officials.</span></div>
  <div><span class="sw sw-eur"></span><span><b>Bronze quotes</b> are foreign voices.</span></div>
  <div><span class="sw sw-obs"></span><span><b>Violet quotes</b> are outside observers.</span></div>
</div>
```

## Section

```html
<details class="part" id="p3" open>
  <summary><div class="sumwrap"><h2><span class="num">3</span>Section title</h2></div></summary>
  <div class="wrap">
    <p class="orient">What this section does: …</p>
    …
    <div class="verdict"><b>Carry this forward:</b> …</div>
    <p class="pg">Section 3: pp. 94-101.</p>
  </div>
</details>
```

`open` on section 1 only, so the page never presents the whole book at the door.

## Containers

```html
<!-- two panels, one shaded -->
<div class="compare">
  <div><h4>Their proposal</h4><p>…</p></div>
  <div class="hi"><h4>The answer</h4><p>…</p></div>
</div>

<!-- stat tiles -->
<div class="stats">
  <div class="stat"><span class="n">$28bn</span><span class="l">Inter-Ally debts</span><span class="p">p. 42</span></div>
</div>

<!-- parallel cards -->
<div class="cards3">
  <div><h4>Kautsky</h4><p>…</p></div>
</div>

<!-- a true sequence: rail with dots, no numbers -->
<ul class="steps">
  <li><span class="st">Congress refuses</span><p>…</p></li>
</ul>

<!-- small arithmetic chain -->
<div class="chain"><span>$3.5bn owed</span><b>+</b><span>$4bn sold back</span><b>=</b><span>$7.5bn shift</span></div>

<!-- quotation with attribution and a gloss -->
<div class="qcard v-us">
  <p>"…"</p>
  <p class="who"><span class="vtag">WASHINGTON</span>Source, quoted at p. 50</p>
  <p class="gloss">Why it matters.</p>
</div>

<!-- the author's own words, larger -->
<div class="pullq v-allies">
  <p>"…"</p>
  <p class="who"><span class="vtag">EUROPE</span>Source, p. 56</p>
</div>

<!-- a judgement bar -->
<div class="verdict"><b>The sentence the chapter turns on:</b> …</div>
```

Voice classes: `v-us`, `v-allies`, `v-observer`.

## Figures

```html
<figure class="fig">
  <div class="svgwrap">
    <svg width="980" height="440" viewBox="0 0 980 440" role="img" aria-label="One sentence describing the picture.">
      <rect x="0" y="0" width="980" height="440" fill="#FAF7F0"/>
      <text x="490" y="60" text-anchor="middle" font-family="Atkinson Hyperlegible,Arial,sans-serif"
            font-size="21" font-weight="700" fill="#1B1B1B">Title</text>
    </svg>
  </div>
  <figcaption>Figure 3. What the reader should notice.</figcaption>
</figure>
```

Rules: explicit hex on every element (no `var()` inside SVG), text never below 19px,
labels inside their boxes, `aria-label` on the `<svg>`.

## Glossary, self-check, sources

```html
<div class="gloss-grid">
  <div class="gterm"><b>Amortise</b><p>Plain-words definition.</p><p class="where">p. 41</p></div>
</div>

<details><summary>1. Question?</summary><p>Answer with a page reference (p. 42).</p></details>
```

## Page chrome

```html
<input type="checkbox" id="density" hidden>
<input type="checkbox" id="wide" hidden>
<div class="ui">
  <label for="density"><span class="dot"></span>Argument only</label>
  <label for="wide" class="wide"><span class="dot"></span>Wide layout</label>
</div>
```

`#density:checked ~ main .prose` hides running explanations; `body:has(#wide:checked)` moves
the column to 1560px. Both are CSS-only by design.
