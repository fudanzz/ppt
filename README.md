# Deck generator

Turn an outline into an HTML presentation deck (reveal.js), then publish it to
GitHub Pages as a browsable gallery.

The generator is a **Claude Code skill**: you hand Claude an outline, it decides
the layout for each slide and writes the markup. The Python here is plumbing —
it wraps slide markup in the shared shell, lints it, and publishes.

## Use it

In Claude Code, from this directory:

```
/ppt outlines/example.md
```

…or just paste an outline and ask for a deck. Claude will read the outline,
plan the slides, write `decks/<slug>/`, build, lint, and deploy.

## Manual commands

```bash
python3 build.py                   # build every deck into docs/
python3 build.py --only my-deck    # build one deck
python3 build.py --serve 8080      # build, then preview on :8080
python3 check.py                   # lint every deck
python3 check.py my-deck --strict  # lint one deck, warnings fail
./deploy.sh                        # build, lint, push, publish to Pages
```

No dependencies beyond Python 3 and (for publishing) `git` + `gh`. reveal.js is
vendored in `framework/vendor/`, so decks work offline.

## Layout

```
decks/<slug>/deck.json      title, accent, author, theme, tags
decks/<slug>/slides.html    the <section> elements — this is the deck
decks/<slug>/assets/        optional images for that deck

framework/deck.css          the design system: tokens + every layout
framework/deck.js           reveal.js bootstrap, dark toggle, PDF export
framework/template.html     the page shell build.py fills in
framework/gallery.html      the index page shell
framework/vendor/           vendored reveal.js 5.2.1

outlines/                   source outlines
docs/                       generated output — served by GitHub Pages
build.py                    assemble decks + gallery
check.py                    lint: overflow, bad classes, missing notes
deploy.sh                   commit, push, enable Pages

.claude/skills/ppt/         the skill Claude follows
  SKILL.md                  procedure and rules
  references/layouts.md     the layout catalog
  references/authoring.md   density rules and the fit budget
  references/deploy.md      publishing and auth
```

`docs/` is generated. Never edit it by hand — change `decks/` or `framework/`
and rebuild.

## Writing an outline

Plain markdown. Headings become sections, bullets become slide content. A short
preamble helps Claude make better choices:

```markdown
# Platform Strategy 2027

Subtitle: Where we invest over the next four quarters
Author: Priya Raman
Accent: #4f46e5

> Audience: exec staff. Purpose: approve the budget. 35 minutes.

## Context: why now
- Enterprise buyers consolidated onto fewer vendors
- Procurement cycles stretched from 60 to 110 days
```

See `outlines/example.md` for a fuller one, and the deck it produced in
`decks/platform-strategy-2027/`.

Claude will not invent figures. If your outline implies a number it doesn't
have, the slide gets a visible `[TK]` and you'll be told which ones to fill in.

## Presenting

| Key | Action |
| --- | --- |
| `→` / `←` / `Space` | Next / previous slide |
| `Esc` | Slide overview |
| `S` | Speaker notes window |
| `F` | Fullscreen |
| `T` | Toggle light / dark |
| `Shift`+`P` | Print view — then use the browser's Save as PDF |
| `Ctrl`+`Shift`+`F` | Search slide text |
| `B` | Pause / black screen |

For PDF export, press `Shift`+`P` (or add `?print-pdf` to the URL), then print
with background graphics enabled and margins set to none.

## Theming

One value in `deck.json` restyles a whole deck:

```json
{ "accent": "#0f766e", "theme": "dark" }
```

Everything — bullets, numbered discs, card highlights, metric emphasis, chart
series, links, the progress bar — derives from `accent`. Pick an accent with
luminance similar to the `#4f46e5` default so text contrast holds up; very light
pastels will fail accessibility.

## Adding a layout

Add the CSS to `framework/deck.css`, then document it in
`.claude/skills/ppt/references/layouts.md` with copy-paste markup. `check.py`
fails any class that isn't defined in `deck.css`, so the two stay in sync.
