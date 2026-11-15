"""The as-of rule a fit reads through: declared and target columns only (#1565).

Audit item 1 of #1554, ruled by Eleonora on 11 November 2026 (option a, "mask"): the feature row a fitter is handed
carries the target columns and the declared columns, each from its own read, and every other column of the anchor row
as `None`. An undeclared column has no availability declaration, so no value of it reaches a fitter. A model that
reads one is still refused with `LookAheadError` by `baseline._check_fitter_stayed_inside`, which is the refusal it
should get rather than a data error about the hole. The training frame (`InformationRule.frame`) is not masked this
way: it still carries the panel's value for an undeclared column.

Frozen exemptions (Eleonora, 12 November 2026, ruling on #1579, option 2). The final test's checksums
(`scripts/final_test_preregistration.py`, `declaration` and `crps_declaration`) hash `asof.py` whole and the source of
`baseline.py`'s fit and backtest code. A frozen declaration reads through the old, unmasked `InformationRule.observation`,
which is why `asof.py` is unchanged: the mask is this subclass, and `baseline.py` and `event_eval.py` take it under the
name `InformationRule` by their import line (an import is not hashed; a changed definition is). The frozen declarations
are named in `FROZEN_READ_EXEMPTIONS` and a declaration is exempt when its declared features equal an entry's as a set.
Every other fit is masked. Adding an entry is her decision; `tests/test_masked_rule.py` pins the list and derives it from
the frozen scripts, so it moves with them.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Dict, FrozenSet, Mapping, NamedTuple, Optional, Sequence, Tuple

from .asof import InformationRule, InformationSet, TARGET_COLUMNS
from .data import DailyObservation

__all__ = ["FROZEN_READ_EXEMPTIONS", "FrozenRead", "MaskedInformationRule", "is_frozen_read"]


class FrozenRead(NamedTuple):
    """One frozen declaration whose fits read through the unmasked observation."""

    features: FrozenSet[str]
    reason: str


_PUBLISHED_H1 = frozenset(
    (
        "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps", "tbill_13w", "tbill_4w", "tga",
        "treasury_settlement",
    )
)

#: The exemptions, by name; closed. Pinned by `tests/test_masked_rule.py`, which derives each from the frozen script.
FROZEN_READ_EXEMPTIONS: Mapping[str, FrozenRead] = MappingProxyType(
    {
        "persistence_and_leap_labels": FrozenRead(
            frozenset(("spread_bps",)),
            "the final test's persistence side of the CRPS cell (`crps_declaration` model_a) and the leap labels "
            "(`leap_labels`, `InformationRule(..., ('spread_bps',))`)",
        ),
        "published_distribution_h1": FrozenRead(
            _PUBLISHED_H1,
            "the published distribution at h = 1: the final test's CRPS_FEATURES (`crps_declaration` model_b), "
            "`published_v1`'s features, and the live record's `published_features(1)`",
        ),
        "published_distribution_h2_5": FrozenRead(
            _PUBLISHED_H1 - {"treasury_settlement"},
            "the live record's `published_features(h)` for h = 2..5, which drop the scheduled field",
        ),
        "scarcity_calendar": FrozenRead(
            frozenset(
                ("spread_bps", "reserve_scarcity_state", "days_to_month_end", "quarter_end", "tax_date",
                 "treasury_settlement")
            ),
            "final-test candidate `scarcity_calendar` (`_FEATURES`)",
        ),
        "dynamic_logit": FrozenRead(
            frozenset(
                ("spread_bps", "days_to_month_end", "quarter_end", "tax_date", "treasury_settlement_coupons",
                 "reserve_balances")
            ),
            "final-test candidate `dynamic_logit` (`_FEATURES`)",
        ),
        "direct_logistic_sofr_p1": FrozenRead(
            frozenset(
                ("spread_bps", "days_to_month_end", "quarter_end", "tax_date", "treasury_settlement",
                 "reserve_balances", "tga", "sofr_p1")
            ),
            "final-test candidate `direct_logistic_sofr_p1` (`_FEATURES`)",
        ),
        "v1_1": FrozenRead(
            frozenset(
                ("reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps", "tbill_13w", "tbill_4w",
                 "tga", "treasury_settlement", "iorb_announced_change_bps", "iorb_days_to_announced_change",
                 "on_rrp_depleted", "reserves_when_depleted", "settlement_day", "settlement_day_when_depleted",
                 "effr_minus_iorb_bp", "reserve_scarcity_state")
            ),
            "final-test candidate `v1_1` (`_FEATURES`)",
        ),
        "stacked_combiner": FrozenRead(
            frozenset(("persistence_logistic", "distributional_gbm", "dynamic_logit")),
            "final-test candidate `stacked_combiner` (`_FEATURES`)",
        ),
    }
)


def is_frozen_read(features: Sequence[str]) -> bool:
    """Whether a declared feature set is a frozen declaration's (as a set, not in order)."""

    declared = frozenset(features)
    return any(entry.features == declared for entry in FROZEN_READ_EXEMPTIONS.values())


class MaskedInformationRule(InformationRule):
    """`InformationRule` whose observation hands a fitter declared and target columns only.

    A frozen declaration (`FROZEN_READ_EXEMPTIONS`) reads through `InformationRule.observation` unchanged.
    """

    def observation(self, rows: Sequence[DailyObservation], info: InformationSet) -> DailyObservation:
        unmasked = super().observation(rows, info)
        if is_frozen_read(self.features):
            return unmasked
        keep = set(TARGET_COLUMNS) | set(self.composed)
        for group in self.groups:
            keep.update(group.columns)
        values: Dict[str, Optional[float]] = {
            column: (value if column in keep else None) for column, value in unmasked.values.items()
        }
        return DailyObservation(unmasked.date, values)
