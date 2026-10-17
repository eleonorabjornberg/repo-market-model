# CI duration: where the unit-test job's time goes (#848, finding #812)

Infrastructure for every hypothesis step; it serves no H step directly. **Nothing is scored here.** No development
data and no lockbox day is read; the figures are seconds of test time. The parts of #812 that are Eleonora's
decision (splitting the job, nightly-only marks, dropping the networking-off pass) are marked questions below and
are not implemented.

## 1. The timing table, before any change

One full one-process run of `unittest discover -s tests` in the rmm environment (`scripts/test_timing_848.py`),
wall seconds. A class's `setUpClass` is counted with that class. This sandbox is slower than the CI runner, so read
the shares, not the absolute seconds.

Wall time 3772 s, ok=True.

| module | seconds | share |
|---|---:|---:|
| test_ml | 1119.6 | 29.7% |
| test_power_study | 374.8 | 9.9% |
| test_visual | 363.8 | 9.6% |
| test_cli_eval | 231.9 | 6.1% |
| test_scoring_protocol_synthetic | 181.5 | 4.8% |
| test_generated_results | 170.2 | 4.5% |
| test_scoring_protocol_coverage | 151.7 | 4.0% |
| test_band_coverage | 137.5 | 3.6% |
| test_live_record | 117.8 | 3.1% |
| test_identified_level_689 | 64.5 | 1.7% |
| test_data | 55.0 | 1.5% |
| test_plain_page | 50.6 | 1.3% |

**The networking-off pass.** In `.github/workflows/tests.yml` the `unit tests (3.11)` job on a recent green push to
main took: suite 1208 s, results-page check 34 s, suite with networking disabled 1203 s (job steps from the Actions
API). The networking-off pass is therefore about 49% of the job: it reruns the same suite in an empty network
namespace.

## 2. Builds, walks and bootstraps that more than one module repeats

`scripts/test_repeats_848.py` wraps the public `repo_model` functions named build, walk, bootstrap, fit, load or
parse, runs the suite, and groups outermost calls by function and argument digest. A repeat is one function with one
digest called from more than one test module. The largest, by seconds spent after the first call:

| function | calls | modules | total s | repeat s |
|---|---:|---|---:|---:|
| repo_model.ingest.parse_snapshots (3468ccf73a40) | 17 | <fixture>, test_confirmation_design, test_data, test_onset, test_tax_date_market_days | 64.9 | 60.8 |
| repo_model.data.build_daily_panel (8766530b303e) | 11 | <fixture>, test_at_risk_by_state, test_visual | 25.4 | 23.4 |
| repo_model.data.build_daily_panel (0e1121252732) | 11 | <fixture>, test_at_risk_by_state, test_visual | 22.7 | 20.7 |
| repo_model.metrics.stationary_bootstrap_indices (d95159c3ac5f) | 537141 | test_benchmarks, test_onset | 10.3 | 10.3 |
| repo_model.metrics.stationary_bootstrap_interval (6f6615d8afe0) | 16 | <fixture>, test_visual | 5.9 | 5.5 |
| repo_model.metrics.stationary_bootstrap_interval (041c7e96fc59) | 14 | <fixture>, test_visual | 4.5 | 4.2 |
| repo_model.spread_mr_variants.walk (2d4a5ac559d5) | 2 | <fixture>, test_spread_mr_variants | 7.7 | 4.0 |
| repo_model.ingest.parse_snapshots (d11d0318c42b) | 21 | <fixture>, test_visual | 2.5 | 2.4 |
| repo_model.ingest.parse_snapshots (a53fb78ebdef) | 7 | <fixture>, test_measurement_fields, test_visual | 2.0 | 1.9 |
| repo_model.settlement_dating.load_snapshot_results (4d606eab3ed7) | 12 | test_announcement_dating_rescore, test_near_threshold_688, test_off_risk_day_681 | 1.7 | 1.6 |

Summed over every repeat group, the avoidable time is about 160 s of the 3770 s run (4%), most of it the
published-panel `build` (`parse_snapshots`) and the panel builds inside `test_at_risk_by_state` and `test_visual`.
The time is elsewhere: `test_ml` alone is 30% and the power-study, synthetic and coverage suites another 25%, and
none of those repeat a build with the same inputs.

## 3. What was shared

`test_onset` and `test_protocol_benchmarks` each built the published panel from the tracked fixtures with the same
cutoff and decision time. They now share one in-process build, `tests/panel_cache.py`. `tests/test_panel_cache.py`
was written first (it failed on the missing module) and shows the cached panel CSV and point-in-time CSV are
byte-identical to a fresh build, and that both callers receive the one cached object. No assertion changed and no
test is skipped. The panel builds in `test_at_risk_by_state` and `test_visual` go through script loaders with their
own arguments and are listed, not shared: sharing them would change what those scripts exercise.

## 4. Before and after

Full suite, one process, same machine, wall seconds: before 3772 s, after 3804 s (both OK).
The difference is within the run-to-run noise of this sandbox. The saving the cache can give is one fixture build
(a few seconds), which is below that noise. **The honest result is that sharing repeated builds does not cut the
job's wall time measurably; the time is in a few long suites and in the second pass.**

## 5. Marked questions for Eleonora (none implemented)

1. **Drop or narrow the networking-off pass.** Measured cost: about 1200 s of about 2450 s of the job on the CI
   runner (49%). It protects against a test reaching a host when `tests/netguard.py` is bypassed (#262).
2. **Split the job** so the suite and the networking pass run in parallel. Measured cost: none in work, job wall
   time would roughly halve; it adds a second required check.
3. **Nightly-only marks** for the slowest classes (`test_ml` partial and scaled cross-conformal, the power-study
   `SimulationTests`, `RecoveryTests`, `ExceedanceBacktestCommandTests`): about 1100 s of the 3772 s run (29%) in
   this sandbox. They would stop running on pull requests.
