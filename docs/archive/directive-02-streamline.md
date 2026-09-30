# Directive: streamline the repository's front door

Runs in parallel with directive 01. Work it as one pull request.

Repo `eleonorabjornberg/repo-market-model`, branch `docs/streamline` from `origin/main`. Do not change `src/`,
`docs/runs/` or any test logic, except the path updates `tests/test_docs_freshness.py` needs.

1. **`notebooks/00_overview.ipynb`.** It must run on Colab in under 60 s: clone, then
   the build command from `REPRODUCIBILITY.md`, then verify digest `d8b716cf`. Sections:
   - what repo pressure is, in plain English;
   - the data (what, why, how), crediting data selection to Nicholas Beroud as the README's People section does;
   - the data by year: pressure days and the reserves regime;
   - what is known at 16:00 the day before;
   - one cell reproducing the lag finding (published-rule persistence 3.104 against as-of 2.509 on the 2,039-day grid
     from 2018-07-05);
   - pressure baselines scored in seconds (climatology and persistence-logistic; Brier and precision-recall);
   - progress and roadmap.
   Label every model figure "pre-as-of; re-score pending". The notebook may use Colab's preinstalled
   pandas, matplotlib and scikit-learn. Colab's interpreter is newer than the `pyproject.toml` ceiling, and the build still reproduces
   digest `d8b716cf` there (checked 30 September 2026). Execute it headless (`jupyter nbconvert --to notebook
   --execute`) before committing.
2. **`docs/figures/overview-light.svg` and `overview-dark.svg`**, shown in the README through `<picture>`. Four data
   groups, each with a one-line *why*:
   - the price of overnight cash (SOFR, TGCR, BGCR);
   - spare cash in the system (reserves, TGA, ON RRP);
   - days when a lot of cash is needed at once (month-, quarter- and tax dates, Treasury settlements);
   - where cash can park instead (bills).
   They flow into "what we know at 4 pm the day before", then into "the chance tomorrow's rate is ≥ 5 bp above what
   the Fed pays on reserves".
3. **README lead:**
   - a plain paragraph;
   - the badge
     `[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eleonorabjornberg/repo-market-model/blob/main/notebooks/00_overview.ipynb)`;
   - the figure;
   - a three-line honest status.
   Leave the generated blocks to `scripts/emit_results.py`.
4. **Housekeeping:**
   - Fold `docs/EXECUTIVE_SUMMARY.md`, `docs/PROJECT_STATUS.md` and `docs/RESEARCH_NOTES.md` into the generated status
     and `METHODOLOGY.md`.
   - Change every "next business day" statement to say the as-of information rule is being implemented.

Acceptance: CI green, and the notebook executes cleanly on a fresh clone. The PR description lists every file moved or
merged.
