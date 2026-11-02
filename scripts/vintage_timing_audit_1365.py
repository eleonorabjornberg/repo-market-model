"""Vintage and release-timing audit of every input (s3c-ann-net) reads at the 18:00 decision (#1365; H5 registration design).

A table, one row per input: source, declared availability (read from `metadata/sources.json`, never typed here), the actual
publication clock with its primary source, holiday and exception rules, whether the stored series is a first print or a later
vintage, known revisions, whether the meaning matches the use, and two flags (staleness: the declaration is later than needed;
leakage risk: it is earlier than evidenced). Nothing is fixed in place and no declaration changes: each problem found is a
marked question on the page.

    python3 scripts/vintage_timing_audit_1365.py build --panel PANEL.csv     # writes audit.json and the page
    python3 scripts/vintage_timing_audit_1365.py check --panel PANEL.csv     # fails when either differs from a rebuild

`PANEL.csv` is the published panel built at 18:00 from the tracked fixtures (`docs/pivot/next-session.md`). The checks that need
no panel read tracked files only. No outcome is read, no score is computed, no day after 2026-09-03 is read.

Stdlib only.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from datetime import date, time, timedelta
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import s3c_announced, spread_mr_calendar as cal  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
OUT_DIR = REPO / "docs" / "research" / "vintage-timing-audit-1365"
RECORD = OUT_DIR / "audit.json"
PAGE = REPO / "docs" / "research" / "vintage-timing-audit-1365-result.md"
HOLIDAYS = REPO / "metadata" / "market_holidays.json"
SOFR_SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "nyfed-sofr-rate" / "20260906T195746Z_3a5e22446415.json"
AUCTIONS = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions" / "20260914T051023Z_722359ea9bc7.json"
POLICY = REPO / "metadata" / "policy_events.json"
RELEASE_TIMES = REPO / "metadata" / "announcement_release_times_1301.json"
TAX_MARKET_DAYS = REPO / "metadata" / "tax_date_market_days.json"

#: The panel columns the modules of the candidate's chain may name. Anything else is a new input and must be audited first.
ALLOWED_COLUMNS = frozenset({
    "quarter_end", "tax_date", "days_to_month_end", "treasury_settlement_coupons", "treasury_settlement_bills",
    "iorb_announced_change_bps", "iorb_days_to_announced_change", "treasury_settlement", "treasury_settlement_soma",
})
#: The panel columns no module of the chain may name.
UNREAD_COLUMNS = (
    "sofr_volume", "sofr_p25", "sofr_p75", "tgcr", "bgcr", "effr", "dealer_treasury_position", "tbill_4w", "tbill_13w",
    "reserve_balances", "tga", "on_rrp", "mmf_assets",
)
#: The modules whose string constants the inventory test scans.
CHAIN_MODULES = (
    "spread_mean_reversion", "spread_mr_fhs", "spread_mr_state_calendar", "spread_mr_calendar", "s3c_announced", "s3c_net",
    "s3c_candidate", "srf_line", "protocol_benchmarks",
)

NYFED_RATES = "https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates"
READ = "read for this audit on 2 November 2026"


def registry() -> Mapping[str, Mapping[str, object]]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def block(reg: Mapping[str, Mapping[str, object]], ref: Mapping[str, str]) -> Mapping[str, object]:
    source = reg[ref["source"]]
    if "field" in ref:
        return source["field_release_lags"][ref["field"]]
    return source[ref.get("block", "release_lag")]


def declared_text(reg: Mapping[str, Mapping[str, object]], ref: Mapping[str, str]) -> str:
    """The declaration as the registry states it, e.g. `15:00 ET, 1 business_days after ref_date`."""

    b = block(reg, ref)
    kind = "scheduled: " if ref.get("block") == "scheduled_availability" else ""
    return f"{ref['source']}" + (f".{ref['field']}" if "field" in ref else "") + f": {kind}{b['available_time']} ET, {b['days']} {b['unit']} after {b['basis']}"


# -- the table ------------------------------------------------------------------------------------------------------------------------

#: Each row's prose is the audit's reading; its `declared_refs` are looked up in the registry at build time. Counts and dates that a check
#: measures are in `checks`, not here.
ROWS: List[dict] = [
    {
        "id": "I1", "role": "forecast", "input": "SOFR: the observed leg of the spread, so the anchor, the level, the scale and every training pair",
        "source": "nyfed_sofr, SOFR (the NY Fed API, snapshot 20260906T195746Z)",
        "declared_refs": [{"source": "nyfed_sofr"}],
        "clock": f"About 08:00 ET on the next business day. A same-day revision at about 14:30 ET, only if the rate moves by more than one basis point, and only on the day of first publication ({NYFED_RATES}, {READ}).",
        "exceptions": "No publication on days the NY Fed treats as holidays, and, with advance notice, on a day the Treasury repo market broadly treats as one (same page). I6 is that schedule.",
        "vintage": "Current vintage. A revision can only land at about 14:30 on the day of first publication, so the stored value is the value public at the 18:00 decision of that day.",
        "revisions": "The API's revisionIndicator is blank on every row, so no revised date can be named; first prints for the past are not recoverable (#940). A revision is at least 2 bp (#1019).",
        "meaning": "The rate for the previous business day's transactions, dated by its effective date. At every decision the anchor is the previous panel row, at 18:00 and at 16:00 alike (checks.anchor).",
        "staleness": "none: the next SOFR is public at about 08:00 on the next business day.",
        "leakage_risk": "none: 15:00 is after the only revision window and before 18:00.",
        "question": None,
    },
    {
        "id": "I2", "role": "forecast", "input": "IORB, and IOER before 2021-07-29: the administered leg of the spread (read at the anchor row)",
        "source": "fred_macro_latest_vintage, IORB and IOER",
        "declared_refs": [{"source": "fred_macro_latest_vintage", "field": "IORB"}, {"source": "fred_macro_latest_vintage", "field": "IOER"}],
        "clock": "Set by the Board and announced in the FOMC implementation note before its effective date: 14:00 for almost every note of the policy register, 10:00 on 3 March 2020 and 17:00 on Sunday 15 March 2020 (metadata/policy_events.json; https://www.federalreserve.gov/monetarypolicy/reserve-balances.htm, " + READ + ").",
        "exceptions": "The two emergency notes of March 2020. The IOER to IORB splice on 2021-07-29 (build_daily_panel rule 7).",
        "vintage": "FRED latest vintage. The registry's ALFRED comparison finds no restated value (revision_policy never_revised).",
        "revisions": "None known.",
        "meaning": "An administered rate, not a market print. The panel's iorb equals the policy register's IORB or IOER in force on every panel day (checks.iorb_concordance).",
        "staleness": "none that reaches the spread: the declaration puts a value at 16:15 on its own date although it is announced earlier, but the spread reads IORB at the anchor row, a day old.",
        "leakage_risk": "none.",
        "question": None,
    },
    {
        "id": "I3", "role": "forecast", "input": "quarter_end flag (the quarter's last business day)",
        "source": "panel column quarter_end (data.quarter_end), a calendar column",
        "declared_refs": [],
        "declared_text": "calendar column (contract.CALENDAR_FEATURES): read from the target row; always known",
        "clock": "None: a function of the date and the market holiday table.",
        "exceptions": "The holiday table (I6): statutory days under 5 U.S.C. 6103 and SIFMA full-close days.",
        "vintage": "Computed, not stored data.",
        "revisions": "None. A table row is a reviewed code change (data.MARKET_HOLIDAYS_SHA256).",
        "meaning": "The last weekday of the quarter that the NY Fed publishes SOFR. The candidate reads it at the target day on direct pairs.",
        "staleness": "none.", "leakage_risk": "none: the schedule is fixed in advance.", "question": None,
    },
    {
        "id": "I4", "role": "forecast", "input": "tax_date flag (the corporate estimated-tax date and the two business days after it)",
        "source": "panel column tax_date (data.tax_date), a calendar column",
        "declared_refs": [],
        "declared_text": "calendar column (contract.CALENDAR_FEATURES): read from the target row; always known",
        "clock": "None: a function of the date. Deadlines are the 15th of April, June, September and December, rolled by 26 U.S.C. 7503 (statute text as cited in data.py; not re-read for this audit, the host refused the Cornell page).",
        "exceptions": "The roll uses District of Columbia holidays (16 April, 19 June from 2021, Labor Day, 25 December), not the market table. IRS notices that postpone a deadline (the 2020 relief) are not modelled (data.py, `_tax_deadline_holidays`).",
        "vintage": "Computed, not stored data.",
        "revisions": "None in the column. The rule has a ruling that the published panel does not carry: on 10 October 2026 (#521) she ruled the window counts market days.",
        "meaning": "The candidate reads the published panel's column, which keeps the District-holiday window; the market-days column differs on the panel days listed in checks.tax_window. A 2020 postponement is not in either.",
        "staleness": "none.", "leakage_risk": "none: the date is statutory.", "question": "Q1",
    },
    {
        "id": "I5", "role": "forecast", "input": "month_end (last two business days), post_month_end_window (first three business days), dom_19_23, and the turn-day labels that pick the ordinary days of the level",
        "source": "functions of the date and the market holiday table (data.in_last_business_days_of_month, derived_features.bday_of_month, turn_days)",
        "declared_refs": [],
        "declared_text": "functions of the date: read from the target row; always known",
        "clock": "None.", "exceptions": "The holiday table (I6).", "vintage": "Computed, not stored data.", "revisions": "None.",
        "meaning": "Business-day counts on the SOFR publication schedule; turn_days reads no source, publication time or revision (its docstring). The candidate's month_end term is these counts, not the panel's days_to_month_end column.",
        "staleness": "none.", "leakage_risk": "none.", "question": None,
    },
    {
        "id": "I6", "role": "forecast", "input": "The grid of panel days, and so the lead h: the market holiday table",
        "source": "metadata/market_holidays.json",
        "declared_refs": [],
        "declared_text": "table fixed in advance (5 U.S.C. 6103 and SIFMA); pinned by sha256",
        "clock": "None: a schedule. Statutory rows from 5 U.S.C. 6103, other rows from SIFMA's recommendation, each with its source URL in the file.",
        "exceptions": "An unscheduled closure is a new reviewed entry. A closure announced after a decision would move the target row of that decision; the table cannot know it.",
        "vintage": "The table as reviewed. It has no vintage of its own.",
        "revisions": "Entries are added by reviewed pull requests only.",
        "meaning": "The table and the SOFR snapshot agree weekday for weekday over the panel's span (checks.holiday_table_vs_sofr): the table is the publication schedule it claims to be.",
        "staleness": "none.", "leakage_risk": "none inside the panel; open only for a future unscheduled closure.", "question": None,
    },
    {
        "id": "I7", "role": "forecast", "input": "Settlement dating: the announcement date and offering amount of each Treasury auction (the two settlement terms, as signed net settlement at every lead)",
        "source": "treasury_auctions (Fiscal Data auctions_query, retrieved 2026-09-14): announcemt_date, issue_date, offering_amt",
        "declared_refs": [{"source": "treasury_auctions", "block": "scheduled_availability"}],
        "clock": "Treasury's announcement files state a release time for most announcements (the maximum is 16:15, one note) and say 'for immediate release' for the rest (metadata/announcement_release_times_1301.json). TreasuryDirect: the list of upcoming auctions is 'Updated every Friday by 10:45 AM, Eastern U.S. time' (https://www.treasurydirect.gov/auctions/how-auctions-work/, " + READ + ").",
        "exceptions": "Cash management bills are ad hoc; most are announced five weekdays before settlement but some are 'for immediate release', with no time to read. Amended announcements exist (checks.amended_announcements).",
        "vintage": "Fiscal Data's final record, not the first announcement. The API keeps no vintage. The candidate counts an auction from 12:00 on announcemt_date (metadata/settlement_announcement_dating.json), which the registry's machine-read block does not state: it reads a settlement at lead 1 only, at 15:00 the panel day before.",
        "revisions": "An amended announcement carries the original announcemt_date on the stored record; the stored amount may be the amended one (checks.amended_announcements). Whether any amount differs from the first print is not shown by the tracked files.",
        "meaning": "The offering is the announced public offering, fixed before the auction. At 18:00 every stated release time is earlier than the decision, so the 12:00 setting gives the same sums as the stated times (checks.release_times).",
        "staleness": "The registry's declaration is later than the candidate's reading at leads 2 to 5 (15:00 the day before against 12:00 on the announcement day): the candidate is ahead of its declaration, which is a registration dependency.",
        "leakage_risk": "Bounded and not observable: the immediate-release announcements are counted from 12:00 on their date, and the amended announcements may be read at a stored amount that was not public on the earlier days.",
        "question": "Q2, Q4, Q6",
    },
    {
        "id": "I8", "role": "forecast", "input": "The maturing estimate and the netting: est_pub_held_mat_by_type_amt, taken as the largest non-null figure among the group's announced auctions; a class announced in part reads 0",
        "source": "treasury_auctions: est_pub_held_mat_by_type_amt; repo_model.net_settlement (metadata/net_settlement.json)",
        "declared_refs": [],
        "declared_text": "read at 12:00 on announcemt_date (metadata/net_settlement.json); no registry block",
        "clock": "Stated in the announcement as an estimate of the maturing publicly held securities. The files give the time of the announcement, not of any later update.",
        "exceptions": "A cash management bill announced after the instant neither makes a class partial nor enters a figure (#738). The SOMA add-on is an auction result and is not in the net.",
        "vintage": "Fiscal Data's stored figure: whether it is the estimate printed at the announcement or a later update is not shown by the tracked files.",
        "revisions": "Not established. The announcement PDFs are the first print and are already on file for the release-time check (#1301); no one has compared their amounts with the stored ones.",
        "meaning": "Offering less maturing is new cash drained or added, which is why the signed net is the regressor. An estimate is read as if it were the maturing amount.",
        "staleness": "none known.", "leakage_risk": "Open: a stored estimate later than its announcement would be read early.", "question": "Q2",
    },
    {
        "id": "I9", "role": "forecast", "input": "SRF policy events: the standing_repo entry in force on the target day (full allotment, and the line)",
        "source": "metadata/policy_events.json, kind standing_repo (srf_line, s3c_candidate)",
        "declared_refs": [],
        "declared_text": "metadata/srf_cap_1241.json: announced_before_ref_date, 1 business day, 16:00 (the candidate decides at 18:00)",
        "clock": "The FOMC statement, 14:00 ET on every entry of the register; the Desk's operating policy statement of 10 December 2025 says standing overnight repo operations 'will no longer have an aggregate operational limit' and run in a full allotment format from 11 December 2025 (https://www.newyorkfed.org/markets/opolicy/operating_policy_251210, " + READ + ").",
        "exceptions": "An entry without a stated time is public from 23:59:59 on its date; none of the standing_repo entries is of that kind (checks.policy_register).",
        "vintage": "A point-in-time register: each entry is dated by its announcement and carries its source URL.",
        "revisions": "None: an entry is superseded by a later one, never edited.",
        "meaning": "Full allotment is read as an absent aggregate limit; the Desk's statement says the same. The line is the minimum bid rate less IORB in force. The entry of 16 September 2026 is after the last scored day.",
        "staleness": "The declared instant (16:00) is earlier than the candidate's (18:00), which reads late and safe. No entry is announced between 16:00 and 18:00 on a panel day, so both instants read the same entries (checks.policy_register).",
        "leakage_risk": "none.", "question": "Q3",
    },
    {
        "id": "I10", "role": "forecast", "input": "SRF policy events: the iorb_rate entry in force on the target day (the other half of the line)",
        "source": "metadata/policy_events.json, kind iorb_rate",
        "declared_refs": [],
        "declared_text": "metadata/srf_cap_1241.json: announced_before_ref_date, 1 business day, 16:00",
        "clock": "As I2: the implementation note, 14:00 ET, with the two emergency notes of March 2020 before the facility existed.",
        "exceptions": "As I9.", "vintage": "A point-in-time register.", "revisions": "None.",
        "meaning": "The same quantity as I2 from a second source; the two agree on every panel day (checks.iorb_concordance).",
        "staleness": "As I9.", "leakage_risk": "none.", "question": "Q3",
    },
    {
        "id": "I11", "role": "built, read by no term", "input": "The IORB announcement table and the FOMC calendar (iorb_window, fomc_day)",
        "source": "fed_iorb_announcements; fomc_calendar",
        "declared_refs": [{"source": "fed_iorb_announcements", "block": "scheduled_availability"}],
        "clock": "As I2 (the FOMC statement time).",
        "exceptions": "None for this arm.", "vintage": "Register and table.", "revisions": "None.",
        "meaning": "TermTable builds both columns for every arm, but (s3c-ann-net) does not list iorb_window or fomc_day among its terms (checks.arm_inventory), so no value of either reaches its fit or its forecast.",
        "staleness": "none.", "leakage_risk": "none: not read.", "question": None,
    },
    {
        "id": "I12", "role": "built, read by no term", "input": "The panel's gross settlement columns (treasury_settlement_coupons, treasury_settlement_bills)",
        "source": "panel columns from treasury_auctions",
        "declared_refs": [{"source": "treasury_auctions", "block": "scheduled_availability"}],
        "clock": "As I7.", "exceptions": "As I7.", "vintage": "As I7.", "revisions": "As I7.",
        "meaning": "The sized arm replaces both settlement flags by the signed net (checks.arm_inventory: sized true), so the gross columns enter only through the unchanged TermTable construction, never as a regressor.",
        "staleness": "none.", "leakage_risk": "none: not a regressor.", "question": None,
    },
    {
        "id": "I13", "role": "split label only", "input": "Reserve balances (the state's reserves leg)",
        "source": "fred_macro_latest_vintage, WRESBAL (the H.4.1 week average)",
        "declared_refs": [{"source": "fred_macro_latest_vintage", "field": "WRESBAL"}],
        "clock": "The H.4.1 is released each Thursday, generally at 4:30 p.m., and may move to the next business day when Thursday is a federal holiday (https://www.federalreserve.gov/releases/h41/, " + READ + ").",
        "exceptions": "A holiday shifts the release (the registry measures one shift of five days, December 2020).",
        "vintage": "FRED latest vintage, never revised; a one-time units rescale of the series is not a revision (registry).",
        "revisions": "None known.",
        "meaning": "The series is the average over the week, not a Wednesday level, although the decision record and asof call it a Wednesday level (#970 measured the difference).",
        "staleness": "Five calendar days declared where an ordinary week is public one day after its Wednesday; the per-release reading is drafted and off (information-set.md).",
        "leakage_risk": "none.", "question": "Q5",
    },
    {
        "id": "I14", "role": "split label only", "input": "Total assets of commercial banks (the state's assets leg)",
        "source": "frb_h8, total_assets (first prints)",
        "declared_refs": [{"source": "frb_h8"}],
        "clock": "The H.8 is released each Friday, generally at 4:15 p.m., on Thursday when Friday is a federal holiday (https://www.federalreserve.gov/releases/h8/, " + READ + ").",
        "exceptions": "A few weeks of 2020, 2021 and 2025 were released twelve days after their Wednesday (registry).",
        "vintage": "First prints, which the extract does not revise.",
        "revisions": "The H.8 revises later; the stored value is the first print, which is what was public.",
        "meaning": "A weekly level used as a ratio denominator against the reserves average.",
        "staleness": "Twelve days declared where nine is usual: three days late on an ordinary week, on the safe side (registry).",
        "leakage_risk": "none: the extract refuses a longer delay.", "question": "Q5",
    },
    {
        "id": "I15", "role": "split label only", "input": "Daily ON RRP take-up (the state's buffer leg)",
        "source": "nyfed_on_rrp, reverse_repo_total_accepted (the Desk's operation results)",
        "declared_refs": [{"source": "nyfed_on_rrp"}],
        "clock": "The operation closes at 13:15 ET and the Desk publishes a summary of results after it; the Desk's page states no clock time (https://www.newyorkfed.org/markets/desk-operations/reverse-repo, " + READ + ").",
        "exceptions": "Operation results include small value exercises (the Desk's page).",
        "vintage": "The Desk's record; no value amended since publication (registry A45).",
        "revisions": "None known for this source.",
        "meaning": "Accepted amount of the day's operation, compared with a USD 100 bn break.",
        "staleness": "Declared at 16:00 the next business day; the results are likely public the same afternoon, but no clock time is stated, so the lag is not measurable.",
        "leakage_risk": "none.", "question": "Q5",
    },
]

NOT_READ = (
    "TGCR, BGCR, SOFR percentiles and volume, EFFR and DFF, the Treasury bill rates, the FR 2004 dealer position, the TGA, "
    "money-fund assets, the OFR repo series, SEC N-MFP, the DTCC GCF index, the Desk's SRF take-up"
)

QUESTIONS: List[dict] = [
    {
        "id": "Q1", "title": "Which tax-date window should the candidate read?",
        "facts": "Her ruling of 10 October 2026 (#521) counts market days in the window. The published panel keeps the District-holiday window until a publish pull request rebuilds it, and the candidate reads the published panel's column. The two differ on the days in checks.tax_window. No IRS postponement is modelled in either (the 2020 relief).",
        "options": [
            "Queue a development directive that re-runs (s3c-ann-net) with the market-days column on the same days and reports the paired difference, changing no panel, declaration or candidate.",
            "Leave it, and record on the registration page that the candidate reads the District-holiday window.",
            "Ask separately whether a postponement by IRS notice (2020) should enter the column.",
        ],
        "default": "1 (a measurement; no claim changes).",
    },
    {
        "id": "Q2", "title": "Are the stored offering and maturing figures the announcement's first print?",
        "facts": "Fiscal Data keeps no vintage, and the tracked announcement files are the first print. A few announcements inside the panel have amended files dated after the stored announcemt_date (checks.amended_announcements). Nobody has compared the files' amounts with the stored ones.",
        "options": [
            "Queue a directive that reads offering and maturing estimate from the announcement files already on file (#1301 fetched all of them), compares them with the stored figures for every settlement day, and lists the days that differ, the amended ones first.",
            "Leave it.",
        ],
        "default": "1 (extraction and comparison only; no score).",
    },
    {
        "id": "Q3", "title": "Should the SRF cap's availability declaration be re-declared at the decision instant?",
        "facts": "metadata/srf_cap_1241.json and repo_model.srf_line state 16:00; the candidate decides at 18:00 (#1312 left this to a later directive). No standing_repo or iorb_rate entry is announced between 16:00 and 18:00 on a panel day, so both instants read the same entries today.",
        "options": [
            "Queue a directive that re-declares the cap's availability at repo_model.decision_instant.DECISION_TIME with a test that the two are equal (a declaration change; it needs her GO).",
            "Leave it until a register entry is announced inside the window.",
        ],
        "default": "2 (no entry in the window).",
    },
    {
        "id": "Q4", "title": "Registration dependency: the registry states the settlement at lead 1 only.",
        "facts": "metadata/sources.json declares a settlement at 15:00 on the panel day before it settles. The candidate reads the announcement at leads 2 to 5, which only the development modules do. The block is frozen by the final-test pre-registration, so any change needs the re-pin and her GO.",
        "options": [
            "Queue a directive that drafts the registry change expressing the announcement dating at leads 2 to 5, with the pre-registration re-pin, for her review.",
            "Hold until she decides to register the candidate.",
        ],
        "default": "2 (nothing is registered).",
    },
    {
        "id": "Q5", "title": "Do the three scarcity-state inputs need their declarations reviewed now?",
        "facts": "The forecast holds the state at its maximum, so the three legs label #1320's state split and nothing else. Their declarations are later than the publications (reserves five days against one, assets twelve against nine, ON RRP the next business day), and the reserves series is a week average used as a Wednesday level.",
        "options": [
            "Leave them: the legs are labels only.",
            "Queue the per-release H.4.1 reading, the Wednesday levels and a review of the H.8 and ON RRP declarations now.",
        ],
        "default": "1 (the state returns as an input only by a later ruling, and the review would then be part of it).",
    },
    {
        "id": "Q6", "title": "The announcements with no stated release time.",
        "facts": "They are counted from 12:00 on their date. At 18:00 only one released after 18:00 would be a leak, and the files cannot show that. #1320 (Table 4d) ties 2020's net-arm loss to them and #1356's cash management bill arm splits out the bills among them.",
        "options": [
            "Leave the setting as it is and keep reporting them.",
            "Queue a development arm that counts them from the next panel day, as a bound.",
        ],
        "default": "1 (a rule change is hers).",
    },
]


# -- the checks (read tracked files only, except the two that need the panel) -------------------------------------------------------------

def _anchor_offsets(panel_rows, reg) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for clock in (time(18, 0), time(16, 0)):
        counts: collections.Counter = collections.Counter()
        for index in range(10, len(panel_rows) - 5):
            counts[str(index - pb._anchor(panel_rows, index, reg, clock))] += 1
        out[clock.isoformat("minutes")] = dict(sorted(counts.items()))
    return out


def _holiday_vs_sofr() -> dict:
    rows = json.loads(SOFR_SNAPSHOT.read_text(encoding="utf-8"))["refRates"]
    have = {r["effectiveDate"] for r in rows}
    closed = {e["date"] for e in json.loads(HOLIDAYS.read_text(encoding="utf-8"))["closed"]}
    first, last = min(have), max(have)
    day, end = date.fromisoformat(first), date.fromisoformat(last)
    missing: List[str] = []
    extra: List[str] = []
    while day <= end:
        text = day.isoformat()
        if day.weekday() < 5:
            if text not in have and text not in closed:
                missing.append(text)
            if text in have and text in closed:
                extra.append(text)
        day += timedelta(days=1)
    indicator = collections.Counter(r["revisionIndicator"] for r in rows)
    return {
        "span": [first, last], "sofr_rows": len(rows), "weekdays_without_sofr_not_in_table": missing,
        "table_days_with_sofr": extra, "revision_indicator": {k or "blank": v for k, v in sorted(indicator.items())},
    }


def _amended_announcements(panel_dates: Sequence[date]) -> dict:
    import re

    records = json.loads(AUCTIONS.read_text(encoding="utf-8"))
    rows = records if isinstance(records, list) else next(v for v in records.values() if isinstance(v, list))
    amended = []
    for r in rows:
        match = re.match(r"A_(\d{8})_", r.get("pdf_filenm_announcemt") or "")
        if not match:
            continue
        filed = f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:]}"
        if filed != r["announcemt_date"] and r["issue_date"] >= panel_dates[0].isoformat():
            amended.append((r["announcemt_date"], filed, r["issue_date"], r["security_type"]))
    record_count = len(amended)
    amended = sorted(set(amended))
    cells = 0
    index_of = {d: i for i, d in enumerate(panel_dates)}
    for stamped, filed, settles, _kind in amended:
        target = date.fromisoformat(settles)
        if target not in index_of:
            continue
        for h in range(1, 6):
            decision = index_of[target] - h
            if decision >= 0 and stamped <= panel_dates[decision].isoformat() < filed:
                cells += 1
    return {
        "records_in_the_snapshot": record_count,
        "records": [
            {"announcemt_date": a, "file_dated": f, "settles": s, "security_type": k} for a, f, s, k in amended
        ],
        "decision_lead_cells_between_the_two_dates": cells,
    }


def _release_times() -> dict:
    data = json.loads(RELEASE_TIMES.read_text(encoding="utf-8"))
    stated = [v for v in data["stated"].values() if v != "immediate"]
    return {
        "files": len(data["stated"]), "with_a_stated_time": len(stated),
        "immediate_release": data["summary"]["for_immediate_release"]["total"],
        "latest_stated_time": max(stated),
        "every_stated_time_before_the_decision": max(stated) < "18:00",
    }


def _policy_register(panel_rows) -> dict:
    entries = json.loads(POLICY.read_text(encoding="utf-8"))["entries"]
    rates = sorted((e for e in entries if e["kind"] == "iorb_rate"), key=lambda e: (e["effective_date"], e["announced_date"]))
    mismatches = []
    compared = 0
    for row in panel_rows:
        day = row.date.isoformat()
        in_force = [e for e in rates if e["effective_date"] <= day]
        if not in_force:
            continue
        compared += 1
        if abs(float(row.values["iorb"]) - float(in_force[-1]["details"]["rate_percent"])) > 1e-9:
            mismatches.append(day)
    window = [
        e["id"] for e in entries
        if e["kind"] in ("standing_repo", "iorb_rate") and e.get("announced_time") and time(16, 0) < time.fromisoformat(e["announced_time"]) <= time(18, 0)
    ]
    return {
        "standing_repo_entries": sum(1 for e in entries if e["kind"] == "standing_repo"),
        "standing_repo_without_stated_time": sum(1 for e in entries if e["kind"] == "standing_repo" and e["time_basis"] != "stated"),
        "announced_after_16_00_and_by_18_00": window,
        "iorb_panel_days_compared": compared, "iorb_panel_mismatches": mismatches,
    }


def _tax_window() -> dict:
    data = json.loads(TAX_MARKET_DAYS.read_text(encoding="utf-8"))
    return {"panel_days_where_the_two_rules_differ": data["panel_days_where_tax_date_differs"]}


def _arm_inventory() -> dict:
    arm = s3c_announced.ANN_NET_ARM
    return {
        "arm": arm.name, "terms": list(arm.location), "sized": arm.sized, "extra": list(arm.extra), "robust": arm.robust,
        "interact_with_state": arm.interact, "training_pairs": s3c_announced.TRAINING_PAIRS,
        "terms_not_in_the_arm": sorted(set(cal.ALL_TERMS) - set(arm.location)),
    }


def checks(panel_path: Path) -> dict:
    reg = registry()
    panel_rows = load_daily_panel(panel_path)
    dates = [row.date for row in panel_rows]
    return {
        "anchor": {"offset_in_panel_rows_by_decision_instant": _anchor_offsets(panel_rows, reg), "decision_days_checked": len(panel_rows) - 15},
        "holiday_table_vs_sofr": _holiday_vs_sofr(),
        "amended_announcements": _amended_announcements(dates),
        "release_times": _release_times(),
        "policy_register": _policy_register(panel_rows),
        "iorb_concordance": None,
        "tax_window": _tax_window(),
        "arm_inventory": _arm_inventory(),
    }


def build_record(panel_path: Path) -> dict:
    reg = registry()
    measured = checks(panel_path)
    measured["iorb_concordance"] = {
        "panel_days_compared": measured["policy_register"]["iorb_panel_days_compared"],
        "mismatches": len(measured["policy_register"]["iorb_panel_mismatches"]),
    }
    rows = []
    for row in ROWS:
        item = {k: v for k, v in row.items() if k not in ("declared_refs", "declared_text")}
        item["declared"] = [declared_text(reg, ref) for ref in row["declared_refs"]] or [row["declared_text"]]
        rows.append(item)
    return {
        "directive": 1365, "hypothesis": "H5", "step": "registration design (information set)",
        "candidate": "sc_s3c_ann_net, (s3c-ann-net)", "decision_instant": "18:00 America/New_York",
        "tier": "development; an audit of declarations and publication clocks, no score",
        "reads_no_outcome": True, "last_day_read": "2026-09-03",
        "rows": rows, "not_read": NOT_READ, "questions": QUESTIONS, "checks": measured,
    }


# -- the page ---------------------------------------------------------------------------------------------------------------------------

def _cell(text: str) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def render_page(record: Mapping[str, object]) -> str:
    c = record["checks"]
    rows = record["rows"]
    anchor = c["anchor"]["offset_in_panel_rows_by_decision_instant"]
    amended = c["amended_announcements"]
    holiday = c["holiday_table_vs_sofr"]
    release = c["release_times"]
    policy = c["policy_register"]
    tax = c["tax_window"]["panel_days_where_the_two_rules_differ"]
    arm = c["arm_inventory"]
    lines: List[str] = []
    out = lines.append
    out("# Vintage and release-timing audit of every input (s3c-ann-net) reads (#1365)")
    out("")
    out("**Hypothesis and step:** H5 (primary goal), registration design (information set). **Development, not a verdict.** An audit of declarations and "
        "publication clocks against primary sources. It scores nothing, reads no outcome and no day after 2026-09-03, fixes nothing in place and changes no "
        "declaration, record or candidate. Her ruling of 2 November 2026 (relayed on #1365) asked for it after an outside publication-readiness review.")
    out("")
    out("Generated by `python3 scripts/vintage_timing_audit_1365.py build`; never hand-edited. The table is `docs/research/vintage-timing-audit-1365/audit.json`.")
    out("")
    out("## What the candidate reads")
    out("")
    out(f"(s3c-ann-net) is (s3) of the state-scaled calendar study, capped at the SRF line from full allotment, with its two settlement terms read from the "
        f"auction announcement and sized by net settlement, decided at {record['decision_instant']}. Its terms are {', '.join(arm['terms'])}; the two "
        f"settlement terms are sized (sized = {arm['sized']}), it carries no extra term, it fits on {arm['training_pairs']} pairs, and the scarcity state is held at "
        f"its maximum, so no state value reaches a forecast. The terms of the calendar module it does not use are {', '.join(arm['terms_not_in_the_arm'])}. "
        f"`tests/test_vintage_timing_audit_1365.py` pins that inventory and fails when a module of the chain names a panel column outside the audited set.")
    out("")
    out(f"Not read, and so not audited: {record['not_read']}.")
    out("")
    out("## The table")
    out("")
    out("Roles: **forecast** is read by the fit or the forecast; **built, read by no term** is constructed by a shared table and reaches no regressor; "
        "**split label only** groups cells in #1320's splits and reaches no forecast. Declared availability is read from `metadata/sources.json` at build time. "
        "Staleness means the declaration is later than the publication; leakage risk means it is earlier than the evidence.")
    out("")
    out("| # | Input | Role | Source | Declared availability | Stale? | Leak risk? | Question |")
    out("|---|---|---|---|---|---|---|---|")
    for r in rows:
        stale = "no" if r["staleness"].startswith("none") else "yes, see below"
        leak = "no" if r["leakage_risk"].startswith("none") else "yes, see below"
        out(f"| {r['id']} | {_cell(r['input'])} | {r['role']} | {_cell(r['source'])} | {_cell('; '.join(r['declared']))} | {stale} | {leak} | {r['question'] or ''} |")
    out("")
    out("## Row by row")
    for r in rows:
        out("")
        out(f"### {r['id']}. {r['input']}")
        out("")
        out(f"- **Source:** {r['source']}")
        out(f"- **Declared:** {'; '.join(r['declared'])}")
        out(f"- **Actual clock and primary source:** {r['clock']}")
        out(f"- **Holiday and exception rules:** {r['exceptions']}")
        out(f"- **Stored vintage:** {r['vintage']}")
        out(f"- **Known revisions:** {r['revisions']}")
        out(f"- **Meaning against use:** {r['meaning']}")
        out(f"- **Staleness (declaration later than needed):** {r['staleness']}")
        out(f"- **Leakage risk (declaration earlier than evidenced):** {r['leakage_risk']}")
    out("")
    out("## What the checks measured")
    out("")
    out(f"- **Anchor.** On the published panel, the number of decision days by the offset, in panel rows, between the decision day and its last public row: "
        f"at 18:00 {anchor['18:00']}, at 16:00 {anchor['16:00']}. The anchor is the previous panel row at both instants, so moving the instant changed no anchor, "
        "and no row newer than the anchor is public.")
    out(f"- **Holiday table against SOFR.** From {holiday['span'][0]} to {holiday['span'][1]} every weekday without a SOFR row is in the table "
        f"({len(holiday['weekdays_without_sofr_not_in_table'])} are not) and no table day has a SOFR row ({len(holiday['table_days_with_sofr'])} do). "
        f"The snapshot's revision indicator by value: {holiday['revision_indicator']}.")
    out(f"- **IORB, two sources.** The panel's iorb and the policy register's IORB or IOER in force agree on {c['iorb_concordance']['panel_days_compared']} "
        f"panel days with {c['iorb_concordance']['mismatches']} mismatches.")
    out(f"- **Policy register.** {policy['standing_repo_entries']} standing_repo entries, {policy['standing_repo_without_stated_time']} without a stated time; "
        f"entries of either kind announced after 16:00 and by 18:00: {policy['announced_after_16_00_and_by_18_00'] or 'none'}.")
    out(f"- **Announcement release times.** {release['with_a_stated_time']} of {release['files']} announcement files state a time, the latest is "
        f"{release['latest_stated_time']}, so every stated time is before the 18:00 decision ({release['every_stated_time_before_the_decision']}); "
        f"{release['immediate_release']} say for immediate release and show no time.")
    out(f"- **Amended announcements.** {amended['records_in_the_snapshot']} records settling inside the panel, on {len(amended['records'])} settlements, have an announcement "
        "file dated after the stored announcemt_date: "
        + "; ".join(f"stamped {a['announcemt_date']}, file {a['file_dated']}, settles {a['settles']} ({a['security_type']})" for a in amended["records"])
        + f". At most {amended['decision_lead_cells_between_the_two_dates']} decision-and-lead cells fall between the two dates of a settlement.")
    out(f"- **Tax window.** The District-holiday window and the market-days window differ on {len(tax)} panel days: {', '.join(tax)}.")
    out("")
    out("## Findings")
    out("")
    out("1. **The spread side is clean at 18:00.** SOFR and IORB are final when read, nothing newer than the anchor is public, and the calendar columns are "
        "functions of a schedule that matches the SOFR publication days exactly. No declaration there is earlier than its evidence.")
    out("2. **Two stored series are not shown to be first prints, and both are on the settlement side** (I7, I8): Fiscal Data's final record stands in for the announcement. "
        "The announcement files are the first print and are on file, so the question is answerable (Q2).")
    out("3. **The tax-date column is not the window she ruled** (I4, Q1).")
    out("4. **The candidate is ahead of its registry declaration at leads 2 to 5** (I7, Q4): a registration dependency, not a leak.")
    out("5. **The three scarcity-state declarations are stale but reach no forecast** (I13 to I15, Q5).")
    out("6. **The SRF cap is declared at 16:00 and used at 18:00** (I9, I10, Q3): the same entries are read today.")
    out("")
    out("## Marked questions for Eleonora")
    for q in record["questions"]:
        out("")
        out(f"**{q['id']}. {q['title']}** {q['facts']}")
        out("")
        for number, option in enumerate(q["options"], start=1):
            out(f"{number}. {option}")
        out("")
        out(f"Default if unanswered: {q['default']}")
    out("")
    out("## What this does not show")
    out("")
    out("- No publication clock was measured from a live feed. The clocks come from the primary pages named in each row (read on the date given), from "
        "Treasury's announcement files (#1301) and from the registry's own provenance. The Cornell text of 26 U.S.C. 6655 and 7503 was refused by the host and is "
        "cited as `data.py` cites it.")
    out("- The NY Fed, Board and TreasuryDirect pages state today's practice; for 2018 to 2026 the registry's recorded readings and the snapshots are the evidence.")
    out("- Whether any stored Treasury amount differs from its first print (Q2), the release time of an immediate-release announcement and the ON RRP "
        "publication time are not recoverable from the tracked files.")
    out("- Nothing here scores a forecast, so no claim about the candidate's skill moves.")
    out("")
    return "\n".join(lines)


# -- commands ---------------------------------------------------------------------------------------------------------------------------

def _json_text(record: Mapping[str, object]) -> str:
    return json.dumps(record, indent=1, sort_keys=False) + "\n"


def build_command(args) -> int:
    record = build_record(args.panel)
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(_json_text(record), encoding="utf-8")
    PAGE.write_text(render_page(record), encoding="utf-8")
    print(json.dumps({"rows": len(record["rows"]), "questions": len(record["questions"]), "record": str(RECORD), "page": str(PAGE)}))
    return 0


def check_command(args) -> int:
    record = build_record(args.panel)
    problems = []
    if RECORD.read_text(encoding="utf-8") != _json_text(record):
        problems.append(f"{RECORD} differs from a rebuild")
    if PAGE.read_text(encoding="utf-8") != render_page(record):
        problems.append(f"{PAGE} differs from a rebuild")
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("build", build_command), ("check", check_command)):
        p = sub.add_parser(name)
        p.add_argument("--panel", type=Path, required=True)
        p.set_defaults(handler=handler)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
