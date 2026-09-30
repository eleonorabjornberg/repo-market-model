# Redesign plan — the pivot

This plan replaces the lanes, tracks and round closes. The evidence for §1 is in
[`lag-assessment.md`](lag-assessment.md). The next session starts at [`next-session.md`](next-session.md). The rulings
are in `docs/decisions/` (`information-set.md`, `workflow.md`, `publish-rule.md`).

## Decided (Eleonora, 30 September 2026)

- **The as-of information set:** adopted. It is implemented in a PR and the fleet is re-scored under it (§1).
- **Workflow:** retire the Mac lanes, tracks and queues now. From here on, cloud sessions and PRs. `main` is the only integration point.
- **Deliverables:** all four.
  1. A pressure-probability forecast.
  2. A plain-language results page.
  3. Model documentation and validation.
  4. A reserve-scarcity indicator.
- **Publish rule:** adopted as proposed. A record is publishable on `main` if `git diff <record commit> main` touches nothing
  under `src/`, `metadata/` or the snapshot fixtures.

- **Settlements** become scheduled inputs, under a `treasury_auctions` availability declaration dated from the
  auction results time.
- **Records scored under the old rule** move to `docs/runs/archive/pre-asof/` in the re-scoring PR.
- **Refit cadence:** monthly (every 21 scored days), declared in each record.
- **Streamlining** runs in its own session and PR, in parallel with the as-of PR.
- **Rewrite the standing rules** (`CLAUDE.md`, the `AGENT_CONTRACT.md` status note) and consolidate the logs into
  [`history.md`](history.md). Both landed with the pivot PR.

## 1. Methodology

- **Information set.** Each input is read at its latest value public at 16:00 on the day before the scored day. Scheduled
  inputs (calendar, FOMC schedule, auction settlements once declared) are read at the scored day. The purge is replaced by
  label observability, and every declaration shares one fold grid. Guards run both ways: leakage and staleness.
- **Benchmarks.** For the distribution, as-of persistence. For the pressure probability, calendar-type climatology and a
  persistence-logistic model. A headline claim is always stated against these, paired, with a bootstrap interval.
- **Targets.**
  - Keep the next-day distribution of SOFR − IORB.
  - **Headline target:** P(SOFR − IORB ≥ +5 bp) and P(≥ +10 bp) at horizons of 1–5 business days.
  - The ≥ +50 bp tail leaves the headline. It happened on 4 days in 8 years, so it becomes a scenario narrative, not a
    forecast claim.
- **Pressure model v1.** An interpretable, calibrated probability model: logistic or ordinal. Inputs: the latest spread
  level, scheduled pressure (month-end, quarter-end, tax date, settlement size) × scarcity state, and TGA change ×
  reserves. After it: recalibration, then gbm as the challenger. The scouting run shows why the order matters. The gbm
  ranks well (AUROC 0.91) but its probabilities are miscalibrated, and it missed the onset of the Oct 2025 pressure.
- **Scarcity indicator.**
  - A declared regime state built from reserves (relative to bank assets where the data allow), ON RRP and the NY Fed's
    Reserve Demand Elasticity (monthly).
  - Validation: pressure-day frequency must rise with it. The descriptive fact to explain is 1 day with SOFR above IORB in
    2021–23, against 69 in 2025.
- **Evaluation.**
  - Walk-forward, refit every 21 scored days (declared in the record), expanding window.
  - Metrics split by regime and by pressure-day type: Brier with its decomposition, CORP reliability, AUROC and lead
    time (early-warning conventions).
  - Pooled numbers are never enough on their own.
- **Calibration.** Re-diagnose on the as-of design before any calibration verdict is repeated. Compare CV+ with online
  conformal (DtACI or conformal PID, with a calendar scorecaster) and with group-conditional coverage over calendar type
  × regime.

## 2. Data

- **Materiality rule (proposed; yours to adopt).** A defect that touches a bounded, listed set of days is documented and
  handled, not a reason to refuse the series. The first application is daily ON RRP (`RRPONTSYD`, two two-operation
  days).
- **Settlements as scheduled inputs.** A `treasury_auctions` availability declaration dated from the auction results
  time. Approved. In scouting it is worth −3% MAE and the best pressure-day Brier.
- **Free sources to price next,** each through the as-of rule:
  - Daily TGA from the Daily Treasury Statement (FiscalData API). This replaces weekly `WTREGEN`.
  - NY Fed repo-operation results: SRF take-up, a censored pressure signal.
  - EFFR and SOFR 1st/99th percentiles.
  - The OFR Short-term Funding Monitor: DVP, GCF and tri-party dispersion, and money-fund holdings.
- **Unchanged:** the point-in-time data layer, fixtures, digests and carries.

## 3. Testing

- **Keep:** leakage and availability guards, the future-perturbation test, panel digest reproduction, record regeneration
  (`test_generated_results`), and CI on every PR with `REPO_MODEL_REQUIRE_ML=1`.
- **Add:** a staleness guard (written red first; mutating the read to p − 1 must fail). Records report per-field staleness.
- **Stop:**
  - Per-block mutation reproduction, except on availability and staleness guards.
  - Name-set arithmetic.
  - Ownership gates.
  - Suite-in-a-clone runs on the Mac.
  CI replaces all four.

## 4. Workflow

- One cloud session per PR, on its own checkout pinned to a SHA. A research run takes about 90 s per configuration here
  (measured), against about 85 min on the Mac.
- **Research mode:** scripts or a notebook on a branch. The PR description carries the config, SHA, panel digest and
  result table. There is no publish gate.
- **Publish mode:** a PR adding the records and the regenerated pages together, under the publish rule, with CI green.
  Branch protection goes on `main` once the first PR shows its check names.
- Judgement calls go to issues labelled `needs-eleonora`. `docs/decisions/` stays hers.
- Retired, with scripts kept on disk as a fallback:
  - the lanes, queues, heartbeats and `STOP`;
  - Tracks A and B, and round closes;
  - the `repo-model-runner` and `two-track-round` skills (one short replacement skill after the first PR works).
- Docs: `round-log.md` and `error-log.md` are frozen as history, and new lessons become tests or preflights. The advisor
  dashboard refresh continues, from PRs instead of rounds.

## 5. Inventory: what three weeks cost, and why

- **Round log, 7–19 Sep:** about 30 closes, a suite with roughly twice as many lines as the source it tests, and 44
  records. [`history.md`](history.md) has the consolidated account.
- **What survives as science:**
  - the point-in-time data layer and its availability declarations;
  - "funding data helps" (direction only);
  - the calibration machinery.
- **Everything measured is conditional on the week-old information set.**

**Error log, about 75 entries, classified:**

| Class | ≈ entries | Examples |
|---|---|---|
| Reach and environment | 22 | folder grants on scheduled firings, VM vs Mac, sleep on battery, DNS, `index.lock`, moved paths, deny lists |
| Probes and scripts | 20 | heredocs, quoting, Linux-isms on macOS, wrong field names, exit codes lost in pipes |
| Orchestration and serialisation | 15 | job order, filename reuse, publish windows, a record published onto a moving panel, the orphaned half-publish |
| State drift | 9 | the handoff wrong about lane and branch state at least 5 times, stale scheduled prompts, numbers cited from memory |
| Wrong brief premises | 8 | a brief contradicting a declared rule, greps of the wrong file, unchecked attributions |
| Methodology and inference | 6 | an aggregate hiding a regime, two mechanisms not separated, a "same panel" claim, a `SAME GRID` guard |

Roughly 85% of the entries are operational, and not one is about the information set. The machinery was built to catch
its own failures. The design question was never asked.

**Bottlenecks, and what removes each:**

| Bottleneck | Removed by |
|---|---|
| About 85 min per scoring run (daily refit × 5 levels × 6 fits) | declared monthly refit plus cloud parallelism |
| The Mac as compute through a VM bridge | cloud sessions on clones |
| The publish window tied to the mount's `HEAD` | the publish rule, and a PR per result |
| A single scoring lane and lockstep round closes | independent PRs |
| Two-track ownership walls, `HUMAN_ONLY` files and deny lists | CI plus review; `docs/decisions/` stays hers |
| The per-block verification ritual (about 20–25 min under contention) | CI on the PR |
| Six state documents drifting against the tree | `STATUS` (decisions pending) and PR descriptions |
| Refusal-first data rules | the materiality rule |
| A fold grid that moves with the declaration | one grid (§1) |
| One-sided guards | leakage plus staleness |
| Metric sprawl | headline metrics against fixed benchmarks; everything else diagnostic |

## 6. What we can borrow (verified links in [`literature.md`](literature.md))

1. **The ragged-edge information set from nowcasting** (Giannone, Reichlin & Small 2008; Bańbura et al. 2013). This is
   the fix itself.
2. **Reserve-demand regime state:**
   - Afonso, Giannone, La Spada & Williams (SR 1019): satiation at about 12–13% of bank assets.
   - The NY Fed's Reserve Demand Elasticity (monthly, since 2024).
   - Anbil et al. (FEDS Note, Aug 2026): issuance sensitivity jumps when Fed liquidity is below 10% of GDP.
   - IMF WP/25/127: about +2 bp per +$100bn TGA.
3. **The pressure probability as an early-warning problem:**
   - calendar-type climatology and persistence baselines (as in the `seiche` repo, whose README reports its ML does not
     beat climatology; AGPL, so ideas only);
   - reliability via CORP and the Brier decomposition (`scores` library);
   - AUROC, Sarlin usefulness and lead time per horizon.
4. **Coverage under regime shift:**
   - DtACI and conformal PID (MIT code), with a calendar scorecaster;
   - group-conditional conformal (`conditionalconformal`);
   - MAPIE for baselines.
5. **Growth-at-Risk template** (Adrian, Boyarchenko & Giannone 2019): a quantile grid smoothed into a distribution, so P(≥ x)
   comes from the same model. Caveat: Plagborg-Møller et al. find the tail adds little over the mean, which is why the
   baselines above are mandatory.
6. **SRF take-up as a censored pressure signal.** The scan reads the 29 Jul 2026 implementation note as SRP rate =
   IORB + 10 bp, so the +10 bp threshold sits at the facility rate. Verify against the note before using it.

## 7. Repo streamlining (a separate PR, in parallel with §8 step 1)

- **README lead:**
  - one plain-English paragraph;
  - the **Open in Colab** badge;
  - the overview figure;
  - a three-line honest status ("results are being re-scored under the as-of rule; old records archived");
  - then the generated blocks, unchanged in form.
- **`notebooks/00_overview.ipynb`**, under a minute on Colab, with no install step beyond cloning:
  1. What repo pressure is, in plain words.
  2. The data: what, why and how (a table plus the figure).
  3. Build the panel from the tracked fixtures and verify the digest.
  4. The data by year: pressure days, reserves regime.
  5. What we know at 16:00: the information-set diagram.
  6. The lag finding in one cell (published-rule persistence against as-of persistence).
  7. Pressure-probability baselines (climatology and persistence-logistic) scored in seconds.
  8. Progress and roadmap.
- **`docs/figures/overview.svg`** (light and dark pairs, as the repo already does). Data groups, each with *why* in one line:
  - the price of overnight cash;
  - how much spare cash is in the system;
  - days when a lot of cash is needed at once;
  - where cash can park instead.
  These flow into "what we know at 4 pm the day before", then into "the chance tomorrow's rate is ≥ 5 bp above the Fed's
  rate paid on reserves".
- **Housekeeping:**
  - Move the 44 records to `docs/runs/archive/pre-asof/` with a README (pending your ruling).
  - Consolidate `EXECUTIVE_SUMMARY`, `PROJECT_STATUS` and `RESEARCH_NOTES` into generated status plus `METHODOLOGY`.
  - Move `AGENT_CONTRACT.md` under `docs/process/`, leaving `CLAUDE.md` and `AGENTS.md` as thin pointers.
  - Remove `.obvious/` (Obvious left the project on 30 Sep).
  - Correct every next-day statement.
  - `tests/test_docs_freshness.py` is updated with the moves.

## 8. Sequence

1. **As-of PR** (fresh cloud session, brief below).
2. **Re-score and publish PR.** Persistence, gbm with none and CV+, the funding declaration, and the pressure baselines.
3. **Streamlining PR** (§7). It can start now, with the numbers filled in after step 2.
4. **Pressure model v1** plus the scarcity indicator.
5. **Calibration re-diagnosis** (CV+ against online conformal).
6. **Data additions** (§2), each priced as-of.
7. **Model documentation and validation report,** in a model-risk structure: purpose and use, data, methodology,
   assumptions and limitations, performance by regime, outcomes analysis, monitoring. The lag finding goes in as a
   validation result.
8. **Plain-language results page** on the site, generated from records.

## Decision records

- `docs/decisions/information-set.md`, `workflow.md` and `publish-rule.md` landed with the pivot PR.
- `docs/decisions/materiality.md` is **proposed, not drafted**. §2 states the rule. It is not in force until Eleonora adopts it.

## Brief — step 1, the as-of PR (a fresh session in the `rmm` environment)

> Repo `eleonorabjornberg/repo-market-model`, branch `asof/information-set` from `origin/main`. Read `docs/pivot/lag-assessment.md`
> first. Implement: (1) per-field as-of reads using
> `baseline._declared_availability` at the decision instant (16:00 on the panel day before T), replacing
> `_feature_index` at every call site (baseline 3243/5315/6410, event_eval 594, ml 2933/3032, tail_diagnostics 347);
> (2) a declared scheduled-input class read at T: the calendar, and Treasury settlements under a new `treasury_auctions`
> availability declaration dated from the auction results time (approved 30 Sep). Verify that instant from Treasury's
> published auction procedure, pick a conservative time, and record the evidence in the declaration's note; (3) training labels admissible only if observable at the fold's decision instant; one fold grid regardless of
> declaration; (4) a staleness guard, red first, whose p−1 mutation must fail, with `_check_decision_relative_availability`
> still passing on every fold; (5) `--refit-every N`, recorded in the declaration. Write tests before code. Do not
> touch `docs/runs/` or the README in this PR. Acceptance: CI green with `REPO_MODEL_REQUIRE_ML=1`. Persistence under
> the new rule gives MAE 2.509 ± 0.01 on the 2,039-day grid. gbm (4 features, none, refit 21) is within 2% of the
> scouting 2.342. Report any mismatch rather than tuning to it.

## Brief — the streamlining PR (a second fresh session, in parallel)

> Repo `eleonorabjornberg/repo-market-model`, branch `docs/streamline` from `origin/main`. Do not change `src/`,
> `docs/runs/` or any test logic, except the path updates `tests/test_docs_freshness.py` needs.
>
> 1. **`notebooks/00_overview.ipynb`.** It must run on Colab in under 60 s: clone, then
>    the build command from `REPRODUCIBILITY.md`, then verify digest `d8b716cf`. Sections:
>    - what repo pressure is, in plain English;
>    - the data (what, why, how), crediting data selection to Nicholas Beroud as the README's People section does;
>    - the data by year: pressure days and the reserves regime;
>    - what is known at 16:00 the day before;
>    - one cell reproducing the lag finding (published-rule persistence 3.104 against as-of 2.509 on the 2,039-day grid
>      from 2018-07-05);
>    - pressure baselines scored in seconds (climatology and persistence-logistic; Brier and AUROC);
>    - progress and roadmap.
>    Label every model figure "pre-as-of; re-score pending". The notebook may use Colab's preinstalled
>    pandas, matplotlib and scikit-learn. Colab's interpreter is newer than the `pyproject.toml` ceiling, and the build still reproduces
>    digest `d8b716cf` there (checked 30 September 2026). Execute it headless (`jupyter nbconvert --to notebook
>    --execute`) before committing.
> 2. **`docs/figures/overview-light.svg` and `overview-dark.svg`**, shown in the README through `<picture>`. Four data
>    groups, each with a one-line *why*:
>    - the price of overnight cash (SOFR, TGCR, BGCR);
>    - spare cash in the system (reserves, TGA, ON RRP);
>    - days when a lot of cash is needed at once (month-, quarter- and tax dates, Treasury settlements);
>    - where cash can park instead (bills).
>    They flow into "what we know at 4 pm the day before", then into "the chance tomorrow's rate is ≥ 5 bp above what
>    the Fed pays on reserves".
> 3. **README lead:**
>    - a plain paragraph;
>    - the badge
>      `[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eleonorabjornberg/repo-market-model/blob/main/notebooks/00_overview.ipynb)`;
>    - the figure;
>    - a three-line honest status.
>    Leave the generated blocks to `scripts/emit_results.py`.
> 4. **Housekeeping:**
>    - Fold `docs/EXECUTIVE_SUMMARY.md`, `docs/PROJECT_STATUS.md` and `docs/RESEARCH_NOTES.md` into the generated status
>      and `METHODOLOGY.md`.
>    - Move `AGENT_CONTRACT.md` to `docs/process/`, leaving `CLAUDE.md` and `AGENTS.md` as thin pointers.
>    - Change every "next business day" statement to say the as-of information rule is being implemented.
>    - Leave `.obvious/` alone (her ruling is pending).
>
> Acceptance: CI green, and the notebook executes cleanly on a fresh clone. The PR description lists every file moved or
> merged.
