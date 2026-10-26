#!/usr/bin/env python3
"""Three findings about the repo market, for the pages (#1177; context for H5; development data, not a verdict).

Eleonora's ruling (23 October 2026, relayed on #1177): the explorer and the plain page carry three observations about the
market, not about the models, every figure read from a committed record or computed from the published panel.

1. **Stress lives on the turn.** The last business day of a month and the first business day of the next carry the
   pressure; the second-last day is ordinary. Computed here from the panel, by regime.
2. **The calendar sets the date; reserve scarcity sets the size.** The per-term effects of #1145, arm (s1), read from
   `docs/research/state-calendar-1145/result.json`.
3. **Every stress episode since April 2020 began on or within a business day of a known calendar date.** The episode list
   is recomputed here from the panel.

The measurement is descriptive. It scores no forecast, fits nothing and chooses nothing; every day it reads is passed
through `lockbox.require_unlocked`. The figures are conditional means, medians and shares of the SOFR - IORB spread in
bp, with the number of days behind each; they carry no interval, because nothing here is a comparison.

`run` writes `docs/research/market-findings-1177/result.json` and the page `docs/research/market-findings-1177-result.md`;
`check` refuses a page that no longer follows its record. `plain_lines` and `explorer_html` render the pages' text from the
two records; `scripts/plain_page.py` and `scripts/emit_visual.py` call them. Stdlib only.
"""

from __future__ import annotations

import argparse
import html
import json
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import data as rm_data  # noqa: E402
from repo_model import lockbox  # noqa: E402
from repo_model import turn_days as td  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "market-findings-1177" / "result.json"
PAGE = RESEARCH / "market-findings-1177-result.md"
STATE_CALENDAR = RESEARCH / "state-calendar-1145" / "result.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
LABEL = "development data, not a verdict"
#: A day is above the line when its whole-bp spread is strictly above it (`docs/decisions/pressure-probability.md`).
THRESHOLD_BP = 5.0
#: A new episode starts after more than this many business days with no day above the line.
EPISODE_GAP = 10
#: Episodes are listed from this day; the one before it is counted, not listed.
EPISODES_SINCE = date(2020, 4, 1)
#: The ordinary comparison day: a day of the month in this range that none of the labels flags.
MID_MONTH = (10, 20)
#: A coupon settlement counts as mid-month when it falls on a day of the month in this range.
MID_MONTH_SETTLEMENT = (13, 19)
#: The arm of #1145 whose per-term effects finding 2 reads, and the two terms it quotes.
ARM = "sc_s1_standardised"
TERMS = ("month_end", "settlement_coupon")
ROLES = ("last", "first", "penultimate", "ordinary")
ROLE_WORDS = {
    "last": "Last business day of the month",
    "first": "First business day of the next month",
    "penultimate": "Second-last business day",
    "ordinary": "Ordinary mid-month day",
}
TERM_WORDS = {"month_end": "Month-end", "settlement_coupon": "Coupon settlement"}
HYPOTHESIS = "H5 (primary goal), context for the pages; not a step of the plan and not a test of any model"


# -- arithmetic ------------------------------------------------------------------------------------------------------


def stats(values: Sequence[float]) -> dict:
    """Count, mean, median and the share strictly above the line, of spreads in bp."""

    if not values:
        raise ValueError("a group of days with no day in it has no statistics")
    return {"n": len(values), "mean": statistics.fmean(values), "median": statistics.median(values),
            "share_above": sum(v > THRESHOLD_BP for v in values) / len(values)}


def require_unlocked_rows(rows) -> None:
    """Refuse a locked day, as every scoring entry point does, although nothing here scores.

    Raises:
        LookAheadError: for a day in a tier `metadata/lockbox.json` has not opened.
    """

    lockbox.require_unlocked([r.date for r in rows], where="market_findings_1177")


def turn_role(day: date) -> Optional[str]:
    """`last` or `first` for a turn day of a month that is not a quarter's last, else `None`."""

    if td.turn_label(day) != td.TURN:
        return None
    return "last" if day == rm_data.last_business_days_of_month(day.year, day.month, count=1)[0] else "first"


def is_penultimate(day: date) -> bool:
    """The second-last business day of a month that is not a quarter's last."""

    return day.month % 3 != 0 and td.penultimate_day(day)


def is_mid_month_ordinary(day: date, *, tax_date: bool = False) -> bool:
    """A day between the 10th and the 20th that is neither a turn day nor a tax date."""

    return (MID_MONTH[0] <= day.day <= MID_MONTH[1] and td.turn_label(day) is None and not tax_date
            and not td.december_26(day))


def role_of(row) -> Optional[str]:
    role = turn_role(row.date)
    if role:
        return role
    if is_penultimate(row.date):
        return "penultimate"
    if is_mid_month_ordinary(row.date, tax_date=float(row.values["tax_date"]) == 1.0):
        return "ordinary"
    return None


def role_table(rows, regime_of: Callable[[date], str]) -> Dict[str, Dict[str, dict]]:
    """Statistics of the spread by regime and role, with the pooled `all` beside the regimes."""

    groups: Dict[str, Dict[str, List[float]]] = {}
    for r in rows:
        role = role_of(r)
        if role is None:
            continue
        for key in (regime_of(r.date), "all"):
            groups.setdefault(key, {}).setdefault(role, []).append(float(r.spread_bps))
    return {key: {role: stats(groups[key][role]) for role in ROLES if role in groups[key]} for key in groups}


def all_months_table(rows, regime_of: Callable[[date], str]) -> Dict[str, Dict[str, dict]]:
    """The last and the first business day of every month, quarter-ends and year-ends included, by regime.

    The turn of a quarter's last month is left out of `role_table`, which is the definition in force (#1135, #1161);
    this table is the wider reading, kept so that a figure quoted over every month can be reproduced.
    """

    firsts: Dict[tuple, object] = {}
    groups: Dict[str, Dict[str, List[float]]] = {}
    for r in rows:
        key = (r.date.year, r.date.month)
        if key not in firsts:
            firsts[key] = r
            groups.setdefault(regime_of(r.date), {}).setdefault("first_any", []).append(float(r.spread_bps))
        if r.date == rm_data.last_business_days_of_month(r.date.year, r.date.month, count=1)[0]:
            groups.setdefault(regime_of(r.date), {}).setdefault("last_any", []).append(float(r.spread_bps))
    return {key: {role: stats(v) for role, v in sorted(roles.items())} for key, roles in groups.items()}


def known_dates(row) -> List[str]:
    """The known calendar dates the row sits on, in a fixed order."""

    label = td.turn_label(row.date)
    found = []
    if label == td.TURN:
        found.append("month-end")
    if label in (td.QUARTER_END_TURN, td.YEAR_END) or float(row.values["quarter_end"]) == 1.0:
        found.append("quarter-end")
    if float(row.values["tax_date"]) == 1.0:
        found.append("tax date")
    if (float(row.values.get("treasury_settlement_coupons") or 0.0) > 0
            and MID_MONTH_SETTLEMENT[0] <= row.date.day <= MID_MONTH_SETTLEMENT[1]):
        found.append("mid-month settlement")
    return found


def episodes(rows, *, threshold: float = THRESHOLD_BP, gap: int = EPISODE_GAP, since: date = EPISODES_SINCE) -> dict:
    """The stress episodes: a new one starts on a day strictly above `threshold` after more than `gap` business days with
    none. Each listed episode (start on or after `since`) names the known dates within one business day of its start.

    `base_rate` is the share of business days from `since` on that are themselves on or next to a known date, the share any
    day would show by chance.
    """

    above = [i for i, r in enumerate(rows) if r.spread_bps > threshold]
    starts = [i for k, i in enumerate(above) if k == 0 or i - above[k - 1] > gap]
    listed, earlier = [], []
    for i in starts:
        dates: List[str] = []
        for j in range(max(0, i - 1), min(len(rows), i + 2)):
            dates += [d for d in known_dates(rows[j]) if d not in dates]
        (earlier if rows[i].date < since else listed).append(
            {"start": rows[i].date.isoformat(), "spread_bp": float(rows[i].spread_bps), "dates": dates, "near": bool(dates)})
    window = [i for i, r in enumerate(rows) if r.date >= since]
    near = sum(any(known_dates(rows[j]) for j in range(max(0, i - 1), min(len(rows), i + 2))) for i in window)
    return {"threshold_bp": threshold, "gap_business_days": gap, "since": since.isoformat(), "episodes": listed,
            "earlier": len(earlier), "earlier_episodes": earlier, "window_days": len(window), "base_rate": near / len(window) if window else 0.0}


def build_record(rows, panel_path) -> dict:
    """The record of findings 1 and 3, from the panel's rows. `panel_path` gives the digest."""

    require_unlocked_rows(rows)
    splits = load_split_declaration(SPLITS)
    found = episodes(rows)
    return {
        "issue": 1177,
        "label": LABEL,
        "hypothesis": HYPOTHESIS,
        "panel_sha256": panel_sha256(Path(panel_path)),
        "first_day": rows[0].date.isoformat(),
        "last_day": rows[-1].date.isoformat(),
        "threshold_bp": THRESHOLD_BP,
        "mid_month_days": list(MID_MONTH),
        "regimes": list(splits.regime_labels),
        "turn": role_table(rows, splits.regime),
        "turn_all_months": all_months_table(rows, splits.regime),
        "episodes": found,
    }


# -- the records the pages read ----------------------------------------------------------------------------------------


def calendar_terms(state: Mapping) -> Dict[str, Dict[str, dict]]:
    """Finding 2: the per-term effects of #1145's arm (s1), in bp, by regime, with their 90% intervals.

    Raises:
        ValueError: if the record lacks the arm, a term or a regime's figures.
    """

    try:
        arm = state["term_effect_intervals"][ARM]
        return {term: {regime: {"mean": float(cell["bp"]["mean"]), "interval": [float(x) for x in cell["bp"]["interval"]],
                                "days": int(cell["days"])} for regime, cell in arm[term].items()} for term in TERMS}
    except (KeyError, TypeError) as exc:
        raise ValueError(f"{STATE_CALENDAR}: no per-term effects for arm {ARM!r} ({exc!r})") from exc


def load_state_calendar(path: Path = STATE_CALENDAR) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_findings(record_path: Path = RECORD, state_path: Path = STATE_CALENDAR) -> dict:
    """Everything the pages need, read from the two committed records.

    Raises:
        ValueError: if a record is not labelled development data or lacks what a finding needs.
    """

    record = json.loads(Path(record_path).read_text(encoding="utf-8"))
    state = load_state_calendar(state_path)
    for name, doc in (("market findings", record), ("state calendar", state)):
        label = str(doc.get("label", ""))
        if "development" not in label or "not a verdict" not in label:
            raise ValueError(f"the {name} record is not labelled as development data, not a verdict (label {label!r})")
    return {"turn": record["turn"], "turn_all_months": record["turn_all_months"], "episodes": record["episodes"],
            "calendar": calendar_terms(state), "regimes": record["regimes"], "first_day": record["first_day"],
            "last_day": record["last_day"], "panel_sha256": record["panel_sha256"],
            "calendar_days_to": state.get("last_target"), "calendar_panel_sha256": state.get("panel_sha256")}


# -- rendering ---------------------------------------------------------------------------------------------------------


def bp(value: float) -> str:
    return "%+.1f" % value


def pct(value: float) -> str:
    return "%d%%" % round(value * 100)


def e(text) -> str:
    return html.escape(str(text))


def table(caption: str, headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    head = "".join('<th scope="col">%s</th>' % e(h) for h in headers)
    body = "".join("<tr><th scope=\"row\">%s</th>%s</tr>" % (e(r[0]), "".join("<td>%s</td>" % c for c in r[1:])) for r in rows)
    return ('<div class="scroll grid2" role="region" aria-label="Table: %s" tabindex="0"><table><caption>%s</caption>'
            '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (e(caption), e(caption), head, body))


def _turn_cell(cell: Optional[dict]) -> str:
    return "none" if cell is None else "%s (%d days)" % (bp(cell["mean"]), cell["n"])


def _regime_phrase(items: Sequence[tuple]) -> str:
    return ", ".join("%s in %s" % (value, name) for name, value in items)


def plain_lines(data: dict, link: Callable[..., str]) -> List[str]:
    """The block of the plain page: three findings in plain words, each term defined where it first appears.

    `link(path, label=None)` renders a link to a file of the repository.
    """

    turn, calendar, found = data["turn"], data["calendar"], data["episodes"]
    shown = [r for r in data["regimes"] if r in turn]  # a declared regime with no day yet has no row
    early, latest = turn[shown[0]], turn[shown[-1]]
    month_end = calendar["month_end"]
    coupon = calendar["settlement_coupon"]
    listed = found["episodes"]
    near = [x for x in listed if x["near"]]
    years = sorted({x["start"][:4] for x in listed})
    every = len(near) == len(listed)
    out = [
        "<p>These are three things about the repo market itself, not about the forecasting model. The market lends cash "
        "overnight against Treasury securities. <strong>SOFR</strong> is the rate on that borrowing. <strong>IORB</strong> "
        "is the interest the Fed pays banks on the cash they hold with it. The <strong>gap</strong> is SOFR minus IORB, "
        "counted in <strong>basis points</strong> (a hundredth of a percentage point). Pressure is a gap more than %g "
        "basis points above zero. This is <strong>development evidence</strong>: a description of what happened, not a "
        "forecast and not a verdict on any model.</p>" % found["threshold_bp"],
        "<h3>1. Stress lives on the turn, not on month-end in general</h3>",
        "<p>The <strong>turn</strong> is the last business day of a month and the first business day of the next. In "
        "%s the gap averaged %s basis points on the last business day and %s on the first business day after it. On "
        "the second-last business day it averaged %s, the same as on an ordinary day in the middle of a month (%s). "
        "The days before the turn are ordinary; the turn carries the pressure. The latest period, %s, has the same shape, "
        "smaller: %s on the last business day, %s on the first and %s on the second-last.</p>" % (
            shown[0], bp(early["last"]["mean"]), bp(early["first"]["mean"]), bp(early["penultimate"]["mean"]),
            bp(early["ordinary"]["mean"]), shown[-1], bp(latest["last"]["mean"]), bp(latest["first"]["mean"]),
            bp(latest["penultimate"]["mean"])),
        table("Average gap in basis points, by market period and type of day (days counted in brackets; months that end a "
              "quarter are left out)",
              ["Market period"] + [ROLE_WORDS[r] for r in ROLES],
              [[regime] + [_turn_cell(turn[regime].get(r)) for r in ROLES] for regime in data["regimes"] if regime in turn]),
        "<h3>2. The calendar sets the date; reserve scarcity sets the size</h3>",
        "<p>The same month-end added about %s basis points to the gap in %s, %s in %s and %s in %s. A <strong>coupon "
        "settlement</strong>, the day the Treasury is paid for newly auctioned notes and bonds, which draws cash out of "
        "the market, added %s, %s and %s in the same three periods. The calendar tells you <em>which</em> days to "
        "watch. How much a date adds follows how scarce <strong>reserves</strong> (the cash banks hold at the Fed) "
        "are. That second half is the project's reading of the pattern; the table shows the sizes, not the cause.</p>" % (
            bp(month_end["2018-19"]["mean"]), "2018-19", bp(month_end["2021-23"]["mean"]), "2021-23",
            bp(month_end["2025-26"]["mean"]), "2025-26", bp(coupon["2018-19"]["mean"]), bp(coupon["2021-23"]["mean"]),
            bp(coupon["2025-26"]["mean"])),
        table("Added to the gap on that kind of day, in basis points, with the 90% interval (state-scaled calendar model)",
              ["Market period", "Month-end", "Coupon settlement"],
              [[regime] + ["%s [%s, %s]" % (bp(calendar[t][regime]["mean"]), bp(calendar[t][regime]["interval"][0]),
                                            bp(calendar[t][regime]["interval"][1])) for t in TERMS]
               for regime in data["regimes"] if all(regime in calendar[t] for t in TERMS)]),
        "<h3>3. Stress episodes begin on known calendar dates</h3>",
        "<p>A <strong>stress episode</strong> starts on a day the gap is above %g basis points after more than %d "
        "business days without one. Since %s there have been %d. Of those, %s began on or within a business day of a known "
        "calendar date: a month-end or quarter-end turn, a mid-month Treasury settlement or a tax date. For scale, "
        "%s of all business days in that period sit on or next to such a date.%s</p>" % (
            found["threshold_bp"], found["gap_business_days"], found["since"], len(listed),
            "all" if every else "%d" % len(near),
            pct(found["base_rate"]),
            "" if not years else " The episodes all began in %s." % (
                years[0] if len(years) == 1 else "%s to %s" % (years[0], years[-1]))),
        table("Stress episodes since %s" % found["since"], ["Start", "Gap, basis points", "Known date on or next to it"],
              [[x["start"], bp(x["spread_bp"]), e(", ".join(x["dates"]) or "none")] for x in listed]),
    ]
    out.append('<p class="src">Where this comes from: %s, %s and %s.</p>' % (
        link("docs/research/market-findings-1177/result.json"), link("docs/research/state-calendar-1145/result.json"),
        link("docs/research/market-findings-1177-result.md", "the study page")))
    return out


def explorer_html(data: dict, link: Callable[..., str]) -> str:
    """View N6 of the explorer: the plain text of the three findings, then how each was measured."""

    body = "\n".join(l for l in plain_lines(data, link) if not l.startswith('<p class="src"'))
    found = data["episodes"]
    method = (
        "<details><summary>Go deeper: how each finding is measured</summary><ul>"
        "<li>Finding 1 is computed from the published panel (digest %s), %s to %s. A turn is the last business day of a "
        "month and the first business day of the next, in months that do not end a quarter (the turn "
        "definition in force). The second-last day is the month's second-last business day. The ordinary day "
        "is any day from the %dth to the %dth that is no turn day and no tax date. Every figure is a mean of the "
        "spread, SOFR minus IORB in basis points, over the days counted.</li>"
        "<li>Finding 2 is read from %s, arm (s1): a model fitted by regime with one standardised effect for each kind of "
        "calendar day. The interval is the 90%% interval of the effect over the refits.</li>"
        "<li>Finding 3: an episode starts on a day the gap is strictly above %g basis points after more than %d "
        "business days with none, as counted on the panel's own calendar. “Near” is one business day either "
        "side. A mid-month settlement is a coupon settlement on the %dth to the %dth.</li>"
        "<li>It is a description of what happened: no forecast, no model comparison, and no day the project holds back "
        "from analysis is read (%s).</li>"
        "</ul>%s</details>" % (
            e(data["panel_sha256"][:8]), e(data["first_day"]), e(data["last_day"]), MID_MONTH[0], MID_MONTH[1],
            link("docs/research/state-calendar-1145/result.json"), found["threshold_bp"], found["gap_business_days"],
            MID_MONTH_SETTLEMENT[0], MID_MONTH_SETTLEMENT[1], link("docs/decisions/lockbox.md", "the rule"),
            '<p class="src">Where this comes from: %s, %s and %s.</p>' % (
                link("docs/research/market-findings-1177/result.json"), link("docs/research/state-calendar-1145/result.json"),
                link("docs/research/market-findings-1177-result.md", "the study page"))))
    return body + "\n" + method


def explorer_lede(data: dict) -> str:
    listed = data["episodes"]["episodes"]
    missed = len(listed) - sum(x["near"] for x in listed)
    every = "every stress episode" if not missed else "all but %d of the stress episodes" % missed
    return ("Three things the data show about the repo market, in a fixed order: stress sits on the turn of the month, "
            "the calendar sets the date and reserve scarcity sets the size, and %s since %s began next to a known "
            "calendar date. A description of what happened, not a forecast." % (every, data["episodes"]["since"]))


def render_page(record: dict, state: dict) -> str:
    """The study page `docs/research/market-findings-1177-result.md`, from the two records."""

    data = {"turn": record["turn"], "turn_all_months": record["turn_all_months"], "episodes": record["episodes"],
            "calendar": calendar_terms(state), "regimes": record["regimes"]}
    plain = lambda path, label=None: "`%s`" % (label or path)
    turn, found, wide = data["turn"], data["episodes"], data["turn_all_months"]
    early = [r for r in data["regimes"] if r in turn][0]
    lines = [
        "# Three market findings (#1177)",
        "",
        "**Hypothesis and step:** %s." % HYPOTHESIS,
        "",
        "**%s.** Descriptive: no forecast is scored, no model is fitted or compared, no locked day is read "
        "(`lockbox.require_unlocked` runs on every row), and no published record moves. Every figure is read from "
        "`docs/research/market-findings-1177/result.json` (panel digest `%s`, %s to %s) or from "
        "`docs/research/state-calendar-1145/result.json`, arm (s1), by `scripts/market_findings_1177.py`. The pages "
        "(`site/plain.html`, the explorer) render these figures and type none." % (
            LABEL.capitalize(), record["panel_sha256"][:8], record["first_day"], record["last_day"]),
        "",
        "## 1. Stress lives on the turn",
        "",
        "Mean spread in bp (SOFR - IORB), with the number of days; median and the share of days above +%g bp beside it. "
        "Months that end a quarter are left out, as the turn definition in force (#1135, #1161) treats them apart." %
        record["threshold_bp"],
        "",
        "| Regime | Day | Days | Mean | Median | Share above +%g bp |" % record["threshold_bp"],
        "|---|---|---|---|---|---|",
    ]
    for regime in list(data["regimes"]) + ["all"]:
        for role in ROLES:
            cell = turn.get(regime, {}).get(role)
            if cell:
                lines.append("| %s | %s | %d | %s | %s | %s |" % (
                    regime if regime != "all" else "all regimes", ROLE_WORDS[role], cell["n"], bp(cell["mean"]),
                    bp(cell["median"]), pct(cell["share_above"])))
    lines += ["", "### The first business day over every month", "",
              "The directive's first-day figure for %s is the first business day of every month, quarter-ends and the "
              "year-end included. Read that way it is %s bp over %d days, with a median of %s bp; read on the definition "
              "above (months that do not end a quarter) it is %s bp over %d days, median %s bp. The wider mean carries the "
              "year-end first day, which printed far above the rest. **Question for Eleonora (not settled here):** which "
              "reading do the pages quote? They quote the definition in force." % (
                  early, bp(wide[early]["first_any"]["mean"]), wide[early]["first_any"]["n"],
                  bp(wide[early]["first_any"]["median"]), bp(turn[early]["first"]["mean"]), turn[early]["first"]["n"],
                  bp(turn[early]["first"]["median"])),
              "", "## 2. The calendar sets the date; reserve scarcity sets the size", "",
              "Per-term effects of arm (s1) of #1145 (`%s`), in bp, with the 90%% interval over the refits." % ARM, "",
              "| Regime | Month-end | Coupon settlement |", "|---|---|---|"]
    for regime in data["regimes"]:
        if all(regime in data["calendar"][t] for t in TERMS):
            cells = ["%s [%s, %s] (%d days)" % (bp(data["calendar"][t][regime]["mean"]), bp(data["calendar"][t][regime]["interval"][0]),
                                                 bp(data["calendar"][t][regime]["interval"][1]), data["calendar"][t][regime]["days"])
                     for t in TERMS]
            lines.append("| %s | %s | %s |" % (regime, cells[0], cells[1]))
    lines += ["", "The table shows how large the same date was in each period. That reserve scarcity is what sets the size is "
              "the project's reading of the pattern, not something this table tests.", "",
              "## 3. Stress episodes begin on known calendar dates", "",
              "An episode starts on a day with a spread strictly above +%g bp after more than %d business days with none. "
              "Listed from %s; the %d earlier episodes are counted and not listed (the latest began %s). A known date is a month-end or "
              "quarter-end turn, a tax date, or a coupon settlement from the %dth to the %dth; \"near\" is one business day "
              "either side of the start." % (
                  found["threshold_bp"], found["gap_business_days"], found["since"], found["earlier"],
                  found["earlier_episodes"][-1]["start"] if found["earlier_episodes"] else "never",
                  MID_MONTH_SETTLEMENT[0], MID_MONTH_SETTLEMENT[1]),
              "", "| Start | Spread, bp | Known date on or next to it |", "|---|---|---|"]
    for x in found["episodes"]:
        lines.append("| %s | %s | %s |" % (x["start"], bp(x["spread_bp"]), ", ".join(x["dates"]) or "none"))
    near = sum(x["near"] for x in found["episodes"])
    lines += ["", "%d of %d listed episodes began near a known date. For scale, %s of the %d business days from %s on sit on or "
              "next to one." % (near, len(found["episodes"]), pct(found["base_rate"]), found["window_days"], found["since"]),
              "", "**Questions for Eleonora (not settled here):** (1) The claim reads \"since 2020\"; the pages say \"since %s\", "
              "which leaves out the March 2020 episode. (2) %s listed episode(s) have no known date within a business day: "
              "%s. Whether 26 December (`turn_days.december_26`, flagged apart by Lens A) or the days around a year-end "
              "count as a known date is a data meaning, so the pages state the count the rule gives." % (
                  found["since"], sum(not x["near"] for x in found["episodes"]),
                  ", ".join(x["start"] for x in found["episodes"] if not x["near"]) or "none"),
              "", "## What this does not show", "",
              "It is a description of one panel. It says nothing about a model, ranks nothing, and a share of days near a "
              "known date is a base rate, not a test. No interval is given for a mean because nothing here is compared.", ""]
    return "\n".join(lines)


# -- commands ------------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    rows = rm_data.load_daily_panel(args.published)
    record = build_record(rows, args.published)
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render_page(record, load_state_calendar()), encoding="utf-8")
    print(f"wrote {RECORD.relative_to(REPO)} and {PAGE.relative_to(REPO)}")
    return 0


def check_command(_args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if PAGE.read_text(encoding="utf-8") != render_page(record, load_state_calendar()):
        print(f"{PAGE.relative_to(REPO)} does not follow its record; run `run`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.set_defaults(func=run_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
