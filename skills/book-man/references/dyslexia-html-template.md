# Dyslexia-first HTML theme

This file is the quick reference for the theme's tokens. The authoritative method and the working shell live in
`references/output-formats/asdiagram-html.md` and `templates/dyslexia-page.html` — copy those, do not
write CSS from scratch.

An older Arial-on-#333 layout with a 700px measure used to be documented here. It is retired: Arial is not a
dyslexia-designed face, the narrow measure caused excess line breaks at the owner's text size, and the pale
ground was wrong. Do not reintroduce it.

## Tokens

| Token | Value | Why |
|---|---|---|
| Ground | `#FAF7F0` | Cream reduces glare that pure white causes. |
| Text | `#1B1B1B` | Off-black is easier than `#000`. |
| Muted | `#4A4640` | Keeps ≥7:1 contrast on the cream ground. |
| Accent | `#0B5C8A` | Links and numbers; 7.4:1 on cream. |
| Key term | `#FFE9A8` amber wash behind bold | Marks terms without relying on colour alone. |
| Card | `#FFFFFF`, `2px solid #E2DBCC` | Separates blocks without shadow noise. |
| Face | Atkinson Hyperlegible, then Arial, Verdana | Designed for low-vision and dyslexic readers. |
| Size | 20px root, ~1.05–1.1rem body, `line-height:1.7` | Ships the ~1.5× size the owner reads at. |
| Measure | `max-width:66ch` on prose blocks, in a centred column | Long lines lose the reader's place. 66ch ≈ 940px at body size; centre the column or it reads as a broken layout. |

## Hard rules

- No italics. `em` renders as underline. Bold carries emphasis, with the amber wash.
- Left-aligned, never justified — justification opens uneven word gaps.
- No JavaScript. Interactivity is `<details>`, `:target`, and checkboxes only; every section renders by default.
- No theme variables inside SVG — `var(--card)` falls back to black and the diagram renders as black boxes.
- Every SVG needs a pixel floor (`.svgwrap svg{min-width:700px}`) inside a scrollable wrapper; never
  `max-width:100%`, which shrinks a 980-unit viewBox to unreadable text on a phone.
- Find attached to a diagram belongs in `<figcaption>`, never as text inside the scroll area.

## Diagram geometry

Fixed box-chain coordinates, label character limits, and the full multi-page build order:
`references/chapter-page-pipeline.md`.
