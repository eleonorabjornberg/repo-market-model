"""Shared contract fixtures, owned by neither track.

This module exists because the ownership gate is path-level and cannot see a
*semantic* collision. Four have been found on this project: the `release_lag`
dict-versus-scalar incompatibility, the duplicate spec filename, the
`calendar`-versus-`unit` naming collision on the same field, and the
event-window digest. The first three reached a merge; the fourth was caught
before one, by applying the rule below to a shape that had not yet collided.
Each time, both tracks stayed perfectly in lane and still shipped halves that do
not compose, because AGENT_CONTRACT.md named a field in prose without giving it
a key name, and each track picked its own.

What lives here, therefore, is every shape both tracks must agree on:
the release-lag schema (`validate_release_lag`, `validate_registry_release_lags`
and the vocabulary they check against), the event-window schema
(`EVENT_WINDOW_KEYS`, `event_window_digest`, `validate_event_windows_document`),
and the forecast quantile grid (`QUANTILE_LEVELS`). None was invented here --
each was lifted from the track that had reasoned it through, unchanged except
in name.

The fix is to make the shared shape executable and put it where neither track
owns it. Both tracks import this module; neither edits it. Changing it is a
human edit, and the ownership gate enforces that.

Stdlib only, by contract.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from types import MappingProxyType
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "BASES",
    "UNIT_FOR_BASIS",
    "END_OF_DAY",
    "AVAILABLE_TIME_RE",
    "QUANTILE_LEVELS",
    "validate_release_lag",
    "validate_registry_release_lags",
    "REVISION_POLICIES",
    "validate_field_release_lag",
    "IDENTITY_TOLERANCE_KEYS",
    "validate_identity_tolerance",
    "resolve_identity_tolerance",
    "validate_registry_identity_tolerances",
    "EVENT_WINDOW_KEYS",
    "event_window_digest",
    "validate_event_windows_document",
    "UndeclaredFeatureError",
    "FEATURE_FIELDS",
    "FEATURE_SOURCES",
    "DERIVED_FEATURES",
    "CALENDAR_FEATURES",
    "UNSOURCED_FEATURES",
    "sources_for_features",
    "TREASURY_BILL_SECURITY_TYPES",
    "TREASURY_COUPON_SECURITY_TYPES",
    "TREASURY_SETTLEMENT_COMPONENTS",
    "TREASURY_SETTLEMENT_IDENTITY",
    "treasury_settlement_component",
    "field_sources_for_features",
]

#: Fixed across every model so pinball loss, interval coverage, and predictive
#: distributions are comparable. The outer pair is the repository's existing
#: 90% interval; the median and quartiles give CRPS more than a three-point grid.
QUANTILE_LEVELS = (0.05, 0.25, 0.50, 0.75, 0.95)

#: The three publication bases the contract recognises, and the day-count unit
#: each one is measured in. The pairing is fixed: see "One rule per basis" in
#: AGENT_CONTRACT.md. `unit` is still declared explicitly rather than derived,
#: so that a source whose author meant the other calendar is a validation
#: error rather than a silent reinterpretation.
UNIT_FOR_BASIS = {
    "ref_date": "business_days",
    "record_date": "calendar_days",
    "snapshot_retrieved_at": None,  # contributes no purge; declares no day count
}

BASES = tuple(UNIT_FOR_BASIS)

#: `available_time` is an HH:MM wall-clock string in the declared `timezone`.
#: Seconds are not carried: nothing in the as-of rule resolves below a minute,
#: and a spurious `:59` invites the reader to believe it does.
AVAILABLE_TIME_RE = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

#: The conservative end-of-day convention, for a source whose publication time
#: within the day is unknown.
END_OF_DAY = "23:59"

_ALLOWED_KEYS = {
    "basis",
    "unit",
    "days",
    "worst_case_calendar_days",
    "available_time",
    "timezone",
    "note",
}

#: Keys a *field-level* release lag may add on top of `_ALLOWED_KEYS`. They
#: exist only at field level: a revision policy declared for a whole source
#: would be the claim this split was made to stop anyone making.
_FIELD_ALLOWED_KEYS = _ALLOWED_KEYS | {"revision_policy", "revision_evidence"}

#: The revision policies a field may declare. One, deliberately: the only
#: property that lets a latest-vintage snapshot stand in for a point-in-time
#: record is that the value never moves after publication.
REVISION_POLICIES = ("never_revised",)


def _is_int(value: object) -> bool:
    # bool is a subclass of int and must not pass as a day count.
    return isinstance(value, int) and not isinstance(value, bool)


def validate_release_lag(source_id: str, release_lag: object) -> list[str]:
    """Return a list of human-readable problems with one `release_lag` object.

    An empty list means the object conforms. This function never raises on
    malformed input and never returns a partial answer: callers that want to
    fail closed raise on a non-empty result.
    """

    problems: list[str] = []

    if not isinstance(release_lag, dict):
        return [f"{source_id}: release_lag must be an object, got {type(release_lag).__name__}"]

    unknown = sorted(set(release_lag) - _ALLOWED_KEYS)
    if unknown:
        problems.append(f"{source_id}: unknown release_lag keys {unknown}")

    basis = release_lag.get("basis")
    if basis not in UNIT_FOR_BASIS:
        problems.append(
            f"{source_id}: basis must be one of {list(BASES)}, got {basis!r}"
        )
        return problems

    note = release_lag.get("note")
    if note is not None and not isinstance(note, str):
        problems.append(f"{source_id}: note must be a string")

    expected_unit = UNIT_FOR_BASIS[basis]

    if expected_unit is None:
        # A snapshot source contributes no purge and MUST NOT be mapped to
        # zero. It therefore carries no day count and no unit at all: a `days:
        # 0` here is the silent zero this contract keeps legislating against,
        # written down as data.
        for key in ("unit", "days", "worst_case_calendar_days", "available_time"):
            if key in release_lag:
                problems.append(
                    f"{source_id}: a {basis} source must not declare {key!r}; it "
                    f"contributes no purge, and a day count here is the "
                    f"mapping-to-zero the contract prohibits"
                )
        if "timezone" in release_lag:
            problems.append(
                f"{source_id}: timezone is declared with no available_time to "
                f"interpret; a declared-and-never-read timezone is how naive "
                f"times got compared across zones once already"
            )
        return problems

    unit = release_lag.get("unit")
    if unit != expected_unit:
        problems.append(
            f"{source_id}: a {basis} source must declare unit "
            f"{expected_unit!r}, got {unit!r}"
        )

    days = release_lag.get("days")
    if not _is_int(days) or days < 0:
        problems.append(
            f"{source_id}: days must be a non-negative integer, got {days!r}"
        )

    if basis == "ref_date":
        bound = release_lag.get("worst_case_calendar_days")
        if not _is_int(bound):
            problems.append(
                f"{source_id}: a ref_date source must declare an integer "
                f"worst_case_calendar_days, got {bound!r}"
            )
        elif _is_int(days) and bound < days + 5:
            problems.append(
                f"{source_id}: worst_case_calendar_days {bound} is below "
                f"days + 5 ({days + 5}); a weekend plus three consecutive "
                f"holidays is the floor, and a bound that is too small makes "
                f"every purge sized from it too small"
            )

    available_time = release_lag.get("available_time")
    if basis == "record_date" and available_time is None:
        problems.append(
            f"{source_id}: a record_date source must declare available_time; "
            f"the rule adds a day when it falls after decision_time, which "
            f"cannot be evaluated without it (use {END_OF_DAY!r} for a source "
            f"whose intraday publication time is unknown)"
        )

    if available_time is not None:
        if not isinstance(available_time, str) or not AVAILABLE_TIME_RE.match(available_time):
            problems.append(
                f"{source_id}: available_time must be an HH:MM string, got "
                f"{available_time!r}"
            )
        timezone = release_lag.get("timezone")
        if not isinstance(timezone, str) or not timezone:
            problems.append(
                f"{source_id}: available_time requires a timezone; comparing "
                f"naive times across declared zones is a leakage bug, not a "
                f"formatting one"
            )
        else:
            try:
                ZoneInfo(timezone)
            except (ZoneInfoNotFoundError, ValueError):
                problems.append(
                    f"{source_id}: timezone {timezone!r} is not an IANA zone"
                )
    elif "timezone" in release_lag:
        problems.append(
            f"{source_id}: timezone is declared with no available_time to "
            f"interpret; drop one or add the other"
        )

    return problems


# --- The feature-to-source map -------------------------------------------
#
# Which sources a model's feature set draws on. Declared, not derived: the
# registry names fields in source vocabulary and the panel names them in
# model vocabulary, and three of the correspondences are pure renames with
# no rule behind them. An inversion that recovered them would be string
# matching, which is the thing the purge block was written to avoid.
#
# Held honest by the three assertions in `tests/test_contract.py`, not by
# anyone remembering to update it. An unasserted list stops describing the
# tree the moment someone adds a column.


class UndeclaredFeatureError(ValueError):
    """A feature name has no declared source and no declared reason to lack one.

    Distinct from a feature whose source is known to be absent: that is
    `UNSOURCED_FEATURES`, which raises with the reason attached. This is the
    name nobody has classified at all.
    """


#: Panel column -> the (source ID, source field) pairs it draws on.
#:
#: Both halves are stated because neither is derivable from the other: the
#: registry declares fields in source vocabulary and the panel uses model
#: vocabulary, and `SOFR`->`sofr`, `WTREGEN`->`tga`, `RRPONTSYD`->`on_rrp`,
#: `mmf_net_assets`->`mmf_assets` are renames with no rule behind them. The
#: field is what makes a field-level release lag addressable: one source can
#: carry an administered rate that is never revised beside a statistical
#: estimate that is, and a lag declared for the source is then wrong for both.
FEATURE_FIELDS = MappingProxyType(
    {
        "sofr": (("nyfed_sofr", "SOFR"),),
        "sofr_volume": (("nyfed_sofr", "SOFR_volume"),),
        "sofr_p25": (("nyfed_sofr", "SOFR_p25"),),
        "sofr_p75": (("nyfed_sofr", "SOFR_p75"),),
        # The administered leg is spliced. IORB begins 2021-07-29, the day the
        # Board consolidated IOER and IORR into a single rate on reserve
        # balances; IOER ends 2021-07-28. They abut exactly -- no overlap, no
        # gap -- and `build_daily_panel` rule 7 raises if that ever stops being
        # true rather than picking a winner. Without the splice the panel
        # begins in July 2021 and contains no stress episode at all: not
        # September 2019, not March 2020, which is to say none of the events
        # this repository exists to model.
        "iorb": (
            ("fred_macro_latest_vintage", "IORB"),
            ("fred_macro_latest_vintage", "IOER"),
        ),
        "tgcr": (("nyfed_tgcr", "TGCR"),),
        "bgcr": (("nyfed_bgcr", "BGCR"),),
        "reserve_balances": (("fred_macro_latest_vintage", "WRESBAL"),),
        "tga": (("fred_macro_latest_vintage", "WTREGEN"),),
        "on_rrp": (("fred_macro_latest_vintage", "RRPONTSYD"),),
        "treasury_settlement": (("treasury_auctions", "treasury_settlement"),),
        "mmf_assets": (("sec_nmfp", "mmf_net_assets"),),
        # The FR 2004 Treasury total. The adapter checks it against its thirteen
        # current-era components and converts millions to billions.
        "dealer_treasury_position": (("nyfed_fr2004", "PDPOSGST-TOT"),),
    }
)

#: The source IDs alone, projected from `FEATURE_FIELDS`. Derived rather than
#: declared: a second literal would be a second thing to keep current, and a
#: list that is not asserted against the thing it describes stops describing
#: it. `tests/test_contract.py` pins the projection against tuples written out
#: longhand, because a projection compared to its own source agrees by
#: construction whatever either says.
FEATURE_SOURCES = MappingProxyType(
    {
        feature: tuple(sorted({source for source, _field in pairs}))
        for feature, pairs in FEATURE_FIELDS.items()
    }
)

# Features computed from other features. Resolved to their constituents, so
# `spread_bps` draws on whatever `sofr` and `iorb` draw on and cannot fall
# out of step with them.
DERIVED_FEATURES = MappingProxyType(
    {
        "spread_bps": ("sofr", "iorb"),
    }
)

# Features that are a function of the scored date alone. These contribute no
# source. They are enumerated rather than inferred: a feature that
# contributes nothing to the purge is exactly the shape of an error, and the
# registry's `snapshot_retrieved_at` rule already establishes that nothing
# gets mapped to a zero gap by default.
CALENDAR_FEATURES = frozenset({"quarter_end", "tax_date"})

# Declared panel columns with no ingesting source. Using one raises, with the
# reason, rather than resolving to an empty source set. Empty since the FR 2004
# adapter gave `dealer_treasury_position` its source; the mechanism stays, and
# `tests/test_contract.py` exercises it with a planted entry rather than letting
# the loop over this mapping pass vacuously.
UNSOURCED_FEATURES = MappingProxyType({})


def sources_for_features(names):
    """The source IDs a feature set draws on, for `max_release_lag_days`.

    Derived features resolve to their constituents. Calendar features
    contribute nothing. An unknown name raises, and so does a declared name
    with no source -- the message carries the reason.

    Returns a sorted tuple, deduplicated. An all-calendar feature set returns
    an empty tuple; `registry.max_release_lag_days` then raises its own
    "sources must select at least one feature source". That is deliberate:
    the guard stays where it already is rather than being restated here,
    where it would agree with itself.
    """

    resolved = set()
    pending = list(names)
    seen = set()
    while pending:
        name = str(pending.pop())
        if name in seen:
            continue
        seen.add(name)
        if name in DERIVED_FEATURES:
            pending.extend(DERIVED_FEATURES[name])
            continue
        if name in CALENDAR_FEATURES:
            continue
        if name in UNSOURCED_FEATURES:
            raise UndeclaredFeatureError(
                f"feature {name!r} has no source: {UNSOURCED_FEATURES[name]}"
            )
        try:
            resolved.update(FEATURE_SOURCES[name])
        except KeyError as exc:
            raise UndeclaredFeatureError(
                f"feature {name!r} is not in contract.FEATURE_SOURCES, "
                f"contract.DERIVED_FEATURES, contract.CALENDAR_FEATURES or "
                f"contract.UNSOURCED_FEATURES. Every panel column must be "
                f"classified in exactly one of them; add it there rather "
                f"than at the call site"
            ) from exc
    return tuple(sorted(resolved))


def field_sources_for_features(names):
    """The (source ID, source field) pairs a feature set draws on.

    The field-level counterpart of `sources_for_features`, resolving derived
    and calendar features by the same rules and raising the same
    `UndeclaredFeatureError` for the same reasons. Returns a sorted,
    deduplicated tuple of pairs, for `registry.max_release_lag_days`.

    Deliberately not implemented in terms of `sources_for_features`, nor it in
    terms of this: the two walks are written out separately so that
    `tests/test_contract.py` can compare each against longhand expectations
    that neither produced. Two functions that delegate to one another agree by
    construction, which is the shape this file has already been caught in once.

    `sources_for_features` is left in place and unchanged. Callers move here
    when they are ready to be priced per field; until then nothing about the
    existing path moves.
    """

    resolved = set()
    pending = list(names)
    seen = set()
    while pending:
        name = str(pending.pop())
        if name in seen:
            continue
        seen.add(name)
        if name in DERIVED_FEATURES:
            pending.extend(DERIVED_FEATURES[name])
            continue
        if name in CALENDAR_FEATURES:
            continue
        if name in UNSOURCED_FEATURES:
            raise UndeclaredFeatureError(
                f"feature {name!r} has no source: {UNSOURCED_FEATURES[name]}"
            )
        try:
            pairs = FEATURE_FIELDS[name]
        except KeyError as exc:
            raise UndeclaredFeatureError(
                f"feature {name!r} is not in contract.FEATURE_FIELDS, "
                f"contract.DERIVED_FEATURES, contract.CALENDAR_FEATURES or "
                f"contract.UNSOURCED_FEATURES. Every panel column must be "
                f"classified in exactly one of them; add it there rather "
                f"than at the call site"
            ) from exc
        resolved.update((str(source), str(field)) for source, field in pairs)
    return tuple(sorted(resolved))


def validate_field_release_lag(source_id, field, block, source_basis):
    """Problems with one entry of a source's `field_release_lags`.

    Same contract as `validate_release_lag`: never raises, returns a list, an
    empty list means the object conforms. Adds the two rules that exist only at
    field level.

    A field on a `snapshot_retrieved_at` source may be priced only if it
    declares `revision_policy: "never_revised"` with a non-empty
    `revision_evidence`. Without that, a field-level `record_date` block is the
    snapshot refusal being talked out of a correct answer -- and that refusal is
    the only thing standing between this project and a benchmark computed on
    values that were revised after the day they are attributed to.

    A field on a source that already has a real basis must NOT claim a revision
    policy. There is nothing for it to license, and a declared-and-never-read
    key is how a timezone got compared across zones once already.
    """

    label = f"{source_id}.{field}"
    problems: list[str] = []

    if not isinstance(block, dict):
        return [
            f"{label}: field_release_lags entry must be an object, got "
            f"{type(block).__name__}"
        ]

    unknown = sorted(set(block) - _FIELD_ALLOWED_KEYS)
    if unknown:
        problems.append(f"{label}: unknown release_lag keys {unknown}")

    policy = block.get("revision_policy")
    evidence = block.get("revision_evidence")
    core = {key: value for key, value in block.items() if key in _ALLOWED_KEYS}

    if block.get("basis") == "snapshot_retrieved_at":
        problems.append(
            f"{label}: a field-level snapshot_retrieved_at block says nothing "
            f"the source did not already say; remove it rather than restating "
            f"the source's basis at field level"
        )
        return problems

    problems.extend(validate_release_lag(label, core))

    if source_basis == "snapshot_retrieved_at":
        if policy not in REVISION_POLICIES:
            problems.append(
                f"{label}: a field of a snapshot_retrieved_at source may be "
                f"priced only with revision_policy in {list(REVISION_POLICIES)}, "
                f"got {policy!r}. Latest vintage stands in for a point-in-time "
                f"record exactly when the value never moves after publication"
            )
        if not isinstance(evidence, str) or not evidence.strip():
            problems.append(
                f"{label}: revision_policy must carry a non-empty "
                f"revision_evidence naming what establishes it. A claim with no "
                f"evidence attached is indistinguishable from an assumption"
            )
    else:
        for key, value in (("revision_policy", policy), ("revision_evidence", evidence)):
            if value is not None:
                problems.append(
                    f"{label}: {key} is declared on a {source_basis} source, "
                    f"where it licenses nothing and will never be read"
                )

    return problems


def validate_registry_release_lags(registry: dict) -> dict[str, list[str]]:
    """Validate every source's `release_lag`. Returns {source_id: problems}.

    Sources declaring no `release_lag` at all are reported, because a missing
    lag reads as a zero lag to anything that skips it.
    """

    offenders: dict[str, list[str]] = {}
    for source_id, source in registry.items():
        if not isinstance(source, dict) or "release_lag" not in source:
            offenders[source_id] = [f"{source_id}: no release_lag declared"]
            continue
        problems = validate_release_lag(source_id, source["release_lag"])
        basis = None
        release_lag = source["release_lag"]
        if isinstance(release_lag, dict):
            basis = release_lag.get("basis")
        field_lags = source.get("field_release_lags", {})
        if not isinstance(field_lags, dict):
            problems.append(f"{source_id}: field_release_lags must be an object")
        else:
            for field in sorted(field_lags):
                problems.extend(
                    validate_field_release_lag(
                        source_id, field, field_lags[field], basis
                    )
                )
        if problems:
            offenders[source_id] = problems
    return offenders


#: Keys an identity `tolerance` object may carry.
IDENTITY_TOLERANCE_KEYS = frozenset({"absolute", "relative_ppm", "unit"})


def validate_identity_tolerance(source_id: str, name: str, tolerance: object) -> list[str]:
    """Problems with one declared identity's `tolerance`. Never raises.

    Same contract as `validate_release_lag`: returns a list, empty means the
    object conforms.

    A tolerance may declare `relative_ppm`, `absolute`, or both. Both is the
    intended form for a quantity whose scale moves: the relative part is the
    bound, and the absolute part is a floor under it so that a rounding
    residual on a small cross-section is not measured against parts per
    million of almost nothing.

    An absolute-only tolerance stays legal, because some identities really are
    exact -- gross subscriptions minus gross redemptions is net flow by
    definition, and a bound of a millionth of a billion is the right statement
    about it. What the schema stops is an absolute-only bound on a quantity
    that moves by orders of magnitude, which is not a tolerance but a number
    that happens to be larger than the worst thing seen so far. The schema
    cannot tell those two apart; a reader can, and now has somewhere to say
    which one this is.
    """

    label = f"{source_id}: identity {name}"
    problems: list[str] = []

    if not isinstance(tolerance, dict):
        return [
            f"{label}: tolerance must be an object, got "
            f"{type(tolerance).__name__}"
        ]

    unknown = sorted(set(tolerance) - IDENTITY_TOLERANCE_KEYS)
    if unknown:
        problems.append(f"{label}: unknown tolerance keys {unknown}")

    unit = tolerance.get("unit")
    if not isinstance(unit, str) or not unit.strip():
        problems.append(f"{label}: tolerance must declare a non-empty unit")

    absolute = tolerance.get("absolute")
    relative = tolerance.get("relative_ppm")

    if absolute is None and relative is None:
        problems.append(
            f"{label}: tolerance must declare absolute, relative_ppm, or both; "
            f"a tolerance that bounds nothing admits everything"
        )

    if absolute is not None:
        if isinstance(absolute, bool) or not isinstance(absolute, (int, float)):
            problems.append(f"{label}: tolerance absolute must be a number")
        elif absolute < 0:
            problems.append(f"{label}: tolerance absolute must not be negative")

    if relative is not None:
        if isinstance(relative, bool) or not isinstance(relative, (int, float)):
            problems.append(f"{label}: tolerance relative_ppm must be a number")
        elif relative <= 0:
            problems.append(
                f"{label}: tolerance relative_ppm must be positive; declare "
                f"absolute alone rather than a relative bound of zero"
            )

    return problems


def resolve_identity_tolerance(tolerance: dict, scale: float) -> float:
    """The bound one identity is held to at one scale.

    `max(absolute, relative_ppm * 1e-6 * abs(scale))`, with a missing part
    contributing nothing. The caller supplies `scale`: the magnitude of the
    quantity the identity is about, not of the residual.

    Scaling a residual by the size of the thing it is a residual *of* is what
    makes it a tolerance rather than a number, and it is not the anchoring
    failure this repository keeps finding: the residual is a difference of the
    two sides and the scale is their magnitude, so a scale computed from the
    same observations cannot move to accommodate the residual. Anchoring would
    be deriving the bound from the residual itself -- which is what calibrating
    an absolute bound against the worst month observed so far quietly does.

    Assumes `validate_identity_tolerance` has already passed.
    """

    absolute = float(tolerance.get("absolute") or 0.0)
    relative = float(tolerance.get("relative_ppm") or 0.0)
    return max(absolute, relative * 1e-6 * abs(float(scale)))


def validate_registry_identity_tolerances(registry: dict) -> dict[str, list[str]]:
    """Validate every declared identity's tolerance. Returns {source_id: problems}.

    A source declaring no identities is not an offender; a source declaring one
    without a conforming tolerance is.
    """

    offenders: dict[str, list[str]] = {}
    for source_id, source in registry.items():
        if not isinstance(source, dict):
            offenders[source_id] = [f"{source_id}: source must be an object"]
            continue
        identities = source.get("identities", [])
        if not isinstance(identities, list):
            offenders[source_id] = [f"{source_id}: identities must be a list"]
            continue
        problems: list[str] = []
        for identity in identities:
            if not isinstance(identity, dict):
                problems.append(f"{source_id}: identity must be an object")
                continue
            name = str(identity.get("name") or "").strip() or "<unnamed>"
            problems.extend(
                validate_identity_tolerance(source_id, name, identity.get("tolerance"))
            )
        if problems:
            offenders[source_id] = problems
    return offenders


#: Keys every declared window must carry. Extra keys are permitted — Track A
#: may want a rationale, a source citation, a revision note — and model-eval
#: ignores them.
EVENT_WINDOW_KEYS = ("name", "start", "end", "checksum")


def event_window_digest(name: str, start: str, end: str) -> str:
    """The normative per-window checksum for `metadata/events.json`.

    An opaque per-window `checksum` pins nothing: an edit that moves `start`
    and leaves `checksum` alone yields a document that still validates. For the
    checksum to detect the edit the contract is worried about, it has to be a
    digest *of the boundaries*.

    Args:
        name: the window's stable slug.
        start, end: ISO date strings, `YYYY-MM-DD`. Strings rather than `date`
            objects on purpose — the digest must be computable from the file's
            own bytes without a parse step that could normalise something, so
            what is hashed is what is written.

    Returns:
        Lowercase hex SHA-256, 64 characters.
    """

    canonical = json.dumps(
        {"name": name, "start": start, "end": end},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_event_windows_document(payload: object) -> list[str]:
    """Every way `payload` fails the event-window schema, as readable problems.

    Returns a list rather than raising so a malformed file reports all of its
    faults in one run. Track A should not have to fix one key, re-run, and
    discover the next. An empty list means conforming.

    The bare-list form that `load_event_windows` also accepts is for fixtures,
    not for the declared file: a list has nowhere to carry a version.
    """

    problems: list[str] = []

    if not isinstance(payload, dict):
        return [
            "document must be a JSON object with 'version' and 'windows', got "
            f"{type(payload).__name__}; the bare-list form load_event_windows "
            "also accepts is for fixtures, not for the declared file, because a "
            "list has nowhere to carry a version"
        ]

    if "version" not in payload:
        problems.append(
            "document has no 'version'; the contract requires the file be versioned"
        )
    elif not isinstance(payload["version"], (int, str)) or not str(
        payload["version"]
    ).strip():
        problems.append(
            f"'version' must be a non-empty int or string, got {payload['version']!r}"
        )

    entries = payload.get("windows")
    if entries is None:
        problems.append("document has no 'windows'")
        return problems
    if not isinstance(entries, list) or not entries:
        problems.append("'windows' must be a non-empty list")
        return problems

    seen_names = set()
    parsed = []
    for position, entry in enumerate(entries):
        label = f"window {position}"
        if not isinstance(entry, dict):
            problems.append(f"{label} is not an object")
            continue

        missing = [key for key in EVENT_WINDOW_KEYS if key not in entry]
        if missing:
            problems.append(f"{label} is missing {', '.join(missing)}")
            continue

        name = entry["name"]
        label = f"window {name!r}"
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{label} has a non-string or empty name")
            continue
        if name in seen_names:
            problems.append(
                f"{label} is declared twice; names identify windows in the journal"
            )
        seen_names.add(name)

        boundaries = {}
        for key in ("start", "end"):
            raw = entry[key]
            if not isinstance(raw, str):
                problems.append(f"{label} has a non-string {key}: {raw!r}")
                continue
            try:
                boundaries[key] = date.fromisoformat(raw)
            except ValueError:
                problems.append(
                    f"{label} has a non-ISO {key}: {raw!r}, expected YYYY-MM-DD"
                )
        if len(boundaries) != 2:
            continue
        if boundaries["end"] < boundaries["start"]:
            problems.append(
                f"{label} ends {boundaries['end']} before it starts {boundaries['start']}"
            )
            continue

        checksum = entry["checksum"]
        if not isinstance(checksum, str) or not checksum.strip():
            problems.append(f"{label} has a non-string or empty checksum")
        else:
            expected = event_window_digest(name, entry["start"], entry["end"])
            if checksum != expected:
                problems.append(
                    f"{label} checksum {checksum!r} does not match its boundaries; "
                    f"expected {expected!r}. Either an edge moved without the digest "
                    "being recomputed, or the digest is not "
                    "event_window_digest(name, start, end)"
                )

        parsed.append((name, boundaries["start"], boundaries["end"]))

    ordered = sorted(parsed, key=lambda item: item[1])
    if parsed != ordered:
        problems.append(
            "windows are not in ascending order of start date; the file is read "
            "by humans checking that a boundary has not moved, and an unsorted "
            "list makes that diff harder than it needs to be"
        )
    for earlier, later in zip(ordered, ordered[1:]):
        if later[1] <= earlier[2]:
            problems.append(
                f"windows {earlier[0]!r} ({earlier[1]}..{earlier[2]}) and "
                f"{later[0]!r} ({later[1]}..{later[2]}) overlap; a day in two "
                "knowledge holdouts is scored twice and spends two budgets"
            )

    return problems


# --- Treasury settlement components ----------------------------------------
#
# The bill / coupon / SOMA split of `treasury_settlement` (human decision,
# 10 Sep; docs/DATA_QUALITY_DECISIONS.md, "Treasury-settlement aggregation").
# Defined here, before the adapter block (A10) that emits them, because the
# split is a shape the data layer produces and the model layer reads: which
# security types count as bills, what "SOMA" means, and how tightly the parts
# must sum to the whole are decisions, and a track that picked them alone would
# be picking the definition its own criterion is checked against.
#
# What was checked before "private" was defined: `offering_amt` does NOT
# include SOMA. The Federal Reserve's rollover bids are noncompetitive tenders
# treated as add-ons to the announced auction size, and Treasury increases the
# total issue by the SOMA award (Federal Reserve Bank of New York, "FAQs:
# Treasury Rollovers"). So the existing aggregate is already the public leg,
# and the SOMA component sits OUTSIDE the identity rather than being the part
# subtracted to reach "private". Defining it as aggregate minus the public
# parts would be a residual, and a residual absorbs every error upstream.

#: Treasury's own bills-versus-coupons split, by the auction record's
#: `security_type`. Enumerated from that convention, not yet from a fixture:
#: the adapter block enumerates the values its fixture carries, and a value in
#: neither set is a refusal and a report -- never a third bucket, and never
#: "everything that is not a bill".
TREASURY_BILL_SECURITY_TYPES = frozenset({"Bill", "CMB"})
TREASURY_COUPON_SECURITY_TYPES = frozenset({"Note", "Bond", "TIPS", "FRN"})

#: Panel column -> (auction-record field it sums, security types it admits,
#: whether it is part of `treasury_settlement`). Units are USD billions, as for
#: the aggregate. `soma_accepted` is an auction RESULT, unlike `offering_amt`,
#: which is announced: the SOMA component may not be dated available before
#: the auction's results are published, and an adapter that dates it by the
#: announcement's `record_date` reads an outcome early.
TREASURY_SETTLEMENT_COMPONENTS = MappingProxyType(
    {
        "treasury_settlement_bill": (
            "offering_amt", TREASURY_BILL_SECURITY_TYPES, True,
        ),
        "treasury_settlement_coupon": (
            "offering_amt", TREASURY_COUPON_SECURITY_TYPES, True,
        ),
        "treasury_settlement_soma": (
            "soma_accepted",
            TREASURY_BILL_SECURITY_TYPES | TREASURY_COUPON_SECURITY_TYPES,
            False,
        ),
    }
)

#: The identity the split must satisfy, in the registry's identity shape.
#: The parts are sums of the same `offering_amt` values the aggregate sums, so
#: the only admissible disagreement is float summation order. 1e-9 USD
#: billions is one dollar: far above that, and far below any real record.
TREASURY_SETTLEMENT_IDENTITY = MappingProxyType(
    {
        "name": "treasury_settlement_is_bills_plus_coupons",
        "left": ("treasury_settlement",),
        "right": ("treasury_settlement_bill", "treasury_settlement_coupon"),
        "tolerance": MappingProxyType({"absolute": 1e-9, "unit": "USD billions"}),
    }
)


def treasury_settlement_component(security_type: str) -> str:
    """The public component an auction of this `security_type` settles into.

    Raises `ValueError` for a type in neither declared set. Classifying the
    unknown as a coupon is the residual trap one level down: a new instrument
    would be silently priced as a note.
    """
    if security_type in TREASURY_BILL_SECURITY_TYPES:
        return "treasury_settlement_bill"
    if security_type in TREASURY_COUPON_SECURITY_TYPES:
        return "treasury_settlement_coupon"
    raise ValueError(
        f"Treasury security_type {security_type!r} is neither a declared bill "
        f"type {sorted(TREASURY_BILL_SECURITY_TYPES)} nor a declared coupon type "
        f"{sorted(TREASURY_COUPON_SECURITY_TYPES)}; extending either set is a "
        "change to src/repo_model/contract.py"
    )
