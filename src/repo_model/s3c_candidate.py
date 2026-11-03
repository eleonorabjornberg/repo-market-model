"""The candidate (s3c): (s3) capped at the Standing Repo Facility line from full allotment onwards (#1255; H5 step 3).

Eleonora, 26 October 2026 (chat, relayed; ledger item 61 on #1116): asked whether (s3) should carry the cap from full allotment onwards,
she answered "it should". (s3c) is (s3) of #1145, unchanged, with every quantile clipped at `min(q, line + 0 bp)` on a target day on
which the facility is at full allotment, and (s3) itself on every other day. The margin is 0 bp and is not tuned (`MARGIN_BP`; #1241 and
#1252 declared it primary).

**Full allotment** is read from the point-in-time register `metadata/policy_events.json` (`repo_model.policy_events`): the facility is at
full allotment on a target day when the `standing_repo` entry in force on that day, among the entries announced at or before the decision
instant, states no aggregate operation limit (`details["aggregate_operation_limit_bn"]` is `None`; the entry of 10 December 2025, effective
11 December, is the first). No date is written here. An entry that re-imposes a limit stops the cap on its effective date; one that removes
it again restarts it. An entry without the field is refused, never read as full allotment.

**Information set.** The entry used is the one `repo_model.srf_line` would use for the line: announced at or before the decision instant
(`repo_model.decision_instant`: 18:00 America/New_York on the decision day since #1312; the dated declarations of #1241 and #1252 keep the earlier instant they were made at) and effective on or before the target day, passed
through `policy_events.require_announced`, which raises `LookAheadError` for an entry announced later. The line itself is
`repo_model.srf_line.srf_line_bps`, unchanged, under the availability declaration of `metadata/srf_cap_1241.json`.

The cap is `repo_model.srf_line.cap_quantiles` with margin 0: monotone, so the quantile levels stay ordered. It fits nothing.

**Probability rule** (#1415; her ruling of 2 November 2026 on #1395). The candidate's probabilities and PIT read their law from
`repo_model.capped_law` with `rule="open_tail"` (b): the capped percentiles, an atom at the line, and the last 1% running on above it
(`PROBABILITY_RULE`, a frozen choice of the candidate, passed explicitly). `capped_law.DEFAULT_RULE` stays `"status_quo"`, so every published
script reproduces bit for bit. The quantiles, and so the grid CRPS and the upper-tail twCRPS, are the capped vector under every rule. Where no
cap applies (no line), and for the uncapped secondary (#1361, #1376), (b) and the status quo coincide.

Stdlib only.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Sequence

from . import capped_law as _law
from .policy_events import PolicyEntry, known_entries, require_announced
from .srf_line import _in_force, cap_quantiles, srf_line_bps

__all__ = ["MARGIN_BP", "PROBABILITY_RULE", "candidate_exceedance", "candidate_law", "candidate_pit_interval", "cap_line", "capped_quantiles",
           "full_allotment"]

#: The margin above the line, in bp. Declared primary by #1241 and #1252 and not tuned.
MARGIN_BP = 0.0
#: The candidate's probability rule, frozen (#1415): (b) of `capped_law.RULES`. Not `capped_law.DEFAULT_RULE`, which stays the published reading.
PROBABILITY_RULE = "open_tail"
_SRF = "standing_repo"
_LIMIT = "aggregate_operation_limit_bn"


def full_allotment(register: Sequence[PolicyEntry], as_of: datetime, target: date) -> bool:
    """Whether the facility is at full allotment on `target`, as known at the naive America/New_York instant `as_of`.

    False when no facility entry is effective on or before `target` among those announced by `as_of`, or the entry in force states an
    aggregate operation limit.

    Raises:
        ValueError: `as_of` is not a naive datetime; or the entry in force has no `aggregate_operation_limit_bn` field.
        LookAheadError: an entry read was announced after `as_of`.
    """

    known = known_entries(register, as_of)
    entry = _in_force(known, _SRF, target)
    if entry is None:
        return False
    require_announced(entry, as_of)
    if _LIMIT not in entry.details:
        raise ValueError(f"policy entry {entry.id} does not state {_LIMIT}: full allotment cannot be read")
    return entry.details[_LIMIT] is None


def cap_line(register: Sequence[PolicyEntry], as_of: datetime, target: date) -> Optional[float]:
    """The line the cap uses on `target`, in bp: the facility line at full allotment, `None` otherwise (no cap)."""

    if not full_allotment(register, as_of, target):
        return None
    return srf_line_bps(register, as_of, target)


def capped_quantiles(quantiles: Sequence[float], register: Sequence[PolicyEntry], as_of: datetime, target: date) -> List[float]:
    """(s3)'s quantiles for `target` as (s3c) forecasts them: clipped at the line at full allotment, a copy of them otherwise."""

    return cap_quantiles(quantiles, cap_line(register, as_of, target), MARGIN_BP)


def candidate_law(quantiles: Sequence[float], register: Sequence[PolicyEntry], as_of: datetime, target: date) -> _law.PiecewiseLaw:
    """The law the candidate emits for `target` from (s3)'s UNCAPPED quantiles: `capped_law.emitted_law` under `PROBABILITY_RULE` (b)."""

    return _law.emitted_law(quantiles, cap_line(register, as_of, target), PROBABILITY_RULE, MARGIN_BP)


def candidate_exceedance(quantiles: Sequence[float], register: Sequence[PolicyEntry], as_of: datetime, target: date, tau: float) -> float:
    """P(spread > tau) on whole basis points under the candidate's law, from (s3)'s uncapped quantiles."""

    return _law.exceedance(quantiles, cap_line(register, as_of, target), tau, PROBABILITY_RULE, MARGIN_BP)


def candidate_pit_interval(quantiles: Sequence[float], register: Sequence[PolicyEntry], as_of: datetime, target: date,
                           outcome_bp: float) -> tuple:
    """The PIT interval `(F(k - 0.5), F(k + 0.5))` of an outcome under the candidate's law (`capped_law.pit_interval`)."""

    return _law.pit_interval(candidate_law(quantiles, register, as_of, target), outcome_bp)
