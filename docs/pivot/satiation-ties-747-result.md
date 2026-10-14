# The fitted satiation kink under ties (#747)

**Serves:** H7, the model-repo side of the estimator (also an input to H5 and H6). Development data, a measurement: no
forecast is scored, nothing here is a verdict, and no day after 2025-12-31 is read. No published figure moves.

## The defect

`satiation.fit_level` kept a new grid point only if its squared error was lower than the best by more than an absolute
`1e-12`, while the errors are in the thousands. When the grid points at or above the sample's highest reserves ratio fit
alike (the hinge is then a straight line in the ratio, so only the intercept differs), floating-point rounding chose among
them and the record still said `fitted: True`. `eleonorabjornberg/repo-market-liquidity#54` measured a jump of up to
4.25 points between refits on synthetic data, against a goalpost of 0.5 points.

## The rule now in force (this pull request)

- Grid points whose squared error is within `KINK_TIE_RTOL = 1e-9` of the best (relative, `abs(sse - best) <= rtol * best`)
  are tied.
- If the tied set spans more than one grid step, the result is `fitted: False`, reason
  "not identified (tied SSE over [lo, hi])", with `tied: [lo, hi]`, and the level is the fixed 0.12, exactly as for any
  other unfitted result. No point is ever returned from a tied set.
- If the tied set is one point, or two neighbours, the lowest squared error wins as before.
- **Why 1e-9.** The error is a sum over hundreds of pairs; rounding moves it by about 1e-13 of itself, so exact ties sit
  far inside 1e-9. On the real refits (below) the tolerance was also tried wider: at 1e-6 no refit of any row has a tied
  set beyond one step, at 1e-4 some do (the objective is nearly flat there, which is a finding, not a tie), at 1e-3 most do.
  1e-9 therefore sits between rounding noise and the first real near-flat refits, three orders from either.

## Callers

Every caller reads `(level, record)` and uses the level; an unfitted record already gives the fixed 0.12, and "not
identified" is such a record, so no caller changes:

| caller | use |
| --- | --- |
| `ml.py`, `_ProjectedHingeDesign.bind` | projected-reserves model, fitted form (`projected_fitted`) |
| `ml.py`, the combined ordinary-day model (`late_level`) | `risk_gbm+combined_fitted` |
| `structural_liquidity.py`, `structural_exceedance.fit_predict` | `structural_fitted` and, through `design.level_source`, the kinked `structural_kinked_fitted` of #626 |

## How many refits become "not identified"

`scripts/satiation_ties_747.py` re-runs the walk-forward refits of the fitted-level rows of #587 and of #626 on the
published panel and the scratch panels, at horizons 1 to 5, and compares the new rule with the old one at every refit. It
scores nothing. Counts by calendar year of the refit's first served anchor are in
`evidence/satiation-ties-747/ties.json`; the refits are in `refits_h{1..5}.json`.

- **None** of the refits of any of the four rows, in any year or at any horizon, is "not identified", and none sets a
  different level from the old rule. The refits that are not fitted are the same as before: those with too few pairs, all
  of 2018 and the early months of 2019.
- The tie is therefore not what moved the kink in the #587 and #626 runs. It remains a guard for the liquidity repo's
  estimator and for any refit on a window whose ratios sit well below the grid's upper end (the likely 2018-19 case does
  not occur in these runs because the 250-pair minimum already refuses the early windows).
- Sensitivity of the tolerance (`not_identified_at_rtol_*` in `ties.json`): none at 1e-9 or 1e-6; some at 1e-4; most at
  1e-3. Choosing a wider tolerance would declare real refits "not identified" and is Eleonora's call, not this
  pull request's.
- Cross-check: the old rule reproduces the levels recorded in `evidence/satiation/refits.json` for the structural and the
  combined rows exactly. For the projected row it reproduces most but not all (the other refits differ in later years,
  since the projected features changed after that record was written); old and new rule agree on those refits too, so the
  difference is not the tie.

Re-scored pages: none, since no level moves.
