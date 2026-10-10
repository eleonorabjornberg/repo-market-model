"""A desk-standard diagnostic of information use (#481): when each input was truly public, and what the models cannot see.

A scratch measurement, not a record. It changes no model, declaration, panel column or published figure and writes
nothing into `docs/runs/`. It reads the published panel (`docs/pivot/next-session.md`), the tracked Treasury auction snapshot, the tracked
Daily Treasury Statement and reverse-repo snapshots, the registries
(`metadata/sources.json`, `metadata/sources_measurement.json`) and the judge's benchmark forecast files (for the scored
days only). No day after 2025-12-31 is read (`docs/decisions/lockbox.md`): every panel is cut at `LAST` on load.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/bench_hH.json   (H = 1..5)
    PYTHONPATH=src python3 scripts/desk_standard_diagnostic.py --panel PUB.csv \\
        --bench 'OUT/bench_h{h}.json' --output docs/pivot/evidence/desk-standard/desk_standard.json

Standard library plus the repository's own `repo_model` (stdlib-only outside `ml.py`). The primary sources the timeline
cites are saved, as text, under `docs/pivot/evidence/desk-standard/sources/` with the checksum of each page read.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, time, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import nowcast, pressure  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

LAST = date(2025, 12, 31)  # the last day read; the near-blind tier starts on 2026-01-01
HORIZONS = (1, 2, 3, 4, 5)
REFIT_EVERY = 21  # the judge's cut-off refit cadence (metadata/pressure_judge.json, cutoff_rule)
DECISION = time(16, 0)
AUCTIONS = REPO / "tests/fixtures/snapshots/funding_inputs/treasury_auctions/20260914T051023Z_722359ea9bc7.json"
REVERSE_REPO = REPO / "tests/fixtures/snapshots/on_rrp_inputs/nyfed_on_rrp"
PUBLISHED_DAILY = REPO / "docs/runs/published_distribution_daily_h1.json"
SPLITS = REPO / "metadata/evaluation_splits.json"
SOURCES = REPO / "metadata/sources.json"
SOURCES_MEASUREMENT = REPO / "metadata/sources_measurement.json"
NOWCAST_DECLARATION = REPO / "metadata/nowcast.json"
FRED_RRP = REPO / "tests/fixtures/snapshots/alfred-rrpontsyd/RRPONTSYD_2026-09-15.csv"
DTS = REPO / "tests/fixtures/snapshots/dts_inputs/treasury_dts_tga"


def dts_tga() -> dict:
    """{statement date: closing TGA balance, USD billions} from every tracked Daily Treasury Statement response, to `LAST`."""

    from repo_model import ingest

    out = {}
    for path in sorted(DTS.glob("*.json")):
        if path.name.endswith(".manifest.json"):
            continue
        for day, value in ingest._treasury_dts_tga_pairs(json.loads(path.read_text())):
            if day <= LAST:
                out[day] = value
    return out


def reverse_repo_by_date() -> dict:
    """{operation date: reverse repo accepted, USD billions} from the Desk's tracked operation results, to `LAST`.

    Every operation date, whenever its records were written: this is the balance the day's operation took, which is what
    a reserves identity needs; when it was public is a separate question (`nowcast.sameday_on_rrp`).
    """

    totals = defaultdict(float)
    for record in nowcast.load_operations(REVERSE_REPO):
        if record.get("operationType") != "Reverse Repo":
            continue
        day = date.fromisoformat(str(record["operationDate"]))
        if day <= LAST:
            totals[day] += float(record["totalAmtAccepted"]) / 1e9
    return dict(totals)


# -- the calendar --------------------------------------------------------------------------------------------------


class Calendar:
    """The panel's business days up to `LAST`, and the decision instant (16:00) read against them.

    A value public at `(day, clock)` is read by the first decision, at 16:00 on a panel day, at or after that
    instant: a value public at exactly 16:00 is read by that day's decision (the registry's own `<=` test), and one
    public at 16:30 by the next panel day's.
    """

    def __init__(self, days):
        self.days = sorted(days)
        self.position = {d: i for i, d in enumerate(self.days)}

    def decision_index(self, day: date, clock: time) -> int:
        """Index of the first panel day whose 16:00 decision is at or after `day` at `clock`."""

        at = bisect.bisect_left(self.days, day)
        if at < len(self.days) and self.days[at] == day and clock > DECISION:
            at += 1
        return at

    def on_or_after(self, day: date) -> int:
        return bisect.bisect_left(self.days, day)

    def add_business_days(self, day: date, count: int) -> date:
        """`count` panel days after the panel day `day` (the registry's `business_days` unit)."""

        return self.days[self.position[day] + count]


def _clock(text: str) -> time:
    hours, minutes = text.split(":")
    return time(int(hours), int(minutes))


# -- 1. the desk information timeline -------------------------------------------------------------------------------

#: What each input's primary source says, and the file under `evidence/desk-standard/sources/` that holds the page.
#: `lag` is `(count, unit)`; unit `business_days` counts panel days after the reference day, `calendar_days` calendar
#: days; `clock` is the earliest public time on that day. `status` says how firm the time is.
TRUTH = {
    "nyfed_sofr": dict(lag=(1, "business_days"), clock="08:00", status="stated",
                       source="nyfed_sofr_page", quote="the New York Fed publishes the SOFR on the New York Fed website at approximately 8:00 a.m. ET"),
    "nyfed_tgcr": dict(lag=(1, "business_days"), clock="08:00", status="stated (same publication as SOFR)",
                       source="nyfed_sofr_page", quote="published with SOFR at approximately 8:00 a.m. ET"),
    "nyfed_bgcr": dict(lag=(1, "business_days"), clock="08:00", status="stated (same publication as SOFR)",
                       source="nyfed_sofr_page", quote="published with SOFR at approximately 8:00 a.m. ET"),
    "nyfed_effr": dict(lag=(1, "business_days"), clock="09:00", status="stated",
                       source="nyfed_reference_rates_info", quote="The EFFR and the OBFR will be published at approximately 9:00 a.m. ET each business day"),
    "nyfed_on_rrp": dict(lag=(0, "business_days"), clock="15:00", status="inferred, not stated",
                         source="nyfed_repo_reverse_repo_operations",
                         quote="the page states no publication time; the Desk's records were last written on the operation date by 15:00 ET on 1985 of 1997 operation days (docs/pivot/nowcast-result.md, section 1)"),
    "nyfed_srf": dict(lag=(0, "business_days"), clock="15:00", status="inferred, not stated",
                      source="nyfed_repo_reverse_repo_operations",
                      quote="the page states no publication time; lastUpdated falls a median 0.7 minutes after the 13:45 close (metadata/sources_measurement.json, nyfed_repo_ops_sameday)"),
    "nyfed_fr2004": dict(lag=(6, "business_days"), clock="16:15", status="stated",
                         source="nyfed_primary_dealer_statistics", quote="Data are updated on Thursdays at approximately 4:15 p.m. with the previous week's statistics"),
    "h41_weekly": dict(lag=(1, "calendar_days"), clock="16:30", status="stated",
                       source="fed_h41_release_page", quote="These data are released each Thursday, generally at 4:30 p.m. The Wednesday level is therefore public the next day"),
    "frb_h8": dict(lag=(9, "calendar_days"), clock="16:15", status="stated (docs in metadata/sources.json, frb_h8.availability_provenance)",
                   source=None, quote="released each Friday, generally at 4:15 p.m.: the second Friday after the Wednesday"),
    "treasury_dts_tga": dict(lag=(1, "business_days"), clock="16:00", status="recorded in the registry; fiscaldata.treasury.gov was not reachable on 10 October 2026, so not re-read",
                             source=None, quote="the statement for a business day is published at 4:00 PM ET on the next business day (metadata/sources_measurement.json, availability_provenance)"),
    "treasury_bill_rates": dict(lag=(0, "business_days"), clock="16:30", status="stated (H.15 bulk file)",
                                source=None, quote="the quotes are obtained at or near 3:30 PM; the H.15 file posts at 16:30 (metadata/sources.json, treasury_bill_rates.availability_provenance)"),
}


def _ours_instant(calendar: Calendar, block: dict, ref: date):
    """`(day, clock)` at which a registry `release_lag` block makes the value for `ref` public, or None past the panel."""

    clock = _clock(block["available_time"])
    count = int(block["days"])
    if block["unit"] == "business_days":
        position = calendar.position[ref] + count
        return (calendar.days[position], clock) if position < len(calendar.days) else None
    return ref + timedelta(days=count), clock


def _truth_instant(calendar: Calendar, truth: dict, ref: date):
    count, unit = truth["lag"]
    clock = _clock(truth["clock"])
    if unit == "business_days":
        position = calendar.position[ref] + count
        return (calendar.days[position], clock) if position < len(calendar.days) else None
    release = ref + timedelta(days=count)
    # a release day that is not a panel day moves to the next panel day (a holiday shifts the Thursday print)
    at = calendar.on_or_after(release)
    return (calendar.days[at], clock) if at < len(calendar.days) else None


def timeline(calendar: Calendar, registry: dict, measurement: dict) -> list:
    """For each input with a stated or inferred earliest time: the declared and true first-readable decision, per reference day."""

    fred = registry["fred_macro_latest_vintage"]["field_release_lags"]
    wednesdays = [d for d in calendar.days if d.weekday() == 2]
    cases = [
        ("SOFR (daily)", "nyfed_sofr", registry["nyfed_sofr"]["release_lag"], calendar.days, "nyfed_sofr"),
        ("TGCR (daily)", "nyfed_tgcr", registry["nyfed_tgcr"]["release_lag"], calendar.days, "nyfed_tgcr"),
        ("BGCR (daily)", "nyfed_bgcr", registry["nyfed_bgcr"]["release_lag"], calendar.days, "nyfed_bgcr"),
        ("EFFR (daily)", "nyfed_effr", registry["nyfed_effr"]["release_lag"], calendar.days, "nyfed_effr"),
        ("ON RRP results (daily)", "nyfed_on_rrp", registry["nyfed_on_rrp"]["release_lag"], calendar.days, "nyfed_on_rrp"),
        ("Standing repo facility and repo operations (daily)", "nyfed_srf", registry["nyfed_srf"]["release_lag"], calendar.days, "nyfed_srf"),
        ("Primary dealer statistics (weekly)", "nyfed_fr2004", registry["nyfed_fr2004"]["release_lag"], wednesdays, "nyfed_fr2004"),
        ("H.4.1 reserves, WRESBAL (weekly)", "h41_weekly", fred["WRESBAL"], wednesdays, "h41_weekly"),
        ("H.4.1 TGA, WTREGEN (weekly)", "h41_weekly", fred["WTREGEN"], wednesdays, "h41_weekly"),
        ("H.4.1 reverse repo, WLRRAOL (weekly)", "h41_weekly", fred["WLRRAOL"], wednesdays, "h41_weekly"),
        ("Daily Treasury Statement, TGA (daily)", "treasury_dts_tga", measurement["treasury_dts_tga"]["release_lag"], calendar.days, "treasury_dts_tga"),
        ("Treasury bill rates (daily)", "treasury_bill_rates", registry["treasury_bill_rates"]["release_lag"], calendar.days, "treasury_bill_rates"),
    ]
    out = []
    for label, key, block, refs, truth_key in cases:
        truth = TRUTH[key]
        lateness = Counter()
        for ref in refs:
            ours = _ours_instant(calendar, block, ref)
            true = _truth_instant(calendar, truth, ref)
            if ours is None or true is None:
                continue
            lateness[calendar.decision_index(*ours) - calendar.decision_index(*true)] += 1
        out.append({
            "input": label,
            "ours": {"basis": block["basis"], "days": block["days"], "unit": block["unit"], "available_time": block["available_time"]},
            "true": {"lag": list(truth["lag"]), "clock": truth["clock"], "status": truth["status"], "source": truth["source"], "quote": truth["quote"]},
            "later_by_panel_days": dict(sorted(lateness.items())),
            "later_by_panel_days_most_common": max(lateness, key=lambda k: (lateness[k], -abs(k))) if lateness else None,
            "reference_days": sum(lateness.values()),
        })
    return out


# -- 2. settlements ------------------------------------------------------------------------------------------------


def _date(text):
    return date.fromisoformat(text) if text and text != "null" else None


def settlement_table(calendar: Calendar, auctions: list) -> dict:
    """Per settlement date: the announcement lead of its bill and coupon auctions, in panel days.

    `by_date[kind][issue_date] = (earliest announcement, latest announcement)`. The lead of a settlement date on
    the panel is the number of panel days from the announcement's own panel day (the first panel day on or after the
    announcement date) to the issue date.
    """

    by_date = {"bill": {}, "coupon": {}}
    auction_dates = {"bill": {}, "coupon": {}}
    skipped = 0
    for record in auctions:
        issue, announced = _date(record["issue_date"]), _date(record["announcemt_date"])
        if issue is None or announced is None or issue > LAST:
            continue
        if issue not in calendar.position:
            skipped += 1
            continue
        kind = "bill" if record["security_type"] == "Bill" else "coupon"
        early, late = by_date[kind].get(issue, (announced, announced))
        by_date[kind][issue] = (min(early, announced), max(late, announced))
        held = _date(record["auction_date"])
        if held is not None:
            first, last = auction_dates[kind].get(issue, (held, held))
            auction_dates[kind][issue] = (min(first, held), max(last, held))
    return {"by_date": by_date, "auction_dates": auction_dates, "issue_dates_off_the_panel": skipped}


def lead_days(calendar: Calendar, issue: date, announced: date) -> int:
    """Panel days between the announcement's panel day and the issue date (announcement read the day it is made)."""

    return calendar.position[issue] - calendar.on_or_after(announced)


def settlements(calendar: Calendar, auctions: list, onsets_by_h: dict, risk_by_h: dict, rows_by_date: dict) -> dict:
    table = settlement_table(calendar, auctions)
    by_date = table["by_date"]
    distribution = {}
    for kind, dated in by_date.items():
        early = Counter(lead_days(calendar, d, e) for d, (e, _) in dated.items())
        late = Counter(lead_days(calendar, d, l) for d, (_, l) in dated.items())
        auction = Counter(lead_days(calendar, d, held) for d, (held, _) in table["auction_dates"][kind].items())
        last_auction = Counter(lead_days(calendar, d, held) for d, (_, held) in table["auction_dates"][kind].items())
        distribution[kind] = {
            "settlement_dates": len(dated),
            "lead_of_the_first_auction": dict(sorted(auction.items())),
            "lead_of_the_last_auction": dict(sorted(last_auction.items())),
            "lead_of_the_earliest_announcement": dict(sorted(early.items())),
            "lead_of_the_last_announcement": dict(sorted(late.items())),
            "share_with_lead_at_least_2": sum(v for k, v in early.items() if k >= 2) / len(dated),
        }
    common = sorted(set.intersection(*(set(onsets_by_h[h]) for h in HORIZONS)))
    per_onset = []
    for onset in common + sorted(set(onsets_by_h[1]) - set(common)):
        entry = {"onset": onset.isoformat(), "scored_at_every_horizon": onset in common}
        values = rows_by_date[onset]
        entry["coupon_settlement_in_panel"] = float(values["treasury_settlement_coupons"] or 0) > 0
        entry["bill_settlement_in_panel"] = float(values["treasury_settlement_bills"] or 0) > 0
        for kind in ("bill", "coupon"):
            pair = by_date[kind].get(onset)
            entry[kind] = None if pair is None else {
                "first_announced": pair[0].isoformat(),
                "last_announced": pair[1].isoformat(),
                "lead_first": lead_days(calendar, onset, pair[0]),
                "lead_last": lead_days(calendar, onset, pair[1]),
            }
        per_onset.append(entry)

    def known(entry, kind, h, which, next_day):
        pair = entry[kind]
        if pair is None:
            return False
        lead = pair[which] - (1 if next_day else 0)
        return lead >= h

    counts = {}
    for h in HORIZONS:
        in_set = [e for e in per_onset if e["scored_at_every_horizon"]]
        cell = {"onsets": len(in_set), "declared": {"any": 0 if h > 1 else sum(1 for e in in_set if e["bill"] or e["coupon"]),
                                                      "bill": 0 if h > 1 else sum(1 for e in in_set if e["bill"]),
                                                      "coupon": 0 if h > 1 else sum(1 for e in in_set if e["coupon"])}}
        for label, which, next_day in (("announced_same_day", "lead_first", False), ("announced_next_day", "lead_first", True),
                                       ("amount_complete_same_day", "lead_last", False)):
            cell[label] = {
                "any": sum(1 for e in in_set if known(e, "bill", h, which, next_day) or known(e, "coupon", h, which, next_day)),
                "bill": sum(1 for e in in_set if known(e, "bill", h, which, next_day)),
                "coupon": sum(1 for e in in_set if known(e, "coupon", h, which, next_day)),
            }
        # coupon settlements that are not already a calendar risk date: the days a coupon clause would add at this lead
        added = [e["onset"] for e in in_set
                 if known(e, "coupon", h, "lead_first", False) and date.fromisoformat(e["onset"]) not in risk_by_h[h]]
        cell["coupon_settlements_that_are_not_risk_dates_at_this_horizon"] = added
        counts[str(h)] = cell
    return {"distribution": distribution, "per_onset": per_onset, "onsets_known_by_horizon": counts,
            "issue_dates_off_the_panel": table["issue_dates_off_the_panel"]}


# -- 3. reserves staleness and a daily proxy -----------------------------------------------------------------------


def weekly_series(calendar: Calendar, rows_by_date: dict, column: str) -> dict:
    """{Wednesday: level} for a weekly H.4.1 column carried on the panel: the value at its first row, dated to the Wednesday on or before."""

    out, last = {}, None
    for day in calendar.days:
        value = rows_by_date[day][column]
        if value is None:
            continue
        if last is None or value != last:
            wednesday = day - timedelta(days=(day.weekday() - 2) % 7)
            out[wednesday] = float(value)
            last = value
    return out


def latest_print(calendar: Calendar, series: dict, decision_index: int, instant_of) -> date | None:
    """The latest Wednesday whose print is readable at the decision on panel index `decision_index`."""

    best = None
    for wednesday in sorted(series):
        instant = instant_of(wednesday)
        if instant is None:
            continue
        if calendar.decision_index(*instant) <= decision_index:
            best = wednesday
        else:
            break
    return best


def reserves(calendar: Calendar, registry: dict, rows_by_date: dict, onsets: list) -> dict:
    block = registry["fred_macro_latest_vintage"]["field_release_lags"]["WRESBAL"]
    truth = TRUTH["h41_weekly"]
    series = weekly_series(calendar, rows_by_date, "reserve_balances")
    declared = lambda w: _ours_instant(calendar, block, w)
    true = lambda w: _truth_instant(calendar, truth, w)
    per_onset = []
    for onset in onsets:
        cells = {}
        for h in HORIZONS:
            position = calendar.position[onset] - h
            if position < 0:
                continue
            read = latest_print(calendar, series, position, declared)
            public = latest_print(calendar, series, position, true)
            if read is None or public is None:
                continue
            decision = calendar.days[position]
            cells[str(h)] = {
                "decision": decision.isoformat(),
                "declared_print": read.isoformat(),
                "public_print": public.isoformat(),
                "age_days_declared": (decision - read).days,
                "age_days_public": (decision - public).days,
                "newer_print_public_and_unread": public > read,
                "reserves_declared": series[read],
                "reserves_public": series[public],
                "unread_change_billions": series[public] - series[read],
            }
        per_onset.append({"onset": onset.isoformat(), "by_horizon": cells})
    summary = {}
    for h in HORIZONS:
        cells = [c["by_horizon"][str(h)] for c in per_onset if str(h) in c["by_horizon"]]
        changes = [abs(c["unread_change_billions"]) for c in cells]
        summary[str(h)] = {
            "onsets": len(cells),
            "age_days_declared": {"min": min(c["age_days_declared"] for c in cells), "median": statistics.median(c["age_days_declared"] for c in cells),
                                  "max": max(c["age_days_declared"] for c in cells)},
            "age_days_public": {"min": min(c["age_days_public"] for c in cells), "median": statistics.median(c["age_days_public"] for c in cells),
                                "max": max(c["age_days_public"] for c in cells)},
            "newer_print_public_and_unread": sum(1 for c in cells if c["newer_print_public_and_unread"]),
            "mean_abs_unread_change_billions": sum(changes) / len(changes),
            "max_abs_unread_change_billions": max(changes),
        }
    # the share of all scored days (all horizons-1 decision days) on which a newer print was public and unread
    all_days = [d for d in calendar.days if d >= date(2018, 6, 28)]
    unread = 0
    for d in all_days:
        position = calendar.position[d]
        read, public = latest_print(calendar, series, position, declared), latest_print(calendar, series, position, true)
        unread += 1 if read and public and public > read else 0
    # the daily proxy: this Wednesday's reserves from the base Wednesday's print, less the changes in the daily TGA and ON RRP
    proxy = daily_proxy(calendar, series, dts_tga(), reverse_repo_by_date(), weekly_series(calendar, rows_by_date, "tga"), onsets)
    return {"declared": {"available_time": block["available_time"], "days": block["days"], "unit": block["unit"]},
            "true": {"lag": truth["lag"], "clock": truth["clock"], "source": truth["source"]},
            "per_onset": per_onset, "summary_by_horizon": summary,
            "decision_days_with_a_newer_print_public_and_unread": unread, "decision_days": len(all_days),
            "daily_proxy": proxy}


def _correlation(a: list, b: list) -> float:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def daily_proxy(calendar: Calendar, series: dict, tga: dict, rrp: dict, weekly_tga: dict, onsets: list) -> dict:
    """Does reserves(W) - reserves(W - 7k) track -(change in daily TGA) - (change in ON RRP) over the same weeks?

    Reserves balance sheet: a rise in the Treasury's account or in the reverse repo facility drains reserves
    one for one, other things equal. The proxy for the Wednesday level `W` from the print `k` weeks earlier is
    `R(W - 7k) - [TGA(W) - TGA(W - 7k)] - [RRP(W) - RRP(W - 7k)]`, with the Daily Treasury Statement's closing TGA
    and the Desk's reverse repo of the two Wednesdays, both read by their own reference date (not as a panel column,
    which carries them lagged). Only Wednesdays are scored, because the H.4.1 level is a Wednesday level.
    """

    result = {}
    for weeks in (1, 2):
        errors, stale, pairs, ceiling = [], [], [], []
        for wednesday in sorted(series):
            base = wednesday - timedelta(days=7 * weeks)
            if base not in series or wednesday > LAST:
                continue
            tga0, tga1 = tga.get(base), tga.get(wednesday)
            rrp0, rrp1 = rrp.get(base, 0.0), rrp.get(wednesday, 0.0)  # a day with no operation took nothing
            if None in (tga0, tga1):
                continue
            actual = series[wednesday] - series[base]
            guess = -(tga1 - tga0) - (rrp1 - rrp0)
            errors.append(abs(actual - guess))
            stale.append(abs(actual))
            pairs.append((actual, guess, wednesday))
            if base in weekly_tga and wednesday in weekly_tga:  # the same identity with the H.4.1's own TGA: a ceiling, not public daily
                ceiling.append((actual, -(weekly_tga[wednesday] - weekly_tga[base]) - (rrp1 - rrp0)))
        n = len(pairs)
        corr = _correlation([p[0] for p in pairs], [p[1] for p in pairs])
        near = {}
        for onset in onsets:
            wed = onset - timedelta(days=(onset.weekday() - 2) % 7)
            for _, _, w in pairs:
                if w == wed:
                    actual, guess, _ = next(p for p in pairs if p[2] == w)
                    near[onset.isoformat()] = {"wednesday": w.isoformat(), "change_actual": actual, "change_proxy": guess, "error": actual - guess}
        result[f"base_{weeks}_weeks_earlier"] = {
            "wednesdays": n,
            "mae_proxy_billions": sum(errors) / n,
            "mae_carry_forward_billions": sum(stale) / n,
            "rmse_proxy_billions": math.sqrt(sum(e * e for e in errors) / n),
            "correlation_of_changes": corr,
            "median_abs_error_proxy_billions": statistics.median(errors),
            "median_abs_error_carry_billions": statistics.median(stale),
            "wednesdays_proxy_closer_than_carry": sum(1 for e, s in zip(errors, stale) if e < s),
            "ceiling_with_the_h41_tga": {
                "wednesdays": len(ceiling),
                "mae_billions": sum(abs(x - y) for x, y in ceiling) / len(ceiling),
                "correlation_of_changes": _correlation([x for x, _ in ceiling], [y for _, y in ceiling]),
            },
            "mean_abs_gap_between_the_dts_tga_and_the_h41_tga_on_wednesdays_billions": sum(
                abs(tga[w] - weekly_tga[w]) for w in weekly_tga if w in tga
            ) / sum(1 for w in weekly_tga if w in tga),
            "onset_weeks": near,
        }
    return result


# -- 4. structural blind spots --------------------------------------------------------------------------------------


def risk_dates(splits, rows_by_date: dict, days: list, h: int) -> set:
    """The risk dates of `metadata/risk_date_severity.json` at horizon `h`: a calendar day type, and at h = 1 a coupon settlement."""

    out = set()
    for day in days:
        values = rows_by_date[day]
        if splits.day_type(values) != "ordinary":
            out.add(day)
        elif h == 1 and float(values["treasury_settlement_coupons"] or 0) > 0:
            out.add(day)
    return out


def cutoff_windows(calendar: Calendar, scored: list, onsets: set, h: int) -> list:
    """Per refit block of the judge's cut-off rule: its first day, the training end, and the onsets in the training window.

    The window is the scored days up to the business day before the block's first decision instant
    (`pressure_judge.choose_cutoffs`). A window with no onset flags nothing (`select_cutoff` returns infinity).
    """

    blocks = []
    for start in range(0, len(scored), REFIT_EVERY):
        block = scored[start:start + REFIT_EVERY]
        last_known = calendar.position[block[0]] - h - 1
        training_end = calendar.days[last_known] if last_known >= 0 else None
        window = [d for d in scored[:start] if training_end is not None and d <= training_end]
        blocks.append({"first_day": block[0], "last_day": block[-1], "training_end": training_end,
                       "window_days": len(window), "window_onsets": sum(1 for d in window if d in onsets)})
    return blocks


def blind_spots(calendar: Calendar, splits, rows_by_date: dict, scored_by_h: dict, onsets_by_h: dict) -> dict:
    common = sorted(set.intersection(*(set(onsets_by_h[h]) for h in HORIZONS)))
    risk_by_h, out, unreachable = {}, {}, {}
    for h in HORIZONS:
        scored = scored_by_h[h]
        risk = risk_dates(splits, rows_by_date, scored, h)
        risk_by_h[h] = risk
        onset_set = set(onsets_by_h[h])
        blocks = cutoff_windows(calendar, scored, onset_set, h)
        empty = {}
        for block in blocks:
            if block["window_onsets"] == 0:
                for d in scored:
                    if block["first_day"] <= d <= block["last_day"] and d in onset_set:
                        empty[d] = block
        by_window = {}
        for block in blocks:
            for d in onsets_by_h[h]:
                if block["first_day"] <= d <= block["last_day"]:
                    by_window[d] = block["window_onsets"]
        off_risk = [d for d in onsets_by_h[h] if d not in risk]
        both = [d for d in off_risk if d in empty]
        unreachable[h] = set(off_risk) | set(empty)
        out[str(h)] = {
            "scored_days": len(scored),
            "onsets": len(onsets_by_h[h]),
            "risk_date_models": {"onsets_off_the_risk_dates": [d.isoformat() for d in off_risk],
                                 "onsets_on_the_risk_dates": len(onsets_by_h[h]) - len(off_risk)},
            "cut_off_rule": {"onsets_in_a_refit_block_whose_training_window_holds_no_onset": [d.isoformat() for d in sorted(empty)],
                             "blocks_with_no_onset_in_the_window": sum(1 for b in blocks if b["window_onsets"] == 0),
                             "blocks": len(blocks),
                             "onsets_by_training_window_onset_count": {d.isoformat(): by_window[d] for d in sorted(by_window)}},
            "blind_to_both": [d.isoformat() for d in both],
            "risk_date_models_cannot_warn": [d.isoformat() for d in sorted(unreachable[h])],
            "cut_off_rule_alone_cannot_warn": [d.isoformat() for d in sorted(empty)],
        }
    # tier 1 at lead >= 1 asks for a flag at some horizon: an onset no horizon can reach is lost to the risk-date models for good
    lost = [d for d in common if all(d in unreachable[h] for h in HORIZONS)]
    return {"by_horizon": out, "common_onsets": [d.isoformat() for d in common], "risk_by_h": risk_by_h,
            "risk_date_models_cannot_warn_at_any_horizon": [d.isoformat() for d in lost],
            "risk_date_models_best_possible_recall_at_lead_1": (len(common) - len(lost)) / len(common)}


# -- 5. the onset count ---------------------------------------------------------------------------------------------


def onset_count(scored_by_h: dict, onsets_by_h: dict) -> dict:
    common = set.intersection(*(set(onsets_by_h[h]) for h in HORIZONS))
    return {
        "scored_first_day_by_horizon": {str(h): scored_by_h[h][0].isoformat() for h in HORIZONS},
        "scored_days_by_horizon": {str(h): len(scored_by_h[h]) for h in HORIZONS},
        "onsets_by_horizon": {str(h): len(onsets_by_h[h]) for h in HORIZONS},
        "onsets_at_h1_not_at_every_horizon": sorted(d.isoformat() for d in set(onsets_by_h[1]) - common),
        "onsets_at_every_horizon": len(common),
        "onset_definition": "pressure.onsets: SOFR - IORB strictly above +5 bp, with no such day on the five panel days before it; identical at every horizon",
    }


# -- 6. the nowcast re-check ----------------------------------------------------------------------------------------


def nowcast_recheck(rows: list) -> dict:
    declaration = nowcast.load_declaration(NOWCAST_DECLARATION)
    operations = nowcast.load_operations(REVERSE_REPO)
    values, excluded = nowcast.sameday_on_rrp(operations)
    built, walks = nowcast.with_nowcast(rows, values, declaration)
    spreads = [r.spread_bps for r in built]
    index = {r.date.isoformat(): i for i, r in enumerate(built)}
    scored = [d["date"] for d in json.loads(PUBLISHED_DAILY.read_text())["days"] if d["date"] <= LAST.isoformat()]
    positions = [index[d] for d in scored]

    def mae(series, members=None):
        pool = positions if members is None else [p for p in positions if p in members]
        return sum(abs(series[p] - spreads[p]) for p in pool) / len(pool)

    pressure_days = {p for p in positions if spreads[p] > 5.0}
    quarter_ends = {p for p in positions if float(built[p].values.get("quarter_end") or 0) == 1.0}
    naive = [None] + [spreads[i - 1] for i in range(1, len(spreads))]

    # alignment: the naive nowcast of row r is the spread of the previous panel row, which is public at 15:00 on r
    gaps = Counter((built[i].date - built[i - 1].date).days for i in range(1, len(built)))
    module_naive_matches = all(abs(walks["naive"].values[p] - naive[p]) < 1e-12 for p in positions)
    # units and dates: the Desk's same-day reverse repo (USD billions) against FRED's RRPONTSYD (USD billions), an independent copy
    fred = {}
    with FRED_RRP.open(newline="", encoding="utf-8") as handle:
        for record in csv.reader(handle):
            if record and record[0][:2] == "20" and record[1] != "":
                fred[date.fromisoformat(record[0])] = float(record[1])
    differences = [abs(values[d] - fred[d]) for d in values if d <= LAST and d in fred]
    # availability: every admitted day was last written on its own date, by 15:00
    reasons = Counter(excluded[d] for d in excluded if d <= LAST)

    primary_features = declaration.candidates[declaration.primary].features
    control_features = declaration.candidates["published_only"].features
    same_day_only = tuple(f for f in primary_features if f in ("rrp_level_tn", "rrp_change_tn", "settlement_100bn"))

    def walk_clipped(features, clip):
        names = tuple(features)
        n = len(built)
        usable = [k for k in range(2, n) if nowcast._feature_values(built, spreads, k, names) is not None]
        out, model, cursor, next_refit, first = [None] * n, None, 0, None, None
        for r in range(1, n):
            while cursor < len(usable) and usable[cursor] < r:
                cursor += 1
            if first is None and cursor >= declaration.min_pairs:
                first, next_refit = r, r
            if next_refit is not None and r == next_refit:
                pairs = usable[:cursor]
                x = [nowcast._feature_values(built, spreads, k, names) for k in pairs]
                y = [spreads[k] - spreads[k - 1] for k in pairs]
                if clip is not None:
                    y = [max(-clip, min(clip, v)) for v in y]
                model = nowcast.fit_ridge(x, y, penalty=declaration.penalty)
                next_refit = r + declaration.refit_every
            if model is None:
                out[r] = spreads[r - 1]
                continue
            x_r = nowcast._feature_values(built, spreads, r, names)
            out[r] = spreads[r - 1] if x_r is None else spreads[r - 1] + model.predict(x_r)
        return out

    changes = [None] + [spreads[i] - spreads[i - 1] for i in range(1, len(spreads))]
    ordered = sorted(abs(changes[p]) for p in positions)

    def row(series):
        return {"mae_bp": mae(series), "mae_pressure_days_bp": mae(series, pressure_days), "mae_quarter_end_days_bp": mae(series, quarter_ends)}

    variants = {"naive": row(naive)}
    for name in ("published_only", "rrp", "settlement", "rrp_settlement"):
        variants[f"declared_{name}"] = row(walks[name].values)
    for clip in (None, 20, 10, 5):
        for label, features in (("primary_features", primary_features), ("no_same_day_input", control_features), ("same_day_inputs_only", same_day_only)):
            if clip is None and label != "same_day_inputs_only":
                continue
            variants[f"{label}__target_clipped_at_{clip}"] = row(walk_clipped(features, clip))
    return {
        "scored_days": len(positions),
        "reproduces_the_published_figures": {"naive_mae_bp": variants["naive"]["mae_bp"], "primary_mae_bp": variants["declared_rrp_settlement"]["mae_bp"]},
        "alignment": {
            "nowcast_row_is_the_scored_row": True,
            "naive_is_the_previous_panel_rows_spread_on_every_scored_day": module_naive_matches,
            "calendar_day_gaps_between_consecutive_panel_rows": {str(k): v for k, v in sorted(gaps.items())},
        },
        "units": {
            "same_day_reverse_repo_days_compared_with_fred_rrpontsyd": len(differences),
            "days_differing_by_more_than_0.01_billion": sum(1 for v in differences if v > 0.01),
            "max_abs_difference_billions": max(differences),
            "largest_same_day_reverse_repo_billions": max(v for d, v in values.items() if d <= LAST),
        },
        "availability": {
            "admitted_days_to_2025-12-31": sum(1 for d in values if d <= LAST),
            "excluded_days_by_reason": dict(reasons),
            "rule": "a day is admitted only if every record's lastUpdated is on the operation date at or before 15:00 ET; the Desk states no publication time, so that a record is served when written is an assumption",
        },
        "spread_changes": {
            "median_abs_bp": statistics.median(ordered), "p90_abs_bp": ordered[int(0.9 * len(ordered))],
            "p99_abs_bp": ordered[int(0.99 * len(ordered))], "max_abs_bp": ordered[-1],
            "days_with_abs_change_above_20_bp": sum(1 for v in ordered if v > 20),
        },
        "variants": variants,
    }


# -- main ----------------------------------------------------------------------------------------------------------


def read_panel(path: Path) -> list:
    """The panel's rows through `LAST`; a later row is dropped on load and never reaches an analysis."""

    return [r for r in load_daily_panel(path) if r.date <= LAST]


def scored_days(document: dict, horizon: int) -> list:
    """The scored days of a benchmark forecast file, refused if any is after `LAST`.

    Raises:
        LookAheadError: a scored day after `LAST` (the near-blind and blind tiers, `docs/decisions/lockbox.md`).
    """

    days = sorted(date.fromisoformat(k) for k in document["forecasts"]["calendar_climatology"]["5"])
    if days and days[-1] > LAST:
        raise LookAheadError(f"h = {horizon}: scored day {days[-1]} is after {LAST}; this diagnostic reads no 2026 day")
    return days


def run(panel: Path, bench: str) -> dict:
    require_unlocked([LAST], where="desk_standard_diagnostic")
    rows = read_panel(panel)
    calendar = Calendar(r.date for r in rows)
    rows_by_date = {r.date: r.values for r in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text())
    measurement = json.loads(SOURCES_MEASUREMENT.read_text())
    auctions = json.loads(AUCTIONS.read_text())["data"]

    scored_by_h, onsets_by_h = {}, {}
    for h in HORIZONS:
        document = json.loads(Path(bench.format(h=h)).read_text())
        scored = scored_days(document, h)
        scored_by_h[h] = scored
        onsets_by_h[h] = list(pressure.onsets(rows, 5.0, scored))
    blind = blind_spots(calendar, splits, rows_by_date, scored_by_h, onsets_by_h)
    risk_by_h = blind.pop("risk_by_h")
    common = sorted(set.intersection(*(set(onsets_by_h[h]) for h in HORIZONS)))
    return {
        "scored_days": f"{scored_by_h[1][0]} to {scored_by_h[1][-1]}",
        "onsets_used_elsewhere": [d.isoformat() for d in common],
        "timeline": timeline(calendar, registry, measurement),
        "settlements": settlements(calendar, auctions, onsets_by_h, risk_by_h, rows_by_date),
        "reserves": reserves(calendar, registry, rows_by_date, common),
        "blind_spots": blind,
        "onset_count": onset_count(scored_by_h, onsets_by_h),
        "nowcast": nowcast_recheck(rows),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--panel", type=Path, required=True, help="the published panel (4ddc3882…)")
    parser.add_argument("--bench", required=True, help="the judge's benchmark forecast files, with {h}")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run(args.panel, args.bench)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "onsets": len(result["onsets_used_elsewhere"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
