#!/usr/bin/env python3
"""Assemble HTML decks and the gallery that indexes them.

This is plumbing only: it wraps hand-authored slide markup in the shared
reveal.js shell, copies assets, and regenerates the gallery. All content and
layout decisions live in decks/<slug>/slides.html.

Layout on disk:

    decks/<slug>/deck.json    deck metadata (title, accent, author, ...)
    decks/<slug>/slides.html  the <section> elements, nothing else
    decks/<slug>/assets/      optional per-deck images (copied verbatim)

Output:

    docs/index.html           gallery
    docs/assets/              shared framework assets (deck.css, vendor/, ...)
    docs/<slug>/index.html    one built deck

Usage:
    python3 build.py                 build every deck + gallery
    python3 build.py --only my-deck  build a single deck (gallery still rebuilt)
    python3 build.py --serve 8080    build, then serve docs/ for preview
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRAMEWORK = ROOT / "framework"
DECKS = ROOT / "decks"
SITE = ROOT / "docs"

# Files/dirs copied from framework/ into docs/assets/
SHARED_ASSETS = ["deck.css", "deck.js", "vendor"]

DEFAULTS = {
    "title": "Untitled deck",
    "subtitle": "",
    "description": "",
    "author": "",
    "date": "",
    "accent": "#4f46e5",
    "theme": "light",
    "lang": "en",
    "tags": [],
    "extra_css": "",
    "draft": False,
}

HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class TopLevelSectionCounter(HTMLParser):
    """Counts top-level <section> elements, treating a vertical stack as one."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.count = 0

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "section":
            if self.depth == 0:
                self.count += 1
            self.depth += 1

    def handle_endtag(self, tag) -> None:
        if tag == "section" and self.depth > 0:
            self.depth -= 1


def count_slides(markup: str) -> int:
    p = TopLevelSectionCounter()
    p.feed(markup)
    p.close()
    return p.count


def load_meta(slug: str, deck_dir: Path) -> dict:
    meta = dict(DEFAULTS)
    meta["tags"] = []
    path = deck_dir / "deck.json"
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"error: {path} is not valid JSON - {exc}")
        unknown = set(raw) - set(DEFAULTS)
        if unknown:
            print(
                f"  ! {slug}: ignoring unknown deck.json keys: "
                f"{', '.join(sorted(unknown))}",
                file=sys.stderr,
            )
        meta.update({k: v for k, v in raw.items() if k in DEFAULTS})

    if not HEX_RE.match(str(meta["accent"])):
        print(
            f"  ! {slug}: accent {meta['accent']!r} is not a hex color, "
            f"using {DEFAULTS['accent']}",
            file=sys.stderr,
        )
        meta["accent"] = DEFAULTS["accent"]
    if meta["theme"] not in ("light", "dark"):
        meta["theme"] = "light"
    if not meta["description"]:
        meta["description"] = meta["subtitle"] or meta["title"]
    return meta


def render(template: str, values: dict) -> str:
    out = template
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    leftover = re.findall(r"\{\{([A-Z_]+)\}\}", out)
    if leftover:
        raise SystemExit(
            f"error: template placeholder(s) never filled: {sorted(set(leftover))}"
        )
    return out


def build_deck(slug: str, deck_dir: Path, template: str):
    slides_path = deck_dir / "slides.html"
    if not slides_path.exists():
        print(f"  - {slug}: no slides.html, skipped", file=sys.stderr)
        return None

    meta = load_meta(slug, deck_dir)
    slides = slides_path.read_text(encoding="utf-8")
    n = count_slides(slides)
    if n == 0:
        print(f"  ! {slug}: slides.html has no <section> elements", file=sys.stderr)

    out_dir = SITE / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    page = render(
        template,
        {
            "LANG": html.escape(meta["lang"], quote=True),
            "THEME": meta["theme"],
            "TITLE": html.escape(meta["title"], quote=True),
            "DESCRIPTION": html.escape(meta["description"], quote=True),
            "ACCENT": meta["accent"],
            "EXTRA_CSS": meta["extra_css"],
            "ASSETS": "../assets",
            "HOME": "../",
            "SLIDES": slides,
        },
    )
    (out_dir / "index.html").write_text(page, encoding="utf-8")

    # Per-deck images, if any
    src_assets = deck_dir / "assets"
    dst_assets = out_dir / "assets"
    if dst_assets.exists():
        shutil.rmtree(dst_assets)
    if src_assets.is_dir():
        shutil.copytree(src_assets, dst_assets)

    print(f"  + {slug}  ({n} slide{'s' if n != 1 else ''})")
    meta["slug"] = slug
    meta["slides"] = n
    return meta


def copy_shared_assets() -> None:
    dst = SITE / "assets"
    dst.mkdir(parents=True, exist_ok=True)
    for name in SHARED_ASSETS:
        src = FRAMEWORK / name
        if not src.exists():
            raise SystemExit(f"error: missing framework asset: {src}")
        target = dst / name
        if src.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)


def _neg_date(value: str) -> str:
    """Invert a YYYY-MM-DD string so plain ascending sort yields newest first."""
    if not value:
        return ""
    return "".join(
        chr(ord("9") - (ord(c) - ord("0"))) if c.isdigit() else c for c in value
    )


def _gallery_card(d: dict) -> str:
    def e(s):
        return html.escape(str(s), quote=True)

    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in (d.get("tags") or []))
    bits = []
    if d["date"]:
        bits.append(f"<span>{e(d['date'])}</span>")
    if d["author"]:
        bits.append(f"<span>{e(d['author'])}</span>")
    bits.append(f"<span>{d['slides']} slides</span>")
    meta_row = '<span class="sep">&middot;</span>'.join(bits)

    sub = f'<p class="g-sub">{e(d["subtitle"])}</p>' if d["subtitle"] else ""
    return f"""        <a class="g-card" href="./{e(d['slug'])}/" style="--accent: {e(d['accent'])}">
          <span class="g-swatch"></span>
          <span class="g-main">
            <h2>{e(d['title'])}</h2>
            {sub}
            <span class="g-meta">{meta_row}</span>
            <span class="g-tags">{tags}</span>
          </span>
          <span class="g-arrow">&rarr;</span>
        </a>"""


def build_gallery(decks: list) -> None:
    tpl_path = FRAMEWORK / "gallery.html"
    if not tpl_path.exists():
        raise SystemExit(f"error: missing {tpl_path}")

    def sort_key(d: dict):
        # Newest first; decks without a date sort last, then alphabetical.
        return (0 if d["date"] else 1, _neg_date(d["date"]), d["title"].lower())

    visible = [d for d in decks if not d.get("draft")]
    visible.sort(key=sort_key)

    if not visible:
        cards = (
            '<p class="empty">No decks yet. Add one under '
            "<code>decks/&lt;slug&gt;/</code> and re-run "
            "<code>python3 build.py</code>.</p>"
        )
    else:
        cards = "\n".join(_gallery_card(d) for d in visible)

    page = render(
        tpl_path.read_text(encoding="utf-8"),
        {
            "CARDS": cards,
            "COUNT": str(len(visible)),
            "BUILT": date.today().isoformat(),
            "ACCENT": visible[0]["accent"] if visible else DEFAULTS["accent"],
        },
    )
    (SITE / "index.html").write_text(page, encoding="utf-8")

    drafts = len(decks) - len(visible)
    note = f", {drafts} draft hidden" if drafts else ""
    print(f"  + gallery ({len(visible)} deck{'s' if len(visible) != 1 else ''}{note})")


def discover(only):
    if not DECKS.is_dir():
        return []
    dirs = sorted(
        p for p in DECKS.iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    if only:
        dirs = [p for p in dirs if p.name == only]
        if not dirs:
            raise SystemExit(f"error: no deck named {only!r} under {DECKS}")
    return dirs


def main() -> int:
    ap = argparse.ArgumentParser(description="Build HTML decks and the gallery.")
    ap.add_argument("--only", metavar="SLUG", help="build just this deck")
    ap.add_argument(
        "--serve",
        nargs="?",
        const=8080,
        type=int,
        metavar="PORT",
        help="serve docs/ after building (default port 8080)",
    )
    ap.add_argument("--clean", action="store_true", help="wipe docs/ before building")
    args = ap.parse_args()

    if args.clean and SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True, exist_ok=True)

    template = (FRAMEWORK / "template.html").read_text(encoding="utf-8")

    print("building decks:")
    built = []
    for deck_dir in discover(args.only):
        meta = build_deck(deck_dir.name, deck_dir, template)
        if meta:
            built.append(meta)

    # The gallery always reflects every deck on disk, even with --only.
    all_meta = built
    if args.only:
        all_meta = []
        for deck_dir in discover(None):
            if not (deck_dir / "slides.html").exists():
                continue
            m = load_meta(deck_dir.name, deck_dir)
            m["slug"] = deck_dir.name
            m["slides"] = count_slides(
                (deck_dir / "slides.html").read_text(encoding="utf-8")
            )
            all_meta.append(m)

    copy_shared_assets()
    build_gallery(all_meta)

    # GitHub Pages: skip Jekyll so paths like _assets are served verbatim.
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    print(f"\ndone - docs/ ready ({len(all_meta)} deck(s))")

    if args.serve:
        import http.server
        import socketserver

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **kw):
                super().__init__(*a, directory=str(SITE), **kw)

            def log_message(self, fmt, *a):  # quieter output
                pass

        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("0.0.0.0", args.serve), Handler) as httpd:
            print(f"serving docs/ on http://localhost:{args.serve}  (ctrl-c to stop)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
