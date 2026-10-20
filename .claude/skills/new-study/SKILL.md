---
name: new-study
description: Lay out a new development study in repo-market-model the way every study is laid out: script, declaration if it has arms, result page, result.json, test, and research-log entry. Use when a directive asks to measure, compare, diagnose or re-run something and report a result.
---

# New study

A study is development evidence, never a verdict (scoring protocol v1). It produces these files, named for the issue
`<n>` it serves and a short slug (pattern of #1014: `scripts/b3_orientation_1014.py`):

| File | What it holds |
|---|---|
| `scripts/<slug>_<n>.py` | The measurement. Stdlib only unless it fits through `repo_model.ml`. Reads the published panel or the tracked fixtures; writes only to the paths it is given and to `docs/research/<slug>-<n>/`. |
| `metadata/<slug>_<n>.json` | Only when the study has arms or variants: the declaration, committed before any score. |
| `docs/research/<slug>-<n>/result.json` | The figures the page quotes, written by the script. |
| `docs/research/<slug>-<n>-result.md` | The page: what was measured, the table with intervals, the split by regime and day type, what it does and does not show. Every figure comes from `result.json`. |
| `tests/test_<slug>_<n>.py` | Written first. Pins the arithmetic on hand cases and any guard the study adds (with a recorded mutation). |
| `docs/research/log/<date>-model-<n>-H<k>-step<j>.md` | The research-log entry: Directive, Step, Tier (development), Pins, Tried (with the variant count), Result, Against kill, Next. Copy the shape of a recent entry. |

Rules that apply to every study:
- Name the hypothesis and step it serves (`docs/research/plan.md`).
- Calendar first: a new spread model reads the calendar columns at the target day on direct pairs. If the study reads a
  calendar-blind series, say so on the page and check whether its producer needs a register row (`register-producer`).
- No locked day (`metadata/lockbox.json`); nothing after the declared end; no edit to `docs/runs/`.
- A kill applies only to a result that is not provisional (Eleonora, 20 October 2026): a calendar-blind result never
  closes a question in either direction.
- Counts go in `result.json`, not in prose that `tests/test_docs_freshness.py` reads as a transcribed count.
- Expected to run longer than about two hours: use `long-run`.

Before the PR: run the study's test, `test_docs_freshness`, and `python3 scripts/pre_review.py --base origin/main`.
