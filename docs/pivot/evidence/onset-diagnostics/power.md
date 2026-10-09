# What 26 onsets can prove (#429)

Declaration `metadata/onset_diagnostics.json` (commit `1ec7f160e91d`), the judge's bootstrap (90% stationary, block length 10, 2000 replications), 500 experiments per cell. A cell is the share of experiments in which the condition holds. A model flags each onset independently with its true recall; only the recall conditions are simulated, not the false-alarm limit. 'Both' is tier 1's recall conditions together: the point recall is at least 0.5 and the lower end of the bootstrap interval is above the climatology recall at the same false alarms.

## Development window: 26 onsets over 1869 days (2018-07-06 to 2025-12-31), the real onset positions.

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.762 | 0.774 | 0.000 | 0.996 | 0.930 | 0.878 | 0.774 | 0.774 | 0.774 |
| 0.6 | 0.892 | 0.902 | 0.000 | 1.000 | 0.986 | 0.960 | 0.902 | 0.902 | 0.902 |
| 0.7 | 0.991 | 0.994 | 0.000 | 1.000 | 1.000 | 1.000 | 0.994 | 0.994 | 0.994 |
| 0.8 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Confirmation window: 1 onset(s), a parameter, evenly spaced over 169 days (no day of the window is read).

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.550 | 0.556 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.6 | 0.600 | 0.570 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.7 | 0.700 | 0.694 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.8 | 0.800 | 0.810 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Confirmation window: 2 onset(s), a parameter, evenly spaced over 169 days (no day of the window is read).

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.798 | 0.812 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.6 | 0.840 | 0.822 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.7 | 0.910 | 0.906 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.8 | 0.960 | 0.946 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Confirmation window: 3 onset(s), a parameter, evenly spaced over 169 days (no day of the window is read).

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.575 | 0.578 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.6 | 0.648 | 0.646 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.7 | 0.784 | 0.772 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.8 | 0.896 | 0.884 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Confirmation window: 4 onset(s), a parameter, evenly spaced over 169 days (no day of the window is read).

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.759 | 0.762 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.6 | 0.821 | 0.838 | 0.998 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 |
| 0.7 | 0.916 | 0.906 | 0.998 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 |
| 0.8 | 0.973 | 0.972 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Confirmation window: 5 onset(s), a parameter, evenly spaced over 169 days (no day of the window is read).

| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | lower end above clim. recall 0.115 | lower end above clim. recall 0.231 | lower end above clim. recall 0.269 | both, clim. recall 0.115 | both, clim. recall 0.231 | both, clim. recall 0.269 |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 0.593 | 0.596 | 0.708 | 0.168 | 0.092 | 0.076 | 0.168 | 0.092 | 0.076 |
| 0.6 | 0.683 | 0.674 | 0.714 | 0.194 | 0.132 | 0.100 | 0.194 | 0.132 | 0.100 |
| 0.7 | 0.837 | 0.834 | 0.690 | 0.270 | 0.210 | 0.198 | 0.270 | 0.210 | 0.198 |
| 0.8 | 0.942 | 0.954 | 0.654 | 0.326 | 0.260 | 0.248 | 0.326 | 0.260 | 0.248 |

