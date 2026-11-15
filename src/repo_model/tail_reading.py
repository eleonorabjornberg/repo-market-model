"""The per-tail reading rule, with both intervals (Eleonora, 12 November 2026, #1592; wording drafted for her to merge).

A tail is 'in line' only when the 90% interval of its ratio holds 1 and the 90% interval of its strict miss share holds the
nominal rate (0.05 for q05 and q95, 0.01 for q01 and q99). Otherwise the ratio call stands ('too thin' above 1, 'too wide'
below 1); a tail whose ratio holds 1 but whose miss share is off is 'miss share off'. #1547 read the ratio alone, so its
'in line' on the post-month-end q05 (miss share 0.091 [0.056, 0.128]) did not mean the tail covers.
"""

from __future__ import annotations

from typing import Optional, Sequence

NOMINAL = {"0.01": 0.01, "0.05": 0.05, "0.95": 0.05, "0.99": 0.01}


def tail_call(ratio: Sequence[float], miss: Optional[Sequence[float]], nominal: float) -> str:
    """The call of one tail from [point, low, high] of its ratio and of its miss share, against the nominal rate."""

    if ratio[1] > 1.0:
        return "too thin"
    if ratio[2] < 1.0:
        return "too wide"
    if miss is None:
        return "ratio holds 1, miss share not read"
    miss_holds_nominal = miss[1] <= nominal <= miss[2]
    if not miss_holds_nominal:
        return "miss share off"
    return "in line"
