"""Point-in-time daily panel loading and validation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from repo_model.contract import (
    resolve_identity_tolerance,
    validate_identity_tolerance,
)


REQUIRED_FIELDS = ("date", "sofr", "iorb")
OPTIONAL_NUMERIC_FIELDS = (
    "sofr_volume",
    "sofr_p25",
    "sofr_p75",
    "tgcr",
    "bgcr",
    "reserve_balances",
    "tga",
    "on_rrp",
    "treasury_settlement",
    "treasury_settlement_bills",
    "treasury_settlement_coupons",
    "treasury_settlement_soma",
    "dealer_treasury_position",
    "mmf_assets",
    "tbill_4w",
    "tbill_13w",
    "quarter_end",
    "tax_date",
)
POINT_IN_TIME_FIELDS = (
    "series_id",
    "ref_date",
    "available_at",
    "value",
    "vintage_id",
    "source_sha",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_STRESS_THRESHOLDS = (
    Path(__file__).parents[2] / "metadata" / "stress_thresholds.json"
)


class DataContractError(ValueError):
    """Raised when a modeling panel violates its declared contract."""


@dataclass(frozen=True)
class DailyObservation:
    date: date
    values: Mapping[str, Optional[float]]

    @property
    def spread_bps(self) -> float:
        return 100.0 * (float(self.values["sofr"]) - float(self.values["iorb"]))


@dataclass(frozen=True)
class PointInTimeObservation:
    """One immutable observation from a specific source vintage."""

    series_id: str
    ref_date: date
    available_at: datetime
    value: float
    vintage_id: str
    source_sha: str


@dataclass(frozen=True)
class AuditReport:
    row_count: int
    start_date: date
    end_date: date
    missing_counts: Mapping[str, int]
    warnings: Sequence[str]


@dataclass(frozen=True)
class SeriesQuality:
    series_id: str
    observation_count: int
    reference_date_count: int
    start_date: date
    end_date: date
    missing_reference_dates: int
    missing_rate: float
    revised_reference_dates: int
    revision_rows: int
    largest_absolute_revision: Optional[float]


# Why a cross-section was kept out of the panel: the closed vocabulary
# `CrossSectionCoverage.exclusion_reason` is recorded under, `None` meaning it was
# admitted. See `docs/DATA_QUALITY_DECISIONS.md`, "An empty repo cross-section is
# excluded, with its reason".
#
#   below_floor   fewer reporting entities than its era's declared floor, or no
#                 declared era to take a floor from (`era_id` is None)
#   no_repo_rows  cleared the floor, but its holdings table was read in a
#                 declared INVESTMENTCATEGORY era and supplied no repo holding
EXCLUSION_BELOW_FLOOR = "below_floor"
EXCLUSION_NO_REPO_ROWS = "no_repo_rows"
EXCLUSION_REASONS = (EXCLUSION_BELOW_FLOOR, EXCLUSION_NO_REPO_ROWS)


# Why one field of an admitted cross-section wrote no row in a vintage that
# would otherwise have re-totalled it: the closed vocabulary
# `CrossSectionCoverage.withheld_fields` records a reason under. The sibling of
# `EXCLUSION_REASONS` one level down -- that one says why a whole cross-section
# wrote nothing, this one says why a single field of an admitted cross-section
# did -- and it exists for the same reason: never a hole that looks like a quiet
# month, and never a zero. See `docs/DATA_QUALITY_DECISIONS.md`, "An empty repo
# cross-section is excluded, with its reason", and "The ON RRP channel is
# derived".
#
#   no_fed_counterparty  the cross-section's repo rows survived the amendment
#                        and none of the surviving submissions filed a Federal
#                        Reserve counterparty among them, so the derivation that
#                        supplies `mmf_on_rrp` had inputs and matched none of
#                        them
WITHHELD_NO_FED_COUNTERPARTY = "no_fed_counterparty"
WITHHELD_FIELD_REASONS = (WITHHELD_NO_FED_COUNTERPARTY,)


@dataclass(frozen=True)
class CrossSectionCoverage:
    """Reporting-entity coverage of one cross-section of a cross-sectional source.

    A source that publishes a periodic cross-section can emit a `ref_date` that
    is present, parseable and internally consistent while representing a small
    fraction of its universe. Missingness reporting cannot see it -- every row
    is there -- and an accounting identity holds just as well on a fraction of a
    market as on all of it. The only thing that distinguishes the two is how
    many entities reported, which is what this records.

    `entity_count` is a count of distinct reporting entities, never a value
    total: the values are the thing under suspicion, so a value threshold would
    be circular.

    `submission_types` is a corroborating record and never an input to the
    decision: how many submissions of each declared type the cross-section
    carries, as `(type, count)` pairs. It is free -- the source states it -- and
    it lets a reader see at a glance that an excluded month was a handful of
    amendments rather than a real month the floor got wrong. It must not become
    a filter: a legitimately amended complete month is entirely amendments and
    would be discarded by one.

    `absent_fields` names the panel series the archive could supply no
    observation of for this cross-section -- because it does not carry the table
    that holds them, or because the report month has no declared
    `INVESTMENTCATEGORY` vocabulary. It is not a coverage failure and does not
    affect `admitted`: an archive filed before 2024-06-10 carries no daily
    shareholder-flow table because the data did not exist, and its balance sheet
    is no less complete for it. Recording it is what keeps "we have no
    observation" from being read off the panel as "we observed nothing", which
    is the same absent-is-not-zero distinction one level up from the rows. For an
    assembled source it is judged on the archives retrieved up to this record's
    own, never on a later one.

    `unmatched_derived_fields` is a **third** kind of absence, not more entries
    in `absent_fields`, and that is why it is a separate field. `absent_fields`
    says the archive could supply no observation: the table is not there, or the
    report month has no declared vocabulary to read it with. This says the
    opposite about the input and the same thing about the output -- the table was
    present, readable and parsed, the field this one derives from *was* observed
    for this cross-section, and the derivation ran over those very rows and
    matched none of them. Folding the two together would lose the distinction
    that makes the second worth recording: "we could not look" and "we looked and
    found nothing" are different facts, and only the second is evidence about the
    market.

    Each entry is a `(field, disposition)` pair, the same shape as
    `submission_types` above, where `disposition` is one of
    `DERIVED_ABSENCE_DECLARED_ZERO` or `DERIVED_ABSENCE_UNDECLARED` -- whether
    the registry's structural-zero declaration for that field covers this
    cross-section's own `ref_date`, not whether one exists at all. That is
    the difference between "these funds held no Fed ON RRP" and "we never found
    it", which is the sentence the published limitation says this repository
    cannot currently write. It is recorded and never resolved: no `0.0` row is
    emitted either way, because coercing an absent declared field to zero
    destroys the distinction the structural-zero declaration exists to preserve.

    Like `absent_fields` it does not affect `admitted`, and it is recorded for
    excluded cross-sections as well as admitted ones. The record is a fact about
    what the adapter observed in the archive, not a claim about what the panel
    contains -- and a cross-section the floor dropped is precisely the one a
    reader may want to re-examine.

    `exclusion_reason` says why a cross-section was kept out of the panel, from
    the closed vocabulary `EXCLUSION_REASONS`, and is `None` when it was
    admitted. `below_floor` is the coverage floor, for both of the refusals
    `reason` tells apart by `era_id`. `no_repo_rows` is a cross-section that
    cleared the floor and whose holdings table was read, in a declared
    `INVESTMENTCATEGORY` era, without supplying a single repo holding. The fund
    industry always holds repo, so a month with none is a vocabulary failure
    until shown otherwise: it is excluded whole, every row with it, rather than
    admitted with a hole beside its balance sheet that reads as a quiet month --
    and never admitted with a zero. It is judged per vintage, so a later record
    of a month admitted earlier can read `no_repo_rows` beside the earlier
    record that reads `None`. It is not `absent_fields`. A missing table or
    an undeclared category era means the archive could not be looked at, and that
    stays a recorded absence on an admitted cross-section, as it was. An unknown
    reason raises `ValueError`: a record whose reason nobody declared is a reason
    nobody can read.

    `withheld_fields` is `exclusion_reason` one level down, and the level is the
    whole of the difference. An amendment can leave a cross-section rightly
    admitted -- its repo rows are all still there -- while removing every
    submission that supplied one *derived* field of it. Re-totalling that field
    over the submissions that are left writes `0.0`: the never-a-zero trap
    reached through supersession by way of the derived field rather than the
    required one, which the per-vintage exclusion does not reach because there is
    nothing to exclude. Such a field writes no row for that vintage and names its
    cause here, as `(field, reason)` pairs from the closed vocabulary
    `WITHHELD_FIELD_REASONS`, with an unknown reason refused by `ValueError`
    exactly as `exclusion_reason` refuses one.

    It is recorded on the vintage that withheld the row and on no other: it says
    what this archive did to a cell an earlier vintage carried, not a standing
    property of the cross-section. That is what keeps it from restating
    `unmatched_derived_fields` under a second name -- that one says the
    derivation ran over observed inputs and matched none of them, which is true
    of every vintage in which it holds, whether or not a row was ever written. A
    first vintage that never matched the Fed records that one and not this one:
    nothing was withheld, because nothing was going to be written.
    """

    source_id: str
    ref_date: date
    entity_unit: str
    entity_count: int
    declared_floor: Optional[int]
    admitted: bool
    row_count: int
    submission_types: tuple = ()
    absent_fields: tuple = ()
    era_id: Optional[str] = None
    unmatched_derived_fields: tuple = ()
    exclusion_reason: Optional[str] = None
    withheld_fields: tuple = ()

    def __post_init__(self) -> None:
        if (
            self.exclusion_reason is not None
            and self.exclusion_reason not in EXCLUSION_REASONS
        ):
            raise ValueError(
                f"{self.source_id} {self.ref_date.isoformat()}: cross-section "
                f"exclusion reason {self.exclusion_reason!r} is not one of "
                f"{', '.join(EXCLUSION_REASONS)}"
            )
        for field, reason in self.withheld_fields:
            if reason not in WITHHELD_FIELD_REASONS:
                raise ValueError(
                    f"{self.source_id} {self.ref_date.isoformat()}: withheld "
                    f"field {field!r} reason {reason!r} is not one of "
                    f"{', '.join(WITHHELD_FIELD_REASONS)}"
                )

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "ref_date": self.ref_date.isoformat(),
            "entity_unit": self.entity_unit,
            "entity_count": self.entity_count,
            "declared_floor": self.declared_floor,
            "era_id": self.era_id,
            "rows": self.row_count,
            "submission_types": {
                str(name): int(count) for name, count in self.submission_types
            },
            "absent_fields": list(self.absent_fields),
            # Its own key, for the same reason it is its own field: a reader who
            # cannot tell "the table was not there" from "the table was there and
            # the derivation matched nothing" will read the second as the first,
            # and the second is the one that carries information.
            "unmatched_derived_fields": [
                {"field": str(field), "disposition": str(disposition)}
                for field, disposition in self.unmatched_derived_fields
            ],
            "exclusion_reason": self.exclusion_reason,
            # Its own key, beside `unmatched_derived_fields` rather than inside
            # it: "the derivation matched nothing" and "this vintage withheld a
            # row an earlier vintage carried" are different facts, and only the
            # second says a `0.0` was declined here.
            "withheld_fields": [
                {"field": str(field), "reason": str(reason)}
                for field, reason in self.withheld_fields
            ],
            "reason": self.reason,
        }

    @property
    def reason(self) -> str:
        """Why this cross-section was refused, or why it was admitted.

        Two refusals, and they are not the same finding. A cross-section below
        its era's floor is a straggler cohort: the floor did its job. A
        cross-section whose `ref_date` falls in no declared era is a gap in the
        registry, and reading it as "below the floor" would report a
        measurement where there was none -- the undeclared thing priced at
        zero, one level up from the values.
        """

        if self.era_id is None:
            return (
                "ref_date falls in no declared coverage era, so no floor "
                "applies to it; declare the era rather than admitting it"
            )
        if self.exclusion_reason == EXCLUSION_NO_REPO_ROWS:
            return (
                "holdings table read in a declared INVESTMENTCATEGORY era "
                "supplied no repo holding, so the cross-section is excluded "
                f"rather than admitted without one (era {self.era_id})"
            )
        if not self.admitted:
            return (
                "reporting entities below the coverage floor declared in the "
                f"source registry for era {self.era_id}"
            )
        return f"admitted against the declared floor for era {self.era_id}"


# Why a source cell yielded no observation: the closed vocabulary every adapter
# in `repo_model.ingest` records an absent cell under. Each reason names the
# token the cell carried, never a guess at what the publisher meant by it -- the
# SEC's N-MFP readme defines no missing-value token at all, so `dot` there says
# what was in the file and nothing more. See `docs/DATA_QUALITY_DECISIONS.md`,
# "An absent value keeps its reason".
#
#   blank       an empty cell, or none at all where a row stops short
#   na          `NA` or `N/A`
#   dot         `.` -- FRED's documented missing observation
#   null        Fiscal Data's string `"null"`, a result not yet published
#   suppressed  FR 2004's `*`, a figure withheld for confidentiality
ABSENCE_BLANK = "blank"
ABSENCE_NA = "na"
ABSENCE_DOT = "dot"
ABSENCE_NULL = "null"
ABSENCE_SUPPRESSED = "suppressed"
ABSENCE_REASONS = (
    ABSENCE_BLANK,
    ABSENCE_NA,
    ABSENCE_DOT,
    ABSENCE_NULL,
    ABSENCE_SUPPRESSED,
)


@dataclass(frozen=True)
class AbsentCell:
    """One source cell that yielded no observation, and the reason it was read as absent.

    Recorded by the adapter at the moment it reads the token, because that is
    the only moment the token is known. A hole in the panel never knew whether
    its cell was blank, `.`, not yet published or suppressed, so a reason
    reconstructed from the panel afterwards would be a guess.

    `field` is the panel series the cell would have supplied. `ref_date` is the
    date that observation would have carried as read -- the as-of, observation
    or quote date, or for a Form N-MFP balance-sheet or holdings cell the
    `REPORTDATE` it was filed under. `source_sha` names the snapshot, so the
    same cell read from two retrievals is two records and not one counted twice.
    """

    source_id: str
    field: str
    ref_date: date
    reason: str
    source_sha: str

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "field": self.field,
            "ref_date": self.ref_date.isoformat(),
            "reason": self.reason,
            "source_sha": self.source_sha,
        }


@dataclass(frozen=True)
class AbsentCellRun:
    """A maximal stretch of absent cells, as the quality report records them.

    One run per snapshot (`source_sha`), field and reason, over consecutive rows
    of that field in the adapter's own row sequence: the rows it read the field
    at, in the order it read them. A row that carried a value ends the run, and
    so does a row absent for another reason. A date the source never wrote a
    row for -- a weekend or a holiday in a business-daily file -- is not a row,
    so it neither ends a run nor counts in one.

    `count` is rows, never calendar days. `first` and `last` are the dates of
    the run's first and last rows in that same order, so a file read newest
    first, as Treasury's bill rates are, has `first` after `last`. `row` is the
    position of the first row in its field's row sequence, counted from zero
    within the snapshot. The dates alone cannot place a run: Form N-MFP reads
    one row per filer, many filers share a `REPORTDATE`, and filer order is not
    date order, so the same first date, last date and count can name different
    rows. `absent_cells_from_quality_report` expands a run back into its cells.
    """

    source_id: str
    source_sha: str
    field: str
    reason: str
    first: date
    last: date
    count: int
    row: int

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "source_sha": self.source_sha,
            "field": self.field,
            "reason": self.reason,
            "first": self.first.isoformat(),
            "last": self.last.isoformat(),
            "count": self.count,
            "row": self.row,
        }


class AbsentCellRecorder:
    """Every cell an adapter reads, collapsed into `AbsentCellRun`s as it is read.

    `append` takes an absent cell -- the call a plain list of `AbsentCell`
    answers too -- and `value` takes a cell that carried a value, which is the
    only thing that tells a run it has ended. `cells` keeps every absent cell,
    one record each. With `keep_row_dates`, `row_dates` maps each
    `(source_id, source_sha, field)` to the date of every row read, in order,
    which is what expanding a run needs; a build does not keep them.
    """

    def __init__(self, *, keep_row_dates: bool = False):
        self.cells: List[AbsentCell] = []
        self.row_dates: Optional[Dict[tuple, List[date]]] = (
            {} if keep_row_dates else None
        )
        self._closed: List[AbsentCellRun] = []
        self._open: Dict[tuple, list] = {}
        self._rows: Dict[tuple, int] = {}

    def append(self, cell: AbsentCell) -> None:
        self.cells.append(cell)
        self._read(
            cell.source_id, cell.source_sha, cell.field, cell.ref_date, cell.reason
        )

    def value(
        self, source_id: str, source_sha: str, field: str, ref_date: date
    ) -> None:
        self._read(source_id, source_sha, field, ref_date, None)

    def _read(self, source_id, source_sha, field, ref_date, reason) -> None:
        rows = (source_id, source_sha, field)
        row = self._rows.get(rows, 0)
        self._rows[rows] = row + 1
        if self.row_dates is not None:
            self.row_dates.setdefault(rows, []).append(ref_date)
        # What a run may extend across: one field of one snapshot. The same
        # field read from another retrieval starts a run of its own.
        key = (source_id, source_sha, field)
        run = self._open.get(key)
        if run is not None and run[0] == reason:
            run[2] = ref_date
            run[3] += 1
            return
        if run is not None:
            self._close(key)
        if reason is not None:
            self._open[key] = [reason, ref_date, ref_date, 1, row, source_sha]

    def _close(self, key) -> None:
        self._closed.append(_absent_cell_run(key, self._open.pop(key)))

    def runs(self) -> tuple:
        """Every run, closed or still open, in report order."""

        pending = [_absent_cell_run(key, state) for key, state in self._open.items()]
        return tuple(sorted(self._closed + pending, key=_absent_cell_run_order))


def _absent_cell_run(key: tuple, state: list) -> AbsentCellRun:
    reason, first, last, count, row, source_sha = state
    return AbsentCellRun(
        source_id=key[0],
        source_sha=source_sha,
        field=key[-1],
        reason=reason,
        first=first,
        last=last,
        count=count,
        row=row,
    )


def _absent_cell_run_order(run: AbsentCellRun):
    return (run.source_id, run.source_sha, run.field, run.row)


def absent_cells_from_quality_report(
    report: Mapping[str, object],
    row_dates: Mapping[tuple, Sequence[date]],
) -> tuple:
    """Read a quality report's absent-cell runs back into one `AbsentCell` per cell.

    `row_dates` is the snapshots' row sequences, as `AbsentCellRecorder` keeps
    them -- a run records where its rows are, not what they are dated, so the
    snapshot it was read from is what expands it. A run is refused when its
    `count` rows, taken from `row`, do not run from `first` to `last`: a count
    that disagrees with the stretch it names -- calendar days for rows, say --
    expands to cells nobody read.
    """

    cells = []
    for run in report["absent_cells"]["runs"]:
        key = (run["source_id"], run["source_sha"], run["field"])
        first = date.fromisoformat(run["first"])
        last = date.fromisoformat(run["last"])
        count = run["count"]
        row = run["row"]
        expanded = list(row_dates.get(key, ())[row : row + count])
        if len(expanded) != count or expanded[0] != first or expanded[-1] != last:
            raise ValueError(
                f"absent-cell run {run['source_id']} {run['field']} "
                f"{run['reason']} at row {row} records {count} rows from "
                f"{first} to {last}, and its snapshot's rows from row {row} "
                f"do not: {len(expanded)} rows"
                + (f" from {expanded[0]} to {expanded[-1]}" if expanded else "")
            )
        cells.extend(
            AbsentCell(
                source_id=run["source_id"],
                field=run["field"],
                ref_date=ref_date,
                reason=run["reason"],
                source_sha=run["source_sha"],
            )
            for ref_date in expanded
        )
    return tuple(cells)


# The three answers a declared identity can give about one `ref_date`. There
# used to be two, and the missing one was not "violated" -- it was this:
#
#   held           every declared term was observed and the residual is within
#                  the declared tolerance
#   violated       every declared term was observed and the residual is not
#   not_evaluable  at least one declared term has no observation for that
#                  `ref_date`, so no residual exists to compare
#
# `not_evaluable` is the one that has to be named. A check that never ran and a
# check that passed are indistinguishable from the outside unless the code says
# which happened, and the failure mode this repo keeps meeting is a guard that
# reads as vigilance because nothing recorded that its input was absent. It is
# the degenerate case of an identity anchored to the thing it is checking: not a
# check that cannot fail because both sides moved together, but a check that
# cannot fail because it has no terms.
IDENTITY_HELD = "held"
IDENTITY_VIOLATED = "violated"
IDENTITY_NOT_EVALUABLE = "not_evaluable"

# The verdict an identity earns over a whole panel when some of its reference
# dates could not be checked. Deliberately not spelled `held`, and deliberately
# not `not_evaluable` either: both would be false. It held where it ran, and a
# caller testing for `held` gets a mismatch, which is the point.
IDENTITY_HELD_WHERE_EVALUABLE = "held_where_evaluable"


@dataclass(frozen=True)
class UnevaluatedIdentity:
    """One `(source, identity, ref_date)` the identity could not be checked on.

    `absent_fields` names the declared terms that have no observation for that
    `ref_date`. Recording the verdict without the terms would be a claim a
    reader cannot act on -- "it did not evaluate" says nothing about whether the
    remedy is a field mapping, a missing table, or a source that never collected
    the column. It is the same reason `CrossSectionCoverage.absent_fields`
    exists, one level up: an absence is only legible once it is named.

    The absent term is never read as `0.0` to make the sum evaluate. An identity
    that "holds" because a missing term was substituted with a zero is strictly
    worse than one that visibly did not run, because the first destroys the
    evidence that anything was missing.

    `era_id` names the `IdentityEra` whose terms were the ones looked for, and
    `undeclared_ref_date` is the second, different way a date can go unchecked:
    it fell in no declared era at all, so there was no term list to look for.
    Recording those two as one verdict with no distinguishing field would be the
    defect `absent_fields` was added to fix, one level out -- "a term was
    withheld this week" and "this repository has declared nothing about this
    week" have different remedies, and only the record says which. `reason` is a
    property for the same reason `CrossSectionCoverage.reason` is: the two
    refusals are not the same finding and the sentence has to say which one
    happened.
    """

    source_id: str
    identity: str
    ref_date: date
    absent_fields: tuple = ()
    era_id: Optional[str] = None
    undeclared_ref_date: bool = False

    @property
    def reason(self) -> str:
        if self.undeclared_ref_date:
            return (
                "this reference date falls in no declared era of this "
                "identity, so no component set applies to it; declare the era "
                "rather than checking the date against another era's terms"
            )
        return (
            "a declared term of this identity has no observation for this "
            "reference date; the identity was not checked"
        )

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "identity": self.identity,
            "ref_date": self.ref_date.isoformat(),
            "verdict": IDENTITY_NOT_EVALUABLE,
            "absent_fields": list(self.absent_fields),
            "era_id": self.era_id,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ViolatedIdentity:
    """One `(source, identity, ref_date)` the identity was checked on and failed.

    The fourth outcome, recorded the way `UnevaluatedIdentity` records the
    third. Every declared term was observed, so a residual exists -- and unlike
    an unevaluable date this one has a number. The number is only readable next
    to the bound it was measured against, which is why both are carried. A bare
    `violated` would be the defect `absent_fields` was added one class up to
    fix: a verdict a reader cannot act on, because 0.312 against a bound of 0.5
    and 0.312 against a bound of 0.0001 are different findings and only the pair
    says which.

    Recording is not tolerating. `build_daily_panel` raises on a violation in a
    source it actually built a column from; see rule 5 there, and
    `docs/DATA_QUALITY_DECISIONS.md`, "Whether a source may abort a build it
    contributes nothing to". The abort had to move because the hop that
    evaluates identities runs before any wide panel exists and therefore cannot
    know which sources a panel depends on. This record is what lets the hop that
    does know ask.
    """

    source_id: str
    identity: str
    ref_date: date
    residual: float
    bound: float

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "identity": self.identity,
            "ref_date": self.ref_date.isoformat(),
            "verdict": IDENTITY_VIOLATED,
            "residual": self.residual,
            "bound": self.bound,
            "reason": (
                "every declared term of this identity was observed for this "
                "reference date and the residual exceeds the declared tolerance"
            ),
        }


@dataclass(frozen=True)
class IdentityEvaluation:
    """What one declared identity actually established over a panel.

    This replaces a bare maximum residual as the thing a caller reads to learn
    "the identities are fine". A float alone cannot answer the question, because
    it is computed only over the reference dates where every term was present
    and carries no trace of the ones where it was not -- so a panel whose first
    5.5 years cannot be checked at all reports exactly the same number as one
    that was checked throughout.

    `verdict` is therefore `held` only when nothing was left unchecked. When
    some reference dates could not be evaluated it is
    `held_where_evaluable`, which no caller can mistake for the former. When any
    reference date was checked and failed it is `violated`, and that answer
    outranks the other two: a panel-level `held_where_evaluable` on an identity
    that failed somewhere would be the same lie by omission, one outcome later.

    `maximum_residual` is the largest residual over every date that produced
    one, **violating dates included**. That is a deliberate choice and it
    reverses nothing: until this class carried violations the function raised on
    the first one, so the field had never seen a violating residual and could
    not have. Keeping it over the passing dates only would have made it a
    summary statistic that cannot report the worst thing it summarises -- a
    number that goes *down* as the data gets worse. It is pinned by
    `IdentityVerdictTests.test_the_maximum_residual_does_not_exclude_the_violating_dates`.
    """

    source_id: str
    name: str
    maximum_residual: Optional[float]
    evaluated_ref_dates: int
    unevaluated: tuple = ()
    violations: tuple = ()

    @property
    def verdict(self) -> str:
        if self.violations:
            return IDENTITY_VIOLATED
        if self.unevaluated:
            return IDENTITY_HELD_WHERE_EVALUABLE
        return IDENTITY_HELD

    @property
    def violated_ref_dates(self) -> tuple:
        """Every reference date this identity was checked on and failed."""

        return tuple(sorted({item.ref_date for item in self.violations}))

    @property
    def fully_evaluated(self) -> bool:
        return not self.unevaluated

    @property
    def absent_fields(self) -> tuple:
        """Every declared term absent on at least one unevaluated date."""

        names: set = set()
        for item in self.unevaluated:
            names.update(item.absent_fields)
        return tuple(sorted(names))

    @property
    def undeclared_ref_dates(self) -> tuple:
        """Every reference date that fell in no declared era of this identity.

        Kept apart from `absent_fields` deliberately: such a date names no
        absent term, because with no era covering it there was no list of terms
        to find one absent from. Folding it in would report an empty absence
        list as "nothing was missing".
        """

        return tuple(
            sorted(
                {item.ref_date for item in self.unevaluated if item.undeclared_ref_date}
            )
        )

    def as_dict(self) -> Mapping[str, object]:
        return {
            "verdict": self.verdict,
            "maximum_residual": self.maximum_residual,
            "evaluated_ref_dates": self.evaluated_ref_dates,
            "unevaluated_ref_dates": [item.as_dict() for item in self.unevaluated],
            # The dates, not a count. A count is exactly what let 5.5 years of
            # an unchecked balance sheet read as one number, and a violation is
            # not less actionable than an absence.
            "violated_ref_dates": [item.as_dict() for item in self.violations],
        }


@dataclass(frozen=True)
class PointInTimeAuditReport:
    row_count: int
    reference_date_count: int
    start_date: date
    end_date: date
    series: Mapping[str, SeriesQuality]
    missing_series: Mapping[str, int]
    warnings: Sequence[str]
    excluded_cross_sections: Sequence[CrossSectionCoverage] = ()
    unevaluated_identities: Sequence[UnevaluatedIdentity] = ()
    violated_identities: Sequence[ViolatedIdentity] = ()
    absent_cell_runs: Sequence[AbsentCellRun] = ()

    def as_dict(self) -> Mapping[str, object]:
        counts = {reason: 0 for reason in ABSENCE_REASONS}
        for run in self.absent_cell_runs:
            counts[run.reason] += run.count
        return {
            "rows": self.row_count,
            "reference_dates": self.reference_date_count,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "series": {
                series_id: {
                    "observations": quality.observation_count,
                    "reference_dates": quality.reference_date_count,
                    "start_date": quality.start_date.isoformat(),
                    "end_date": quality.end_date.isoformat(),
                    "missing_reference_dates": quality.missing_reference_dates,
                    "missing_rate": quality.missing_rate,
                    "revised_reference_dates": quality.revised_reference_dates,
                    "revision_rows": quality.revision_rows,
                    "largest_absolute_revision": quality.largest_absolute_revision,
                }
                for series_id, quality in sorted(self.series.items())
            },
            "missing_series": dict(sorted(self.missing_series.items())),
            # Deliberately its own key, never folded into `missing_series` or a
            # series' `missing_reference_dates`. "We declined to admit this
            # cross-section" and "this cross-section had gaps" are different
            # facts about the data, the same way a structural zero and a missing
            # observation are, and a reader has to be able to tell them apart.
            "excluded_cross_sections": [
                coverage.as_dict()
                for coverage in sorted(
                    self.excluded_cross_sections,
                    key=lambda item: (item.source_id, item.ref_date),
                )
            ],
            # Its own key for the same reason excluded_cross_sections is its
            # own key. "This identity was checked and held" and "this identity
            # was not checked" are different facts, and a reader who cannot
            # tell them apart will read the second as the first -- which is
            # the whole defect this records.
            "unevaluated_identities": [
                item.as_dict()
                for item in sorted(
                    self.unevaluated_identities,
                    key=lambda item: (item.source_id, item.identity, item.ref_date),
                )
            ],
            # Its own key again, and for the third time the same reason. "Held",
            # "not checked" and "checked and failed" are three different facts,
            # and this one used to reach a reader as a traceback and a build
            # that stopped -- which is a report only for whoever was watching
            # the build. Every violating reference date is named, with its
            # residual and its bound, because a count of violations is not
            # something anyone can act on.
            "violated_identities": [
                item.as_dict()
                for item in sorted(
                    self.violated_identities,
                    key=lambda item: (item.source_id, item.identity, item.ref_date),
                )
            ],
            # Every source cell that yielded no observation, with the reason it
            # was read as absent, and a count per reason -- every reason in the
            # vocabulary, so a zero is stated rather than left to be inferred.
            # Its own key, never folded into `missing_reference_dates`: that
            # counts holes in the panel, and a hole does not know its token.
            # The cells are written as runs of consecutive rows, which expand
            # back to one record per cell; one record per cell made a FRED
            # graph CSV's pre-inception blanks twelve megabytes of report.
            "absent_cells": {
                "counts": counts,
                "runs": [
                    run.as_dict()
                    for run in sorted(
                        self.absent_cell_runs, key=_absent_cell_run_order
                    )
                ],
            },
            "warnings": list(self.warnings),
        }


def _parse_float(raw: str, field: str, row_number: int) -> Optional[float]:
    value = raw.strip()
    if value == "":
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise DataContractError(
            f"row {row_number}: {field!r} must be numeric, got {raw!r}"
        ) from exc
    if not math.isfinite(parsed):
        raise DataContractError(f"row {row_number}: {field!r} must be finite")
    return parsed


def load_daily_panel(path: Path) -> List[DailyObservation]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataContractError("CSV has no header")
        missing_headers = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_headers:
            raise DataContractError(f"missing required columns: {', '.join(missing_headers)}")

        observations: List[DailyObservation] = []
        numeric_fields = [field for field in reader.fieldnames if field != "date"]
        for row_number, row in enumerate(reader, start=2):
            try:
                observation_date = date.fromisoformat(row["date"].strip())
            except (AttributeError, ValueError) as exc:
                raise DataContractError(
                    f"row {row_number}: date must use YYYY-MM-DD"
                ) from exc
            values = {
                field: _parse_float(row.get(field, ""), field, row_number)
                for field in numeric_fields
            }
            for field in ("sofr", "iorb"):
                if values.get(field) is None:
                    raise DataContractError(f"row {row_number}: {field!r} is required")
            observations.append(DailyObservation(observation_date, values))

    if not observations:
        raise DataContractError("CSV contains no observations")
    return observations


def _required_text(row: Mapping[str, Optional[str]], field: str, row_number: int) -> str:
    raw = row.get(field)
    value = raw.strip() if raw is not None else ""
    if not value:
        raise DataContractError(f"row {row_number}: {field!r} is required")
    return value


def _parse_available_at(raw: str, row_number: int) -> datetime:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataContractError(
            f"row {row_number}: 'available_at' must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DataContractError(
            f"row {row_number}: 'available_at' must include a UTC offset"
        )
    return parsed


def load_point_in_time_panel(
    path: Path,
    *,
    cutoff: Optional[datetime] = None,
) -> List[PointInTimeObservation]:
    """Load the canonical long panel, optionally filtered by observable cutoff.

    Revisions remain separate rows. Filtering is based only on ``available_at``;
    the loader never fills or carries values across reference dates.
    """

    if cutoff is not None and (cutoff.tzinfo is None or cutoff.utcoffset() is None):
        raise DataContractError("cutoff must include a UTC offset")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataContractError("CSV has no header")
        if len(reader.fieldnames) != len(POINT_IN_TIME_FIELDS) or set(
            reader.fieldnames
        ) != set(POINT_IN_TIME_FIELDS):
            raise DataContractError(
                "point-in-time CSV columns must be exactly: "
                + ", ".join(POINT_IN_TIME_FIELDS)
            )

        observations: List[PointInTimeObservation] = []
        for row_number, row in enumerate(reader, start=2):
            series_id = _required_text(row, "series_id", row_number)
            raw_ref_date = _required_text(row, "ref_date", row_number)
            try:
                ref_date = date.fromisoformat(raw_ref_date)
            except ValueError as exc:
                raise DataContractError(
                    f"row {row_number}: 'ref_date' must use YYYY-MM-DD"
                ) from exc
            available_at = _parse_available_at(
                _required_text(row, "available_at", row_number),
                row_number,
            )
            value = _parse_float(
                _required_text(row, "value", row_number),
                "value",
                row_number,
            )
            if value is None:  # pragma: no cover - _required_text rules this out
                raise DataContractError(f"row {row_number}: 'value' is required")
            vintage_id = _required_text(row, "vintage_id", row_number)
            source_sha = _required_text(row, "source_sha", row_number)
            if not SHA256_PATTERN.fullmatch(source_sha):
                raise DataContractError(
                    f"row {row_number}: 'source_sha' must be a lowercase SHA-256 digest"
                )
            observations.append(
                PointInTimeObservation(
                    series_id=series_id,
                    ref_date=ref_date,
                    available_at=available_at,
                    value=value,
                    vintage_id=vintage_id,
                    source_sha=source_sha,
                )
            )

    if not observations:
        raise DataContractError("point-in-time CSV contains no observations")

    availability = [row.available_at for row in observations]
    if availability != sorted(availability):
        raise DataContractError("point-in-time rows must be appended in availability order")

    vintage_keys = [(row.series_id, row.ref_date, row.vintage_id) for row in observations]
    if len(vintage_keys) != len(set(vintage_keys)):
        raise DataContractError("duplicate series/ref_date/vintage_id row")

    publication_keys = [
        (row.series_id, row.ref_date, row.available_at) for row in observations
    ]
    if len(publication_keys) != len(set(publication_keys)):
        raise DataContractError("duplicate series/ref_date/available_at row")

    if cutoff is None:
        return observations
    return [row for row in observations if row.available_at <= cutoff]


def audit_point_in_time_panel(
    observations: Iterable[PointInTimeObservation],
    *,
    expected_ref_dates: Optional[Mapping[str, Iterable[date]]] = None,
    excluded_cross_sections: Optional[Iterable[CrossSectionCoverage]] = None,
    unevaluated_identities: Optional[Iterable[UnevaluatedIdentity]] = None,
    violated_identities: Optional[Iterable[ViolatedIdentity]] = None,
    absent_cell_runs: Optional[Iterable[AbsentCellRun]] = None,
) -> PointInTimeAuditReport:
    """Summarize coverage and revisions without treating a revision as coverage.

    By default, missingness is measured against the union of dates represented by
    the supplied panel. Callers with a source calendar may pass a per-series date
    grid in ``expected_ref_dates``; this is preferable for low-frequency series.
    No value is imputed or carried forward by this report.
    """

    rows = list(observations)
    if not rows:
        raise DataContractError("point-in-time panel contains no observations")
    if [row.available_at for row in rows] != sorted(row.available_at for row in rows):
        raise DataContractError("point-in-time rows must be appended in availability order")

    panel_dates = sorted({row.ref_date for row in rows})
    by_series: Dict[str, List[PointInTimeObservation]] = {}
    for row in rows:
        by_series.setdefault(row.series_id, []).append(row)

    series_report: Dict[str, SeriesQuality] = {}
    warnings: List[str] = []
    for series_id, series_rows in sorted(by_series.items()):
        by_reference: Dict[date, List[PointInTimeObservation]] = {}
        for row in series_rows:
            by_reference.setdefault(row.ref_date, []).append(row)
        reference_dates = sorted(by_reference)
        if expected_ref_dates is None:
            expected = set(panel_dates)
        else:
            expected = set(expected_ref_dates.get(series_id, reference_dates))
        observed = set(reference_dates)
        missing = len(expected - observed)
        denominator = len(expected)
        revised = 0
        revision_rows = 0
        largest_revision: Optional[float] = None
        for ref_date, vintages in by_reference.items():
            ordered = sorted(vintages, key=lambda row: row.available_at)
            if len(ordered) <= 1:
                continue
            revised += 1
            revision_rows += len(ordered) - 1
            for previous, current in zip(ordered, ordered[1:]):
                magnitude = abs(current.value - previous.value)
                largest_revision = (
                    magnitude
                    if largest_revision is None
                    else max(largest_revision, magnitude)
                )
            if any(
                current.available_at <= previous.available_at
                for previous, current in zip(ordered, ordered[1:])
            ):
                warnings.append(
                    f"{series_id} {ref_date}: revisions do not have increasing availability"
                )
        series_report[series_id] = SeriesQuality(
            series_id=series_id,
            observation_count=len(series_rows),
            reference_date_count=len(reference_dates),
            start_date=reference_dates[0],
            end_date=reference_dates[-1],
            missing_reference_dates=missing,
            missing_rate=(missing / denominator if denominator else 0.0),
            revised_reference_dates=revised,
            revision_rows=revision_rows,
            largest_absolute_revision=largest_revision,
        )

    return PointInTimeAuditReport(
        row_count=len(rows),
        reference_date_count=len(panel_dates),
        start_date=panel_dates[0],
        end_date=panel_dates[-1],
        series=series_report,
        missing_series={
            series_id: len(set(expected_dates))
            for series_id, expected_dates in (expected_ref_dates or {}).items()
            if series_id not in by_series
        },
        warnings=warnings,
        excluded_cross_sections=tuple(excluded_cross_sections or ()),
        unevaluated_identities=tuple(unevaluated_identities or ()),
        violated_identities=tuple(violated_identities or ()),
        absent_cell_runs=tuple(absent_cell_runs or ()),
    )


def expected_ref_dates_from_registry(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, Sequence[date]]:
    """Build per-series coverage grids from declared native-frequency peers.

    Within each source and cadence, the most complete series is the reference
    calendar. This avoids comparing a weekly series with a daily series or a
    2018-start series with a 1954-start series. It also respects actual source
    holidays without silently inventing a holiday calendar.
    """

    rows = list(observations)
    dates_by_series: Dict[str, set[date]] = {}
    for row in rows:
        dates_by_series.setdefault(row.series_id, set()).add(row.ref_date)

    expected: Dict[str, Sequence[date]] = {}
    declared_fields: set[str] = set()
    for source_id, source in registry.items():
        raw_frequencies = source.get("field_frequencies")
        if not isinstance(raw_frequencies, Mapping):
            continue
        fields = [str(field) for field in source.get("fields", [])]
        if set(raw_frequencies) != set(fields):
            raise DataContractError(
                f"{source_id}: field_frequencies must declare every source field"
            )
        overlap = declared_fields.intersection(fields)
        if overlap:
            raise DataContractError(
                f"series belong to multiple field-frequency declarations: {sorted(overlap)}"
            )
        declared_fields.update(fields)
        by_frequency: Dict[str, List[str]] = {}
        for field in fields:
            frequency = raw_frequencies[field]
            if frequency not in {
                "calendar_daily", "business_daily", "weekly", "monthly", "event"
            }:
                raise DataContractError(
                    f"{source_id}: unsupported frequency {frequency!r} for {field}"
                )
            by_frequency.setdefault(str(frequency), []).append(field)
        for frequency, peers in by_frequency.items():
            present = [field for field in peers if dates_by_series.get(field)]
            if not present:
                continue
            anchor = max(present, key=lambda field: len(dates_by_series[field]))
            anchor_dates = dates_by_series[anchor]
            absent = [field for field in peers if field not in present]
            for field in absent:
                expected[field] = tuple(sorted(anchor_dates))
            for field in present:
                own_dates = dates_by_series[field]
                if frequency == "event":
                    expected[field] = tuple(sorted(own_dates))
                    continue
                start, end = min(own_dates), max(own_dates)
                expected[field] = tuple(
                    sorted(value for value in anchor_dates if start <= value <= end)
                )

    for series_id, observed in dates_by_series.items():
        expected.setdefault(series_id, tuple(sorted(observed)))
    return expected


def write_point_in_time_audit_report(
    observations: Iterable[PointInTimeObservation],
    path: Path,
    *,
    expected_ref_dates: Optional[Mapping[str, Iterable[date]]] = None,
    excluded_cross_sections: Optional[Iterable[CrossSectionCoverage]] = None,
    unevaluated_identities: Optional[Iterable[UnevaluatedIdentity]] = None,
    violated_identities: Optional[Iterable[ViolatedIdentity]] = None,
    absent_cell_runs: Optional[Iterable[AbsentCellRun]] = None,
) -> PointInTimeAuditReport:
    """Write a deterministic JSON missingness/revision report."""

    report = audit_point_in_time_panel(
        observations,
        expected_ref_dates=expected_ref_dates,
        excluded_cross_sections=excluded_cross_sections,
        unevaluated_identities=unevaluated_identities,
        violated_identities=violated_identities,
        absent_cell_runs=absent_cell_runs,
    )
    payload = json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    return report


#: How a coverage era declares its bounds. Inclusive at both ends, and a
#: calendar month rather than a date, because the cross-section a floor judges
#: is a calendar month -- see `_nmfp_cross_section`. Declaring a bound as a date
#: would invite the reader to believe a floor can change mid-month.
COVERAGE_ERA_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

COVERAGE_ERA_KEYS = frozenset(
    {
        "era_id",
        "start",
        "end",
        "minimum_reporting_entities",
        "observed_minimum_entities",
        "observed_complete_months",
        "note",
    }
)


@dataclass(frozen=True)
class CoverageEra:
    """One declared era of a source's reporting universe, and its floor.

    `minimum_reporting_entities` is the floor. The other two numbers are what
    it was calibrated from and are carried beside it deliberately: a floor
    whose calibration input is not stated is a number nobody can check, and
    the registry has already been through one round of exactly that.

    Bounds are inclusive `YYYY-MM` strings. They are *declared*, never derived
    from the counts the floor judges -- a floor that infers its own eras from
    the data it is guarding is the anchoring failure this repository keeps
    finding, and `validate_coverage_eras` refuses a declaration that leaves
    any month between the first and last era unclaimed rather than letting one
    be filled in by proximity.
    """

    era_id: str
    start: str
    end: str
    minimum_reporting_entities: int
    observed_minimum_entities: int
    observed_complete_months: int
    note: str = ""

    def contains(self, ref_date: date) -> bool:
        return self.start <= f"{ref_date.year:04d}-{ref_date.month:02d}" <= self.end


@dataclass(frozen=True)
class CoverageFloor:
    """A source's declared coverage floors, one per era of its universe.

    Replaces the `(entity_unit, floor)` pair this function used to return. That
    pair bundled two scalars that always travelled together; the floor is no
    longer a scalar, and returning `(entity_unit, something_with_methods)`
    would keep the shape of an answer that no longer exists.

    There is exactly one way to ask for a floor -- `era_for` -- and it returns
    `None` for a `ref_date` in no declared era rather than a number. A second
    accessor that raised, or one that fell back to the nearest era, would be a
    second reading of the same question, and the fallback is the silent zero
    this repository legislates against: an undeclared date admitted on a floor
    that was calibrated for a different universe.
    """

    entity_unit: str
    eras: tuple

    def era_for(self, ref_date: date) -> Optional[CoverageEra]:
        """The era governing `ref_date`, or `None` if none declares it."""

        for era in self.eras:
            if era.contains(ref_date):
                return era
        return None


def validate_coverage_eras(source_id: str, declared: object) -> tuple:
    """Read and check a source's declared eras, or say exactly what is wrong.

    Every branch here is a way the declaration can stop guarding while still
    looking like a declaration, so each one raises with its own message.
    """

    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        raise DataContractError(
            f"{source_id}: cross_section.eras must be a list of declared eras"
        )
    if not declared:
        raise DataContractError(
            f"{source_id}: cross_section.eras is empty; a source that emits "
            "cross-sections and declares no era has no floor anywhere"
        )
    eras = []
    for entry in declared:
        if not isinstance(entry, Mapping):
            raise DataContractError(
                f"{source_id}: each cross_section.eras entry must be an object"
            )
        unknown = sorted(set(entry) - COVERAGE_ERA_KEYS)
        if unknown:
            raise DataContractError(
                f"{source_id}: cross_section.eras entry has unpermitted keys "
                f"{unknown}"
            )
        missing = sorted(COVERAGE_ERA_KEYS - {"note"} - set(entry))
        if missing:
            raise DataContractError(
                f"{source_id}: cross_section.eras entry lacks required keys "
                f"{missing}"
            )
        era_id = entry["era_id"]
        if not isinstance(era_id, str) or not era_id.strip():
            raise DataContractError(
                f"{source_id}: cross_section.eras entry needs a non-empty era_id"
            )
        for key in ("start", "end"):
            bound = entry[key]
            if not isinstance(bound, str) or not COVERAGE_ERA_MONTH.match(bound):
                raise DataContractError(
                    f"{source_id}: era {era_id} has a {key} of {bound!r}; "
                    "bounds are inclusive YYYY-MM months"
                )
        if entry["start"] > entry["end"]:
            raise DataContractError(
                f"{source_id}: era {era_id} starts at {entry['start']} and ends "
                f"at {entry['end']}, which declares no months at all"
            )
        counts = {}
        for key in (
            "minimum_reporting_entities",
            "observed_minimum_entities",
            "observed_complete_months",
        ):
            value = entry[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise DataContractError(
                    f"{source_id}: era {era_id} {key} must be an integer"
                )
            counts[key] = value
        floor = counts["minimum_reporting_entities"]
        if floor < 1:
            # The prohibited silent zero, written down as data. A floor of 0
            # admits every cross-section and reads, to the next person, as a
            # check that ran.
            raise DataContractError(
                f"{source_id}: era {era_id} minimum_reporting_entities must be "
                f"at least 1; {floor} admits every cross-section and guards nothing"
            )
        if counts["observed_complete_months"] < 1:
            raise DataContractError(
                f"{source_id}: era {era_id} declares a floor calibrated from "
                "no observed month; state the months it was measured over"
            )
        if floor > counts["observed_minimum_entities"]:
            # A floor above the smallest complete month observed in its own era
            # refuses a month that era saw. Whatever it is guarding against, it
            # is not stragglers, and the number is wrong on its own evidence.
            raise DataContractError(
                f"{source_id}: era {era_id} floor {floor} exceeds the smallest "
                f"complete month it was calibrated from "
                f"({counts['observed_minimum_entities']}), so it refuses a "
                "cross-section its own calibration observed"
            )
        note = entry.get("note", "")
        if not isinstance(note, str):
            raise DataContractError(
                f"{source_id}: era {era_id} note must be a string"
            )
        eras.append(
            CoverageEra(
                era_id=era_id.strip(),
                start=entry["start"],
                end=entry["end"],
                minimum_reporting_entities=floor,
                observed_minimum_entities=counts["observed_minimum_entities"],
                observed_complete_months=counts["observed_complete_months"],
                note=note,
            )
        )
    eras.sort(key=lambda era: era.start)
    seen = set()
    for era in eras:
        if era.era_id in seen:
            raise DataContractError(
                f"{source_id}: cross_section.eras declares era_id {era.era_id!r} twice"
            )
        seen.add(era.era_id)
    for earlier, later in zip(eras, eras[1:]):
        if later.start <= earlier.end:
            raise DataContractError(
                f"{source_id}: eras {earlier.era_id} and {later.era_id} overlap "
                f"at {later.start}; one month cannot have two floors"
            )
        if _month_after(earlier.end) != later.start:
            # A gap between declared eras is worse than an undeclared tail: the
            # months in it look covered, because they lie inside the declared
            # range, and are refused anyway.
            raise DataContractError(
                f"{source_id}: eras {earlier.era_id} and {later.era_id} leave "
                f"{_month_after(earlier.end)} undeclared; declare every month "
                "between the first era and the last"
            )
    return tuple(eras)


def _month_after(month: str) -> str:
    year, index = int(month[:4]), int(month[5:])
    return f"{year + 1:04d}-01" if index == 12 else f"{year:04d}-{index + 1:02d}"


def declared_coverage_floor(
    source_id: str,
    source: Mapping[str, object],
) -> CoverageFloor:
    """Read one source's declared cross-section coverage floors.

    Returns a `CoverageFloor` carrying the entity unit and one `CoverageEra`
    per declared era. Raises if the source does not declare one, or declares
    one that cannot guard anything.

    Fails closed on purpose. An adapter reaches this function only because it
    knows how to count that source's reporting entities, and a counted quantity
    with no declared floor is a measurement nothing acts on. The registry is
    where the floors live -- they are claims about the source, not about the
    code, and Track A owns the registry.

    The floor is per era because one absolute cannot hold across a universe
    that changes size. `sec_nmfp` falls from 730 reporting series in 2010 to
    307 in 2024: the single floor of 200 this replaced was 27 percent of the
    early universe and 65 percent of the late one, which is not one floor
    applied twice but two different rules wearing one number.
    """

    declaration = source.get("cross_section")
    if not isinstance(declaration, Mapping):
        raise DataContractError(
            f"{source_id}: emits cross-sections but the registry declares no "
            "cross_section coverage floor"
        )
    permitted = {"entity_unit", "eras", "note"}
    unknown = sorted(set(declaration) - permitted)
    if unknown:
        raise DataContractError(
            f"{source_id}: cross_section has unpermitted keys {unknown}"
        )
    entity_unit = declaration.get("entity_unit")
    if not isinstance(entity_unit, str) or not entity_unit.strip():
        raise DataContractError(
            f"{source_id}: cross_section.entity_unit must be a non-empty string "
            "naming what is counted"
        )
    if "eras" not in declaration:
        raise DataContractError(
            f"{source_id}: cross_section declares no eras; the floor is per era"
        )
    return CoverageFloor(
        entity_unit=entity_unit.strip(),
        eras=validate_coverage_eras(source_id, declaration["eras"]),
    )


# The two readings of a derived field that ran and matched nothing. They are the
# two halves of the sentence the published limitation says this repository cannot
# write, and the only thing that separates them is whether the registry's
# declaration for that field covers the month in hand -- which is a reviewer's
# judgement recorded in `metadata/sources.json`, not something a parser can
# conclude from an empty match.
#
# Neither one is a zero. A declared structural zero means a reviewer has said the
# true value is zero, over a stated period, for a stateable reason; it still does
# not license this
# adapter to write a `0.0` row, because a row is an observation and there was
# none. The declaration is what lets a *reader* treat the gap as a zero, at the
# point where they can also see who said so and on what grounds.
DERIVED_ABSENCE_DECLARED_ZERO = "declared_structural_zero"
DERIVED_ABSENCE_UNDECLARED = "no_declaration"


@dataclass(frozen=True)
class StructuralZeroPeriod:
    """One declared structural zero: the reviewer's grounds and the months it covers.

    `start` carries the registry's `from`, which cannot be spelled as an
    attribute name, and `None` means unbounded below. `through` is the
    registry's `through`. Both bounds are inclusive.

    The asymmetry -- `through` required, `from` optional -- is the point of
    the grammar rather than a corner cut. A structural zero is almost always
    a statement about a period that ended: the facility did not exist yet,
    the instrument was not eligible, the table did not carry the category. A
    declaration left open at the top annexes every month the source has not
    reached, including months no reviewer has seen, and it does so silently
    because nothing about it looks unbounded. Left open at the bottom it
    annexes only the past, which is finite and already reviewed, and it
    spares a reviewer inventing a start date for something that was true
    before the series began.

    `when` is still required and still the reviewer's prose. The period does
    not replace it: the dates say *which* cross-sections a declaration covers
    and `when` says on what grounds, which is the half no date can carry and
    the half a reader needs in order to disagree with it.
    """

    when: str
    through: date
    start: Optional[date] = None

    def covers(self, ref_date: date) -> bool:
        """True when a cross-section dated `ref_date` falls inside the declaration."""

        if ref_date > self.through:
            return False
        return self.start is None or ref_date >= self.start


def _structural_zero_bound(
    source_id: str, field: str, key: str, raw: object
) -> date:
    """One inclusive ISO bound of a structural-zero declaration, or a refusal.

    Refusing an unparseable bound rather than dropping the declaration is the
    same ruling `validate_coverage_eras` makes one screen up: a declaration
    that silently stops declaring is worse than one that fails loudly,
    because the disposition it produces -- `DERIVED_ABSENCE_UNDECLARED` --
    is a real answer that a reader has no way to tell from a typo.
    """

    if not isinstance(raw, str) or not raw.strip():
        raise DataContractError(
            f"{source_id}: structural_zeros entry for {field!r} has a {key} "
            f"of {raw!r}; bounds are inclusive ISO YYYY-MM-DD dates"
        )
    try:
        return date.fromisoformat(raw.strip())
    except ValueError as exc:
        raise DataContractError(
            f"{source_id}: structural_zeros entry for {field!r} has a {key} "
            f"of {raw!r}, which is not an ISO YYYY-MM-DD date"
        ) from exc


def declared_structural_zeros(
    source_id: str,
    source: Mapping[str, object],
) -> Mapping[str, StructuralZeroPeriod]:
    """Read one source's declared structural zeros, each field to the period it covers.

    This is the registry declaration nothing in this package used to read. It was
    declared, shape-checked by `tests/test_contract.py`, and never consulted --
    and a declaration nothing reads cannot distinguish anything, which is why a
    field nobody observed and a derivation that found nothing had the same
    representation: no row, and no way to tell which had happened.

    Fails open, unlike `declared_coverage_floor` next door, and the asymmetry is
    deliberate. A missing coverage floor means a counted quantity nothing acts
    on, so refusing is the only safe answer. An empty `structural_zeros` is the
    honest state of a source nobody has reviewed yet -- `AGENT_CONTRACT.md` says
    in as many words that an empty `structural_zeros` is not a finding -- so
    raising on one would make every unreviewed source unreadable and would push a
    reviewer towards declaring something to make the build pass, which is the one
    outcome this field must never reward.

    Returns the declared **period** per field, not the prose, and that is the
    difference between two questions this used to conflate. `when` is
    free-form prose that `tests/test_contract.py` requires only to be a
    non-empty string, so a reader holding only `when` can answer "is this
    field declared a structural zero at all" -- which separates "they held
    none" from "we never found it" -- and can never answer "is it declared
    for *this* month".

    For `sec_nmfp` those two questions have different answers, which is why
    the second one had to become askable. Thirty-three repo months record a
    derivation that ran and matched nothing; thirty-two of them (2010-11 to
    2013-08) precede the facility, and one, 2026-07-31, is a month the
    facility existed and these funds did not use it. A single declaration
    answering "declared at all" makes both read
    `DERIVED_ABSENCE_DECLARED_ZERO` and so erases the one month that is the
    entire reason to look -- a reviewer's statement about the pre-facility
    era, silently extended over a month nobody reviewed.

    `through` is required for that reason and not out of tidiness: an
    optional upper bound would leave the unbounded declaration expressible,
    and the unbounded declaration is precisely the one that gets this case
    wrong. `DERIVED_ABSENCE_DECLARED_ZERO` is now a period assertion, and
    `_nmfp_unmatched_derived_fields` decides it against the cross-section's
    own ref_date.

    `structural_zeros_reviewed` is deliberately not re-checked here.
    `tests/test_contract.py` already requires an unreviewed source's
    `structural_zeros` to be empty, so a non-empty declaration is reviewed by
    construction; restating that rule here would be the second copy of a rule
    that `tests/test_contract.py` names as how one field came to be called
    `calendar` on one side and `unit` on the other.
    """

    declarations = source.get("structural_zeros")
    if not isinstance(declarations, Sequence) or isinstance(declarations, (str, bytes)):
        raise DataContractError(
            f"{source_id}: structural_zeros must be a list of declarations"
        )
    found: Dict[str, StructuralZeroPeriod] = {}
    for declaration in declarations:
        if not isinstance(declaration, Mapping):
            raise DataContractError(
                f"{source_id}: each structural_zeros entry must be an object"
            )
        field = declaration.get("field")
        when = declaration.get("when")
        if not isinstance(field, str) or not field.strip():
            raise DataContractError(
                f"{source_id}: a structural_zeros entry names no field"
            )
        if not isinstance(when, str) or not when.strip():
            raise DataContractError(
                f"{source_id}: structural_zeros entry for {field!r} states no "
                "'when'; a structural zero nobody bounded is not reviewable"
            )
        through = declaration.get("through")
        if through is None:
            raise DataContractError(
                f"{source_id}: structural_zeros entry for {field!r} states no "
                "'through'; a declaration with no last covered cross-section "
                "covers every month the source has not reached yet"
            )
        last = _structural_zero_bound(source_id, field, "through", through)
        # Absent -- or an explicit null, which is how JSON writes absent --
        # means unbounded below. Anything else is parsed and must parse.
        first = None
        if declaration.get("from") is not None:
            first = _structural_zero_bound(
                source_id, field, "from", declaration["from"]
            )
            if first > last:
                raise DataContractError(
                    f"{source_id}: structural_zeros entry for {field!r} runs "
                    f"from {first.isoformat()} through {last.isoformat()}, "
                    "which declares no cross-sections at all"
                )
        # Two declarations for one field would make the disposition depend on
        # iteration order, and the answer here is one disposition per field.
        # Refusing costs less than picking one. Two periods for one field are
        # the same defect wearing a grammar: the union of two declared spans
        # is a third declaration nobody wrote.
        if field.strip() in found:
            raise DataContractError(
                f"{source_id}: structural_zeros declares {field.strip()!r} twice"
            )
        found[field.strip()] = StructuralZeroPeriod(
            when=when.strip(), through=last, start=first
        )
    return found


def validate_publication_gaps(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, int]:
    """Fail if observed ref-date publication gaps exceed a declared bound."""

    field_bounds: Dict[str, tuple[str, int]] = {}
    for source_id, source in registry.items():
        lag = source.get("release_lag")
        if not isinstance(lag, Mapping) or lag.get("basis") != "ref_date":
            continue
        bound = lag.get("worst_case_calendar_days")
        if isinstance(bound, bool) or not isinstance(bound, int):
            raise DataContractError(
                f"{source_id}: ref_date source lacks a valid publication-gap bound"
            )
        for field in source.get("fields", []):
            if field in field_bounds:
                raise DataContractError(f"series {field!r} belongs to multiple sources")
            field_bounds[str(field)] = (source_id, bound)

    worst: Dict[str, int] = {}
    for row in observations:
        if row.series_id not in field_bounds:
            continue
        source_id, bound = field_bounds[row.series_id]
        gap = (row.available_at.date() - row.ref_date).days
        if gap < 0:
            raise DataContractError(
                f"{row.series_id} {row.ref_date}: available_at predates ref_date"
            )
        worst[row.series_id] = max(worst.get(row.series_id, 0), gap)
        if gap > bound:
            raise DataContractError(
                f"{row.series_id} was published {gap} calendar days after its "
                f"ref_date, but {source_id} declares {bound}"
            )
    return worst


@dataclass(frozen=True)
class IdentityEra:
    """One era of a declared identity: a date window and the terms that hold in it.

    An additive identity over a published series is a claim about a vocabulary,
    and a vocabulary has a history. FR 2004's `PDPOSGST-TOT` equals the sum of
    its components on every weekly as-of date from 2013-04-03, but the
    components are not the same set throughout: there is no floating-rate-note
    bucket before 2015-01-07, and the over-eleven-year nominal coupon bucket is
    one series (`PDPOSGSC-G11`) through 2021-12-29 and two (`-G11L21`, `-G21`)
    from 2022-01-05. An identity declared over the current thirteen terms alone
    can be evaluated on 243 of the tracked extract's 700 weekly dates and is
    `not_evaluable` on the other 457 -- honest, and also five sixths of the
    history left unchecked by a guard that reads as vigilance.

    The alternative that has to be refused rather than merely not chosen is one
    identity declared over the union of every era's components: on a date in an
    early era the later era's terms are simply absent, so the union identity
    is `not_evaluable` everywhere -- and if an absent term is read as `0.0` to
    make the sum close, it *holds* everywhere instead, which turns absence into
    a measured value. `docs/DATA_QUALITY_DECISIONS.md` forbids exactly that, and
    `_identity_verdict` never forms the sums when a term is missing. Eras are
    how the identity is made evaluable without it.

    Both bounds are inclusive and both are optional. That is deliberately not
    `_StructuralZeroWindow`'s asymmetry, where `through` is required and `from`
    is not. A structural zero with no last covered cross-section is an unbounded
    claim that some field is always zero, and what is refused there is the claim
    outliving the regime that made it true. An era is the opposite shape: the
    whole content of the current era is that it has not ended, and giving it a
    `through` would mean writing a future date by hand. Unboundedness is
    constrained instead by the overlap rule in `declared_identity_eras`, which
    refuses two eras unbounded on the same side because they necessarily
    overlap.
    """

    era_id: str
    left: tuple
    right: tuple
    start: Optional[date] = None
    through: Optional[date] = None

    @property
    def fields(self) -> tuple:
        """Every term this era declares, left side then right."""

        return (*self.left, *self.right)

    def covers(self, ref_date: date) -> bool:
        if self.start is not None and ref_date < self.start:
            return False
        if self.through is not None and ref_date > self.through:
            return False
        return True


def _identity_era_bound(
    source_id: str, name: str, era_id: str, key: str, value: object
) -> date:
    if not isinstance(value, str):
        raise DataContractError(
            f"{source_id}: identity {name} era {era_id} has a {key} that is "
            f"not an ISO date string"
        )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DataContractError(
            f"{source_id}: identity {name} era {era_id} has a {key} that is "
            f"not an ISO date: {value!r}"
        ) from exc


def _identity_era_terms(
    source_id: str, name: str, era_id: str, side: str, declared: object
) -> tuple:
    if not isinstance(declared, list) or not declared:
        raise DataContractError(
            f"{source_id}: identity {name} era {era_id} states no {side} terms; "
            f"an era is a component set and inherits none"
        )
    return tuple(str(field) for field in declared)


def declared_identity_eras(
    source_id: str, name: str, identity: Mapping[str, object]
) -> tuple:
    """The eras one declared identity is evaluated over, in date order.

    An identity with no `eras` key gets a single unbounded era carrying its
    top-level `left` and `right`. That is not a special case bolted on: it means
    every caller iterates one shape and the un-era'd declaration cannot drift
    down a second code path that the era'd one is not tested on.

    Each declared era states its own `left` and `right` in full and inherits
    neither. Inheritance is what would put the union declaration back: an era
    that omits a side and picks up the identity's would be checked against terms
    that did not exist in it.

    The refusals, each of which is a malformed declaration and therefore a fault
    in what this repository wrote rather than a finding about a source's data:

    * an `eras` value that is not a non-empty list, or an entry that is not an
      object, or one with no `id`, or two entries sharing an `id`;
    * an era stating no `left` or no `right` terms;
    * a `from` or `through` that is not an ISO date string;
    * an era whose `from` is after its `through` -- a window that covers no
      date, which would silently make every date in it undeclared;
    * two eras whose windows overlap, which includes two eras unbounded on the
      same side. Overlapping eras make the term set for a date depend on which
      one is consulted first, and a term set chosen by list order is not a
      declaration.

    One more, and it is about the seam rather than about the eras: when `eras`
    is declared, the identity's top-level `left` and `right` must restate its
    most recent era's, term for term and in order. The top-level declaration
    cannot simply go away -- `tests/test_contract.py` reads it as the shape both
    tracks build against, and the registry interface is a shared, human-owned
    guard. Leaving it unchecked beside the eras would be the duplicated-fact
    failure this repository keeps meeting: two statements of the current
    component set with nothing holding them together. So it is required to be
    the same statement.
    """

    left = identity.get("left")
    right = identity.get("right")
    if not isinstance(left, list) or not isinstance(right, list):
        raise DataContractError(f"{source_id}: malformed accounting identity")
    top_left = tuple(str(field) for field in left)
    top_right = tuple(str(field) for field in right)

    declared = identity.get("eras")
    if declared is None:
        return (IdentityEra(era_id="", left=top_left, right=top_right),)
    if not isinstance(declared, list) or not declared:
        raise DataContractError(
            f"{source_id}: identity {name} declares eras, which must be a "
            f"non-empty list"
        )

    eras: List[IdentityEra] = []
    seen: set = set()
    for entry in declared:
        if not isinstance(entry, Mapping):
            raise DataContractError(
                f"{source_id}: identity {name} has an era that is not an object"
            )
        era_id = str(entry.get("id") or "").strip()
        if not era_id:
            raise DataContractError(f"{source_id}: identity {name} has an era with no id")
        if era_id in seen:
            raise DataContractError(
                f"{source_id}: identity {name} declares era {era_id} twice"
            )
        seen.add(era_id)
        start = (
            _identity_era_bound(source_id, name, era_id, "from", entry["from"])
            if entry.get("from") is not None
            else None
        )
        through = (
            _identity_era_bound(source_id, name, era_id, "through", entry["through"])
            if entry.get("through") is not None
            else None
        )
        if start is not None and through is not None and start > through:
            raise DataContractError(
                f"{source_id}: identity {name} era {era_id} runs from "
                f"{start.isoformat()} through {through.isoformat()}, which "
                f"covers no reference date"
            )
        eras.append(
            IdentityEra(
                era_id=era_id,
                left=_identity_era_terms(
                    source_id, name, era_id, "left", entry.get("left")
                ),
                right=_identity_era_terms(
                    source_id, name, era_id, "right", entry.get("right")
                ),
                start=start,
                through=through,
            )
        )

    # `date.min` and `date.max` stand in for the open ends only for the sort and
    # the comparison below, and never leave this function: an era's own bounds
    # stay `None`, so `covers` cannot come to depend on a sentinel date.
    ordered = sorted(eras, key=lambda era: (era.start or date.min, era.through or date.max))
    for earlier, later in zip(ordered, ordered[1:]):
        if (later.start or date.min) <= (earlier.through or date.max):
            raise DataContractError(
                f"{source_id}: identity {name} eras {earlier.era_id} and "
                f"{later.era_id} overlap; every reference date must fall in at "
                f"most one era"
            )

    latest = ordered[-1]
    if (latest.left, latest.right) != (top_left, top_right):
        raise DataContractError(
            f"{source_id}: identity {name} declares eras, so its top-level "
            f"terms must restate its most recent era {latest.era_id}; they do "
            f"not"
        )
    return tuple(ordered)


def _identity_verdict(
    left_fields: Sequence[str],
    right_fields: Sequence[str],
    values: Mapping[str, Optional[float]],
    tolerance: Mapping[str, object],
) -> tuple:
    """Answer one declared identity on one reference date.

    Returns `(verdict, residual, absent_fields, bound)`. The verdict is one of
    `IDENTITY_HELD`, `IDENTITY_VIOLATED` or `IDENTITY_NOT_EVALUABLE`; the
    residual is `None` for the last, because on that reference date there is no
    residual -- not a large one, not a zero one, none.

    An absent term is never read as `0.0`. The sums are not formed at all when
    a term is missing, so nothing here can turn "we did not observe it" into
    "we observed nothing". Substituting a zero would make the identity evaluate
    and, on a balance sheet, would usually make it fail loudly -- but on a panel
    where the missing terms sit on the same side it can just as easily make it
    hold, and an identity that holds because a missing term was imputed is worse
    than one that visibly did not run: the first destroys the evidence.
    """

    absent = tuple(
        field
        for field in (*left_fields, *right_fields)
        if values.get(field) is None
    )
    if absent:
        return IDENTITY_NOT_EVALUABLE, None, absent, None
    left_value = sum(float(values[field]) for field in left_fields)
    right_value = sum(float(values[field]) for field in right_fields)
    residual = abs(left_value - right_value)
    # The scale is the magnitude of the quantity the identity is about, and it
    # is taken from the larger side rather than from a named term, so that the
    # rule reads the same for an identity that has no term called "net assets".
    scale = max(abs(left_value), abs(right_value))
    bound = resolve_identity_tolerance(dict(tolerance), scale)
    verdict = IDENTITY_HELD if residual <= bound else IDENTITY_VIOLATED
    return verdict, residual, (), bound


def validate_accounting_identities(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, "IdentityEvaluation"]:
    """Validate declared additive identities on the latest supplied vintages.

    Returns one `IdentityEvaluation` per declared identity, keyed
    `"{source_id}:{name}"`. Deliberately not a bare maximum residual any more.
    That float was computed over the intersection of the declared terms'
    reference dates, so a panel whose first years cannot be checked at all
    produced exactly the same answer as one checked throughout, and a caller
    asking "are the identities fine?" could not tell the two apart. `verdict` is
    `held` only when every reference date any term was observed on was actually
    checked.

    Neither a violated nor an unevaluable reference date raises. Both are
    recorded -- the unevaluable one named term by named term, the violated one
    with its residual and the bound it was measured against. A *malformed
    declaration* still raises, and the distinction is the whole of it: a broken
    registry is a fault in what this repository wrote, and a violated identity
    is a finding about data a source published. The two do not get the same
    channel.

    The abort that used to live here has moved to `build_daily_panel`, which is
    the first hop that knows whether the panel contains a column from the source
    the violation is in. `sec_nmfp` supplies no column to any build -- the
    pricing function refuses `mmf_assets` in all of them -- and a violated
    identity in it was halting builds of the eight columns that have nothing to
    do with it. See `docs/DATA_QUALITY_DECISIONS.md`, "Whether a source may
    abort a build it contributes nothing to". This is a scoping of the guard.
    A violated identity in a source the panel depends on still stops the panel.

    Which reference dates belong in the panel is a policy question and it is not
    this function's to answer -- but it can no longer be answered by accident.

    Each reference date is checked against the terms of *its own era*. An
    identity may declare `eras`, and then the term set is a function of the
    date rather than a constant; one that does not gets a single unbounded era
    and is evaluated exactly as before. See `IdentityEra` for why a source's
    vocabulary having a history is not the same problem as its data having
    holes, and `declared_identity_eras` for what a malformed era declaration is
    refused for. A date covered by no declared era is recorded `not_evaluable`
    with `undeclared_ref_date` set, never skipped: a date the declaration is
    silent about is not a date the identity held on.
    """

    latest = {}
    for row in observations:
        key = (row.series_id, row.ref_date)
        previous = latest.get(key)
        if previous is None or row.available_at > previous.available_at:
            latest[key] = row

    evaluations: Dict[str, IdentityEvaluation] = {}
    for source_id, source in registry.items():
        identities = source.get("identities", [])
        if not isinstance(identities, list):
            raise DataContractError(f"{source_id}: identities must be a list")
        for identity in identities:
            if not isinstance(identity, Mapping):
                raise DataContractError(f"{source_id}: identity must be an object")
            name = str(identity.get("name") or "").strip()
            left = identity.get("left")
            right = identity.get("right")
            tolerance = identity.get("tolerance")
            if (
                not name
                or not isinstance(left, list)
                or not isinstance(right, list)
                or not isinstance(tolerance, Mapping)
            ):
                raise DataContractError(f"{source_id}: malformed accounting identity")
            tolerance_problems = validate_identity_tolerance(source_id, name, tolerance)
            if tolerance_problems:
                raise DataContractError("; ".join(tolerance_problems))
            eras = declared_identity_eras(source_id, name, identity)
            fields = sorted({field for era in eras for field in era.fields})
            dates_by_field = {
                field: {ref_date for series_id, ref_date in latest if series_id == field}
                for field in fields
            }
            # The union, not the intersection. Every reference date on which any
            # declared term was observed is a date this identity has something
            # to say about -- including "I could not be checked here". Iterating
            # the intersection is what made 5.5 years of an unchecked balance
            # sheet invisible: those dates were not failing the identity, they
            # were never reaching it.
            observed_dates = set().union(*dates_by_field.values()) if fields else set()
            maximum = 0.0
            complete_dates = 0
            unevaluated: List[UnevaluatedIdentity] = []
            violations: List[ViolatedIdentity] = []
            for ref_date in sorted(observed_dates):
                # At most one era can cover it: `declared_identity_eras` refuses
                # an overlap, so this is a lookup and not a precedence rule.
                era = next((item for item in eras if item.covers(ref_date)), None)
                if era is None:
                    # Recorded, not skipped. A date the declaration says nothing
                    # about is not a date the identity held on, and dropping it
                    # here would leave `evaluated_ref_dates` counting it as
                    # checked. Same finding as `CrossSectionCoverage`'s
                    # "ref_date falls in no declared coverage era", one hop down.
                    unevaluated.append(
                        UnevaluatedIdentity(
                            source_id=source_id,
                            identity=name,
                            ref_date=ref_date,
                            undeclared_ref_date=True,
                        )
                    )
                    continue
                # Exactly this era's terms are looked for, and no others. A term
                # that belongs only to a different era is not consulted, so its
                # absence here is not an absence -- it is a series that did not
                # exist yet.
                values = {
                    field: (
                        latest[(field, ref_date)].value
                        if (field, ref_date) in latest
                        else None
                    )
                    for field in era.fields
                }
                verdict, residual, absent, bound = _identity_verdict(
                    era.left, era.right, values, tolerance
                )
                if verdict == IDENTITY_NOT_EVALUABLE:
                    unevaluated.append(
                        UnevaluatedIdentity(
                            source_id=source_id,
                            identity=name,
                            ref_date=ref_date,
                            absent_fields=absent,
                            era_id=era.era_id,
                        )
                    )
                    continue
                complete_dates += 1
                if verdict == IDENTITY_VIOLATED:
                    # Recorded, not raised, and deliberately symmetric with the
                    # branch above it. This function runs at the first hop,
                    # before any wide panel exists, so it cannot know whether
                    # the panel will contain a column from this source -- and
                    # that is the only fact that makes a violation here a reason
                    # to stop a build. `build_daily_panel` knows it and raises;
                    # see rule 5 there.
                    violations.append(
                        ViolatedIdentity(
                            source_id=source_id,
                            identity=name,
                            ref_date=ref_date,
                            residual=residual,
                            bound=bound,
                        )
                    )
                # Not in an `else`. A violating residual is still a residual,
                # and a maximum computed over the passing dates alone would fall
                # as the data got worse.
                maximum = max(maximum, residual)
            if not complete_dates:
                # Counted while iterating rather than intersected beforehand,
                # because with eras "complete" is a question about one date and
                # the terms of *its* era. The refusal itself is unchanged: an
                # identity no reference date can be checked on is a declaration
                # that cannot fail, which is the degenerate guard this module
                # exists to refuse.
                raise DataContractError(
                    f"{source_id}: identity {name} has no complete reference date"
                )
            evaluations[f"{source_id}:{name}"] = IdentityEvaluation(
                source_id=source_id,
                name=name,
                maximum_residual=maximum,
                evaluated_ref_dates=len(observed_dates) - len(unevaluated),
                unevaluated=tuple(unevaluated),
                violations=tuple(violations),
            )
    return evaluations


def load_stress_thresholds(
    path: Path = DEFAULT_STRESS_THRESHOLDS,
) -> Mapping[str, object]:
    """Load and validate the versioned stress-target declaration."""

    try:
        declaration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"cannot load stress threshold metadata: {exc}") from exc
    if not isinstance(declaration, dict):
        raise DataContractError("stress threshold metadata must be an object")
    if isinstance(declaration.get("version"), bool) or not isinstance(
        declaration.get("version"), int
    ):
        raise DataContractError("stress threshold metadata needs an integer version")
    if declaration.get("primary_rule") != "fixed_bp":
        raise DataContractError("stress threshold primary_rule must be 'fixed_bp'")
    raw_taus = declaration.get("taus_bp")
    if not isinstance(raw_taus, list):
        raise DataContractError("stress threshold metadata needs a taus_bp list")
    try:
        taus = tuple(float(tau) for tau in raw_taus)
    except (TypeError, ValueError) as exc:
        raise DataContractError("stress thresholds must be numeric") from exc
    if taus != (5.0, 10.0, 20.0, 50.0):
        raise DataContractError("stress thresholds must be exactly 5, 10, 20, and 50 bp")
    expected_columns = [f"stress_gt_{tau:g}bp" for tau in taus]
    if declaration.get("label_columns") != expected_columns:
        raise DataContractError("stress label_columns must match the declared taus_bp")
    secondary = declaration.get("secondary_rule")
    if not isinstance(secondary, dict):
        raise DataContractError("stress threshold metadata needs a secondary_rule")
    if secondary.get("type") != "trailing_percentile":
        raise DataContractError("secondary stress rule must be 'trailing_percentile'")
    if secondary.get("history") != "rows_strictly_before_label_row":
        raise DataContractError("trailing stress rule must use only pre-label rows")
    if secondary.get("full_sample_allowed") is not False:
        raise DataContractError("full-sample stress percentiles are prohibited")
    return declaration


def _finite_values(values: Sequence[float]) -> List[float]:
    checked: List[float] = []
    for position, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise DataContractError(f"stress value {position} is not numeric")
        number = float(value)
        if not math.isfinite(number):
            raise DataContractError(f"stress value {position} is not finite")
        checked.append(number)
    return checked


def stress_label_threshold(
    values: Sequence[float],
    index: int,
    window: int,
    probability: float,
) -> float:
    """Return a trailing percentile based strictly on rows before ``index``."""

    if isinstance(index, bool) or not isinstance(index, int):
        raise DataContractError("stress label index must be an integer")
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise DataContractError("stress label window must be a positive integer")
    if index < window or index > len(values):
        raise DataContractError("stress label threshold has insufficient trailing history")
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise DataContractError("stress label probability must be numeric")
    quantile = float(probability)
    if not 0.0 <= quantile <= 1.0:
        raise DataContractError("stress label probability must be in [0, 1]")

    history = sorted(_finite_values(values[index - window : index]))
    position = (len(history) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return history[lower]
    weight = position - lower
    return history[lower] * (1.0 - weight) + history[upper] * weight


def fixed_bp_stress_label_columns(
    spreads_bp: Sequence[float],
    declaration: Optional[Mapping[str, object]] = None,
) -> List[Mapping[str, int]]:
    """Build the primary state-label columns from declared fixed thresholds."""

    metadata = declaration or load_stress_thresholds()
    if metadata.get("primary_rule") != "fixed_bp":
        raise DataContractError("fixed-bp labels require primary_rule 'fixed_bp'")
    raw_taus = metadata.get("taus_bp")
    if not isinstance(raw_taus, (list, tuple)):
        raise DataContractError("fixed-bp labels require taus_bp")
    taus = _finite_values(raw_taus)  # type: ignore[arg-type]
    values = _finite_values(spreads_bp)
    return [
        {f"stress_gt_{tau:g}bp": int(spread > tau) for tau in taus}
        for spread in values
    ]


def audit_panel(observations: Iterable[DailyObservation]) -> AuditReport:
    rows = list(observations)
    if not rows:
        raise DataContractError("panel contains no observations")

    dates = [row.date for row in rows]
    if dates != sorted(dates):
        raise DataContractError("dates must be sorted in ascending order")
    duplicates = sorted({value for value in dates if dates.count(value) > 1})
    if duplicates:
        raise DataContractError(f"duplicate dates: {', '.join(map(str, duplicates))}")

    all_fields = sorted({field for row in rows for field in row.values})
    missing_counts: Dict[str, int] = {
        field: sum(row.values.get(field) is None for row in rows) for field in all_fields
    }
    warnings: List[str] = []
    for index, row in enumerate(rows, start=1):
        values = row.values
        if values.get("sofr_p25") is not None and values.get("sofr_p75") is not None:
            if values["sofr_p25"] > values["sofr_p75"]:  # type: ignore[operator]
                warnings.append(f"{row.date}: SOFR p25 exceeds p75")
        for field in ("sofr_volume", "reserve_balances", "tga", "on_rrp"):
            if values.get(field) is not None and values[field] < 0:  # type: ignore[operator]
                warnings.append(f"{row.date}: {field} is negative")
        for field in ("quarter_end", "tax_date"):
            if values.get(field) not in (None, 0.0, 1.0):
                warnings.append(f"{row.date}: {field} should be 0 or 1")

    return AuditReport(
        row_count=len(rows),
        start_date=dates[0],
        end_date=dates[-1],
        missing_counts=missing_counts,
        warnings=warnings,
    )


#: Every declared panel column except the `date` index, in the order the
#: model layer declares them. The join attempts each one and refuses the ones
#: latest vintage cannot carry faithfully; it is not a shorter list of the
#: columns someone expects to succeed, because a column that quietly stopped
#: being attempted would be indistinguishable from one that has no data.
PANEL_COLUMNS = tuple(
    field for field in REQUIRED_FIELDS if field != "date"
) + OPTIONAL_NUMERIC_FIELDS

# A business day with no Treasury settlement reads 0.0 (human decision, 11 Sep
# 2026; docs/DATA_QUALITY_DECISIONS.md, "Panel columns"). See
# `build_daily_panel` rule 8. This is the one place the exception to rule 4 is
# declared: a column not named here keeps its holes.
#
#: The auction snapshot: the one source a settlement zero may be read from. The
#: zero is a claim about what its record lists, so a column drawn from any other
#: source cannot take it.
SETTLEMENT_ZERO_SOURCE = "treasury_auctions"

#: What "nothing settled" is judged on, per declared column.
#:
#:   leg  the column's own series has no observation that day: no auction of
#:        that kind settled
#:   day  no series of the snapshot has an observation that day: nothing settled
#:        at all. For the SOMA leg, which the adapter withholds whole on a day
#:        whose auction was not yet held while the public legs of that day stay
#:        observed -- so its own absence alone is not a zero.
SETTLEMENT_ZERO_LEG = "leg"
SETTLEMENT_ZERO_DAY = "day"
SETTLEMENT_ZERO_COLUMNS = MappingProxyType(
    {
        "treasury_settlement": SETTLEMENT_ZERO_LEG,
        "treasury_settlement_bills": SETTLEMENT_ZERO_LEG,
        "treasury_settlement_coupons": SETTLEMENT_ZERO_LEG,
        "treasury_settlement_soma": SETTLEMENT_ZERO_DAY,
    }
)

#: Treasury's issue dates are Eastern calendar dates, so a retrieval instant is
#: read on that calendar before it bounds them.
SETTLEMENT_CALENDAR = "America/New_York"


@dataclass(frozen=True)
class DailyPanelBuild:
    """A wide daily panel and the record of how it was built.

    `refusals` maps a column that was *not* built to the reason the pricing
    function gave for refusing it, verbatim. A refused column is absent from
    every row's `values` -- never present and quietly carrying a revised
    number -- and the reason travels with the panel so a reader of the manifest
    does not have to re-derive it.

    `holes` counts, per built column, the `ref_date`s in the panel that carry
    no value for it. A hole is not a zero and is not the previous day's value;
    it is recorded and left empty. A settlement zero (`build_daily_panel` rule
    8) is a value and is not counted here; it is counted in `settlement_zeros`.
    It is counted over the grid the panel actually carries -- see
    `incomplete_dates`.

    `settlement_zeros` counts, per built column and over the same grid, the
    values that are rule 8 settlement zeros. Beside `holes` because they are
    the two different facts about a column's absences: a hole is an absence
    left empty, a settlement zero is an absence the auction record answered.
    Without this the manifest published one of them and a reader of a panel
    could see how much of a column was missing and not how much of it was a
    zero written in place of an absence. Since A25 the set of dates eligible
    for a zero is derived from the build cutoff and the snapshot's coverage,
    so this count is also the audit of that bound on the build that ran.

    It counts the zeros **written**, not the dates eligible for one. Those are
    different sets, and the cheap count over the eligible dates over-reports on
    exactly the columns that have the most data: a date carrying a real
    settlement observation is eligible and is not a zero. A column that takes
    no settlement zero -- every column outside `SETTLEMENT_ZERO_COLUMNS`, and a
    declared one on a build where nothing was filled -- records zero rather
    than omitting the key, to the standard `incomplete_dates` states next.

    `incomplete_dates` counts the `ref_date`s that the union of the sources
    reported but that this panel does not carry, because a `REQUIRED_FIELDS`
    column had no observation on them. It is never a default: a build that
    dropped nothing records zero, and a reader can tell that apart from a build
    that was never asked.

    `empty_columns` names the built columns that are a hole on every row. Built
    and empty is not the same fact as built, and until it was stated the only
    way to read it off a manifest was to compare each of `holes` against
    `row_count` -- which no reader of `built_columns` does, so `tgcr`, `bgcr`
    and `treasury_settlement` sat in that list beside `sofr` with nothing to
    separate them. On the published build all three are a hole on all 2104 rows.

    It is read off `holes` -- `holes[column] == row_count` -- and never from a
    second pass over the rows. A second count would key on a grid of its own
    and could disagree with the published one on an incomplete date, and then
    the manifest and this tuple would be describing two different panels.

    An empty column is **also** still in `built_columns`. The build attempted
    it and carried it, and that is what `built_columns` has always meant;
    nothing that reads it changes meaning because this exists.

    A build with no rows reports **no** empty columns, not every column.
    `holes[column] == row_count` is true of every column when `row_count` is 0,
    and the cheap reading of it says a panel carrying no rows is empty in every
    column -- when what it says is nothing about any of them. Rule 6 raises
    before `build_daily_panel` can return such a build, so no caller reaches
    that case through the join today; the guard is written here anyway, because
    this is a property of a public frozen dataclass and is read on whatever
    `DailyPanelBuild` a reader holds.

    Deliberately not in the file manifest, for the reason the comment above
    `write_daily_panel`'s `"required_columns"` gives for this key and for
    `settlement_zeros`.
    """

    observations: Sequence[DailyObservation]
    built_columns: Sequence[str]
    refusals: Mapping[str, str]
    holes: Mapping[str, int]
    build_cutoff: datetime
    decision_time: object
    incomplete_dates: int
    settlement_zeros: Mapping[str, int]

    @property
    def empty_columns(self) -> Sequence[str]:
        """The built columns that are a hole on every row, sorted. See above."""

        row_count = len(self.observations)
        if row_count == 0:
            return ()
        return tuple(
            sorted(
                column
                for column in self.built_columns
                if self.holes[column] == row_count
            )
        )


def _priceable_columns(
    columns: Iterable[str],
    registry: Mapping[str, Mapping[str, object]],
    decision_time,
) -> tuple[List[str], Dict[str, str]]:
    """Split declared columns into the ones latest vintage may carry, and why not.

    The test is `registry.max_release_lag_days`, called -- not restated. A
    column is built exactly when the pricing function returns a purge for the
    `(source, field)` pairs behind it, and refused exactly when it raises. That
    delegation is the whole point: a field on a `snapshot_retrieved_at` source
    with no `revision_policy` is refused there because its latest value may
    differ from the value that stood on the day, and a second copy of that rule
    here would be free to drift from the registry it is supposed to describe.

    Both refusal channels are named rather than caught as bare `ValueError`.
    `RegistryContractError` is the pricing function declining to price;
    `UndeclaredFeatureError` is `contract` declining to resolve a column to
    sources at all -- an unsourced or calendar-only column. Anything else
    raised from here is a fault, not a refusal, and is left to propagate.
    """

    from .contract import UndeclaredFeatureError, field_sources_for_features
    from .registry import RegistryContractError, max_release_lag_days

    built: List[str] = []
    refusals: Dict[str, str] = {}
    for column in columns:
        try:
            pairs = field_sources_for_features([column])
            max_release_lag_days(registry, pairs, decision_time=decision_time)
        except (RegistryContractError, UndeclaredFeatureError) as exc:
            refusals[column] = str(exc)
            continue
        built.append(column)
    return built, refusals


def _source_supplied_anything(
    source: Mapping[str, object], supplied_series: set[str]
) -> bool:
    """Did this source contribute any observation this build can see?

    Keyed on the source's declared `fields` -- the series it says it carries --
    checked against the `series_id`s in the visible rows. Not keyed on the terms
    of the identity being checked, which are a subset of those fields: a source
    that supplied a field its identity does not name still supplied something,
    and its identity is then answerable in the ordinary way rather than exempt.

    A source that declares no `fields` returns `True`, and is evaluated exactly
    as before. "Supplied nothing" is a claim about a declared vocabulary, and a
    source that declares none gives no ground to make it from; reading the
    absent list as the empty list would exempt every such source instead of
    none of them. See `build_daily_panel` rule 5.
    """

    declared = source.get("fields")
    if not isinstance(declared, list):
        return True
    return any(str(field) in supplied_series for field in declared)


def _settlement_retrieval_date(
    source_sha: str, snapshot_retrieved_at: Optional[Mapping[str, str]]
) -> date:
    """The Eastern calendar date a settlement snapshot was retrieved on, or a refusal.

    The retrieval date is the upper bound of what the snapshot can speak to.
    Without it a zero has no bound, and the only fill left is up to the panel's
    last date -- which writes "nothing settled" on days the record was never
    asked about. So a snapshot with no retrieval timestamp, a blank one, one that
    does not parse, or one with no UTC offset is refused rather than filled.
    """

    from zoneinfo import ZoneInfo

    raw = (snapshot_retrieved_at or {}).get(source_sha)
    parsed = None
    if raw is not None and str(raw).strip():
        try:
            parsed = datetime.fromisoformat(str(raw).strip().replace("Z", "+00:00"))
        except ValueError:
            parsed = None
    if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DataContractError(
            f"{SETTLEMENT_ZERO_SOURCE} snapshot {source_sha} supplied settlement "
            f"observations but carries no usable retrieval timestamp ({raw!r}); a "
            "business day with no settlement reads 0.0 only up to the snapshot's "
            "retrieval date, and is never zero-filled without that bound"
        )
    return parsed.astimezone(ZoneInfo(SETTLEMENT_CALENDAR)).date()


def _settlement_publication(
    registry: Mapping[str, Mapping[str, object]]
) -> "tuple[int, object, object]":
    """The auction source's declared publication rule, as rule 1 reads it.

    A settlement dated d is observable from `d + days` at `available_time` in
    `timezone` -- the registry's own `release_lag`, which is what the adapter
    writes into `available_at` on the rows that *are* there. Rule 8 bounds an
    absence, and an absence has no row to carry its own `available_at`, so it
    is bounded by the same declared rule applied to the same date. This is one
    reading of "when is a settlement observable", not a second one.

    The basis must be `record_date`, which on this dataset is the settlement
    date itself (`metadata/sources.json`, `treasury_auctions`: record_date
    "equals issue_date on every row of the tracked snapshot and never precedes
    its auction_date"), so the grid date *is* the record date. Any other basis
    is refused rather than reinterpreted: `ref_date` + `business_days` needs
    the holiday calendar this repository does not have, and
    `snapshot_retrieved_at` declares no publication instant at all. A zero
    whose bound had to be guessed is the unbounded zero again, one level in.
    """

    from datetime import time as _time
    from zoneinfo import ZoneInfo

    release_lag = registry.get(SETTLEMENT_ZERO_SOURCE, {}).get("release_lag")
    if not isinstance(release_lag, Mapping) or release_lag.get("basis") != "record_date":
        basis = (
            release_lag.get("basis") if isinstance(release_lag, Mapping) else release_lag
        )
        raise DataContractError(
            f"{SETTLEMENT_ZERO_SOURCE} declares release_lag basis {basis!r}, so this "
            "build cannot say when a settlement dated that day is published; a "
            "business day with no settlement reads 0.0 only once the record that "
            "would have listed one is observable at the build cutoff, and that "
            "bound is never guessed"
        )
    return (
        int(release_lag["days"]),
        _time.fromisoformat(str(release_lag["available_time"])),
        ZoneInfo(str(release_lag["timezone"])),
    )


def _settlement_zero_dates(
    visible: Sequence[PointInTimeObservation],
    built: Sequence[str],
    grid: Sequence[date],
    snapshot_retrieved_at: Optional[Mapping[str, str]],
    registry: Mapping[str, Mapping[str, object]],
    build_cutoff: datetime,
) -> Dict[str, frozenset]:
    """Rule 8: per declared built column, the grid dates that read 0.0.

    See `build_daily_panel` rule 8. Returns only columns in
    `SETTLEMENT_ZERO_COLUMNS`; a column absent from the result keeps rule 4.
    """

    from .contract import FEATURE_FIELDS

    for column in SETTLEMENT_ZERO_COLUMNS:
        pairs = FEATURE_FIELDS.get(column) or ()
        sources = sorted({str(source_id) for source_id, _field in pairs})
        if sources != [SETTLEMENT_ZERO_SOURCE]:
            raise DataContractError(
                f"column {column!r} is declared to read 0.0 on a day with no "
                f"settlement, but it is drawn from {sources or 'no source'}, not "
                f"the auction snapshot {SETTLEMENT_ZERO_SOURCE!r}; a settlement "
                "zero is a claim about what the auction record lists, and no "
                "other source can make it"
            )

    declared = [column for column in built if column in SETTLEMENT_ZERO_COLUMNS]
    if not declared:
        return {}

    # Every series the snapshot supplies to any panel column, not only to the
    # declared or built ones: "nothing settled that day" is a fact about the
    # whole record, and a narrower build must not see a withheld SOMA day as
    # an empty one because the aggregate was not asked for.
    snapshot_series = {
        str(field)
        for pairs in FEATURE_FIELDS.values()
        for source_id, field in pairs
        if str(source_id) == SETTLEMENT_ZERO_SOURCE
    }
    settlements = [row for row in visible if row.series_id in snapshot_series]
    if not settlements:
        return {}

    first_by_snapshot: Dict[str, date] = {}
    observed: Dict[str, set] = {}
    for row in settlements:
        first = first_by_snapshot.get(row.source_sha)
        if first is None or row.ref_date < first:
            first_by_snapshot[row.source_sha] = row.ref_date
        observed.setdefault(row.series_id, set()).add(row.ref_date)
    coverage = [
        (first, _settlement_retrieval_date(source_sha, snapshot_retrieved_at))
        for source_sha, first in sorted(first_by_snapshot.items())
    ]
    # The cutoff bound. Rule 1 removed every row published after the cutoff, so
    # on a grid date whose settlement record is not yet published the absence of
    # a settlement row is rule 1's doing and not the record's. Writing 0.0 there
    # would read a value off a page nobody could turn yet. The retrieval bound
    # above is a different question -- what the snapshot can speak to at all --
    # and neither implies the other: a snapshot retrieved well past the cutoff
    # covers dates the cutoff cannot see.
    published_days, published_time, published_zone = _settlement_publication(registry)
    covered = [
        ref_date
        for ref_date in grid
        if datetime.combine(
            ref_date + timedelta(days=published_days),
            published_time,
            tzinfo=published_zone,
        )
        <= build_cutoff
        and any(first <= ref_date <= last for first, last in coverage)
    ]
    settled_any = set().union(*observed.values())

    zeros: Dict[str, frozenset] = {}
    for column in declared:
        if SETTLEMENT_ZERO_COLUMNS[column] == SETTLEMENT_ZERO_DAY:
            settled = settled_any
        else:
            settled = set().union(
                *(observed.get(str(field), set()) for _s, field in FEATURE_FIELDS[column])
            )
        zeros[column] = frozenset(ref_date for ref_date in covered if ref_date not in settled)
    return zeros


def build_daily_panel(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
    *,
    build_cutoff: datetime,
    decision_time,
    columns: Sequence[str] = PANEL_COLUMNS,
    snapshot_retrieved_at: Optional[Mapping[str, str]] = None,
) -> DailyPanelBuild:
    """Join long point-in-time observations into the wide daily panel.

    This is the hop that was missing: `DailyObservation` was constructed in
    exactly one place, inside `load_daily_panel`, parsing a hand-written CSV.

    Four rules, and three of them are about not re-deciding something this
    repository has already decided once.

    **1. Indexed by `ref_date`; a cell carries the latest vintage available at
    `build_cutoff`.** Rows whose `available_at` is after the cutoff do not
    exist for this build. Among the rest, the cell for `(column, ref_date)` is
    the row with the greatest `available_at`. The cutoff is a property of the
    build and is returned so the manifest can record it.

    **2. The join does not subtract the release lag. The purge does.** The
    value at `ref_date` d is the value whose `ref_date` is d -- not the value
    from d minus the source's lag. `splits.rolling_origin` and
    `event_eval.evaluate_event_window` already hold the last training row a
    full release lag clear of the scored day. A join that shifted values by
    that lag as well would apply the gap twice: it would silently destroy
    training rows and move every reported number, while looking careful.
    `decision_time` is passed *through* to the pricing function and is never
    used to move a value.

    **3. A column is built only if the pricing function will price it.** See
    `_priceable_columns`. Refused columns are absent, with the reason recorded.

    **4. No forward fill.** A `ref_date` with no observation for a built column
    gets `None`, counted in `holes`. Absent is not zero and is not yesterday.
    Rule 8 is the one declared exception, and only for the columns it names.

    **6. The grid is the dates the panel is readable on.** The union of every
    source's `ref_date`s is not a panel: an administered rate that prints every
    calendar day and a market rate that prints on business days produce rows
    where the target is undefined, and `REQUIRED_FIELDS` then makes the file
    unreadable by `load_daily_panel` -- so `build` wrote something `backtest`
    could not open, and that gap sat on Milestone A's critical path. A
    `ref_date` missing any built `REQUIRED_FIELDS` column is therefore not a
    row. This is not rule 4 in reverse: an *optional* column with no
    observation is still a hole and still recorded. A weekend is not a hole in
    SOFR, it is a day `sofr - iorb` does not exist, and the count of dropped
    dates goes in the manifest so the distinction is auditable rather than
    asserted. `holes` is counted over the retained grid, because a hole count
    over a grid the panel does not carry describes nothing.

    **7. A column declared from more than one field is a splice, and the fields
    must partition the dates.** `iorb` is drawn from IORB and, before
    2021-07-29, from IOER. Where two fields both report the same `ref_date` the
    tie-break in rule 1 would pick one of them by `available_at` -- and two
    fields read out of a single latest-vintage snapshot share an `available_at`
    and a `vintage_id` exactly, so the winner would be whichever the iteration
    reached last. That is a silent choice about what a series means, so it
    raises instead.

    **5. A violated identity in a source this panel built a column from stops
    the build.** This is where that abort belongs and it is why it moved here.
    `validate_accounting_identities` runs one hop earlier, inside
    `build_point_in_time_snapshot`, where no wide panel exists yet -- so it
    could see the violation but not whether anything depended on the source,
    and it halted every build regardless. `sec_nmfp` supplies no column to any
    build, because the pricing function refuses `mmf_assets` in all of them
    under rule 3, so a violated N-MFP identity was stopping builds of the eight
    columns that have nothing to do with it. The verdict is now always recorded
    in the quality report and the abort is scoped to a source that actually
    supplied a column that was built. See `docs/DATA_QUALITY_DECISIONS.md`,
    "Whether a source may abort a build it contributes nothing to".

    Scoped on the columns *and* on the supply, because the first half alone keys
    on what the panel declares rather than on what arrived. A source whose
    column is priceable and whose file this build holds none of was still
    evaluated -- over zero observations, which is neither `held` nor `violated`
    but `no complete reference date`, raised as a contract error. That is a
    source that supplied nothing failing a build, which is the thing this rule
    exists to stop, reaching it through the one channel the scoping did not
    cover. A source is checked when the panel built a column from it *and* it
    supplied at least one of its declared series. A source that supplied some of
    them but never enough to complete a reference date is not exempt: that is a
    finding about the data, and it still raises.

    This is a scoping and not a loosening, and the second half is what keeps it
    honest: a violated identity in a source the panel *does* contain still stops
    the panel, and never by dropping the offending rows.

    The identities are evaluated over the rows this build can see, for the same
    reason rule 1 gives -- a vintage that arrives after `build_cutoff` does not
    exist for this build, and neither does a violation only that vintage
    reveals.

    **8. A business day with no Treasury settlement reads 0.0, inside the
    snapshot's coverage only** (human decision, 11 Sep 2026;
    `docs/DATA_QUALITY_DECISIONS.md`, "Panel columns"). The auction record lists
    every settlement, so a day it lists none of settled nothing: a true zero, not
    a fill. The columns that take it are `SETTLEMENT_ZERO_COLUMNS`, declared in
    this module; every other column keeps rule 4. Five conditions, all of them:

    * the date is on the grid rule 6 retained. No row is made for a date off
      it, and there is no holiday calendar and no `weekday()` here: the grid is
      the panel's own statement of which days are business days;
    * a settlement dated that day would have been observable at `build_cutoff`,
      by the auction source's declared `release_lag` -- rule 1's own
      arithmetic, applied to the date rather than to a row, because an absence
      carries no `available_at` of its own. See `_settlement_publication`. A
      grid date whose settlement record is not yet published stays a hole: rule
      1 already removed any settlement row dated there, so its absence is rule
      1's doing and not the record's, and a zero written over it is a value
      from the future wearing a zero;
    * the date is inside a supplying snapshot's coverage: from that snapshot's
      first settlement date to the Eastern calendar date of its retrieval
      timestamp, taken from `snapshot_retrieved_at` (source SHA-256 to the
      manifest's `retrieved_at`), both inclusive. A day the snapshot cannot
      speak to -- before its first settlement, or after it was retrieved --
      stays a hole. A snapshot that supplied settlement rows and has no usable
      retrieval timestamp raises `DataContractError`: never a zero without its
      bound;
    * the declared column's own series has no visible observation that day
      (`leg`), or, for the SOMA leg, no series of the snapshot has one (`day`).
      The adapter withholds the SOMA leg whole on a day an auction was not yet
      held, while that day's public legs stay observed, so a SOMA absence beside
      a settlement is a withheld result and stays a hole;
    * the column is drawn from `SETTLEMENT_ZERO_SOURCE` alone. A declaration
      naming a column from any other source raises `DataContractError`.

    The aggregate `treasury_settlement` is declared with its components, so on
    every zero day `treasury_settlement = bills + coupons` still holds rather
    than meeting a hole on its left. A zero is a value, so it is not counted in
    `holes`; it is counted in `settlement_zeros`, per built column and over the
    same grid, so the manifest publishes how much of a column is a written zero
    beside how much of it is missing. The fill happens here, at the build;
    `load_daily_panel` reads what the build wrote and decides nothing.

    Separately bounded by `build_cutoff` since A25, and the bound is the second
    condition above. Until then the rule held by a coincidence of another
    column's release lag: a settlement is published at 23:59 Eastern on its own
    settlement date, and on a build carrying `sofr` every grid date needs a SOFR
    value that is not published until the next business day at 15:00 Eastern, so
    a settlement on any grid date was already visible at whatever cutoff made
    that grid date a row. That is a property of the registry's declared lags and
    not of this rule, and a build declaring no `REQUIRED_FIELDS` column has no
    such guarantee -- the grid end is then held by whatever column the caller did
    declare, which may be published hours earlier on the same day. The two bounds
    are different questions and neither implies the other: the retrieval bound
    asks what the snapshot can speak to, the cutoff bound asks what this build
    could read, and a snapshot retrieved well after the cutoff covers dates the
    cutoff cannot see. On the tracked registry the cutoff bound does not bind on
    any build that declares `sofr`, which is every published one; it is not a
    value, it is the rule those builds happened to satisfy.

    Raises `DataContractError` if the cutoff is naive, if no declared column
    survives pricing, if nothing is left to index, under rule 5, or under rule 8.
    """

    from .contract import FEATURE_FIELDS

    if build_cutoff.tzinfo is None or build_cutoff.utcoffset() is None:
        raise DataContractError("build_cutoff must include a UTC offset")

    declared = list(columns)
    built, refusals = _priceable_columns(declared, registry, decision_time)
    if not built:
        raise DataContractError(
            "no declared column survived pricing: "
            + "; ".join(f"{name}: {reason}" for name, reason in sorted(refusals.items()))
        )

    # Source field -> panel column, for the built columns only. `FEATURE_FIELDS`
    # is the one place the rename is written down; deriving it by string
    # matching on `series_id` is the thing that block was written to avoid.
    column_for_series: Dict[str, str] = {}
    for column in built:
        for _source_id, field in FEATURE_FIELDS[column]:
            column_for_series[str(field)] = column

    visible = [row for row in observations if row.available_at <= build_cutoff]

    latest: Dict[tuple, PointInTimeObservation] = {}
    contributors: Dict[tuple, set] = {}
    for row in visible:
        column = column_for_series.get(row.series_id)
        if column is None:
            continue
        key = (column, row.ref_date)
        contributors.setdefault(key, set()).add(str(row.series_id))
        previous = latest.get(key)
        if previous is None or (row.available_at, row.vintage_id) > (
            previous.available_at,
            previous.vintage_id,
        ):
            latest[key] = row

    if not latest:
        raise DataContractError(
            f"no observation for any built column is available at {build_cutoff.isoformat()}"
        )

    # Rule 5. Only the sources behind the columns this build actually made, so
    # the question asked is "did a source this panel depends on violate an
    # identity", not "did any source in the registry". Restricting the registry
    # rather than filtering the answers is deliberate: a source that supplied
    # nothing should not be able to fail this build through any channel,
    # including a malformed declaration of its own.
    built_sources = {
        str(source_id) for column in built for source_id, _field in FEATURE_FIELDS[column]
    }
    # ...and only the sources that supplied something. A column can be priceable
    # and built from a source this build holds no file of -- `funding_inputs/`
    # carries no FR 2004 export -- and the restriction above admits it anyway,
    # because it keys on the built columns and not on what arrived. Rule 5 then
    # evaluated an identity over zero observations, and the evaluator raised
    # `no complete reference date`: a source that supplied nothing failing the
    # build, through exactly the channel the paragraph above says it should not
    # be able to use.
    #
    # Keyed on the source's declared series; see `_source_supplied_anything`.
    # Keying it on whether the identity has a complete reference date would be a
    # different rule wearing the same clothes -- that one also skips a source
    # whose terms were observed but never together on one date, and that case
    # must still raise. `sec_nmfp` reaches its unevaluable dates through it.
    supplied_series = {str(row.series_id) for row in visible}
    depended_on = {
        source_id: source
        for source_id, source in registry.items()
        if source_id in built_sources
        and source.get("identities")
        and _source_supplied_anything(source, supplied_series)
    }
    if depended_on:
        for evaluation in sorted(
            validate_accounting_identities(visible, depended_on).values(),
            key=lambda item: (item.source_id, item.name),
        ):
            if not evaluation.violations:
                continue
            worst = max(evaluation.violations, key=lambda item: item.residual)
            supplied = sorted(
                column
                for column in built
                if any(
                    str(source_id) == evaluation.source_id
                    for source_id, _field in FEATURE_FIELDS[column]
                )
            )
            raise DataContractError(
                f"{evaluation.source_id}: identity {evaluation.name} is violated on "
                f"{len(evaluation.violated_ref_dates)} reference date(s) "
                f"({', '.join(item.isoformat() for item in evaluation.violated_ref_dates)}); "
                f"worst residual {worst.residual:g} exceeds tolerance {worst.bound:g} on "
                f"{worst.ref_date}. This panel builds {', '.join(supplied)} from that "
                "source, so the build stops here rather than reporting a column whose "
                "source does not reconcile"
            )

    # Rule 7. Checked before any row is assembled, so an overlapping splice is
    # reported as the ambiguity it is rather than resolved by iteration order.
    overlaps = sorted(
        (column, ref_date, sorted(series))
        for (column, ref_date), series in contributors.items()
        if len(series) > 1
    )
    if overlaps:
        column, ref_date, series = overlaps[0]
        raise DataContractError(
            f"column {column!r} is declared from more than one field and they "
            f"overlap: {' and '.join(series)} both report {ref_date.isoformat()}"
            f"{f' (and {len(overlaps) - 1} further date(s))' if len(overlaps) > 1 else ''}. "
            "A spliced column's fields must partition the reference dates; "
            "which field wins on a shared date is a decision about what the "
            "series means and this build will not make it silently"
        )

    ref_dates = sorted({ref_date for _column, ref_date in latest})

    # Rule 6. `date` is in REQUIRED_FIELDS but is the index, not a column.
    required = [column for column in built if column in REQUIRED_FIELDS]
    retained = [
        ref_date
        for ref_date in ref_dates
        if all(latest.get((column, ref_date)) is not None for column in required)
    ]
    incomplete_dates = len(ref_dates) - len(retained)
    if not retained:
        raise DataContractError(
            "no reference date carries every required column ("
            + ", ".join(required)
            + f"); {incomplete_dates} date(s) were reported and none is a row"
        )

    # Rule 8, over the retained grid and nothing wider.
    zero_dates = _settlement_zero_dates(
        visible, built, retained, snapshot_retrieved_at, registry, build_cutoff
    )

    rows: List[DailyObservation] = []
    holes: Dict[str, int] = {column: 0 for column in built}
    # Counted in the write, not from `zero_dates` and not from the eligible
    # dates behind it: what the manifest reports is what went into the rows.
    # Keyed over every built column, so a column that took none says zero --
    # see `DailyPanelBuild`.
    settlement_zeros: Dict[str, int] = {column: 0 for column in built}
    for ref_date in retained:
        values: Dict[str, Optional[float]] = {}
        for column in built:
            row = latest.get((column, ref_date))
            if row is None and ref_date in zero_dates.get(column, ()):
                settlement_zeros[column] += 1
                values[column] = 0.0
            elif row is None:
                holes[column] += 1
                values[column] = None
            else:
                values[column] = row.value
        rows.append(DailyObservation(ref_date, values))

    return DailyPanelBuild(
        observations=tuple(rows),
        built_columns=tuple(built),
        refusals=dict(sorted(refusals.items())),
        holes=holes,
        build_cutoff=build_cutoff,
        decision_time=decision_time,
        incomplete_dates=incomplete_dates,
        settlement_zeros=settlement_zeros,
    )


def write_daily_panel(
    build: DailyPanelBuild, path: Path, *, source_shas: Sequence[str] = ()
) -> Path:
    """Write a built panel as CSV and its build manifest beside it.

    The CSV carries the built columns and nothing else, and an empty cell for a
    hole -- the encoding `load_daily_panel` already reads as absent. Note that
    a panel missing a `REQUIRED_FIELDS` column will not load back through
    `load_daily_panel`; that is a true report of what the sources support at
    latest vintage, not a defect in the writer, and inventing the column to
    make the round trip succeed is exactly what rule 3 forbids.

    The manifest is the committable half, as with the N-MFP archive set: the
    panel bytes are derived from gitignored raw snapshots and are not tracked.
    Returns the manifest path.

    The manifest carries `sha256`, the lowercase hex SHA-256 of the panel bytes
    as written -- the same convention the run records use. It is read back off
    disk with `path.read_bytes()` rather than taken over the text this function
    just rendered. The two agree here and would agree on most inputs, which is
    exactly why the distinction has to be made deliberately: a digest over a
    second rendering is a claim about a string that was never the file, and it
    stays green while the encoding, the line terminator or the write itself
    drifts away from it. `path` is what a later reader will hash, so `path` is
    what this hashes.

    Without it a manifest was a claim about a *name*: `baseline._bind_build_manifest`
    could bind a run record to it only by extent -- row count and end dates --
    and said so in the artifact as `build_manifest_binding.kind = "extent"`.
    Since Track B's B12 that function compares this `sha256` with the scored
    panel's and reports `kind = "digest"` where the manifest carries one, still
    checking the extent beside it; `"extent"` is now what a manifest written
    before the digest landed gets. What this function owes that comparison is
    a digest of the bytes and not of a second rendering, which is the paragraph
    above.
    """

    header = ["date", *build.built_columns]
    lines = [",".join(header)]
    for observation in build.observations:
        cells = [observation.date.isoformat()]
        for column in build.built_columns:
            value = observation.values.get(column)
            cells.append("" if value is None else format(value, ".15g"))
        lines.append(",".join(cells))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # The bytes on disk, not the text above: see the docstring.
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    dates = [observation.date for observation in build.observations]
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest = {
        "path": str(path),
        "build_cutoff": build.build_cutoff.isoformat(),
        "decision_time": str(build.decision_time),
        "row_count": len(build.observations),
        "sha256": digest,
        "start_date": dates[0].isoformat(),
        "end_date": dates[-1].isoformat(),
        "built_columns": list(build.built_columns),
        "refused_columns": dict(build.refusals),
        "holes": dict(build.holes),
        "incomplete_dates": build.incomplete_dates,
        # `settlement_zeros` (A27) and `empty_columns` (A28) are both on
        # `DailyPanelBuild` and are both deliberately not written here yet.
        # Adding either key changes what a re-run of the published build
        # writes, and `test_generated_results` compares the rebuilt
        # `panel.build_manifest` with the one
        # `docs/runs/persistence_funding.json` records key by key: a new key is
        # "present on one side only" and the Milestone A reproduction goes red.
        # Their own docstrings say the answer to that is a report and a
        # re-scored record, and `CLAUDE.md` refuses a rewrite of a published
        # record inside a block. So both facts are published to every reader of
        # a build and the file half waits on the human -- one human commit, for
        # both keys at once, with every affected record re-scored. See
        # `tests/test_data.TreasurySettlementZeroTests` (A27) and
        # `tests/test_data.EmptyColumnTests` (A28).
        "required_columns": [
            column for column in build.built_columns if column in REQUIRED_FIELDS
        ],
        "source_shas": list(source_shas),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def verify_daily_panel(panel_path: Path, manifest_path: Path) -> str:
    """Check a panel's bytes against the `sha256` its manifest records.

    Recomputes the SHA-256 of `panel_path` as it is on disk and compares it
    with the manifest's `sha256`, the field `write_daily_panel` writes. Returns
    the digest they agreed on. Raises `DataContractError` on disagreement,
    naming both digests and both paths, because "a digest did not match" is
    unactionable without knowing which file and which claim.

    The digest is taken over `panel_path.read_bytes()` and nothing else. Not
    over the panel loaded and re-rendered, and not over its text: a digest over
    a second rendering is a claim about a string that was never the file, and
    it stays green through exactly the encoding, line-terminator and write
    drift a digest exists to catch. `write_daily_panel`'s docstring makes the
    same point from the writing side; this is the reading side of it, and the
    two have to hash the same thing or the pair is decorative.

    Nor is it a comparison of extent. Row count, first date and last date are
    what `baseline._bind_build_manifest` falls back to when a manifest carries
    no digest, and it reports that as `build_manifest_binding.kind = "extent"`
    precisely because a file can keep all three while every value in it changes.
    Verification that agrees with extent verification on every input it will
    ever see is extent verification. Since B12 the binder prefers this `sha256`
    where the manifest has one and says `kind = "digest"`; that is the stronger
    of the two claims, and it exists because this function wrote the field.

    A manifest with no `sha256`, or one whose `sha256` is not 64 lowercase hex
    characters, is refused rather than passed. Every manifest written before
    the digest landed is such a manifest, and "there was no digest to compare"
    is not "the digest matched" -- a verifier that returns successfully on one
    of them reports the absence of evidence as evidence.

    The manifest's own `"path"` is deliberately not consulted. It records where
    the panel was written, which is an absolute path from a machine that may
    not be this one; binding on it would make a verified panel unverifiable the
    moment it moved, and it says nothing about the bytes either way.
    """

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataContractError(f"{manifest_path}: manifest is not valid JSON: {exc}")
    if not isinstance(manifest, dict):
        raise DataContractError(f"{manifest_path}: manifest is not a JSON object")

    recorded = manifest.get("sha256")
    if recorded is None:
        raise DataContractError(
            f"{manifest_path} carries no 'sha256', so there is no digest to compare "
            f"against {panel_path}; a manifest written before the digest landed is "
            "refused rather than passed"
        )
    if not isinstance(recorded, str) or not SHA256_PATTERN.match(recorded):
        raise DataContractError(
            f"{manifest_path}: 'sha256' is {recorded!r}, not 64 lowercase hex "
            f"characters, so there is no digest to compare against {panel_path}"
        )

    computed = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    if computed != recorded:
        raise DataContractError(
            f"{panel_path} hashes to {computed}, but {manifest_path} records "
            f"{recorded}. The panel is not the file the manifest describes"
        )
    return computed
