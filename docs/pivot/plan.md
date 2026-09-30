# Redesign plan — the pivot

The project's current plan. The evidence for §1 is in
[`lag-assessment.md`](lag-assessment.md). The next session starts at [`next-session.md`](next-session.md). The rulings
are in `docs/decisions/` (`information-set.md`, `workflow.md`, `publish-rule.md`).

## Decided (Eleonora, 30 September 2026)

- **Information set:** each input is read as-of its decision instant, per field (`docs/decisions/information-set.md`).
  Treasury settlements are scheduled inputs, dated from the auction results time. Records are refitted monthly, with
  the cadence declared in each record. Records scored under the earlier rule move to `docs/runs/archive/pre-asof/`.
- **Workflow:** directives, then sessions, then pull requests (`docs/decisions/workflow.md`).
- **Publishing:** `docs/decisions/publish-rule.md`.
- **Deliverables:** all four.
  1. A pressure-probability forecast.
  2. A plain-language results page.
  3. Model documentation and validation.
  4. A reserve-scarcity indicator.

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
- **Pressure model v1.** Under the standing stress-target decision (`docs/process/AGENT_CONTRACT.md`, Evaluation), the pressure
  probability is an exceedance **derived from the predictive distribution**, not a separately fitted classifier. So v1
  is the as-of distributional model's exceedance at +5 and +10 bp. Its inputs are the latest spread, scheduled pressure
  (month-end, quarter-end, tax date, settlement size) × scarcity state, and TGA change × reserves. It is recalibrated and
  judged against two benchmarks, calendar-type climatology and a persistence-logistic model. In scouting, the
  persistence-logistic beat every gbm classifier overall, and the gbm missed the onset of the Oct 2025 pressure.
  **A direct probability model would need Eleonora to re-rule that decision.** It is an open question, not a plan.
- **Scarcity indicator.**
  - A declared regime state built from reserves (relative to bank assets where the data allow), ON RRP and the NY Fed's
    Reserve Demand Elasticity (monthly).
  - Validation: pressure-day frequency must rise with it. The descriptive fact to explain is 1 day with SOFR above IORB in
    2021–23, against 69 in 2025.
- **Evaluation.**
  - Walk-forward, refit every 21 scored days (declared in the record), expanding window.
  - Metrics split by regime and by pressure-day type: Brier with its decomposition, CORP reliability, precision-recall
    and lead time.
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
- **Mutations** are recorded only for leakage, availability and staleness guards. Everything else is covered by CI
  and review.

## 4. Workflow

`docs/decisions/workflow.md` sets out directives, sessions and pull requests, and how to review them. In practice:
- **Research runs** are scripts or a notebook on a branch, with results in the pull request. They take about 90 s per
  configuration in a cloud checkout.
- **Publish runs** follow the publish rule.
- **Branch protection** goes on `main` once the first pull request shows its check names.

## 5. What we can borrow (verified links in [`literature.md`](literature.md))

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
   - precision-recall, Sarlin usefulness and lead time per horizon.
4. **Coverage under regime shift:**
   - DtACI and conformal PID (MIT code), with a calendar scorecaster;
   - group-conditional conformal (`conditionalconformal`);
   - MAPIE for baselines.
5. **Growth-at-Risk template** (Adrian, Boyarchenko & Giannone 2019): a quantile grid smoothed into a distribution, so P(≥ x)
   comes from the same model. Caveat: Plagborg-Møller et al. find the tail adds little over the mean, which is why the
   baselines above are mandatory.
6. **SRF take-up as a censored pressure signal.** The scan reads the 29 Jul 2026 implementation note as SRP rate =
   IORB + 10 bp, so the +10 bp threshold sits at the facility rate. Verify against the note before using it.

## 6. Repo streamlining

Done in PR #24: the README lead with the plain-English overview and figure, the Colab notebook
(`notebooks/00_overview.ipynb`), the status pages folded into `METHODOLOGY.md`, and the contract moved to
`docs/process/`.

## 7. Sequence

Each step is one directive. Briefs are in [`directives/`](directives).

1. **The as-of information set:** [`01`](directives/01-as-of-information-set.md).
2. **Streamline the front door:** done, PR #24.
3. **Re-score and publish:** [`03`](directives/03-rescore-publish.md), after step 1 merges.
4. **Retire the legacy ownership gates:** [`04`](directives/04-retire-legacy-gates.md): done, PR #30.
5. **Review CI and the test suite:** [`05`](directives/05-review-ci-and-tests.md), after 04.
6. **Pressure model v1 and the scarcity indicator**, after step 3.
7. **Calibration re-diagnosis:** CV+ against online conformal.
8. **Data additions** (§2), each priced as-of.
9. **Model documentation and validation report,** in a model-risk structure: purpose and use, data, methodology,
   assumptions and limitations, performance by regime, outcomes analysis, monitoring. The lag finding goes in as a
   validation result.
10. **Plain-language results page** on the site, generated from records.

## Decision records

- In force: `docs/decisions/information-set.md`, `workflow.md` and `publish-rule.md`.
- Open, for Eleonora:
  - the materiality rule (§2);
  - whether the pressure probability may come from a direct model (§1).
  Neither is in force until she rules.
