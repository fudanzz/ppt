# Layout catalog

Every layout defined in `framework/deck.css`. Copy the markup, replace the
content. Classes not listed here do not exist — check before inventing one.

Structural contract: each slide is one top-level `<section>`. A slide class
`l-*` selects the layout. Inside, most content layouts use the
`.s-head` / `.s-body` pair, which pins the heading to the top and vertically
centers the body in the remaining space.

```html
<section class="l-two">
  <div class="s-head">...</div>   <!-- heading block, fixed height -->
  <div class="s-body">...</div>   <!-- grows, centers its content -->
  <p class="footnote">...</p>     <!-- optional, pins to bottom -->
  <aside class="notes">...</aside>
</section>
```

---

## 1. Title slide — `l-title`

Opens the deck. Gets an automatic accent wash in the top-right corner.

```html
<section class="l-title">
  <p class="eyebrow">Q4 Business Review</p>
  <h1>Platform Strategy 2027</h1>
  <p class="lede">Where we invest over the next four quarters.</p>
  <div class="meta">
    <span>Priya Raman</span>
    <span class="dot"></span>
    <span>3 November 2026</span>
    <span class="dot"></span>
    <span>Internal</span>
  </div>
  <aside class="notes">Opening framing goes here.</aside>
</section>
```

Keep `h1` under ~45 characters so it stays on two lines. The `.lede` is capped
at 24ch on this layout by design — one sentence.

## 2. Section divider — `l-section`

Marks a new part of the deck. Sunken background so it reads as a breath.
Use one per major outline heading; skip them in decks under ~8 slides.

```html
<section class="l-section">
  <p class="s-num">Part 02</p>
  <h2>What changed this year</h2>
  <p class="lede">Three shifts that reset our assumptions.</p>
  <aside class="notes">Transition: close out part 1, set up part 2.</aside>
</section>
```

## 3. Bullets — no layout class needed

The default slide is a flex column, so a plain head/body works.

```html
<section>
  <div class="s-head">
    <p class="eyebrow">Context</p>
    <h2>Three forces reshaped demand</h2>
  </div>
  <div class="s-body">
    <ul>
      <li class="fragment">Enterprise buyers consolidated onto fewer vendors</li>
      <li class="fragment">Procurement cycles stretched from 60 to 110 days</li>
      <li class="fragment">Security review became the gating step, not pricing</li>
    </ul>
  </div>
  <aside class="notes">Talk track for each bullet.</aside>
</section>
```

`class="fragment"` reveals that item on the next keypress. Use it when you want
to pace a reveal; omit it when the audience should see the whole list at once.
Don't fragment more than ~5 items on one slide.

### Term + description list

When each bullet needs a definition rather than a phrase:

```html
<ul class="defs">
  <li>
    <span class="d-term">Activation</span>
    <span class="d-desc">First workspace created within 7 days of signup.</span>
  </li>
  <li>
    <span class="d-term">Expansion</span>
    <span class="d-desc">Net new seats on an existing contract, excluding renewals.</span>
  </li>
</ul>
```

### Numbered list

Use `<ol>` instead of `<ul>` — it renders accent-tinted numbered discs
automatically. Reserve it for genuine sequences.

## 4. Two columns — `l-two`

```html
<section class="l-two">
  <div class="s-head">
    <h2>Build versus buy</h2>
  </div>
  <div class="s-body">
    <div class="cols">
      <div class="col">
        <h3>What we build</h3>
        <ul>
          <li>Ingest and transform pipeline</li>
          <li>Policy engine</li>
        </ul>
      </div>
      <div class="col">
        <h3>What we buy</h3>
        <ul>
          <li>Identity and SSO</li>
          <li>Billing and invoicing</li>
        </ul>
      </div>
    </div>
  </div>
  <aside class="notes">...</aside>
</section>
```

Width variants on `.cols`: `narrow-left` (2fr/3fr) and `narrow-right` (3fr/2fr).
Pair a short label column with a wider prose column using these.

## 5. Cards — `cards` + `cols-N`

Two to four parallel items with a short body each. `cols-N` sets the column
count (`cols-2` … `cols-5`).

```html
<section>
  <div class="s-head">
    <h2>Four investment areas</h2>
  </div>
  <div class="s-body">
    <div class="cards cols-4">
      <div class="card">
        <div class="c-icon">&#9881;</div>
        <h3>Reliability</h3>
        <p>Cut p99 latency and eliminate the top three incident classes.</p>
      </div>
      <div class="card accent">
        <div class="c-icon">&#9889;</div>
        <h3>Onboarding</h3>
        <p>Self-serve setup in under ten minutes, no solutions engineer.</p>
      </div>
      <div class="card">
        <div class="c-icon">&#128274;</div>
        <h3>Compliance</h3>
        <p>SOC 2 Type II and the EU data residency requirement.</p>
      </div>
      <div class="card">
        <div class="c-icon">&#128202;</div>
        <h3>Insight</h3>
        <p>Usage analytics customers can act on without our help.</p>
      </div>
    </div>
  </div>
</section>
```

`card accent` highlights the one card that matters most — use it at most once
per slide. `.c-icon` holds a single emoji or HTML entity; keep it to one glyph.
At `cols-4`, hold card body text to ~12 words.

## 6. Metrics / KPI row — `metrics` + `cols-N`

```html
<section>
  <div class="s-head">
    <p class="eyebrow">Fiscal 2026</p>
    <h2>Where we landed</h2>
  </div>
  <div class="s-body">
    <div class="metrics cols-3">
      <div class="metric up">
        <div class="m-val">34<span class="m-unit">%</span></div>
        <div class="m-label">Revenue growth</div>
        <div class="m-sub">vs. 21% last year</div>
      </div>
      <div class="metric">
        <div class="m-val">1.9<span class="m-unit">M</span></div>
        <div class="m-label">Monthly active seats</div>
        <div class="m-sub">Up from 1.4M</div>
      </div>
      <div class="metric">
        <div class="m-val">112<span class="m-unit">%</span></div>
        <div class="m-label">Net revenue retention</div>
        <div class="m-sub">Target was 108%</div>
      </div>
    </div>
  </div>
  <aside class="notes">...</aside>
</section>
```

`metric up` tints the value with the accent — mark the headline number only.
Put the unit in `.m-unit` so it renders smaller than the digits.

## 7. Big number — `l-big`

One number that deserves the whole slide.

```html
<section class="l-big">
  <p class="eyebrow">Cost of the status quo</p>
  <div class="b-val">$4.2M</div>
  <p class="b-label">Annual spend on tooling three teams each bought separately.</p>
  <aside class="notes">...</aside>
</section>
```

Keep `.b-val` to roughly 6 characters — it renders at 170px.

## 8. Quote — `l-quote`

```html
<section class="l-quote">
  <blockquote>
    Procurement stopped asking what it costs and started asking who else runs it.
  </blockquote>
  <p class="attrib">
    <span class="a-name">Dana Whitfield</span>
    VP Infrastructure, Northwind Logistics
  </p>
  <aside class="notes">...</aside>
</section>
```

The opening curly quote is drawn by CSS — do not type one. Quotes must come
from the outline; never attribute words to a real person who did not say them.

## 9. Steps (horizontal) — `steps`

A process of 3–5 stages read left to right.

```html
<section>
  <div class="s-head"><h2>How a deal moves</h2></div>
  <div class="s-body">
    <div class="steps">
      <div class="step done">
        <div class="st-n">STEP 1</div>
        <h3>Discovery</h3>
        <p>Map the buying committee and the gating constraint.</p>
      </div>
      <div class="step done">
        <div class="st-n">STEP 2</div>
        <h3>Technical review</h3>
        <p>Security questionnaire and architecture walkthrough.</p>
      </div>
      <div class="step">
        <div class="st-n">STEP 3</div>
        <h3>Commercial</h3>
        <p>Pricing, terms, and the renewal clause.</p>
      </div>
    </div>
  </div>
</section>
```

`step done` gives the stage an accent rule — use it to show progress.

## 10. Timeline (vertical) — `timeline`

Dated milestones. Better than `steps` when the labels are dates or there are
more than five rows.

```html
<section>
  <div class="s-head"><h2>Rollout plan</h2></div>
  <div class="s-body">
    <div class="timeline">
      <div class="tl-row">
        <div class="tl-when">Q1 2027</div>
        <div class="tl-what">
          <h3>Internal dogfood</h3>
          <p>Two teams, feature-flagged, no external traffic.</p>
        </div>
      </div>
      <div class="tl-row">
        <div class="tl-when">Q2 2027</div>
        <div class="tl-what">
          <h3>Design partners</h3>
          <p>Six accounts under NDA with weekly feedback calls.</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

Cap at 5 rows. Beyond that, split across two slides.

## 11. Compare — `compare`

Two sides weighed against each other.

```html
<section>
  <div class="s-head"><h2>Migrate now or wait a quarter</h2></div>
  <div class="s-body">
    <div class="compare">
      <div class="cmp pro">
        <h3>&#10003; Migrate now</h3>
        <ul>
          <li>Unblocks the EU launch in Q2</li>
          <li>One freeze window instead of two</li>
        </ul>
      </div>
      <div class="cmp">
        <h3>&#10007; Wait</h3>
        <ul>
          <li>Needs a second freeze in Q3</li>
          <li>EU launch slips a full quarter</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

`cmp pro` marks the recommended side. Keep the two lists the same length.

## 12. Table

Plain `<table>` is already styled. Add `class="num"` to numeric cells for
right alignment and tabular figures, and `class="total"` to a summary row.

```html
<section class="dense">
  <div class="s-head"><h2>Spend by team</h2></div>
  <div class="s-body">
    <table>
      <thead>
        <tr><th>Team</th><th class="num">FY26</th><th class="num">FY27 ask</th></tr>
      </thead>
      <tbody>
        <tr><td>Platform</td><td class="num">$1.2M</td><td class="num">$1.6M</td></tr>
        <tr><td>Data</td><td class="num">$0.8M</td><td class="num">$0.9M</td></tr>
        <tr class="total"><td>Total</td><td class="num">$2.0M</td><td class="num">$2.5M</td></tr>
      </tbody>
    </table>
  </div>
  <p class="footnote">Excludes headcount. Source: finance plan v4.</p>
</section>
```

Hold tables to 6 rows and 5 columns. Add `dense` to the section for anything
near those limits.

## 13. Code

```html
<section class="dense">
  <div class="s-head"><h3>Policy as configuration</h3></div>
  <div class="s-body">
    <pre><code class="language-yaml" data-line-numbers="2-3">policy:
  residency: eu-west-1
  retention_days: 30
  export: deny</code></pre>
  </div>
</section>
```

- Set `class="language-*"` so highlighting applies.
- `data-line-numbers="2-3"` emphasizes those lines; `data-line-numbers` alone
  just numbers them.
- Code must start immediately after `<code...>` with no leading newline, or the
  block renders with a blank first line.
- Max ~14 lines and ~62 columns. Trim to the lines that make the point.

## 14. Image beside text — `figure`

```html
<section class="l-two">
  <div class="s-head"><h2>The new setup flow</h2></div>
  <div class="s-body">
    <div class="cols narrow-right">
      <figure class="figure">
        <img src="./assets/setup.png" alt="Setup wizard, step 2 of 3" />
        <figcaption>Step 2 now defaults to the detected region.</figcaption>
      </figure>
      <div class="col">
        <ul>
          <li>Three screens instead of seven</li>
          <li>Region detected, not asked</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

Put images in `decks/<slug>/assets/` and reference them as `./assets/<file>`.
Always write real `alt` text.

## 15. Full-bleed image — `l-full`

```html
<section class="l-full">
  <img class="bg-img" src="./assets/warehouse.jpg" alt="Automated sorting floor" />
  <div class="overlay">
    <h2>Where the constraint actually lives</h2>
    <p>Sortation throughput, not truck capacity.</p>
  </div>
</section>
```

The overlay gradient assumes a reasonably dark lower third. On a light image,
darken the image itself rather than fighting the gradient.

## 16. Chart — `chart-wrap`

**Invoke the `dataviz` skill before writing chart markup.** Render inline SVG;
do not pull in a charting library or embed a raster image.

```html
<section>
  <div class="s-head">
    <h2>Growth concentrated in enterprise</h2>
    <p>New ARR by segment, FY24&ndash;FY26</p>
  </div>
  <div class="s-body">
    <div class="chart-wrap">
      <svg viewBox="0 0 900 380" role="img" aria-label="New ARR by segment, FY24 to FY26">
        <!-- bars, axes, labels -->
      </svg>
      <div class="legend">
        <span class="lg"><span class="sw" style="background: var(--accent)"></span>Enterprise</span>
        <span class="lg"><span class="sw" style="background: var(--ink-3)"></span>Mid-market</span>
      </div>
    </div>
  </div>
  <p class="footnote">Source: ARR snapshot, 30 September 2026.</p>
</section>
```

Give the `<svg>` a `viewBox` and no fixed width/height so it scales. Make the
headline state the finding, not the chart type.

## 17. Closing — `l-end`

```html
<section class="l-end">
  <h2>What we need from you today</h2>
  <div class="contact">
    <span>Approve the $2.5M platform envelope</span>
    <span>Name an executive sponsor for EU residency</span>
    <span class="muted small">priya@example.com</span>
  </div>
  <aside class="notes">Make the ask explicit, then stop talking.</aside>
</section>
```

End on the ask or the takeaway — never on a bare "Thank you" or "Questions?".

---

## Inline helpers

Usable inside any layout.

| Class | Effect |
| --- | --- |
| `eyebrow` | Small uppercase accent kicker above a heading |
| `lede` | Large muted intro sentence |
| `rule` | 56px accent bar, as a divider under a heading |
| `footnote` | Bottom-pinned source line with a top border |
| `muted` / `small` / `micro` | Dimmer text / 19px / 15px |
| `pill` | Accent chip, e.g. a status tag |
| `pill plain` | Neutral chip |
| `dense` (on `<section>`) | Shrinks the slide's type scale ~12% |
| `stack` / `row` | Flex column / row |
| `gap1`…`gap6` | Flex gap, 6px → 56px |
| `grow` | Flex-grow with `min-height: 0` |
| `center` | Center text and cross-axis items |
| `tight` | Tighter line height |
| `cols-1`…`cols-5` | Column count for `cards` and `metrics` |

## Vertical stacks

Nesting `<section>` inside `<section>` makes a vertical sub-deck, reached with
the down arrow. `build.py` counts the stack as one slide. Use it only for
optional appendix detail — most decks should stay linear.

## Speaker notes

`<aside class="notes">` on any slide. Press `S` during presentation for the
speaker window. Notes accept HTML, so short lists are fine.
