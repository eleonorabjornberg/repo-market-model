# Directive: the visual layer, descriptive half

Can run now, alongside 01. It touches nothing under `src/`, `metadata/` or `tests/fixtures/snapshots/`, so under
`docs/decisions/publish-rule.md` it changes the publishability of no record. Work it as one pull request.

## Why

Deliverables 2 (the plain-language results page) and 3 (documentation and validation) need figures a reader can
learn from. Plan §7 puts the results page last, step 10. This directive brings forward the half that does not depend on
the re-score: the data, the market mechanics, the information rule and the process. The model chapters wait for
directive 03 and plan step 6.

## Decided (Eleonora, 30 September 2026)

- **Home:** GitHub Pages from this repository. The portfolio site links to it; nothing is carried by hand into the
  site repository.
- **Voice:** one page for every reader, in layers. Each chapter has a one-sentence finding, the chart, a plain
  explanation, and a "Go deeper" fold with definitions, provenance and the notebook cell that reproduces it.
- **Starting point:** the prototype in `06-prototype/` (now `scripts/emit_visual.py` and [`site/template.html`](../../../site/template.html)), chapters 2 and 3, generated from the verified
  panel (digest `4ddc3882…`, money series in USD billions since #41). Its look is under Eleonora's review; treat its
  code as the baseline, not its copy as final.

## The chapters

| # | Chapter | In this PR |
|---|---|---|
| 1 | The plumbing | Yes. Lenders, the repo segments behind SOFR, borrowers, and the Fed's administered rates |
| 2 | Eight years in one line | Yes, as prototyped |
| 3 | Why it happens | Yes, as prototyped: reserves against the spread, and pressure days by day type and year |
| 4 | What's known at 4 pm | The publication clock of each input only. No lag-impact figures |
| 5 | Making a forecast | No: listed as planned. Needs as-of records (03) and pressure model v1 (step 6) |
| 6 | Grading it honestly | No: listed as planned. Needs as-of records (03) |
| 7 | The scarcity gauge | No: listed as planned. Needs step 6 |
| 8 | How it was built | Yes. Directives, sessions, pull requests, the guards, the publish rule, and the lag finding as a validation result, without its numbers |

## Do

1. **Move the prototype into place.** `06-prototype/emit_visual.py` becomes `scripts/emit_visual.py`;
   `06-prototype/template.html` becomes `site/template.html`. Delete `06-prototype/` in the same PR.
2. **Generator.** Standard library only. It rebuilds the panel from the fixtures with the repository's own `build`
   command and refuses on a digest mismatch. It reads `metadata/` read-only and writes `docs/visual/data/*.json`, each
   with a provenance block (commit, panel SHA-256, inputs). It renders `site/index.html`, and it refuses if a
   placeholder is left unfilled. No number on the page is typed.
3. **Annotations.** Put every event label and every claim about market structure in `docs/visual/annotations.json`,
   each with a primary-source URL (Federal Reserve, New York Fed, Treasury, or a record in this repository). Never put
   them in `metadata/`.
4. **Chapter 1.** Before drawing the Standing Repo Facility rate relative to IORB, verify it against the current FOMC
   implementation note; plan §5.6 flags the reading as unverified. Show only rates that note states.
5. **Chapter 4.** Draw each panel input's publication clock from its declaration in `metadata/sources.json`, relative
   to a 16:00 decision. The interactive date picker waits for directive 01 and must use 01's as-of reader rather than
   a second implementation.
6. **Fail closed for model chapters.** The generator refuses to render a run record unless the record declares the
   as-of information rule, under whatever field directive 01 introduces. Test the refusal with a pre-as-of record.
7. **Page.** One self-contained HTML file.
   - D3 7.9.0 pinned from cdnjs.
   - Public Sans and Source Serif 4 from Google Fonts, with fallback stacks.
   - Colour tokens for light and dark.
   - Nothing computed in the browser beyond filtering, hovering and selecting.
   - Keyboard focus visible, reduced motion respected, an `aria-label` on every chart, colour never the only cue.
8. **Tests: `tests/test_visual.py`.**
   - Regeneration reproduces the committed page and data byte for byte.
   - There are no unfilled placeholders.
   - Every annotation has a source URL.
   - The reserve-unit guard fires on a rescaled panel.
   - The fail-closed gate refuses a pre-as-of record.
9. **Deploy.** Add `.github/workflows/pages.yml` to deploy `site/` on pushes to `main`.
10. **Wire into publishing.** A publish PR runs `scripts/emit_visual.py` alongside `scripts/emit_results.py`, so records
    and the page land in one commit. Say so in `CLAUDE.md`.
11. **Front door.** Add one link to the page under the README's overview figure, leaving the generated blocks
    untouched. Update plan §7 and `next-session.md` to show that step 10's descriptive half is this directive.

## Acceptance

- CI is green, `test_visual` included.
- `git diff --name-only main -- src/ metadata/ tests/fixtures/snapshots/` prints nothing.
- The page and its data regenerate byte for byte from the PR head.
- No figure from a run record appears anywhere on the page.
- The pull request shows a screenshot of each chapter in light, dark and at 390 px.
- **Before the site links to the page,** Eleonora's finance advisor reviews the market-structure claims in chapters
  1–3. This does not gate the merge.

## Constraints

- The descriptive charts make no causal claim, and say so where a reader might infer one.
- No hand-written dates on the page. The data range comes from the panel and "when" is the commit.
- The stress windows are a scoring holdout: kept out of the headline score and reported on their own
  (`docs/process/AGENT_CONTRACT.md`, Evaluation). Copy must not say that no model is trained on them.

## Found while drafting (raise as `finding` issues; do not settle them in this PR)

Both items found while drafting are now settled. They are kept here so the history reads; neither is work for this
PR.

1. **Reserve and TGA units. Settled by #41 (PR #69).** The panel carries `reserve_balances` and `tga` in USD
   billions, at digest `4ddc3882…`. The prototype divides by `1e3` to chart trillions, and its millions guard is gone.
   Do not add another unit conversion: the values are already billions.
2. **`quarter_end` on weekend quarter-ends. Settled by #44 (PR #54).** `quarter_end` now marks the last business day
   of the quarter from a tracked market holiday table (`docs/decisions/calendar-columns.md`).
