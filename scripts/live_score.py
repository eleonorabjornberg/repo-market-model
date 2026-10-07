"""Score the live record (#215), only on its pre-registered dates.

Pre-registered by Eleonora's decision of 3 October 2026 (#215), before any day
was logged:

* **Scoring dates:** 2027-04-01, 2027-10-01, then every 1 October. On each,
  every logged day whose target day is in the outcome panel and before the
  scoring date is scored, cumulatively from the first logged day. What the
  script enforces about the date is two checks (#257): the date must be a scoring
  date (`require_scoring_date`, `ValueError`), and it must have come, which is
  today's date in America/New_York not being before it (`require_clock`,
  `LookAheadError`; an override flag lets a run proceed and is recorded in the
  output). Neither decides which days may be scored: that is
  `metadata/lockbox.json`, below.
* **The primary result** (Eleonora's ruling of 4 October 2026 on #215): the
  CRPS of the published distribution (#169's gbm with nested conformal PID)
  against as-of persistence's, at h = 1, both read from each day's file alone
  (`crps_from_record`). The pass rule, its labels and the block-10 sensitivity
  interval are the final test's CRPS cell's (#220, #221): the mean paired
  difference (persistence - published) above 0 and its 90% lower bound above
  0 (`crps_verdict`, `crps_result`, the final test's own functions). CRPS at
  h = 2 to 5 is reported only, and each of its cells carries, next to its
  verdict label, Eleonora's label of 4 October 2026 (#229) verbatim
  (`NOT_EVIDENCE`): "different model from h = 1, and as-of persistence does
  not widen with horizon, so this comparison favours the model; not evidence."
* **Reported only:** Brier for each event target (+5 bp, +10 bp, #139's plain
  leap), horizon and model, paired against each baseline (baseline minus
  model, a positive mean favouring the model), with a 90% stationary-bootstrap
  interval, split by regime and pressure-day type where the cells allow. A
  target is scored only if the scored period holds at least
  `onset.MINIMUM_EVENTS` events of it; below that it is reported as
  inconclusive, with no paired figure.
* **The primary result's verdict** is fixed at the first scoring date that
  scores any day (CRPS has no minimum event count: every day counts). Every
  later date is an update and never replaces it (`headline_status`).
* **The lockbox** (#277, Eleonora's ruling on #269 item 6): logged days are
  blind-tier days, and this script scores them through the same mechanism as
  every comparison. Every day it scores goes through
  `lockbox.require_unlocked` (`_require_scored_days_unlocked`), which reads
  `metadata/lockbox.json` and raises `LookAheadError` on a day in a tier that is
  not opened. A scoring date opens only the days before it: `lockbox.split_tier`
  splits the blind tier there, and committing that split is Eleonora's own
  action (#256). No heading in `lockbox.md` gates the script.
* **The blind gap** (Eleonora's ruling of 5 October 2026 on #235, "Option 2",
  and "keep reported only"): at each horizon, the target days after the panel
  end (2026-09-03) and before the first target day the live record carries
  (`live/2026-10-05.json`'s `targets`). They are scored once, on the first
  scoring date only (`GAP_SCORING_DATE`), in the same run as its live cells,
  as a separate block (`score_gap`), from forecasts `scripts/live_gap.py`
  reconstructs at the pinned code. Every gap cell is reported only, carries
  `GAP_LABEL` verbatim and never reaches the verdict. Scoring a gap day on any
  other date refuses (`require_gap_scoring`, `ValueError`), and its days go
  through the lockbox guard like every other scored day.

* **Provenance** (#257): the result carries the time it started (UTC), the SHA-256
  of the outcome panel, the command that built the panel and the one that scored,
  the code SHA, `sys.version`, the digest of `metadata/live_requirements.lock`,
  every live record's digest, each earlier result's digest, and `skipped_records`:
  every record and horizon it did not score, with the reason (`NO_OUTCOME` or
  `NOT_YET_DUE`). Nothing is skipped silently. The outcome panel must be one
  `scripts/live_raw.py build-panel` built from archived bytes
  (`require_registered_panel`, `ValueError`): `--archive-dir` is a checkout of the
  `live-raw` branch.
* **Event cells** (#257, review finding 30): the Brier cells' bootstrap uses block
  length h + 1, the horizon overlap the final test's event cells and this
  script's CRPS cells use (`EVENT_BLOCK_RULE`, `EVENT_SEED_RULE`).
* **Integrity** (#254): before reading any record, the script verifies the
  live log (`load_records`, `scripts/live_integrity.py`'s `verify`). Every
  file's SHA-256 must equal its #225 digest, the hash chain must be unbroken,
  and every file must have been added by `github-actions[bot]` in an add-only
  commit. Every record's `code.pinned_sha` must also be a registered
  transition in `metadata/live_pin.json` (#255). Otherwise it refuses
  (`ValueError`). `--live-dir` is therefore a
  clean checkout of `live-log`, and `--digests` holds the #225 comments, one
  JSON object per line, each with `author` and `body`.

Results are published whatever they show, as a new record:

    PYTHONPATH=src python3 scripts/live_score.py --date YYYY-MM-DD --live-dir LIVE \\
        --digests DIGESTS.jsonl --panel PANEL --archive-dir LIVE_RAW --output OUT.json \\
        [--gap-dir GAP --pinned-tree PINNED] [--previous EARLIER.json ...] [--override-clock]

`--gap-dir` is required on the first scoring date and refused on every other; with it,
`--pinned-tree` (a checkout of the pin) is required, and the gap's day boundaries are
asserted equal to the ones that tree computes (#257, review finding 39).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.metrics import (  # noqa: E402
    crps_from_quantiles, crps_trapezoid_from_quantiles, stationary_bootstrap_interval,
)
from repo_model.baseline import _seed_from  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import MONTH_END_RULE, load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
LOCK = REPO / "metadata" / "live_requirements.lock"
EASTERN = ZoneInfo("America/New_York")
#: Why a record's horizon is not in a result (`skipped_records`): nothing is skipped silently (#257).
NO_OUTCOME = "target day is not in the outcome panel"
NOT_YET_DUE = "target day is not before the scoring date"
#: The event cells' block rule and seed derivation, declared in the draft amendment (#257, finding 30).
EVENT_BLOCK_RULE = ("stationary bootstrap, mean block length h + 1: the horizon overlap, as the final "
                    "test's event cells and the CRPS cells use")
EVENT_SEED_RULE = ("`baseline._seed_from((scoring date, cell, horizon, model, baseline[, regime or "
                   "day type]))` for each Brier cell")
FIRST_SCORING_DATES = (date(2027, 4, 1), date(2027, 10, 1))
#: The live record's primary result (ruling of 4 October 2026 on #215).
HEADLINE = {"target": "crps", "horizon": 1}
#: The fewest days a regime or day-type cell needs before it carries an interval
#: (#276, ruling #269 item 14). A cell below it reports its mean and "too few
#: days", whatever a bootstrap replicate would have drawn. **Proposed, not
#: decided**: the number is Eleonora's; 20 is the minimum the final test's pages
#: already use (`onset.MINIMUM_EVENTS`, there a count of events), applied here to
#: days. Published records adopt it only at their next publish.
MINIMUM_CELL_DAYS = onset.MINIMUM_EVENTS
TOO_FEW_DAYS = "too few days"
#: From this year each calendar year is its own regime (#276, ruling #269 item 4).
FIRST_YEAR_REGIME = 2027
HORIZONS = (1, 2, 3, 4, 5)
#: Each target, the baselines it is paired with.
BASELINES = {
    "+5bp": ("persistence_logistic", "calendar_climatology"),
    "+10bp": ("persistence_logistic", "calendar_climatology"),
    "leap": (onset.LEAP_PERSISTENCE_LOGISTIC, onset.LEAP_CALENDAR_CLIMATOLOGY),
}
SIGN = "paired = Brier(baseline) - Brier(model) per day; a positive mean favours the model"
#: Eleonora's ruling of 4 October 2026 (#229), verbatim: every h = 2 to 5 CRPS
#: cell carries it, next to its verdict label. At h = 2 to 5 the published
#: distribution is pressure model v1's declaration, not the CRPS record's, and
#: as-of persistence's quantiles are the same at every horizon.
NOT_EVIDENCE = ("different model from h = 1, and as-of persistence does not widen with "
                "horizon, so this comparison favours the model; not evidence.")
#: What the h = 2 to 5 distribution is (#267, second review finding 8): the one-step
#: gbm's quantiles served stale, so q25/q50/q75 are identical at h = 2 to 5 and only
#: the PID outer pair (q05/q95) differs. Stated beside the verdict label, not in it:
#: the label is Eleonora's wording, verbatim.
INTERIOR_DESIGN = ("at h = 2 to 5 the published q25, q50 and q75 are the one-step gbm served "
                   "stale, identical across h = 2 to 5; only the conformal PID outer pair "
                   "(q05, q95) differs by horizon.")
CRPS_SIGN = ("paired = CRPS(persistence) - CRPS(published) per day; a positive mean favours "
             "the published distribution")
#: The blind gap (#235). The first logged day: its targets bound the gap.
FIRST_LIVE_DAY = date(2026, 10, 5)
#: The gap is scored once, on the first scoring date, and on no other.
GAP_SCORING_DATE = FIRST_SCORING_DATES[0]
#: Eleonora's ruling of 5 October 2026 on #235, verbatim: every gap cell carries it.
GAP_LABEL = ("blind but not live: forecasts reconstructed after the fact by the frozen code "
             "from inputs fetched at scoring time (latest vintage); reported only, not evidence")


def _live():
    """`scripts/live_record.py`, loaded once."""

    global _LIVE
    if _LIVE is None:
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_record", REPO / "scripts" / "live_record.py")
        _LIVE = module_from_spec(spec)
        spec.loader.exec_module(_LIVE)
    return _LIVE


_LIVE = None


def _integrity():
    """`scripts/live_integrity.py`, loaded once."""

    global _INTEGRITY
    if _INTEGRITY is None:
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_integrity", REPO / "scripts" / "live_integrity.py")
        _INTEGRITY = module_from_spec(spec)
        spec.loader.exec_module(_INTEGRITY)
    return _INTEGRITY


_INTEGRITY = None


def _pins():
    """`scripts/live_pin.py`, loaded once."""

    global _PINS
    if _PINS is None:
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_pin", REPO / "scripts" / "live_pin.py")
        _PINS = module_from_spec(spec)
        spec.loader.exec_module(_PINS)
    return _PINS


_PINS = None


def load_records(live_dir: Path, digests, manifest=None) -> list:
    """The live log's records, after the log is verified (#254) and each record's pin is registered (#255).

    Raises:
        ValueError: no digests, any integrity check failing, a malformed
            record, a dry run, or a record made at a code SHA that is not a
            registered transition in `metadata/live_pin.json`.
    """

    if digests is None:
        raise ValueError("the live record is scored only against its #225 digests: pass --digests")
    integrity = _integrity()
    integrity.verify(live_dir, integrity.parse_digests(digests))
    pins = _pins()
    manifest = pins.load_manifest() if manifest is None else manifest
    live = _live()
    records = []
    for path in sorted((Path(live_dir) / "live").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        live.validate_record(record)
        if record.get("dry_run"):
            raise ValueError(f"{path} is a dry run, not a logged day")
        pins.require_registered(record["code"]["pinned_sha"], manifest)
        records.append(record)
    return records


def _final_test():
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("live_score_final_test", REPO / "scripts" / "final_test_preregistration.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The final test's CRPS cell (#220, #221): its pass rule, labels and settings.
final_test = _final_test()
crps_verdict = final_test.crps_verdict
crps_result = final_test.crps_result


def now_utc() -> datetime:
    """The wall clock, in UTC. Module-level so that tests patch it (never a flag or environment variable)."""

    return datetime.now(timezone.utc)


def today_new_york() -> date:
    """Today's date in America/New_York, the calendar the scoring dates are fixed in."""

    return now_utc().astimezone(EASTERN).date()


def require_clock(day: date, *, override: bool = False) -> dict:
    """Refuse a scoring date that has not yet come in New York (#257, review finding 4).

    `require_scoring_date` checks the argument against the pre-registered list;
    this checks it against the clock, so a synthetic record cannot be scored on
    2026-10-06 by naming 2027-04-01. `override` lets a run proceed anyway, and
    only if the output records that it did.

    Returns the clock block the result carries: when it was read (UTC), today's
    New York date and whether the override was used.

    Raises:
        LookAheadError: if today in New York is before `day` and `override` is false.
    """

    checked = now_utc()
    today = checked.astimezone(EASTERN).date()
    early = today < day
    if early and not override:
        raise LookAheadError(
            f"{day} has not come: today in America/New_York is {today}, and the live record "
            f"is scored on its scoring date or after it (#257)"
        )
    return {"checked_at_utc": checked.isoformat(), "today_new_york": today.isoformat(),
            "override": early}


def is_scoring_date(day: date) -> bool:
    if day in FIRST_SCORING_DATES:
        return True
    return day.year >= 2028 and (day.month, day.day) == (10, 1)


def require_scoring_date(day: date) -> None:
    if not is_scoring_date(day):
        raise ValueError(
            f"{day} is not a scoring date: the live record is scored on 2027-04-01, "
            f"2027-10-01 and every 1 October after, and on no other date (#215)"
        )


def _require_scored_days_unlocked(days, *, where: str) -> None:
    """Refuse a scored day in a tier `metadata/lockbox.json` has not opened (#277).

    Raises:
        LookAheadError: naming the tier and the first offending day.
    """

    require_unlocked([date.fromisoformat(str(day)) for day in days], where=where)


def headline_status(day: date, *, days: int, previous) -> str:
    """`inconclusive`, `headline_verdict` or `update`, for the primary result on `day`.

    `previous` is the earlier scoring results, each with its `date` and
    `headline_status`. The verdict is fixed once, at the first date whose
    primary cell scores any day (CRPS has no minimum event count); every result
    after it is an update, whatever it scores.

    Raises:
        ValueError: if a previous result is dated on or after `day`.
    """

    for result in previous:
        if date.fromisoformat(result["date"]) >= day:
            raise ValueError(
                f"a previous result is dated {result['date']}, not before {day}"
            )
    if any(result["headline_status"] in ("headline_verdict", "update") for result in previous):
        return "update"
    if days > 0:
        return "headline_verdict"
    return "inconclusive"


def crps_from_record(record, side: str, h: int, outcome: float) -> float:
    """One day's CRPS for `side` at horizon `h`, from the day's file alone.

    Raises:
        ValueError: if the file carries no such distribution.
    """

    block = record.get("distributions") or {}
    try:
        levels = block["levels"]
        quantiles = block[side]["quantiles_bps"][str(h)]
    except (KeyError, TypeError) as error:
        raise ValueError(f"the file carries no {side} distribution at h={h}") from error
    return crps_from_quantiles(levels, quantiles, outcome)


def integral_crps_from_record(record, side: str, h: int, outcome: float) -> float:
    """`crps_from_record`'s companion: the trapezoid-weighted integral (#259), reported only."""

    block = record.get("distributions") or {}
    try:
        levels = block["levels"]
        quantiles = block[side]["quantiles_bps"][str(h)]
    except (KeyError, TypeError) as error:
        raise ValueError(f"the file carries no {side} distribution at h={h}") from error
    return crps_trapezoid_from_quantiles(levels, quantiles, outcome)


def _regime(splits, when: date) -> str:
    """The regime of `when`: the declared one, else its calendar year from 2027, else "undeclared"."""

    try:
        return splits.regime(when)
    except ValueError:
        return str(when.year) if when.year >= FIRST_YEAR_REGIME else "undeclared"


def _small_cell(differences, positions):
    """The cell's entry when it has fewer than `MINIMUM_CELL_DAYS` days, else None.

    The mean is reported; the interval is not, so a small cell never gets one
    by the luck of the bootstrap seed.
    """

    if len(positions) >= MINIMUM_CELL_DAYS:
        return None
    entry = {"days": len(positions), "note": TOO_FEW_DAYS, "minimum_days": MINIMUM_CELL_DAYS}
    if positions:
        entry["mean"] = sum(differences[k] for k in positions) / len(positions)
    return entry


def score_crps(records, rows, splits, day: date) -> dict:
    """The CRPS cells, cumulatively over `records`: h = 1 primary, h = 2 to 5 reported only."""

    by_date = {row.date: row for row in rows}
    out = {}
    for h in HORIZONS:
        days, published, persistence, regimes, types = [], [], [], [], []
        integral_published, integral_persistence = [], []
        for record in records:
            when = date.fromisoformat(record["targets"][h - 1]["target_date"])
            if when >= day or when not in by_date:
                continue
            row = by_date[when]
            days.append(when)
            published.append(crps_from_record(record, "published", h, row.spread_bps))
            persistence.append(crps_from_record(record, "persistence", h, row.spread_bps))
            integral_published.append(integral_crps_from_record(record, "published", h, row.spread_bps))
            integral_persistence.append(integral_crps_from_record(record, "persistence", h, row.spread_bps))
            regimes.append(_regime(splits, when))
            types.append(splits.reporting_day_type(when, row.values))
        _require_scored_days_unlocked(days, where=f"live_score.score_crps h={h}")
        primary = h == HEADLINE["horizon"]
        cell = {"days": len(days), "role": "primary" if primary else "reported only",
                "first": days[0].isoformat() if days else None,
                "last": days[-1].isoformat() if days else None,
                "sign_convention": CRPS_SIGN}
        if not primary:
            cell["verdict_label"] = NOT_EVIDENCE
            cell["design"] = INTERIOR_DESIGN
        if not days:
            cell["result" if primary else "note"] = "inconclusive" if primary else "no scored day"
            out[f"crps/h{h}"] = cell
            continue
        differences = [a - b for a, b in zip(persistence, published)]
        seed = _seed_from((str(day), "crps", str(h)))
        block = final_test.CRPS_BLOCK_LENGTH + (h - 1)

        def mean_of(indices):
            return sum(differences[i] for i in indices) / len(indices)

        def interval(block_length):
            lower, upper = stationary_bootstrap_interval(
                mean_of, len(differences), block_length=block_length, seed=seed,
                replications=onset.REPLICATIONS, level=onset.LEVEL,
            )
            return {"lower": lower, "upper": upper, "level": onset.LEVEL,
                    "method": "stationary_bootstrap", "block_length": block_length,
                    "replications": onset.REPLICATIONS, "seed": seed}

        cell.update(
            {
                "crps_persistence_bps": sum(persistence) / len(days),
                "crps_published_bps": sum(published) / len(days),
                "mean_difference_bps": mean_of(range(len(days))),
                "interval": interval(block),
                "sensitivity_interval": interval(final_test.CRPS_SENSITIVITY_BLOCK_LENGTH),
            }
        )
        # Reported only (#259): the same paired difference, scored by the trapezoid-weighted
        # integral. It never reaches the verdict, the result or the primary cell.
        integral = [a - b for a, b in zip(integral_persistence, integral_published)]

        def integral_mean(indices):
            return sum(integral[i] for i in indices) / len(indices)

        lower, upper = stationary_bootstrap_interval(
            integral_mean, len(integral), block_length=block, seed=seed,
            replications=onset.REPLICATIONS, level=onset.LEVEL,
        )
        cell["integral_sensitivity"] = {
            "role": "reported only",
            "rule": "trapezoid-weighted CRPS integral (`metrics.crps_trapezoid_from_quantiles`)",
            "crps_integral_persistence_bps": sum(integral_persistence) / len(days),
            "crps_integral_published_bps": sum(integral_published) / len(days),
            "mean_difference_bps": integral_mean(range(len(days))),
            "interval": {"lower": lower, "upper": upper, "level": onset.LEVEL,
                         "method": "stationary_bootstrap", "block_length": block,
                         "replications": onset.REPLICATIONS, "seed": seed},
        }
        every = list(range(len(days)))
        for label, keys in (("by_regime", regimes), ("by_day_type", types)):
            cell[label] = {}
            for key in sorted(set(keys)):
                positions = [k for k in every if keys[k] == key]
                cell[label][key] = _small_cell(differences, positions) or onset.paired_difference(
                    persistence, published, positions, block_length=block,
                    seed=_seed_from((str(day), "crps", str(h), key)))
        if primary:
            # A reported-only cell (h = 2 to 5) carries no verdict: it cannot pass or fail, and
            # its label says it is not evidence (#267, second review finding 19).
            cell["verdict"] = crps_verdict(cell)
            cell["result"] = crps_result(cell["verdict"])
        out[f"crps/h{h}"] = cell
    return out


def _outcome(target, cell_name, spread):
    if cell_name == "leap":
        return 1 if onset.whole_bp(spread) - target["anchor_spread_bp"] > target["leap_threshold_bp"] else 0
    return 1 if exceeds_bp(spread, float(cell_name[1:-2])) else 0


def _paired(baseline, model, positions, h, *parts):
    return onset.paired_difference(
        baseline, model, positions, block_length=h + 1,
        seed=_seed_from(tuple(str(part) for part in parts)),
    )


def _opening():
    """`scripts/final_test_opening.py`, loaded once: the final test's group scoring (#363)."""

    global _OPENING
    if _OPENING is None:
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_score_final_opening", REPO / "scripts" / "final_test_opening.py")
        _OPENING = module_from_spec(spec)
        spec.loader.exec_module(_OPENING)
    return _OPENING


_OPENING = None


def _event_groups(cell_name, h, dates, rows, splits, day, cache):
    """The final test's group for a Brier cell, as positions into `dates` (#363).

    The leap cell gets the leap-onset group (`onset.leap_onset_group`); the +5 bp and +10 bp
    cells get the at-risk group (`onset.day_groups`). Both are read from the panel rows before
    `day` only: a group never reads a day the scoring date has not opened.
    """

    before = [row for row in rows if row.date < day]
    if cell_name == "leap":
        if h not in cache:
            rule = InformationRule(json.loads(final_test.REGISTRY.read_text()), ("spread_bps",),
                                   decision_time=final_test.DECISION, horizon=h)
            cache[h] = onset.LeapTargets(before, rule, final_test.leap_jump_bp(h))
        return {onset.GROUP_LEAP_ONSET: onset.leap_onset_group(cache[h], dates)}
    return {onset.GROUP_ONSET: onset.day_groups(before, dates, splits)[onset.GROUP_ONSET]}


def _paired_cell(losses, baseline, name, positions, regimes, types, h, day, cell_name, tail=()):
    """The model paired against one baseline over `positions`: all days, by regime, by day type.

    `tail` is added to every seed after the baseline, so a group's cells draw their own.
    """

    paired = {"all_days": _paired(losses[baseline], losses[name], positions, h, day, cell_name, h, name,
                                  baseline, *tail)}
    gaps = [x - y for x, y in zip(losses[baseline], losses[name])]
    for label, keys in (("by_regime", regimes), ("by_day_type", types)):
        paired[label] = {}
        for key in sorted({keys[k] for k in positions}):
            part = [k for k in positions if keys[k] == key]
            paired[label][key] = _small_cell(gaps, part) or _paired(
                losses[baseline], losses[name], part, h, day, cell_name, h, name, baseline, *tail, key)
    return paired


def _group_cell(group, positions, outcomes, losses, columns, models, baselines, regimes, types, h, day,
                cell_name):
    """One final-test group inside a Brier cell: its Brier, paired cells and false-alarm level."""

    events = sum(outcomes[k] for k in positions)
    cell = {"days": len(positions), "events": events, "role": "reported only"}
    if not positions:
        cell["result"] = "inconclusive"
        cell["reason"] = "no days in the group"
        return cell
    cell["false_alarm_level"] = _opening().false_alarm_level(group, positions, outcomes, columns)
    if events < onset.MINIMUM_EVENTS:
        cell["result"] = "inconclusive"
        cell["reason"] = f"{events} events, below the minimum of {onset.MINIMUM_EVENTS}"
        return cell
    cell["models"] = {}
    for name in models:
        entry = {"brier": sum(losses[name][k] for k in positions) / len(positions), "paired": {}}
        for b in baselines:
            paired = _paired_cell(losses, b, name, positions, regimes, types, h, day, cell_name,
                                  tail=(group,))
            paired["all_days"]["label"] = _opening().label(paired["all_days"], events)
            entry["paired"][b] = paired
        cell["models"][name] = entry
    cell["baseline_brier"] = {b: sum(losses[b][k] for k in positions) / len(positions) for b in baselines}
    return cell


def score(records, rows, splits, day: date) -> dict:
    """Every Brier cell, cumulatively over `records`, on the outcomes in `rows`: reported only.

    Each cell also carries the final test's group for it, under `groups` (#363).
    """

    by_date = {row.date: row for row in rows}
    leap_targets = {}
    out = {"cells": {}}
    for cell_name, baselines in BASELINES.items():
        for h in HORIZONS:
            days, outcomes, model, bench, regimes, types = [], [], {}, {b: [] for b in baselines}, [], []
            for record in records:
                target = record["targets"][h - 1]
                when = date.fromisoformat(target["target_date"])
                if when >= day or when not in by_date:
                    continue
                row = by_date[when]
                days.append(when.isoformat())
                outcomes.append(_outcome(target, cell_name, row.spread_bps))
                for name, entry in record["models"].items():
                    model.setdefault(name, []).append(entry["forecasts"][str(h)][cell_name])
                for name in baselines:
                    bench[name].append(record["baselines"][name]["forecasts"][str(h)][cell_name])
                regimes.append(_regime(splits, when))
                types.append(splits.reporting_day_type(when, row.values))
            _require_scored_days_unlocked(days, where=f"live_score.score {cell_name} h={h}")
            events = sum(outcomes)
            cell = {"days": len(days), "events": events, "first": days[0] if days else None,
                    "last": days[-1] if days else None, "models": {}, "role": "reported only"}
            groups = _event_groups(cell_name, h, [date.fromisoformat(d) for d in days], rows, splits, day,
                                   leap_targets)
            losses = {name: [(p - y) ** 2 for p, y in zip(column, outcomes)]
                      for name, column in {**model, **bench}.items()}
            columns = {**model, **bench}
            cell["groups"] = {group: _group_cell(group, positions, outcomes, losses, columns, list(model),
                                                 baselines, regimes, types, h, day, cell_name)
                              for group, positions in groups.items()}
            if events < onset.MINIMUM_EVENTS:
                cell["result"] = "inconclusive"
                cell["reason"] = f"{events} events, below the minimum of {onset.MINIMUM_EVENTS}"
                out["cells"][f"{cell_name}/h{h}"] = cell
                continue
            every = list(range(len(days)))
            for name in model:
                entry = {"brier": sum(losses[name]) / len(days), "paired": {}}
                for b in baselines:
                    entry["paired"][b] = _paired_cell(losses, b, name, every, regimes, types, h, day,
                                                      cell_name)
                cell["models"][name] = entry
            cell["baseline_brier"] = {b: sum(losses[b]) / len(days) for b in baselines}
            out["cells"][f"{cell_name}/h{h}"] = cell
    return out


def skipped_records(records, rows, day: date) -> list:
    """Every (record, horizon) the cells did not score, with the reason: nothing is skipped silently (#257).

    A record's horizon is scored when its target day is before `day` and in the
    outcome panel (`score_crps`, `score`). Any other is listed here.
    """

    by_date = {row.date for row in rows}
    out = []
    for record in records:
        for target in record["targets"]:
            when = date.fromisoformat(target["target_date"])
            if when >= day:
                reason = NOT_YET_DUE
            elif when in by_date:
                continue
            else:
                reason = NO_OUTCOME
            out.append({"decision_day": record["decision_day"], "horizon": target["horizon"],
                        "target_date": when.isoformat(), "reason": reason})
    return out


def _code_sha() -> str:
    done = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_provenance(*, started_at: datetime, panel: Path, argv, panel_provenance, record_digests,
                     previous) -> dict:
    """What produced a result: when, from which bytes, by which command and code (#257, finding 4).

    `panel_provenance` is the sidecar `scripts/live_raw.py build-panel` writes
    beside the outcome panel: the command that built it and the archived inputs
    it was built from. `record_digests` are the live records' SHA-256s as
    verified; `previous` are the earlier results' files, linked by digest.
    """

    previous_scores = []
    for path in previous:
        data = Path(path).read_bytes()
        previous_scores.append({"date": json.loads(data)["date"], "sha256": _sha256_bytes(data)})
    return {
        "started_at_utc": started_at.astimezone(timezone.utc).isoformat(),
        "panel_sha256": _sha256_bytes(Path(panel).read_bytes()),
        "panel_build_command": panel_provenance["build_command"],
        "panel_inputs": panel_provenance.get("inputs", []),
        "scoring_command": shlex.join(str(part) for part in argv),
        "code_sha": _code_sha(),
        "dependency_lock_sha256": _sha256_bytes(LOCK.read_bytes()),
        "python_version": sys.version,
        "live_records": list(record_digests),
        "previous_scores": previous_scores,
    }


# -- the blind gap (#235) ------------------------------------------------------


def require_gap_scoring(day: date) -> None:
    """Refuse to score a gap day except on the first scoring date.

    The gap's days are scored through `score_crps` and `score`, so
    `lockbox.require_unlocked` guards each of them like any other scored day.

    Raises:
        ValueError: on any date but `GAP_SCORING_DATE`.
    """

    if day != GAP_SCORING_DATE:
        raise ValueError(
            f"the blind gap is scored once, on {GAP_SCORING_DATE}, not on {day} (#235)"
        )


def first_live_targets(record) -> dict:
    """The first logged day's target day at each horizon: the gap ends before them."""

    if record.get("decision_day") != FIRST_LIVE_DAY.isoformat():
        raise ValueError(
            f"the gap is bounded by the record for {FIRST_LIVE_DAY}, not "
            f"{record.get('decision_day')}"
        )
    return {target["horizon"]: date.fromisoformat(target["target_date"])
            for target in record["targets"]}


def gap_target_days(h: int, first_targets, live=None) -> list:
    """The gap at horizon `h`: decision days after the panel end, before the first live target.

    `live` is the `live_record` module whose calendar is used: main's by default,
    the pinned tree's for `pinned_gap_days`.
    """

    live = live or _live()
    out, current = [], live.PANEL_END
    while True:
        current = live.next_decision_days(current, 1)[0]
        if current >= first_targets[h]:
            return out
        out.append(current)


def gap_decision_days(first_targets) -> dict:
    """Each decision day whose forecast reaches a gap day, with the horizons it reaches one at."""

    live = _live()
    out = {}
    for h in HORIZONS:
        for target in gap_target_days(h, first_targets):
            day = target
            for _ in range(h):
                day = live.previous_decision_day(day)
            out.setdefault(day, []).append(h)
    return {day: tuple(horizons) for day, horizons in sorted(out.items())}


def validate_gap_record(record) -> None:
    """A reconstructed gap forecast's schema. Raises `ValueError` naming what is wrong.

    It is a live record's schema plus `reconstruction`, which carries
    `GAP_LABEL` verbatim, for a decision day before `FIRST_LIVE_DAY`. The extra
    key is why `live_record.validate_record` refuses it: a gap record is never
    a live record.
    """

    live = _live()
    keys = set(live.RECORD_KEYS) | {"reconstruction"}
    if not isinstance(record, dict) or set(record) != keys:
        raise ValueError(f"a gap record holds exactly {sorted(keys)}")
    block = record["reconstruction"]
    if not isinstance(block, dict) or block.get("label") != GAP_LABEL:
        raise ValueError(f"reconstruction.label must be, verbatim: {GAP_LABEL}")
    if block.get("scoring_date") != GAP_SCORING_DATE.isoformat():
        raise ValueError(f"reconstruction.scoring_date must be {GAP_SCORING_DATE}")
    datetime.fromisoformat(block.get("fetched_at") or "")
    if record["record_version"] != live.RECORD_VERSION:
        raise ValueError(f"record_version must be {live.RECORD_VERSION}")
    day = date.fromisoformat(record["decision_day"])
    if day >= FIRST_LIVE_DAY:
        raise ValueError(f"{day} is a live-record day, never a gap record's")
    datetime.fromisoformat(record["decision_instant"])
    for key in ("sha", "pinned_sha"):
        if not isinstance(record["code"].get(key), str) or len(record["code"][key]) != 40:
            raise ValueError(f"code.{key} must be a full commit SHA")
    inputs = record["inputs"]
    if not inputs.get("snapshots"):
        raise ValueError("inputs.snapshots is empty")
    for key in ("build_cutoff", "panel_sha256", "panel_last_date"):
        if not inputs.get(key):
            raise ValueError(f"inputs.{key} is missing")
    if [target.get("horizon") for target in record["targets"]] != list(HORIZONS):
        raise ValueError(f"targets must hold horizons {list(HORIZONS)} in order")
    for target in record["targets"]:
        if date.fromisoformat(target["target_date"]) <= day:
            raise ValueError("a target day falls after its decision day")
        if not isinstance(target.get("anchor_spread_bp"), int):
            raise ValueError("targets.anchor_spread_bp must be whole basis points")
    if set(record["models"]) != {model["name"] for model in live.MODELS}:
        raise ValueError(f"models must hold exactly {[model['name'] for model in live.MODELS]}")
    for name, model in record["models"].items():
        live._forecast_block(model.get("forecasts"), live.TARGET_NAMES, f"models.{name}.forecasts")
    if set(record["baselines"]) != set(live.BASELINE_NAMES):
        raise ValueError(f"baselines must hold exactly {sorted(live.BASELINE_NAMES)}")
    for name, targets in live.BASELINE_NAMES.items():
        live._forecast_block(record["baselines"][name].get("forecasts"), targets,
                             f"baselines.{name}.forecasts")
    live._validate_distributions(record["distributions"])


def _as_gap_cell(cell) -> dict:
    """A cell, reported only: no result, `GAP_LABEL` next to any verdict label."""

    cell = dict(cell)
    # A gap cell cannot pass or fail; one with too little to score says so.
    if cell.pop("result", None) == "inconclusive":
        cell["note"] = "inconclusive"
    cell["role"] = "reported only"
    cell["gap_label"] = GAP_LABEL
    return cell


def require_gap_boundaries_equal(pinned, first_targets) -> None:
    """The gap's days, as the pinned tree computes them, equal main's (#257, finding 39).

    The forecasts run at the pinned code, but the gap's day boundaries are
    computed here, from main's `live_record.py` and holiday table. `pinned` is
    each horizon's gap target days as the pinned tree's own `live_record.py`
    computes them (`pinned_gap_days`).

    Raises:
        ValueError: naming the horizon and the days that differ.
    """

    for h in HORIZONS:
        here = [day.isoformat() for day in gap_target_days(h, first_targets)]
        there = list(pinned.get(h, pinned.get(str(h), [])))
        if here != there:
            extra = sorted(set(here) ^ set(there))
            raise ValueError(
                f"the gap at h={h} differs between main and the pinned tree "
                f"({len(here)} days here, {len(there)} there; differing: {extra[:5]})"
            )


def pinned_gap_days(tree: Path, first_targets) -> dict:
    """Each horizon's gap target days, computed by the pinned tree's own `live_record.py`.

    Raises:
        ValueError: if `tree` is not a checkout of the pin in `metadata/live_pin.json`.
    """

    from importlib.util import module_from_spec, spec_from_file_location

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tree, capture_output=True, text=True)
    pin = _pins().load_manifest()["current"]
    if head.returncode != 0 or head.stdout.strip() != pin:
        raise ValueError(f"{tree} is not a checkout of the pinned code {pin}")
    spec = spec_from_file_location("live_record_pinned", Path(tree) / "scripts" / "live_record.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return {h: [day.isoformat() for day in gap_target_days(h, first_targets, live=module)]
            for h in HORIZONS}


def score_gap(records, first_live, rows, splits, day: date, *, override_clock: bool = False,
              pinned_days=None) -> dict:
    """The blind gap's cells (#235), scored once: every one reported only.

    `records` are the reconstructed gap forecasts (`validate_gap_record`);
    `first_live` is the first logged day's record, whose targets bound the gap.
    At each horizon only the records whose target day is in that horizon's gap
    are scored, with `score_crps` and `score`, the live cells' own functions
    and bootstrap settings. The reconstructed forecasts are carried in the
    output with their inputs' digests.

    The gap carries the same clock guard and skipped-record list as the live
    cells (#257, finding 39). `pinned_days` (`pinned_gap_days`), when given, is
    asserted equal to the boundaries computed here.

    Raises:
        ValueError: before anything is read, unless `require_gap_scoring`
            passes; on a malformed or repeated gap record, or boundaries that
            differ from the pinned tree's.
        LookAheadError: if `day` has not come in New York (`require_clock`), or on a
            gap day the lockbox has not opened.
    """

    clock_block = require_clock(day, override=override_clock)
    require_gap_scoring(day)
    bounds = first_live_targets(first_live)
    if pinned_days is not None:
        require_gap_boundaries_equal(pinned_days, bounds)
    for record in records:
        validate_gap_record(record)
    decided = [record["decision_day"] for record in records]
    if len(decided) != len(set(decided)):
        raise ValueError("a gap decision day is reconstructed twice")
    crps, cells, boundaries = {}, {}, {}
    for h in HORIZONS:
        days = gap_target_days(h, bounds)
        in_gap = set(days)
        chosen = [record for record in records
                  if date.fromisoformat(record["targets"][h - 1]["target_date"]) in in_gap]
        reached = {date.fromisoformat(record["targets"][h - 1]["target_date"]) for record in chosen}
        boundaries[str(h)] = {
            "first": days[0].isoformat(), "last": days[-1].isoformat(), "days": len(days),
            "first_live_target": bounds[h].isoformat(),
            "not_reconstructed": sorted(day.isoformat() for day in in_gap - reached),
        }
        crps[f"crps/h{h}"] = _as_gap_cell(score_crps(chosen, rows, splits, day)[f"crps/h{h}"])
        for name, cell in score(chosen, rows, splits, day)["cells"].items():
            if name.endswith(f"/h{h}"):
                cells[name] = _as_gap_cell(cell)
    skipped = []
    for h in HORIZONS:
        in_gap = set(gap_target_days(h, bounds))
        chosen = [r for r in records
                  if date.fromisoformat(r["targets"][h - 1]["target_date"]) in in_gap]
        skipped += [entry for entry in skipped_records(chosen, rows, day) if entry["horizon"] == h]
    return {
        "directive": "#235",
        "label": GAP_LABEL,
        "role": "reported only",
        "clock": clock_block,
        "boundaries_checked_against_pinned_tree": pinned_days is not None,
        "skipped_records": skipped,
        "boundaries": boundaries,
        "crps": crps,
        "cells": cells,
        "forecasts": sorted(records, key=lambda record: record["decision_day"]),
    }


# -- pressure model v2, logged alongside v1 (#245) -------------------------------

#: v2's own block: separate from v1's cells, and it never enters v1's verdict.
V2_LABEL = ("pressure model v2 (#244), logged alongside the unchanged v1 from its first logged day: its "
            "own blind record. v2 was chosen on 2018-2025, after #243, so only these logged days are "
            "evidence for it. This block never enters v1's verdict.")
V2_CRPS_SIGN = ("paired = CRPS(persistence) - CRPS(v2) per day; a positive mean favours v2")
V2_VS_V1_SIGN = ("paired = CRPS(v1 published) - CRPS(v2) per day, on the days both are logged; a positive "
                 "mean favours v2; reported only")
V2_SIDE = "published_v2"
V2_HORIZON = 1
V2_HORIZON_KEY = str(V2_HORIZON)


def v2_logged(record) -> bool:
    """Whether `record` carries v2's distribution at h = 1."""

    try:
        return V2_HORIZON_KEY in record["distributions"][V2_SIDE]["quantiles_bps"]
    except (KeyError, TypeError):
        return False



def v2_crps(record, outcome: float) -> float:
    """One day's CRPS for v2 at h = 1, from the day's file alone.

    Raises:
        ValueError: if the day was not logged with v2: v2 is never scored on a day it was not logged.
    """

    if not v2_logged(record):
        raise ValueError(
            f"{record.get('decision_day')} was not logged with pressure model v2: v2 is scored only on "
            f"the days it was logged (#245)"
        )
    return crps_from_record(record, V2_SIDE, V2_HORIZON, outcome)


def _paired_crps_cell(days, benchmark, model, regimes, types, day, *, seed_parts, sign, role, verdict: bool):
    """A CRPS cell paired `benchmark - model` per day, with `score_crps`'s interval, splits and rule."""

    h = V2_HORIZON
    cell = {"days": len(days), "role": role, "first": days[0].isoformat() if days else None,
            "last": days[-1].isoformat() if days else None, "sign_convention": sign}
    if not days:
        cell["result" if verdict else "note"] = "inconclusive" if verdict else "no scored day"
        return cell
    differences = [a - b for a, b in zip(benchmark, model)]
    seed = _seed_from((str(day), *seed_parts))
    block = final_test.CRPS_BLOCK_LENGTH + (h - 1)

    def mean_of(indices):
        return sum(differences[i] for i in indices) / len(indices)

    def interval(block_length):
        lower, upper = stationary_bootstrap_interval(
            mean_of, len(differences), block_length=block_length, seed=seed,
            replications=onset.REPLICATIONS, level=onset.LEVEL,
        )
        return {"lower": lower, "upper": upper, "level": onset.LEVEL,
                "method": "stationary_bootstrap", "block_length": block_length,
                "replications": onset.REPLICATIONS, "seed": seed}

    cell.update({
        "crps_benchmark_bps": sum(benchmark) / len(days),
        "crps_model_bps": sum(model) / len(days),
        "mean_difference_bps": mean_of(range(len(days))),
        "interval": interval(block),
        "sensitivity_interval": interval(final_test.CRPS_SENSITIVITY_BLOCK_LENGTH),
    })
    every = list(range(len(days)))
    for label, keys in (("by_regime", regimes), ("by_day_type", types)):
        cell[label] = {}
        for key in sorted(set(keys)):
            positions = [k for k in every if keys[k] == key]
            cell[label][key] = _small_cell(differences, positions) or onset.paired_difference(
                benchmark, model, positions, block_length=block,
                seed=_seed_from((str(day), *seed_parts, key)))
    if verdict:
        cell["verdict"] = crps_verdict(cell)
        cell["result"] = crps_result(cell["verdict"])
    return cell


def score_v2(records, rows, splits, day: date) -> dict:
    """Pressure model v2's block: its primary cell and its comparison with v1, over the days v2 was logged.

    * `crps/h1`: CRPS at h = 1, v2 against as-of persistence, over the logged days that carry v2 only,
      under the final test's pass rule, labels and bootstrap settings (`score_crps`'s).
    * `v2_vs_v1/h1`: v1's published distribution against v2, paired on those same days, reported only.

    A record without v2's block is not scored here (`v2_crps` refuses it). Nothing in this block is read
    by v1's cells, `primary_result` or `headline_status`.
    """

    by_date = {row.date: row for row in rows}
    logged = [record for record in records if v2_logged(record)]
    days, persistence, v2, v1, regimes, types = [], [], [], [], [], []
    for record in logged:
        when = date.fromisoformat(record["targets"][V2_HORIZON - 1]["target_date"])
        if when >= day or when not in by_date:
            continue
        row = by_date[when]
        days.append(when)
        persistence.append(crps_from_record(record, "persistence", V2_HORIZON, row.spread_bps))
        v2.append(v2_crps(record, row.spread_bps))
        v1.append(crps_from_record(record, "published", V2_HORIZON, row.spread_bps))
        regimes.append(_regime(splits, when))
        types.append(splits.reporting_day_type(when, row.values))
    _require_scored_days_unlocked(days, where="live_score.score_v2")
    primary = _paired_crps_cell(days, persistence, v2, regimes, types, day,
                                seed_parts=("v2", "crps", "1"), sign=V2_CRPS_SIGN, role="primary (v2)",
                                verdict=True)
    against = _paired_crps_cell(days, v1, v2, regimes, types, day,
                                seed_parts=("v2", "vs_v1", "1"), sign=V2_VS_V1_SIGN, role="reported only",
                                verdict=False)
    return {
        "label": V2_LABEL,
        "logged_days": [record["decision_day"] for record in logged],
        "first_logged_day": logged[0]["decision_day"] if logged else None,
        "crps/h1": primary,
        "v2_vs_v1/h1": against,
        "primary_result": primary.get("result"),
    }


def assemble(records, rows, splits, day: date, *, previous, gap_records=None,
             require_gap: bool = False, override_clock: bool = False, provenance=None,
             pinned_days=None) -> dict:
    """The scoring result: the live cells, the primary result, and the gap block apart.

    The primary result and its status are read off the live cells alone; the
    gap block (`score_gap`) is added beside them and never read back. The
    result carries the clock it was scored under, the records it did not score
    and why (`skipped_records`), and `provenance` when given (`build_provenance`).

    Raises:
        LookAheadError: before anything is computed, if `day` has not come in New York
            (`require_clock`) and `override_clock` is false.
        ValueError: if `require_gap` and no gap records are given.
    """

    clock_block = require_clock(day, override=override_clock)
    if require_gap and gap_records is None:
        raise ValueError(
            f"{day} scores the blind gap in the same run as its live cells (#235); "
            f"pass --gap-dir"
        )
    result = score(records, rows, splits, day)
    result["crps"] = score_crps(records, rows, splits, day)
    v2 = score_v2(records, rows, splits, day)
    headline = result["crps"][f"{HEADLINE['target']}/h{HEADLINE['horizon']}"]
    result.update(
        {
            "date": day.isoformat(),
            "directive": "#215",
            "logged_days": [record["decision_day"] for record in records],
            "sign_convention": SIGN,
            "minimum_events": onset.MINIMUM_EVENTS,
            "month_end_rule": MONTH_END_RULE,
            "headline": HEADLINE,
            "crps_sign_convention": CRPS_SIGN,
            "primary_result": headline.get("result"),
            "headline_status": headline_status(day, days=headline["days"], previous=previous),
            "clock": clock_block,
            "skipped_records": skipped_records(records, rows, day),
            "event_block_rule": EVENT_BLOCK_RULE,
            "event_seed": EVENT_SEED_RULE,
        }
    )
    if v2["first_logged_day"] is not None:
        # v2's block is separate and is added after v1's keys are all set; v1's keys are never read from it.
        v2["headline_status"] = headline_status(
            day, days=v2["crps/h1"]["days"],
            previous=[{"date": r["date"], "headline_status": r["v2"]["headline_status"]}
                      for r in previous if r.get("v2", {}).get("headline_status")])
        result["v2"] = v2
    if provenance is not None:
        result["provenance"] = provenance
    if gap_records is not None:
        first = [record for record in records if record["decision_day"] == FIRST_LIVE_DAY.isoformat()]
        if not first:
            raise ValueError(f"the live record has no file for {FIRST_LIVE_DAY}, which bounds the gap")
        result["gap"] = score_gap(gap_records, first[0], rows, splits, day,
                                  override_clock=override_clock, pinned_days=pinned_days)
    return result


#: The code the live scorer is (#282, ruling on #269 item 5), hashed the way the final test's
#: `_CRPS_SOURCE` is: each root and every top-level name of its file it mentions, so the
#: cells, the intervals, the minimum-cell rule, the regime and month-end splits and the gap
#: scoring are all covered. The clock, integrity, pin and provenance code scores nothing and is
#: left out (`tests/test_live_score_freeze.py` lists it and refuses a scoring function outside).
LIVE_SOURCE = (
    ("scripts/live_score.py", (
        "crps_from_record", "integral_crps_from_record", "headline_status", "_regime", "_small_cell",
        "score_crps", "_outcome", "_paired", "_event_groups", "_paired_cell", "_group_cell", "score",
        "skipped_records", "first_live_targets", "gap_target_days", "gap_decision_days",
        "validate_gap_record", "_as_gap_cell", "require_gap_boundaries_equal", "pinned_gap_days",
        "require_gap_scoring", "score_gap", "assemble", "_require_scored_days_unlocked",
        "EVENT_BLOCK_RULE", "EVENT_SEED_RULE", "NOT_EVIDENCE", "INTERIOR_DESIGN", "GAP_LABEL",
    )),
    ("scripts/final_test_preregistration.py", ("crps_verdict", "crps_result", "leap_jump_bp",
                                               "CRPS_BLOCK_LENGTH", "CRPS_SENSITIVITY_BLOCK_LENGTH")),
    ("scripts/final_test_opening.py", ("false_alarm_level", "label")),
    ("src/repo_model/metrics.py", ("crps_from_quantiles", "crps_trapezoid_from_quantiles",
                                   "stationary_bootstrap_interval")),
    ("src/repo_model/baseline.py", ("_seed_from",)),
    ("src/repo_model/onset.py", ("paired_difference", "whole_bp", "day_groups", "leap_onset_group",
                                 "LeapTargets", "MINIMUM_EVENTS", "REPLICATIONS", "LEVEL")),
    ("src/repo_model/data.py", ("exceeds_bp",)),
    ("src/repo_model/lockbox.py", ("require_unlocked",)),
    ("src/repo_model/evaluation_splits.py", ("SplitDeclaration", "MONTH_END_RULE", "DAY_TYPES",
                                             "DAY_TYPE_COLUMNS", "quarter_end_window_label",
                                             "load_split_declaration")),
)


def live_declaration() -> dict:
    """Everything the live scorer is: its scoring code and the constants it reads."""

    source = {}
    for path, names in LIVE_SOURCE:
        source[path] = {**source.get(path, {}), **final_test._top_level_source(path, names)}
    return {
        "constants": {
            "horizons": list(HORIZONS), "minimum_cell_days": MINIMUM_CELL_DAYS,
            "minimum_events": onset.MINIMUM_EVENTS, "replications": onset.REPLICATIONS,
            "level": onset.LEVEL, "first_year_regime": FIRST_YEAR_REGIME,
            "baselines": {cell: list(names) for cell, names in BASELINES.items()},
        },
        "source_sha256": source,
    }


def live_declaration_checksum() -> str:
    text = json.dumps(live_declaration(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _raw():
    """`scripts/live_raw.py`, loaded once."""

    global _RAW
    if _RAW is None:
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_raw", REPO / "scripts" / "live_raw.py")
        _RAW = module_from_spec(spec)
        spec.loader.exec_module(_RAW)
    return _RAW


_RAW = None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True)
    parser.add_argument("--live-dir", required=True, type=Path)
    parser.add_argument("--digests", type=Path, default=None,
                        help="the #225 digest comments, one JSON object per line (#254)")
    parser.add_argument("--panel", required=True, type=Path,
                        help="the outcome panel, built by `scripts/live_raw.py build-panel`")
    parser.add_argument("--archive-dir", required=True, type=Path,
                        help="a checkout of the `live-raw` branch: the panel's inputs must be in it (#257)")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--previous", action="append", default=[], type=Path)
    parser.add_argument("--gap-dir", type=Path, default=None,
                        help="the reconstructed gap forecasts (scripts/live_gap.py); "
                             "the first scoring date only")
    parser.add_argument("--pinned-tree", type=Path, default=None,
                        help="a checkout of the pinned code: the gap's day boundaries are asserted "
                             "equal to its own (required with --gap-dir)")
    parser.add_argument("--override-clock", action="store_true",
                        help="score a date that has not come; recorded in the output (#257)")
    args = parser.parse_args(argv)
    started = now_utc()
    day = date.fromisoformat(args.date)
    require_scoring_date(day)
    clock_block = require_clock(day, override=args.override_clock)
    if args.output.exists():
        raise ValueError(f"{args.output} exists: a result is published as a new record")
    if args.gap_dir is not None:
        require_gap_scoring(day)
        if args.pinned_tree is None:
            raise ValueError("--gap-dir needs --pinned-tree: the gap's boundaries are checked against the pinned code")
    elif day == GAP_SCORING_DATE:
        raise ValueError(f"{day} scores the blind gap in the same run (#235): pass --gap-dir")

    records = load_records(args.live_dir, args.digests)
    panel_provenance = _raw().require_registered_panel(args.panel, args.archive_dir)
    integrity = _integrity()
    record_digests = [{"decision_day": path.stem, "sha256": integrity.file_sha256(path)}
                      for path in sorted((args.live_dir / "live").glob("*.json"))]
    archive_report = _raw().verify_records(args.archive_dir, args.live_dir)
    previous = [json.loads(path.read_text(encoding="utf-8")) for path in args.previous]
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    gap_records, pinned_days = None, None
    if args.gap_dir is not None:
        gap_records = [json.loads(path.read_text(encoding="utf-8"))
                       for path in sorted((args.gap_dir / "gap").glob("*.json"))]
        first = [record for record in records if record["decision_day"] == FIRST_LIVE_DAY.isoformat()]
        if not first:
            raise ValueError(f"the live record has no file for {FIRST_LIVE_DAY}, which bounds the gap")
        pinned_days = pinned_gap_days(args.pinned_tree, first_live_targets(first[0]))
    provenance = build_provenance(
        started_at=started, panel=args.panel,
        argv=["scripts/live_score.py", *(sys.argv[1:] if argv is None else argv)],
        panel_provenance=panel_provenance, record_digests=record_digests, previous=args.previous)
    provenance["raw_archive"] = archive_report
    result = assemble(records, rows, splits, day, previous=previous, gap_records=gap_records,
                      require_gap=day == GAP_SCORING_DATE, override_clock=args.override_clock,
                      provenance=provenance, pinned_days=pinned_days)
    result["clock"] = {**result["clock"], "first_read_at_utc": clock_block["checked_at_utc"]}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "headline_status": result["headline_status"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
