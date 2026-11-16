"""The live forecast of the registered H5 candidate, (s3c-ann-net) (#1629; finding #1625; registration #1510).

The candidate is `sc_s3c_ann_net` (`docs/research/h5-candidate.json`): (s3) of the state-scaled calendar study, with its two settlement terms
read from the auction announcement and sized by net settlement (`s3c_announced.ANN_NET_ARM`), capped at the Standing Repo Facility line from
full allotment onwards with a margin of zero (`s3c_candidate`). This module makes its 23 quantiles at h = 1..5 for one decision day, for the live
record (`scripts/live_record.py`, protocol block, `prospective_log.REGISTERED_CANDIDATES`). It adds no model: it runs the frozen code's own walk.

**The same walk.** The frozen walks (`scripts/s3c_announced_settlement_1288.py`, `extra_walks`) call `spread_mr_state_calendar.walk` over every
decision day of the panel, refitting every `smr.REFIT_EVERY` decision days from the first day with enough history. A forecast on a day is
the walk's forecast on that day, so a live forecast that refitted on its own schedule would be another model. This module therefore walks every panel day up to the
decision day, as the frozen walk does, and takes the last day's forecast: the same refit days, the same fit, the same quantiles
(`tests/test_h5_live_candidate_1629.py` pins the equality quantile for quantile). The cap is read at the decision instant of the decision
day (`decision_instant.DECISION_TIME`, 18:00 New York), per target.

**The panel.** The live record's extended panel (`scripts/live_record.extend_panel`): real rows to the business day before the decision day,
then placeholder rows for the decision day and its targets, which carry the calendar columns and the scheduled settlement columns only.
No spread of a placeholder row is read: the as-of rule (`asof.InformationRule`, inside the walk) refuses it (`LookAheadError`).

**Inputs.** The auction records are the live run's own fetch of the Treasury's Fiscal Data, read at their announcement (12:00 on
`announcemt_date`, `metadata/settlement_announcement_dating.json`, `metadata/net_settlement.json`). Two inputs are tracked files, not fetched: the table of
announced IORB changes (`IORB_TABLE`) and the policy register (`metadata/policy_events.json`). The table is read against the panel (`require_iorb_table_current`): a
rate change the panel has seen and the table does not list is refused (`StaleReadError`), because it would be read as no change. The register's
staleness (a facility entry announced and not yet recorded) is not checked here and is listed as not checked in the pull request of #1629.

Stdlib only.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

from . import announced_iorb, net_settlement, policy_events, s3c_announced, s3c_candidate, s3c_net, settlement_dating
from . import spread_mr_state_calendar as sc
from .asof import StaleReadError
from .data import DailyObservation, next_business_day
from .decision_instant import DECISION_TIME
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import HORIZONS

__all__ = ["CANDIDATE_ID", "IORB_TABLE", "candidate_forecast", "require_iorb_table_current"]

REPO = Path(__file__).resolve().parents[2]
#: The id the live record logs the candidate under (`prospective_log.REGISTERED_CANDIDATES`; `docs/research/h5-candidate.json`). The walk's arm is
#: `s3c_announced.ANN_NET_ARM`, (s3-ann-net) by its own name: the cap of (s3c) is applied to its quantiles below, as the studies do.
CANDIDATE_ID = "sc_s3c_ann_net"
IORB_TABLE = REPO / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
DATING = REPO / "metadata" / "settlement_announcement_dating.json"
NET_DECLARATION = REPO / "metadata" / "net_settlement.json"


def require_iorb_table_current(real_rows: Sequence[DailyObservation], announcements: Sequence[announced_iorb.IorbAnnouncement]) -> None:
    """Refuse a table of announced IORB changes that does not hold the rate the panel observed on its last real row.

    The table is a tracked file: a change announced after its last row would be read as no change. The panel's `iorb` on the last real row is
    the rate in force that day, observed; the table's rate in force that day (the last row effective on or before it) must be the same.

    Raises:
        StaleReadError: the two rates differ, or the table has no row in force that day.
        ValueError: there is no real row, or its `iorb` is missing.
    """

    if not real_rows:
        raise ValueError("no real row to check the IORB table against")
    last = real_rows[-1]
    observed = last.values.get("iorb")
    if observed is None:
        raise ValueError(f"the panel's last real row ({last.date}) has no iorb to check the IORB table against")
    observed_bps = round(float(observed) * 100)
    in_force = [a for a in announcements if a.effective <= last.date]
    if not in_force:
        raise StaleReadError(f"the IORB table has no row in force on {last.date}")
    rate_bps = in_force[-1].rate_bps
    if rate_bps != observed_bps:
        raise StaleReadError(
            f"the IORB table reads {rate_bps} bp in force on {last.date}, the panel observed {observed_bps} bp: "
            f"a change is missing from {IORB_TABLE.name}"
        )


def candidate_forecast(
    extended: Sequence[DailyObservation],
    decision_day: date,
    *,
    registry: Mapping[str, Mapping[str, object]],
    splits: SplitDeclaration,
    auction_records: Sequence[Mapping[str, object]],
    iorb_table: Optional[Sequence[announced_iorb.IorbAnnouncement]] = None,
    register: Optional[Sequence[policy_events.PolicyEntry]] = None,
) -> Dict[int, List[float]]:
    """The candidate's 23 quantiles (bp) for each lead 1..5 of the decision on `decision_day`, `{h: [q_1, ..., q_23]}`.

    `extended` is the live record's panel (`live_record.extend_panel` at lead 5). `auction_records` are the Fiscal Data records of the run's
    own fetch. `iorb_table` and `register` default to the tracked files.

    Raises:
        ValueError: the panel does not end its real rows on the business day before `decision_day`, has no row for the day or its five targets,
            or the walk issued no forecast for the day.
        StaleReadError: the IORB table does not hold the rate the panel observed (`require_iorb_table_current`).
        LookAheadError: a read is after the decision instant (the as-of rule, `policy_events.require_announced`).
    """

    dates = [row.date for row in extended]
    if decision_day not in dates:
        raise ValueError(f"the panel has no row for the decision day {decision_day}")
    index = dates.index(decision_day)
    if index == 0 or next_business_day(dates[index - 1], 1) != decision_day:
        raise ValueError(f"the panel's last real row is not the business day before {decision_day}")
    if len(dates) < index + 1 + max(HORIZONS):
        raise ValueError(f"the panel does not carry the {max(HORIZONS)} target days after {decision_day}")
    iorb_table = announced_iorb.load_announcements(IORB_TABLE) if iorb_table is None else iorb_table
    require_iorb_table_current(extended[:index], iorb_table)
    register = policy_events.load_register() if register is None else register

    results = settlement_dating.auction_results(auction_records, settlement_dating.load_result_dating(DATING))
    auctions = net_settlement.auction_records(auction_records, net_settlement.load_declaration(NET_DECLARATION))
    panel = list(extended)
    walk = sc.walk(
        panel, dates[: index + 1],
        s3c_announced.AnnouncedTermTable(panel, iorb_table, results, decision_time=DECISION_TIME),
        s3c_net.constant_states(panel), (s3c_announced.ANN_NET_ARM,),
        sizes=s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=DECISION_TIME),
        registry=registry, decision_time=DECISION_TIME, splits=splits,
    )
    issued = walk.forecasts[s3c_announced.ANN_NET_ARM.name].get(decision_day)
    if issued is None:
        raise ValueError(f"the walk issued no forecast for {decision_day}")
    instant = datetime.combine(decision_day, DECISION_TIME)
    return {h: s3c_candidate.capped_quantiles(issued[h], register, instant, dates[index + h]) for h in HORIZONS}
