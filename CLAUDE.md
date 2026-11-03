# CLAUDE.md

HTML presentation decks built on reveal.js, published to GitHub Pages.

## Generating a deck

Use the `ppt` skill (`.claude/skills/ppt/SKILL.md`) — invoke it with `/ppt`, or
follow it directly whenever the task is "make a deck / slides / a presentation
from this outline". Do not improvise a deck without reading
`references/layouts.md` first; the layout catalog is the contract between the
skill and `framework/deck.css`.

## Workflow

```bash
python3 build.py --only <slug>   # assemble decks/<slug>/ into docs/
python3 check.py <slug>          # lint — must pass before publishing
./deploy.sh                      # commit, push, publish
```

A deck is not done until `check.py` reports zero errors.

## Conventions

- `decks/<slug>/slides.html` contains **only** top-level `<section>` elements.
  `build.py` supplies the `<html>`/`<head>`/`.reveal`/`.slides` scaffold.
- `docs/` is generated output. Never hand-edit it; it is overwritten on build.
  It *is* committed, because GitHub Pages serves `main` branch `/docs`.
- Layout comes from the classes in `framework/deck.css`. `check.py` fails any
  class not defined there, so a new layout means editing `deck.css` **and**
  documenting it in `references/layouts.md`.
- Inline `style=` is for genuine one-off values, not for building layouts.
- Every content slide needs `<aside class="notes">`.
- Charts: invoke the `dataviz` skill first, render inline SVG in `.chart-wrap`.
- A deck's whole palette derives from `accent` in `deck.json` — change that one
  value rather than hardcoding colors.

## Content integrity

Never invent numbers, quotes, dates, or attributions that the source outline
does not contain. Where a figure is implied but missing, put a visible `[TK]`
on the slide and list every placeholder when reporting back.

## Environment notes

- Python 3 stdlib only — there is no pip and no Node in this sandbox.
- reveal.js 5.2.1 is vendored under `framework/vendor/`; decks work offline.
- There is no browser here, so rendering cannot be screenshot-verified.
  `check.py` is the substitute: its overflow estimate is a text-metrics
  heuristic against the 1120×608 content box. Keep its geometry constants in
  sync if `deck.css` padding or type scale changes.
- Publishing needs `gh auth login`, which only the user can run interactively.
