---
name: ppt
description: Generate an HTML presentation deck (reveal.js) from a user-provided outline, then build and publish it. Use when the user asks to make a deck, slides, a presentation, a "ppt", or to turn an outline/notes/doc into slides — and when they ask to restyle, extend, or re-deploy an existing deck in this repo.
---

# Deck generator

Turn an outline into a reveal.js deck in `decks/<slug>/`, build it into `docs/`,
and publish to GitHub Pages.

You are doing the design work. `build.py` only wraps your slide markup in the
shared shell — it makes no layout decisions. Your job is choosing the right
layout per slide and writing content that fits.

## Inputs

The outline may arrive as a file path argument, pasted text, or an existing file
in `outlines/`. Resolve it in that order. If no outline is findable, ask for one
rather than inventing a topic.

Before writing slides, settle these — infer from the outline where you can, and
ask only when a wrong guess would mean redoing the deck:

| Need | Default if unstated |
| --- | --- |
| Slug | kebab-case from the title |
| Audience & purpose | infer from outline tone |
| Accent color | `#4f46e5` |
| Light or dark | `light` |
| Author / date | author blank, date = today |
| Target slide count | one slide per outline leaf, merged where thin |

## Procedure

1. **Read the outline fully** before writing anything. Note its depth — top-level
   headings usually become section dividers, leaves become content slides.

2. **Read `references/layouts.md`.** It is the catalog of every available layout
   with copy-paste markup. Do not invent new CSS classes when a layout exists;
   if you genuinely need a new one, add it to `framework/deck.css` *and* document
   it in the catalog.

3. **Read `references/authoring.md`** for content density rules, the fit budget,
   and speaker-note conventions. These are what keep slides from overflowing.

4. **Plan the deck** before writing markup. For each slide: a one-line purpose,
   the chosen layout, and the headline. Keep the plan in your head or in a short
   list — do not create a plan file unless the user asks. Sanity-check the arc:
   title → context → body sections → takeaway → close.

5. **Write `decks/<slug>/deck.json`** — see the schema below.

6. **Write `decks/<slug>/slides.html`** — only top-level `<section>` elements, no
   `<html>`/`<head>`/`.reveal`/`.slides` wrapper. `build.py` supplies all of that.

7. **If a slide needs a chart**, invoke the `dataviz` skill before writing any
   chart markup, and render inline SVG inside `.chart-wrap`. Never screenshot a
   chart. Use the deck accent as the primary series color.

8. **Build**: `python3 build.py --only <slug>`.

9. **Verify** with `python3 check.py <slug>`. It flags overflow risk, bad layout
   class names, unbalanced tags, and missing speaker notes. Fix what it reports
   and rebuild. A deck that fails `check.py` is not done.

10. **Publish**: `./deploy.sh`. Read `references/deploy.md` first — it covers the
    one-time GitHub auth, and what to do when auth is missing. Report the live
    URL back to the user.

## deck.json schema

Every key is optional except `title`. Unknown keys are ignored with a warning.

```json
{
  "title": "Platform Strategy 2027",
  "subtitle": "Where we invest over the next four quarters",
  "description": "Used for <meta> tags and the gallery",
  "author": "Priya Raman",
  "date": "2026-11-03",
  "accent": "#4f46e5",
  "theme": "light",
  "lang": "en",
  "tags": ["strategy", "internal"],
  "extra_css": "",
  "draft": false
}
```

- `accent` must be a 3- or 6-digit hex color. The whole deck derives tints,
  borders, and text shades from it, so one value restyles everything.
- `theme` is `light` or `dark`. Viewers can toggle at runtime with `T`.
- `draft: true` builds the deck but hides it from the gallery index.
- `extra_css` is injected into the deck's `<style>` block for genuine one-offs.
  Prefer adding a reusable layout to `deck.css` over piling up `extra_css`.

## Hard rules

- **`slides.html` holds slide markup only.** No document scaffold.
- **Never hand-edit `docs/`.** It is generated output; your edits get
  overwritten on the next build. Edit `decks/<slug>/` or `framework/` instead.
- **One idea per slide.** If a slide needs more than ~6 bullets or ~45 words of
  body text, split it or move the detail into speaker notes.
- **Every content slide gets `<aside class="notes">`.** That is where the actual
  talk track lives; the slide itself stays sparse.
- **Use the layout classes.** Inline `style=` is for a genuine one-off value
  (a grid span, an image aspect), not for building a layout from scratch.
- **Don't restate the outline verbatim.** Sharpen headlines into claims. "Revenue
  grew" is a topic; "Revenue grew 34% on enterprise renewals" is a headline.
- **Preserve the user's facts exactly.** Never invent numbers, quotes, dates, or
  attributions that the outline does not contain. If the outline implies a
  figure you do not have, write a visible `[TK]` placeholder and list every one
  of them in your final summary so the user can fill them in.

## Updating an existing deck

Edit `decks/<slug>/slides.html` in place, rerun `build.py --only <slug>`,
`check.py <slug>`, then `deploy.sh`. Keep the slug stable so the published URL
does not change.
