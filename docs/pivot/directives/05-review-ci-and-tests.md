# Directive: review CI and the test suite

Can run at any time after directive 04, since both touch `.github/workflows/tests.yml`. Work it as one pull request.
Removing a test is a claim that nothing it guarded still needs guarding, so every removal names its reason.

## What is already measured (30 September 2026, a 2-core cloud checkout)

- **The whole suite takes about 530 s in one process with the ml extra installed. Without it, it takes about 48 s**
  (`--durations` under an interpreter with no numpy or scikit-learn, so the ML tests skip). Nearly all the time is
  `tests/test_ml.py` and `tests/test_tail_diagnostics.py`, which refit gradient-boosted models.
- **The ML time is concentrated in eight test methods,** which take about 375 s of the ML modules' roughly 470 s:

  | Time | Test class |
  |---|---|
  | 64 s | `ExceedanceTailAccountTests` |
  | 63 s | `TailAccountTests` |
  | 62 s | `GradientBoostedCrossConformalTests` |
  | 44 s | `GradientBoostedArxFeatureTests` |
  | 42 s | `ScaledCrossConformalTests` |
  | 40 s | `PartialCrossConformalTests` |
  | 40 s | `test_tail_diagnostics.KnotRefitTests` |
  | 22 s | `GradientBoostedCrossAsymmetricConformalTests` |

  Several of them guard configurations whose status is now open: the asymmetric calibrations were retired before the pivot,
  and the scaled and partial variants are unpublished or conditional on the old information set. Rescale their
  fixtures; do not delete a guard whose code still ships.
- **The slowest non-ML tests:**

  | Time | Test |
  |---|---|
  | 17 s | `test_data.RequestedColumnsBuildTests` (a digest rebuild) |
  | 6 s | `test_generated_results.MilestoneAReproductionTests` |
  | 4 s | `test_data.LaneDocstringColumnClaimTests` |
  | 4 s | `test_data.PanelYear2025DiagnosticTests` |

  Everything else is under 3 s.
- **What `tests.yml` runs:**
  - A matrix of the full suite without the extra: two interpreters on a pull request, three on a push or the weekly
    schedule.
  - An `ml` job that reinstalls the extra and runs the **full suite again** on a push, or on a pull request touching
    the ML surface.
  - The legacy `ownership` job.
  - A push to `main` also triggers `status.yml`, whose bot commits `docs/status.json` back onto `main` after every
    merge. That leaves every open branch one commit behind.
- **The suite's own history:**
  - Its line count is about twice that of the code it tests.
  - Many modules carry docstrings and classes written for the earlier workflow: lane docstrings, track ownership, round
    closes, mutation records.
  - Some tests pin facts that the pivot has changed, for example guards anchored on claims in the old contract text.

## Do

1. **Measure CI itself.**
   `gh run list --repo eleonorabjornberg/repo-market-model --workflow tests.yml --limit 30 --json databaseId,event,conclusion,createdAt,updatedAt`,
   then `gh run view <id> --json jobs` for per-job times. Report the wall time and compute minutes per pull request
   and per push.
2. **Classify every test module and class** in a table in the pull request:
   - **invariant**: leakage, availability, staleness, contract tests 1–5, the dependency boundary, record regeneration,
     panel digest, docs freshness;
   - **behaviour**: a function's documented behaviour;
   - **pinned figure**: an exact published number;
   - **legacy**: exists for the earlier workflow or its documents;
   - **redundant**: the same property tested twice.
3. **Keep every invariant.** Remove or rewrite legacy tests, stating the reason for each. Merge redundant ones.
   Convert pinned-figure tests that directive 03 will invalidate into tests that regenerate from records.
4. **Make the ML tests fast** without weakening them: smaller fixtures, fewer boosting iterations inside tests, and one
   shared fitted model per class where the property allows. If any test must stay slow, mark it and run it only on
   pushes to `main` and the weekly schedule.
5. **Reshape CI.**
   - On pull requests: one interpreter for the fast suite, plus the ml job running only the ML modules.
   - On pushes to `main` and the weekly schedule: the full matrix.
   - Decide `status.yml`: generate `docs/status.json` inside the pull request that changes its inputs, or drop it. Say
     which, and why.
6. **Update `CLAUDE.md` if a command or rule changes.**

## Acceptance

- No invariant test removed.
- Zero `expectedFailure`.
- CI green.
- The pull request reports before and after: wall time, compute minutes, and the number of tests per class of the
  table (the report may carry counts; `docs/` may not).
- Every removed or rewritten test is listed with its reason.
