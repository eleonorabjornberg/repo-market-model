"""Cleared-DVP segment test (#187): the pre-declared inputs and the win rule.

Eleonora's request of 2 October 2026: "Let's do a test with the data we can
access, see if it makes a difference, and if it improves the model we make an
effort to include the data." SOFR is BGCR (tri-party and GCF) plus FICC-cleared
DVP repo; this tests the cleared-DVP segment directly. Everything below was
fixed and committed before any scoring run, and every item is reported whatever
its result.

**The candidate inputs** (`CANDIDATES`), each read as-of under
`docs/decisions/information-set.md`:

* `dvp_volume_share`: (SOFR volume − BGCR volume) / SOFR volume. Both are
  New York Fed fields of one publication instant (`nyfed_sofr`, `nyfed_bgcr`),
  so it needs no new source.
* `dvp_volume_share_chg20`: its change over 20 panel rows (business days).
* `ofr_dvp_minus_bgcr_bp`: the OFR's overnight DVP average rate, preliminary
  (`REPO-DVP_AR_OO-P`, source `ofr_stfm_repo`), minus BGCR, in whole basis
  points. The OFR published it in real time from `OFR_REAL_TIME_START`; the
  values before that were filled in later, so the column is `None` before it.
  The backfilled column (`ofr_dvp_minus_bgcr_bp_backfill`) exists for one
  sensitivity only, labelled "sensitivity: pre-publication backfill, not
  admissible under the information-set rule", and chooses nothing.
* `sofr_tgcr` and `bgcr_tgcr`: #127's spreads, re-reported on this grid.

**The groups** (`GROUPS`): each input on its own; the volume pair together
(`dvp_volume_pair`); and the three DVP inputs together (`dvp_all`). The OFR
rate and `dvp_all` are scored on the OFR window, 2020-09-09 to 2025-12-31 (the
days the rate was public); every other group on 2018-06-29 to 2025-12-31. No
day on or after 2026-01-01 is scored (`docs/decisions/lockbox.md`).

**Sensitivities** (`SENSITIVITIES`) are information only. They sit outside the
family below and can never count: the OFR rate read with a one-business-day
lag instead of the declared two, and the pre-publication backfill.

**The win rule** (Eleonora's scope comment on #187, 2 October 2026: "Don't let
the experiment win by luck"), fixed before any scoring:

1. *The family* is every paired comparison the PR reports, sensitivities
   aside: each group, at +5 and +10 bp, at horizons 1-5, against pressure
   model v1 as published by #124 and against the persistence-logistic, on all
   scored days (`POOLED`) and on onset days (`ONSET`, #160's method: a scored
   day whose previous panel day is not above +5 bp on whole basis points);
   and each group's CRPS against the published funding declaration
   (horizon 1). `family_size()` states its size.
2. *Family-wise control.* Each comparison gets a one-sided paired
   stationary-bootstrap p-value for improvement, and one for deterioration
   (`ml.paired_bootstrap_p_values`, `P_VALUE_REPLICATIONS` replications, each
   comparison's own block length and seed). Improvement p-values are Holm
   corrected across the whole family at `FAMILY_LEVEL`; so, separately, are
   the deterioration p-values. The 90% intervals in the tables decide nothing.
3. *A win*, for one group at one threshold, needs every one of:
   a. its pooled comparison survives the correction against **both**
      benchmarks at `MIN_SURVIVING_HORIZONS` or more of the five horizons;
   b. the pooled point estimate improves on both benchmarks at **every**
      horizon at that threshold;
   c. the point estimate improves on both benchmarks in **both** stress
      regimes (`STRESS_REGIMES`) at every horizon 1-5 at that threshold;
   d. none of the group's comparisons is significantly worse after the
      correction: not the other threshold, not CRPS, not onset days.
4. *Never a win:* a sensitivity, and any group scored on the OFR window, which
   holds no 2018-19 episode; at best those are "promising, unconfirmed".
5. *Outcomes:* "win" (the "Publish?" issue proposes inclusion); "promising"
   (a group that is not a win, but meets 3a-3d with the Holm condition in 3a
   replaced by an uncorrected one-sided p-value at or below `FAMILY_LEVEL`,
   or misses exactly one of 3a-3d); "no effect" otherwise. Even a win is not
   final until the locked 2026 period is opened once for it (#151).

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published
panel, declaration or record reads these columns. The scoring script
(`scripts/dvp_segment_inputs.py`) switches them on for its own run, as
`scripts/early_warning_inputs.py` does for #127's.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .data import DailyObservation

__all__ = [
    "CANDIDATES",
    "COLUMN_FIELDS",
    "Candidate",
    "FAMILY_LEVEL",
    "GROUPS",
    "Group",
    "MIN_SURVIVING_HORIZONS",
    "OFR_DVP_RATE_FIELD",
    "OFR_REAL_TIME_START",
    "OFR_SOURCE_ID",
    "OFR_WINDOW",
    "FULL_WINDOW",
    "P_VALUE_REPLICATIONS",
    "SENSITIVITIES",
    "STRESS_REGIMES",
    "VOLUME_CHANGE_ROWS",
    "build_columns",
    "classify",
    "comparison_key",
    "family_size",
    "holm",
]

#: The OFR's Short-term Funding Monitor repo collection (#187).
OFR_SOURCE_ID = "ofr_stfm_repo"
#: The overnight/open DVP average rate, preliminary: the input's series.
OFR_DVP_RATE_FIELD = "REPO-DVP_AR_OO-P"
#: The OFR began publishing its repo data in real time on 2020-09-09; every
#: value before it was filled in later, and was not public on its own day.
OFR_REAL_TIME_START = date(2020, 9, 9)

#: The change window of `dvp_volume_share_chg20`, in panel rows.
VOLUME_CHANGE_ROWS = 20

#: Scored windows, first and last scored day. The full window is the
#: lockbox-permitted one every corrected record uses (#124); the OFR window is
#: the days the OFR rate was public.
FULL_WINDOW = (date(2018, 6, 29), date(2025, 12, 31))
OFR_WINDOW = (OFR_REAL_TIME_START, date(2025, 12, 31))

#: The win rule (module docstring), fixed before scoring.
FAMILY_LEVEL = 0.10
MIN_SURVIVING_HORIZONS = 3
STRESS_REGIMES = ("2018-19", "2025-26")
#: Enough that a Holm threshold of `FAMILY_LEVEL / family_size()` is
#: reachable: the smallest attainable p-value is 1 / (replications + 1).
P_VALUE_REPLICATIONS = 20000
THRESHOLDS = (5.0, 10.0)
HORIZONS = (1, 2, 3, 4, 5)
BENCHMARKS = ("pressure_model_v1", "persistence_logistic")
#: The two day sets each Brier comparison is made on.
POOLED = "all_days"
ONSET = "onset_days"
#: #160's onset day: the previous panel day is not above this, on whole bp.
ONSET_BP = 5.0


class Candidate(NamedTuple):
    """One pre-declared input: its name, definition and the columns it adds."""

    name: str
    definition: str
    columns: Tuple[str, ...]


class Group(NamedTuple):
    """One scored run: the inputs it adds and the window it is scored on."""

    name: str
    inputs: Tuple[str, ...]
    window: Tuple[date, date]
    #: Why the group can never be a win, or `None`.
    capped: Optional[str] = None


class Sensitivity(NamedTuple):
    """Information only: outside the family, it decides nothing."""

    name: str
    group: str
    label: str
    window: Tuple[date, date]
    #: The columns read in place of the group's, `{group column: column}`.
    replaces: Tuple[Tuple[str, str], ...] = ()
    #: The `ofr_stfm_repo` release lag read instead of the declared one.
    release_lag_days: Optional[int] = None


#: The pre-declared candidates, in the issue's order. Fixed before scoring.
CANDIDATES: Tuple[Candidate, ...] = (
    Candidate(
        "dvp_volume_share",
        "(SOFR volume − BGCR volume) / SOFR volume, the cleared-DVP share of "
        "SOFR's volume (nyfed_sofr SOFR_volume, nyfed_bgcr BGCR_volume)",
        ("dvp_volume_share",),
    ),
    Candidate(
        "dvp_volume_share_chg20",
        "dvp_volume_share's change over 20 panel rows (business days)",
        ("dvp_volume_share_chg20",),
    ),
    Candidate(
        "ofr_dvp_minus_bgcr_bp",
        "the OFR overnight DVP average rate, preliminary (REPO-DVP_AR_OO-P), "
        "minus BGCR, in whole basis points; None before 2020-09-09",
        ("ofr_dvp_minus_bgcr_bp",),
    ),
    Candidate(
        "sofr_tgcr",
        "SOFR − TGCR, in bp (#127, re-reported for comparison)",
        ("sofr_tgcr_bps",),
    ),
    Candidate(
        "bgcr_tgcr",
        "BGCR − TGCR, in bp (#127, re-reported for comparison)",
        ("bgcr_tgcr_bps",),
    ),
)

_NO_STRESS_EPISODE = (
    "scored on the OFR window (2020-09-09 to 2025-12-31), which holds no "
    "2018-19 episode: at most 'promising, unconfirmed' (#187, win rule item 4)"
)

#: Every scored group: each input on its own, the volume pair, all three DVP
#: inputs. Fixed before scoring.
GROUPS: Tuple[Group, ...] = (
    Group("dvp_volume_share", ("dvp_volume_share",), FULL_WINDOW),
    Group("dvp_volume_share_chg20", ("dvp_volume_share_chg20",), FULL_WINDOW),
    Group("ofr_dvp_minus_bgcr_bp", ("ofr_dvp_minus_bgcr_bp",), OFR_WINDOW, _NO_STRESS_EPISODE),
    Group("sofr_tgcr", ("sofr_tgcr",), FULL_WINDOW),
    Group("bgcr_tgcr", ("bgcr_tgcr",), FULL_WINDOW),
    Group("dvp_volume_pair", ("dvp_volume_share", "dvp_volume_share_chg20"), FULL_WINDOW),
    Group(
        "dvp_all",
        ("dvp_volume_share", "dvp_volume_share_chg20", "ofr_dvp_minus_bgcr_bp"),
        OFR_WINDOW,
        _NO_STRESS_EPISODE,
    ),
)

BACKFILL_LABEL = (
    "sensitivity: pre-publication backfill, not admissible under the "
    "information-set rule"
)
ONE_DAY_LAG_LABEL = (
    "sensitivity: ofr_stfm_repo read one business day after its date, not the "
    "declared two"
)
_BACKFILL = (("ofr_dvp_minus_bgcr_bp", "ofr_dvp_minus_bgcr_bp_backfill"),)

#: Information only. Fixed before scoring.
SENSITIVITIES: Tuple[Sensitivity, ...] = (
    Sensitivity("ofr_dvp_minus_bgcr_bp@lag1", "ofr_dvp_minus_bgcr_bp", ONE_DAY_LAG_LABEL, OFR_WINDOW,
                release_lag_days=1),
    Sensitivity("dvp_all@lag1", "dvp_all", ONE_DAY_LAG_LABEL, OFR_WINDOW, release_lag_days=1),
    Sensitivity("ofr_dvp_minus_bgcr_bp@backfill", "ofr_dvp_minus_bgcr_bp", BACKFILL_LABEL, FULL_WINDOW,
                replaces=_BACKFILL),
    Sensitivity("dvp_all@backfill", "dvp_all", BACKFILL_LABEL, FULL_WINDOW, replaces=_BACKFILL),
)

_SOFR_VOLUME = ("nyfed_sofr", "SOFR_volume")
_BGCR_VOLUME = ("nyfed_bgcr", "BGCR_volume")
_OFR_RATE = (OFR_SOURCE_ID, OFR_DVP_RATE_FIELD)
_BGCR = ("nyfed_bgcr", "BGCR")

#: Every new column's source fields, for the as-of rule. **Off**: switched on
#: only by the scoring script, never part of `contract.FEATURE_FIELDS`.
#: `sofr_tgcr_bps` and `bgcr_tgcr_bps` are #127's (`early_warning.COLUMN_FIELDS`).
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "dvp_volume_share": (_SOFR_VOLUME, _BGCR_VOLUME),
    "dvp_volume_share_chg20": (_SOFR_VOLUME, _BGCR_VOLUME),
    "ofr_dvp_minus_bgcr_bp": (_OFR_RATE, _BGCR),
    "ofr_dvp_minus_bgcr_bp_backfill": (_OFR_RATE, _BGCR),
}


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def build_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with every candidate column added, each from its own and earlier rows.

    Reads `sofr_volume`, `bgcr_volume`, `ofr_dvp_rate` and `bgcr` where
    present (rates in percent, volumes in USD billions). A column whose inputs
    are missing on a row it needs is `None` there. `ofr_dvp_minus_bgcr_bp` is
    `None` on every row dated before `OFR_REAL_TIME_START`, whatever the
    snapshot holds: the value for such a day was filled in later and was not
    public at any decision instant the as-of rule would read it at. Only
    `ofr_dvp_minus_bgcr_bp_backfill`, the sensitivity's column, keeps it.
    """

    shares: List[Optional[float]] = []
    out: List[DailyObservation] = []
    for position, row in enumerate(rows):
        values: Dict[str, Optional[float]] = dict(row.values)
        sofr_volume, bgcr_volume = _get(row, "sofr_volume"), _get(row, "bgcr_volume")
        share = (
            None
            if sofr_volume is None or bgcr_volume is None or sofr_volume <= 0.0
            else (sofr_volume - bgcr_volume) / sofr_volume
        )
        shares.append(share)
        values["dvp_volume_share"] = share
        earlier = shares[position - VOLUME_CHANGE_ROWS] if position >= VOLUME_CHANGE_ROWS else None
        values["dvp_volume_share_chg20"] = (
            None if share is None or earlier is None else share - earlier
        )
        rate, bgcr = _get(row, "ofr_dvp_rate"), _get(row, "bgcr")
        spread = None if rate is None or bgcr is None else float(round((rate - bgcr) * 100.0))
        values["ofr_dvp_minus_bgcr_bp_backfill"] = spread
        values["ofr_dvp_minus_bgcr_bp"] = None if row.date < OFR_REAL_TIME_START else spread
        out.append(DailyObservation(row.date, values))
    return out


def family_size() -> int:
    """How many comparisons the Holm correction runs over (win rule, item 1)."""

    brier = len(GROUPS) * len(THRESHOLDS) * len(HORIZONS) * len(BENCHMARKS) * 2  # pooled, onset
    crps = len(GROUPS)
    return brier + crps


def holm(p_values: Mapping[str, float], level: float = FAMILY_LEVEL) -> Dict[str, bool]:
    """Holm's step-down procedure: which hypotheses are rejected at `level`.

    Sorts the p-values ascending and rejects the k-th smallest (k from 1) while
    it is at or below `level / (m - k + 1)`; the first that is not stops it, and
    every later one is kept. Controls the family-wise error rate at `level`
    under any dependence between the tests. Ties are broken by key, so the
    result does not depend on the mapping's order.
    """

    if not 0.0 < level < 1.0:
        raise ValueError(f"level must be in (0, 1), got {level}")
    for key, p in p_values.items():
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"p-value of {key!r} is {p}, outside [0, 1]")
    m = len(p_values)
    rejected = {key: False for key in p_values}
    for k, key in enumerate(sorted(p_values, key=lambda name: (p_values[name], name)), start=1):
        if p_values[key] > level / (m - k + 1):
            break
        rejected[key] = True
    return rejected


def comparison_key(group: str, *parts: object) -> str:
    """One comparison's name in the family: `group|brier|day set|tau|h|benchmark` or `group|crps`."""

    return "|".join([group, *(f"{part:g}" if isinstance(part, float) else str(part) for part in parts)])


#: The outcome categories, best first.
OUTCOMES = ("win", "promising", "no effect")


def classify(group: Group, results: Mapping[str, Mapping[str, object]]) -> dict:
    """The group's outcome under the win rule (module docstring, items 3-5).

    `results` maps every `comparison_key` of the family to its entry: `mean`
    (positive favours the group: benchmark minus group for Brier, control
    minus group for CRPS), `p_improve`, `p_worse`, and the Holm verdicts
    `holm_improve` and `holm_worse` from the whole family; Brier entries on all
    days also carry `regimes`, `{regime label: mean}`, with `None` for a regime
    the window holds no day of. Every condition is reported per threshold, so
    a reader can see which one a group missed.
    """

    name = group.name
    own = {key: entry for key, entry in results.items() if key.split("|", 1)[0] == name}
    worse = sorted(key for key, entry in own.items() if entry["holm_worse"])
    by_threshold = {}
    for tau in THRESHOLDS:
        pooled = {
            (h, bench): own[comparison_key(name, "brier", POOLED, tau, h, bench)]
            for h in HORIZONS
            for bench in BENCHMARKS
        }
        surviving = [h for h in HORIZONS if all(pooled[h, b]["holm_improve"] for b in BENCHMARKS)]
        uncorrected = [
            h for h in HORIZONS if all(pooled[h, b]["p_improve"] <= FAMILY_LEVEL for b in BENCHMARKS)
        ]
        regimes_missed = sorted(
            f"h{h} {bench} {regime}"
            for h in HORIZONS
            for bench in BENCHMARKS
            for regime in STRESS_REGIMES
            if not ((pooled[h, bench]["regimes"].get(regime) or 0.0) > 0.0)
        )
        conditions = {
            "a_survives_correction": len(surviving) >= MIN_SURVIVING_HORIZONS,
            "b_improves_every_horizon": all(entry["mean"] > 0.0 for entry in pooled.values()),
            "c_improves_in_both_stress_regimes": not regimes_missed,
            "d_nothing_significantly_worse": not worse,
        }
        met = all(conditions.values())
        uncorrected_met = len(uncorrected) >= MIN_SURVIVING_HORIZONS and all(
            value for key, value in conditions.items() if key != "a_survives_correction"
        )
        missed = [key for key, value in conditions.items() if not value]
        if met and group.capped is None:
            outcome = "win"
        elif met or uncorrected_met or len(missed) == 1:
            outcome = "promising"
        else:
            outcome = "no effect"
        by_threshold[f"{tau:g}"] = {
            "outcome": outcome,
            "conditions": conditions,
            "horizons_surviving_correction": surviving,
            "horizons_surviving_uncorrected": uncorrected,
            "stress_regime_cells_not_improved": regimes_missed,
        }
    best = min((entry["outcome"] for entry in by_threshold.values()), key=OUTCOMES.index)
    return {
        "outcome": best,
        "capped": group.capped,
        "significantly_worse": worse,
        "by_threshold": by_threshold,
    }
