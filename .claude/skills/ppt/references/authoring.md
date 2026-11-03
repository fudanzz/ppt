# Authoring rules

How to pick layouts and size content so slides don't overflow. Read alongside
`layouts.md`.

## The fit budget

The design canvas is **1280 × 720** with 56px vertical and 80px horizontal
padding, so the usable content box is **1120 × 608**.

Nothing clips the overflow — content just runs off the bottom edge, and you
won't see it unless you count. So count.

Rough vertical costs at the default type scale:

| Element | Height |
| --- | --- |
| `.eyebrow` | 30px |
| `h2` (one line) | 43px |
| `h2` (two lines) | 85px |
| `.s-head` bottom margin | 38px |
| One `<li>` (one line) | 51px |
| One `<li>` (two lines) | 84px |
| `.lede` line | 37px |
| `.card` (3-line body) | ~175px |
| `.metric` | ~150px |
| `.tl-row` | ~95px |
| Table header + row | 40px + 46px |
| `pre` line | 26px |
| `.footnote` | 48px |

**A typical content slide: eyebrow + two-line h2 + margin = 153px, leaving
455px for the body — about 8 single-line bullets, or 5 that wrap to two lines.**

When you're over budget, in this order:
1. Cut words. Most bullets lose a third of their length with no loss of meaning.
2. Move the detail into `<aside class="notes">`.
3. Add `class="dense"` to the section (buys ~12%).
4. Split into two slides.

Never shrink type with inline `style=` to force a fit — that breaks the visual
system across the deck.

## Hard caps

| Thing | Cap |
| --- | --- |
| Bullets per slide | 6 |
| Words per bullet | 14 |
| Words of body text per slide | 45 |
| `h1` characters | 45 |
| `h2` characters | 60 |
| Cards per row | 4 (3 is better) |
| Metrics per row | 4 |
| Timeline rows | 5 |
| Steps | 5 |
| Table rows / columns | 6 / 5 |
| Code lines / columns | 14 / 62 |
| `.b-val` characters | 6 |

## Choosing a layout

Match the layout to the *shape of the idea*, not to variety for its own sake:

| The idea is… | Use |
| --- | --- |
| A list of related points | bullets |
| Terms needing definition | `ul.defs` |
| A real sequence or ranking | `<ol>` |
| 2–4 parallel things | `cards` |
| Numbers that are the point | `metrics` |
| One number that is the point | `l-big` |
| Two things weighed | `compare` |
| Two things merely adjacent | `l-two` |
| A process | `steps` (≤5, no dates) or `timeline` (dated) |
| A trend or distribution | chart (invoke `dataviz`) |
| Precise multi-dimensional values | table |
| Someone else's words | `l-quote` |
| A new part of the deck | `l-section` |

Repetition is fine when the shape repeats — three `metrics` slides in a row beat
contorting two of them into layouts that don't fit. What you want to avoid is
the same layout for ideas of *different* shapes.

## Headlines

The headline carries the message. Write the conclusion, not the topic.

- Topic: "Customer churn" → Headline: "Churn is concentrated in month two"
- Topic: "Hiring plan" → Headline: "We need six engineers before the EU launch"
- Topic: "Results" → Headline: "Revenue grew 34% on enterprise renewals"

A reader who sees only the headlines should get the whole argument. After
drafting, read your headlines in sequence — if they don't tell a story, the
deck's structure is wrong, not just its wording.

## Deck arc

```
Title
Context / why now           1–2 slides
[Section divider]
Body                        grouped into 2–4 sections
[Section divider]
Takeaway / recommendation   1 slide
The ask / close             1 slide
```

Drop section dividers below ~8 slides. Above ~25 slides, ask whether the back
half belongs in an appendix (a vertical stack, or a `draft` second deck).

## Speaker notes

Every content slide gets `<aside class="notes">`. This is what makes sparse
slides work — the detail lives in the notes, not on screen.

Write what you would *say*, not a repeat of the bullets:

```html
<aside class="notes">
  The month-two cliff is the whole story — 60% of churn lands in a 30-day
  window. Anchor on that before moving to causes. If asked about month one:
  that's mostly failed activation, which we cover two slides on.
</aside>
```

Include anticipated questions and the transition to the next slide. Skip notes
only on `l-title` and `l-section` where there is nothing to say.

## Fragments

`class="fragment"` on a list item reveals it on the next keypress. Use it when
you want the audience listening to you rather than reading ahead — a build of
3–5 points, or a punchline you don't want spoiled. Skip it when the list is
reference material the audience should scan at once. Never fragment more than
5 items on one slide, and don't fragment a single-item slide.

## Accessibility and contrast

- Real `alt` text on every image; `alt=""` only for pure decoration.
- Charts get `role="img"` and an `aria-label` stating the finding.
- Never encode meaning in color alone — pair it with a label, icon, or position.
- The accent is used for text in `--accent-ink`, which is darkened against the
  light background. A very light accent (pastels, yellows) will fail contrast.
  Prefer accents with a luminance comparable to the `#4f46e5` default.
- Check the deck in both light and dark (`T` toggles) before publishing.

## Numbers and sourcing

- Format consistently across the deck: `$4.2M`, `34%`, `1.9M` — pick a style
  and hold it.
- Put the unit in `.m-unit` inside `.m-val` so it renders smaller.
- Any slide with data the audience might question gets a `.footnote` naming the
  source and as-of date.
- **Never invent a figure.** If the outline implies a number you don't have,
  write `[TK]` on the slide and report every placeholder to the user at the end.
