#!/usr/bin/env python3
"""Lint a deck's slides.html before publishing.

Catches the failure modes that are invisible until someone presents the deck:
content running off the bottom of a slide, class names that don't exist in
deck.css, missing speaker notes, broken image paths, and unfilled [TK] markers.

The overflow check is a heuristic text-metrics estimate, not a browser layout.
It is tuned to flag real problems; treat a WARN as "go look at that slide".

Usage:
    python3 check.py              # every deck
    python3 check.py my-deck      # one deck
    python3 check.py --strict     # exit non-zero on warnings too
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECKS = ROOT / "decks"
DECK_CSS = ROOT / "framework" / "deck.css"

# --- Canvas geometry (must track framework/deck.css) -------------------------
CANVAS_H = 720
CANVAS_W = 1280
PAD_V = 56
PAD_H = 80
BODY_H = CANVAS_H - 2 * PAD_V   # 608
BODY_W = CANVAS_W - 2 * PAD_H   # 1120

# Average glyph advance as a fraction of font size, for a humanist sans.
GLYPH = 0.52

# Classes reveal.js provides that won't appear in deck.css.
REVEAL_CLASSES = {
    "reveal", "slides", "notes", "fragment", "fade-in", "fade-out", "fade-up",
    "fade-down", "fade-left", "fade-right", "grow", "shrink", "strike",
    "highlight-red", "highlight-green", "highlight-blue", "current-visible",
    "semi-fade-out", "r-stretch", "r-fit-text", "r-frame", "stack", "present",
    "past", "future", "hljs", "code-wrapper",
}

VOID = {"img", "br", "hr", "input", "meta", "link", "source", "col"}

# Content caps from references/authoring.md
CAPS = {
    "bullets": 6,
    "bullet_words": 14,
    "h1_chars": 45,
    "h2_chars": 60,
    "cards": 4,
    "metrics": 4,
    "timeline_rows": 5,
    "steps": 5,
    "table_rows": 6,
    "table_cols": 5,
    "code_lines": 14,
    "code_cols": 62,
    "bigval_chars": 6,
}


class Node:
    __slots__ = ("tag", "classes", "attrs", "children", "text", "parent", "line")

    def __init__(self, tag, attrs=None, line=0, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.classes = set((self.attrs.get("class") or "").split())
        self.children = []
        self.text = ""
        self.parent = parent
        self.line = line

    def find_all(self, tag=None, cls=None):
        out = []
        for c in self.children:
            if (tag is None or c.tag == tag) and (cls is None or cls in c.classes):
                out.append(c)
            out.extend(c.find_all(tag, cls))
        return out

    def direct(self, tag=None, cls=None):
        return [
            c
            for c in self.children
            if (tag is None or c.tag == tag) and (cls is None or cls in c.classes)
        ]

    def all_text(self):
        return re.sub(r"\s+", " ", self.raw_text()).strip()

    def raw_text(self):
        """Concatenated descendant text with whitespace preserved.

        Needed for <pre>, where newlines and column widths are meaningful.
        """
        s = self.text
        for c in self.children:
            if "notes" in c.classes:
                continue
            s += c.raw_text()
        return s

    def has_ancestor_class(self, cls):
        p = self.parent
        while p is not None:
            if cls in p.classes:
                return True
            p = p.parent
        return False

    def has_ancestor_tag(self, tag):
        p = self.parent
        while p is not None:
            if p.tag == tag:
                return True
            p = p.parent
        return False


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.stack = [self.root]
        self.errors = []

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, attrs, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(n)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                if i != len(self.stack) - 1:
                    unclosed = [s.tag for s in self.stack[i + 1:]]
                    self.errors.append(
                        f"line {self.getpos()[0]}: </{tag}> closed while "
                        f"{', '.join('<' + u + '>' for u in unclosed)} still open"
                    )
                del self.stack[i:]
                return
        self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")

    def handle_data(self, data):
        self.stack[-1].text += data

    def close(self):
        super().close()
        if len(self.stack) > 1:
            for s in self.stack[1:]:
                self.errors.append(f"line {s.line}: <{s.tag}> never closed")


# --- Height estimation ------------------------------------------------------

def lines(text, width_px, font_px):
    """Estimated wrapped line count for text in a box."""
    text = text.strip()
    if not text:
        return 0
    per_line = max(8, int(width_px / (font_px * GLYPH)))
    return max(1, math.ceil(len(text) / per_line))


def est_height(node, width, scale=1.0):
    """Estimate rendered height of a node's subtree, in px.

    `width` is the available content width; `scale` shrinks the type scale
    (used for section.dense).
    """
    t, cls = node.tag, node.classes

    if "notes" in cls:
        return 0

    def f(px):
        return px * scale

    # --- Grid/flex containers: height is the tallest child, not the sum ---
    if "cols" in cls:
        kids = node.direct()
        if not kids:
            return 0
        if "narrow-left" in cls:
            parts = [2 / 5, 3 / 5]
        elif "narrow-right" in cls:
            parts = [3 / 5, 2 / 5]
        else:
            parts = [1 / len(kids)] * len(kids)
        gap = 56
        inner = width - gap * (len(kids) - 1)
        return max(
            est_height(k, inner * parts[min(i, len(parts) - 1)], scale)
            for i, k in enumerate(kids)
        )

    # Row-like containers lay children side by side, so height is the tallest.
    if cls & {"tl-row", "legend", "row", "meta"}:
        kids = node.direct()
        if not kids:
            return lines(node.all_text(), width, f(23)) * f(33)
        if "tl-row" in cls:
            # grid-template-columns: 112px 1fr, gap 26px
            widths = [112.0] + [width - 112 - 26] * (len(kids) - 1)
        else:
            widths = [width / len(kids)] * len(kids)
        tallest = max(
            est_height(k, widths[min(i, len(widths) - 1)], scale)
            for i, k in enumerate(kids)
        )
        return tallest + (36 if "tl-row" in cls else 0)

    if cls & {"cards", "metrics", "compare", "steps"}:
        kids = node.direct()
        if not kids:
            return 0
        ncols = len(kids)
        for c in cls:
            m = re.fullmatch(r"cols-(\d)", c)
            if m:
                ncols = int(m.group(1))
        ncols = max(1, ncols)
        gap = 26 if "compare" in cls else 18
        colw = (width - gap * (ncols - 1)) / ncols
        rows = math.ceil(len(kids) / ncols)
        tallest = max(est_height(k, colw, scale) for k in kids)
        return tallest * rows + gap * (rows - 1)

    # --- Leaf-ish blocks with known chrome ---
    if t == "table":
        rows = node.find_all("tr")
        head = [r for r in rows if r.has_ancestor_tag("thead")]
        return 40 * len(head) + 46 * (len(rows) - len(head))

    if t == "pre":
        code = node.raw_text()
        return max(1, len(code.splitlines())) * f(26) + 36

    if t == "img":
        if "bg-img" in cls:
            return 0
        return 260  # object-fit image in a figure; capped by flex in practice

    if t in ("ul", "ol"):
        total = 0
        for li in node.direct("li"):
            own = re.sub(r"\s+", " ", li.text).strip()
            indent = 38 if t == "ol" else 26
            fs = f(19) if li.has_ancestor_class("defs") else f(23)
            if "d-term" in {c for k in li.direct() for c in k.classes}:
                fs = f(23)
            n = lines(own or li.all_text(), width - indent, fs)
            total += n * fs * 1.42 + f(18)
            for sub in li.direct("ul") + li.direct("ol"):
                total += est_height(sub, width - indent, scale) + f(12)
        return total

    # Typographic leaves
    text = node.all_text()
    if t == "h1":
        return lines(text, width, f(68)) * f(76)
    if t == "h2":
        return lines(text, width, f(38)) * f(43)
    if t == "h3":
        return lines(text, width, f(27)) * f(31)
    if "eyebrow" in cls or "s-num" in cls or "st-n" in cls:
        return lines(text, width, f(15)) * f(21) + f(12)
    if "lede" in cls:
        return lines(text, width, f(27)) * f(37)
    if "b-val" in cls:
        return 160
    if "m-val" in cls:
        return 58
    if "footnote" in cls:
        return lines(text, width, f(15)) * f(21) + 32
    if t == "blockquote":
        return lines(text, min(width, 30 * 40 * GLYPH), f(40)) * f(51) + 70
    if t == "svg" or "chart-wrap" in cls:
        return 300

    # Containers that just stack their children
    if node.children or t in ("div", "section", "figure", "p", "span", "aside"):
        total = sum(est_height(c, width, scale) for c in node.children)
        if node.text.strip() and not node.children:
            fs = f(19) if cls & {"small", "m-label"} else f(23)
            total += lines(node.text, width, fs) * fs * 1.45
        elif node.text.strip():
            fs = f(23)
            total += lines(node.text, width, fs) * fs * 1.45
        # known padded boxes
        if cls & {"card", "metric", "cmp"}:
            total += 52
        if "s-head" in cls:
            total += 38  # bottom margin
        if "tl-row" in cls:
            total += 36
        if t == "p" and not node.children and not node.text.strip():
            return 0
        return total

    if node.text.strip():
        fs = f(23)
        return lines(node.text, width, fs) * fs * 1.45
    return 0


def slide_height(sec):
    scale = 0.88 if "dense" in sec.classes else 1.0
    if "l-full" in sec.classes:
        return 0  # padding-free, overlay is bottom-anchored
    return sum(est_height(c, BODY_W, scale) for c in sec.children)


# --- Checks -----------------------------------------------------------------

class Report:
    def __init__(self, slug):
        self.slug = slug
        self.items = []

    def add(self, level, slide, msg):
        self.items.append((level, slide, msg))

    @property
    def errors(self):
        return [i for i in self.items if i[0] == "FAIL"]

    @property
    def warns(self):
        return [i for i in self.items if i[0] == "WARN"]


def known_classes():
    if not DECK_CSS.exists():
        return set()
    css = DECK_CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", css)) | REVEAL_CLASSES


def label(sec, idx):
    h = sec.find_all("h1") + sec.find_all("h2") + sec.find_all("h3")
    name = h[0].all_text()[:44] if h else (sec.all_text()[:44] or "(no heading)")
    return f"slide {idx} — {name}"


def check_deck(slug, deck_dir, strict):
    rep = Report(slug)
    sp = deck_dir / "slides.html"
    if not sp.exists():
        rep.add("FAIL", "-", "no slides.html")
        return rep

    raw = sp.read_text(encoding="utf-8")
    tree = Tree()
    tree.feed(raw)
    tree.close()
    for e in tree.errors:
        rep.add("FAIL", "-", f"malformed HTML: {e}")

    # Scaffold that build.py supplies must not be duplicated here.
    for bad in ("<html", "<head", "<body", 'class="reveal"', 'class="slides"'):
        if bad in raw:
            rep.add("FAIL", "-", f"slides.html must not contain {bad!r}")

    sections = tree.root.direct("section")
    if not sections:
        rep.add("FAIL", "-", "no top-level <section> elements")
        return rep

    stray = [c for c in tree.root.children if c.tag not in ("section", "#root")]
    for s in stray:
        if s.tag != "#root" and (s.text.strip() or s.children or s.tag != "p"):
            rep.add(
                "WARN", "-",
                f"line {s.line}: <{s.tag}> sits outside any <section> and will not render",
            )

    allowed = known_classes()
    all_layouts = {c for c in allowed if c.startswith("l-")}

    for i, sec in enumerate(sections, 1):
        who = label(sec, i)
        layouts = sec.classes & all_layouts
        if len(layouts) > 1:
            rep.add("FAIL", who, f"multiple layout classes: {sorted(layouts)}")

        # Unknown class names
        for n in [sec] + sec.find_all():
            for c in n.classes:
                if c.startswith("language-") or c.startswith("highlight-"):
                    continue
                if c not in allowed:
                    rep.add(
                        "FAIL", who,
                        f"class {c!r} on <{n.tag}> is not defined in deck.css",
                    )

        # Overflow
        h = slide_height(sec)
        if h > BODY_H * 1.02:
            rep.add(
                "FAIL", who,
                f"content overflows: ~{h:.0f}px of {BODY_H}px "
                f"({h / BODY_H:.0%}) — cut text, add class=\"dense\", or split",
            )
        elif h > BODY_H * 0.92:
            rep.add(
                "WARN", who,
                f"nearly full: ~{h:.0f}px of {BODY_H}px ({h / BODY_H:.0%})",
            )

        # Speaker notes
        is_chrome = bool(sec.classes & {"l-title", "l-section"})
        notes = sec.find_all(cls="notes")
        if not notes and not is_chrome:
            rep.add("WARN", who, "no <aside class=\"notes\"> speaker notes")
        elif notes and not notes[0].all_text() and not notes[0].text.strip():
            rep.add("WARN", who, "speaker notes are empty")

        # Caps
        top_lists = [
            l for l in sec.find_all("ul") + sec.find_all("ol")
            if not l.has_ancestor_class("defs") and l.parent and l.parent.tag != "li"
        ]
        for lst in top_lists:
            items = lst.direct("li")
            in_box = any(
                lst.has_ancestor_class(c) for c in ("cmp", "card", "col", "cols")
            )
            if len(items) > CAPS["bullets"] and not in_box:
                rep.add(
                    "WARN", who,
                    f"{len(items)} bullets in one list (cap {CAPS['bullets']})",
                )
            for li in items:
                w = len(re.sub(r"\s+", " ", li.text).strip().split())
                if w > CAPS["bullet_words"] + 4:
                    rep.add(
                        "WARN", who,
                        f"bullet is {w} words (cap {CAPS['bullet_words']}): "
                        f"“{li.text.strip()[:52]}…”",
                    )

        for tag, cap_key in (("h1", "h1_chars"), ("h2", "h2_chars")):
            for n in sec.find_all(tag):
                txt = n.all_text()
                if len(txt) > CAPS[cap_key]:
                    rep.add(
                        "WARN", who,
                        f"<{tag}> is {len(txt)} chars (cap {CAPS[cap_key]})",
                    )

        for cls, cap_key, what in (
            ("cards", "cards", "cards"),
            ("metrics", "metrics", "metrics"),
            ("steps", "steps", "steps"),
        ):
            for box in sec.find_all(cls=cls):
                n = len(box.direct())
                if n > CAPS[cap_key]:
                    rep.add("WARN", who, f"{n} {what} in one row (cap {CAPS[cap_key]})")

        for tl in sec.find_all(cls="timeline"):
            n = len(tl.direct(cls="tl-row"))
            if n > CAPS["timeline_rows"]:
                rep.add(
                    "WARN", who,
                    f"{n} timeline rows (cap {CAPS['timeline_rows']}) — split the slide",
                )

        for tbl in sec.find_all("table"):
            rows = tbl.find_all("tr")
            body = [r for r in rows if not r.has_ancestor_tag("thead")]
            ncols = max((len(r.direct("td")) + len(r.direct("th")) for r in rows), default=0)
            if len(body) > CAPS["table_rows"]:
                rep.add("WARN", who, f"table has {len(body)} body rows (cap {CAPS['table_rows']})")
            if ncols > CAPS["table_cols"]:
                rep.add("WARN", who, f"table has {ncols} columns (cap {CAPS['table_cols']})")

        for pre in sec.find_all("pre"):
            code = pre.raw_text()
            ls = code.splitlines()
            if code.startswith("\n"):
                rep.add(
                    "WARN", who,
                    "code block starts with a newline — renders a blank first line",
                )
            if len(ls) > CAPS["code_lines"]:
                rep.add("WARN", who, f"code block is {len(ls)} lines (cap {CAPS['code_lines']})")
            over = [n for n, l in enumerate(ls, 1) if len(l) > CAPS["code_cols"]]
            if over:
                rep.add(
                    "WARN", who,
                    f"code line(s) {over[:4]} exceed {CAPS['code_cols']} columns",
                )
            codes = pre.find_all("code")
            if codes and not any(
                c.startswith("language-") for cd in codes for c in cd.classes
            ):
                rep.add("WARN", who, "code block has no language-* class, so no highlighting")

        for bv in sec.find_all(cls="b-val"):
            if len(bv.all_text()) > CAPS["bigval_chars"] + 2:
                rep.add(
                    "WARN", who,
                    f"l-big value “{bv.all_text()}” is long; it renders at 170px",
                )

        # Images
        for img in sec.find_all("img"):
            src = img.attrs.get("src", "")
            if not src:
                rep.add("FAIL", who, "<img> has no src")
                continue
            if not re.match(r"^(https?:|data:|//)", src):
                p = (deck_dir / src.lstrip("./")).resolve()
                if not p.exists():
                    rep.add("FAIL", who, f"image not found: {src}")
            if "alt" not in img.attrs:
                rep.add("WARN", who, f"<img src={src!r}> has no alt attribute")
            elif not img.attrs["alt"].strip() and "bg-img" in img.classes:
                rep.add("WARN", who, "full-bleed background image has empty alt")

        for svg in sec.find_all("svg"):
            if "aria-label" not in svg.attrs and not svg.find_all("title"):
                rep.add("WARN", who, "<svg> chart has no aria-label or <title>")
            if "viewBox" not in svg.attrs and "viewbox" not in svg.attrs:
                rep.add("WARN", who, "<svg> has no viewBox, so it will not scale")

        # Unfilled placeholders
        body_text = sec.all_text()
        for marker in ("[TK]", "TKTK", "TODO", "XXX", "Lorem ipsum"):
            if marker.lower() in body_text.lower():
                rep.add("WARN", who, f"unfilled placeholder {marker!r} on the slide")

    # Deck-level arc
    if "l-title" not in sections[0].classes:
        rep.add("WARN", label(sections[0], 1), "first slide is not class=\"l-title\"")
    last = sections[-1]
    if not (last.classes & {"l-end", "l-big", "l-quote"}):
        rep.add(
            "WARN", label(last, len(sections)),
            "last slide is not a closing layout (l-end)",
        )
    if len(sections) > 25:
        rep.add("WARN", "-", f"{len(sections)} slides — consider an appendix")

    return rep


def main():
    ap = argparse.ArgumentParser(description="Lint decks before publishing.")
    ap.add_argument("slug", nargs="?", help="deck to check (default: all)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failure")
    args = ap.parse_args()

    if not DECKS.is_dir():
        print("no decks/ directory", file=sys.stderr)
        return 1

    dirs = sorted(p for p in DECKS.iterdir() if p.is_dir() and not p.name.startswith("."))
    if args.slug:
        dirs = [p for p in dirs if p.name == args.slug]
        if not dirs:
            print(f"error: no deck named {args.slug!r}", file=sys.stderr)
            return 2
    if not dirs:
        print("no decks to check")
        return 0

    total_f = total_w = 0
    for d in dirs:
        rep = check_deck(d.name, d, args.strict)
        nf, nw = len(rep.errors), len(rep.warns)
        total_f += nf
        total_w += nw
        status = "FAIL" if nf else ("warn" if nw else "ok")
        print(f"\n{d.name}: {status}  ({nf} error(s), {nw} warning(s))")
        cur = None
        for level, slide, msg in rep.items:
            if slide != cur:
                print(f"  {slide}")
                cur = slide
            mark = "✗" if level == "FAIL" else "!"
            print(f"    {mark} {msg}")

    print(f"\ntotal: {total_f} error(s), {total_w} warning(s)")
    if total_f:
        return 1
    if args.strict and total_w:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
