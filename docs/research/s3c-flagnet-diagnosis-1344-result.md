# (s3c-ann-flagnet): where it gains, why it loses in 2020, and a draft prospective test (#1344)

**Hypothesis and step:** H5 (primary goal), step 3, the arm (s3c-ann-flagnet) beside the candidate (s3c-ann-net); her ruling of 1 November 2026 (ledger item 95, on #1326 question 1): test and diagnose the better arm. **Development data, not a verdict** (scoring protocol v1, #640). Nothing is registered or published; (s3c-ann-net) stays the candidate.

Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999` (built at the 18:00 decision instant). The walks are #1321's, rebuilt as merged and checked against its record: every pooled, lead and regime mean of the four models equals it to 1e-9 and the fitted-shift table equals it (True). Diagnostic intervals: 90% stationary bootstrap, block 10, 2000 replications, seed 1344, over the units of each group; they are not the protocol's studentized test, whose figures are #1321's. d is the arm less the reference, so below zero is a gain for the arm. The days of a group are resampled in date order as if consecutive (#1221). A share of the grid CRPS difference can exceed 100% when other groups have the opposite sign.

## Answers (development window; diagnostic intervals; readings from the interval on mean d)

1. **Where the Brier gain sits (H-f: undecided).** Against (s3c-ann-net), over the settlement-day target cells the Brier difference is skill +5.7%; d -0.0028 [-0.0056, -0.0002]: **gain**; over the neither-settles cells skill +4.8%; d -0.0021 [-0.0035, -0.0008]: **gain**. Summed over the cells where the spread went above +5 bp it is -18.76 (mean P(> +5 bp) 0.568 against the candidate's 0.527), over the others -4.01. By regime: 2018-19 skill +7.6%; d -0.0125 [-0.0188, -0.0066]: **gain**; 2020 skill -5.3%; d +0.0012 [-0.0005, +0.0036]: **undecided**.
2. **The 2020 loss (H-g, an over-shift: not supported).** At leads 2 to 5 in 2020 the realised settlement-day premium is +0.28 [-0.37, +1.16] bp; the fitted settlement shift is +0.89 [+0.54, +1.31] for (s3c-ann-net) and +1.38 [+0.89, +1.98] for (s3c-ann-flagnet); the flagnet's settlement-day bias (error on settlement days less the others; negative: forecast too high) is -0.74 [-1.52, +0.13]. The 2020 grid CRPS difference on settlement-day targets at leads 2 to 5: skill -5.4%; d +0.0976 [+0.0106, +0.2264]: **loss**.
3. **The immediate-release cash management bill days (H-h against (s3c-ann-net): not supported; against (s3c-ann): not read).** The 2020 grid CRPS difference with those days in: skill -3.2%; d +0.0470 [+0.0096, +0.0956]: **loss**; with them left out: skill -3.1%; d +0.0460 [+0.0080, +0.0911]: **loss**. They are 69 of the 2020 target days.
4. **In plain words.** Over the development window the grid CRPS difference is small (skill +0.6%; d -0.0091 [-0.0210, +0.0030]: **undecided**). The Brier gain is not confined to settlement days (it is a gain on both sets of days, above), and the grid CRPS difference does not sit there either: 102% of the grid CRPS difference sits on days when no leg settles, 157% in 2018-19, 119% where the scarcity state of the decision day is 3 and 91% on the cells where the spread went above +5 bp. On bill-only settlement days the arm is worse than the candidate: skill -0.3%; d +0.0058 [+0.0001, +0.0121]: **loss**. In 2020 the loss sits on settlement-day targets (110% of it), on coupon settlement days (115%) and in March to June (90%); leaving out the immediate-release days does not remove it. From 2020-04-03, where the confirmation days fall, the mean grid CRPS difference is -0.0008 (skill -0.08%): the development gain on grid CRPS is a 2018-19 gain. The shares rest on few days in places (the coupon-settlement days of 2020 are a few dozen) and the mechanisms are readings of the tables, not tested.

## Readings of the declared hypotheses

| hypothesis | reading |
|---|---|
| H-f | **undecided** |
| H-g | **not supported** |
| H-h against ann | **not read** |
| H-h against annnet | **not supported** |

## Table 1. Where (s3c-ann-flagnet) differs from (s3c-ann-net), development window

**Pooled** (grain: the decision day, the five leads averaged)

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| pooled | 9,275 | 1,855 | skill +0.6%; d -0.0091 [-0.0210, +0.0030]: **undecided** | skill +1.1%; d -0.0094 [-0.0201, +0.0013]: **undecided** | skill +5.3%; d -0.0025 [-0.0039, -0.0011]: **gain** | n/a |

**By lead**

| lead | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| h=1 | 1,855 | 1,855 | skill +1.0%; d -0.0147 [-0.0287, -0.0006]: **gain** | skill +1.7%; d -0.0139 [-0.0260, -0.0018]: **gain** | skill +7.8%; d -0.0033 [-0.0051, -0.0017]: **gain** | +32% |
| h=2 | 1,855 | 1,855 | skill +0.7%; d -0.0113 [-0.0249, +0.0021]: **undecided** | skill +1.3%; d -0.0109 [-0.0226, +0.0008]: **undecided** | skill +5.0%; d -0.0022 [-0.0038, -0.0007]: **gain** | +25% |
| h=3 | 1,855 | 1,855 | skill +0.6%; d -0.0095 [-0.0215, +0.0026]: **undecided** | skill +1.2%; d -0.0102 [-0.0212, +0.0009]: **undecided** | skill +5.7%; d -0.0027 [-0.0044, -0.0012]: **gain** | +21% |
| h=4 | 1,855 | 1,855 | skill +0.4%; d -0.0065 [-0.0191, +0.0069]: **undecided** | skill +0.8%; d -0.0067 [-0.0184, +0.0057]: **undecided** | skill +4.2%; d -0.0020 [-0.0035, -0.0007]: **gain** | +14% |
| h=5 | 1,855 | 1,855 | skill +0.2%; d -0.0033 [-0.0164, +0.0104]: **undecided** | skill +0.6%; d -0.0052 [-0.0168, +0.0072]: **undecided** | skill +4.3%; d -0.0021 [-0.0035, -0.0008]: **gain** | +7% |

**By whether a leg settles on the target day**

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 4,722 | 946 | skill -0.0%; d +0.0003 [-0.0238, +0.0278]: **undecided** | skill -0.2%; d +0.0026 [-0.0173, +0.0246]: **undecided** | skill +5.7%; d -0.0028 [-0.0056, -0.0002]: **gain** | -2% |
| neither settles | 4,553 | 913 | skill +1.5%; d -0.0188 [-0.0322, -0.0063]: **gain** | skill +4.3%; d -0.0219 [-0.0341, -0.0108]: **gain** | skill +4.8%; d -0.0021 [-0.0035, -0.0008]: **gain** | +102% |

**By settlement-day type of the target day**

| type | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| bill settlement day | 3,881 | 777 | skill -0.0%; d +0.0009 [-0.0121, +0.0159]: **undecided** | skill -0.6%; d +0.0063 [-0.0060, +0.0207]: **undecided** | skill +1.9%; d -0.0009 [-0.0024, +0.0005]: **undecided** | -5% |
| bill settlement day with a cash management bill | 1,760 | 352 | skill -1.0%; d +0.0096 [-0.0049, +0.0302]: **undecided** | skill -6.2%; d +0.0107 [-0.0019, +0.0319]: **undecided** | skill -0.9%; d +0.0001 [-0.0002, +0.0004]: **undecided** | -20% |
| bill settlement day without one | 2,121 | 425 | skill +0.2%; d -0.0062 [-0.0269, +0.0149]: **undecided** | skill -0.1%; d +0.0026 [-0.0164, +0.0201]: **undecided** | skill +2.1%; d -0.0017 [-0.0044, +0.0009]: **undecided** | +15% |
| coupon settlement day | 1,205 | 242 | skill +0.8%; d -0.0158 [-0.1473, +0.1115]: **undecided** | skill +1.2%; d -0.0159 [-0.1155, +0.0871]: **undecided** | skill +20.6%; d -0.0131 [-0.0300, +0.0006]: **undecided** | +22% |
| neither settles | 4,553 | 913 | skill +1.5%; d -0.0188 [-0.0322, -0.0063]: **gain** | skill +4.3%; d -0.0219 [-0.0341, -0.0108]: **gain** | skill +4.8%; d -0.0021 [-0.0035, -0.0008]: **gain** | +102% |

**By leg**

| leg | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| bill only | 3,517 | 704 | skill -0.3%; d +0.0058 [+0.0001, +0.0121]: **loss** | skill -0.8%; d +0.0089 [+0.0031, +0.0155]: **loss** | skill -1.6%; d +0.0007 [+0.0001, +0.0014]: **loss** | -24% |
| both legs | 364 | 73 | skill +2.1%; d -0.0456 [-0.1793, +0.0789]: **undecided** | skill +1.4%; d -0.0193 [-0.1548, +0.1112]: **undecided** | skill +22.9%; d -0.0162 [-0.0386, +0.0018]: **undecided** | +19% |
| coupon only | 841 | 169 | skill +0.1%; d -0.0029 [-0.1543, +0.1365]: **undecided** | skill +1.1%; d -0.0144 [-0.1217, +0.0800]: **undecided** | skill +19.4%; d -0.0117 [-0.0303, +0.0018]: **undecided** | +3% |
| neither | 4,553 | 913 | skill +1.5%; d -0.0188 [-0.0322, -0.0063]: **gain** | skill +4.3%; d -0.0219 [-0.0341, -0.0108]: **gain** | skill +4.8%; d -0.0021 [-0.0035, -0.0008]: **gain** | +102% |

**By regime of the target day**

| regime | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 2018-19 | 1,795 | 361 | skill +2.0%; d -0.0730 [-0.1228, -0.0220]: **gain** | skill +2.0%; d -0.0635 [-0.1119, -0.0148]: **gain** | skill +7.6%; d -0.0125 [-0.0188, -0.0066]: **gain** | +157% |
| 2020 | 1,255 | 251 | skill -3.2%; d +0.0470 [+0.0096, +0.0956]: **loss** | skill -5.2%; d +0.0300 [-0.0037, +0.0720]: **undecided** | skill -5.3%; d +0.0012 [-0.0005, +0.0036]: **undecided** | -70% |
| 2021-23 | 3,740 | 748 | skill +0.2%; d -0.0010 [-0.0029, +0.0011]: **undecided** | skill +1.1%; d -0.0001 [-0.0004, +0.0003]: **undecided** | skill +2.6%; d -0.0000 [-0.0000, +0.0000]: **undecided** | +4% |
| 2024 | 1,250 | 250 | skill +0.3%; d -0.0034 [-0.0128, +0.0045]: **undecided** | skill +0.2%; d -0.0004 [-0.0018, +0.0007]: **undecided** | skill +1.0%; d -0.0002 [-0.0005, +0.0000]: **undecided** | +5% |
| 2025-26 | 1,235 | 249 | skill +0.1%; d -0.0031 [-0.0156, +0.0089]: **undecided** | skill +0.9%; d -0.0081 [-0.0179, -0.0002]: **gain** | skill +1.9%; d -0.0012 [-0.0025, -0.0002]: **gain** | +4% |

**By calendar month of the target day**

| month | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| April | 725 | 145 | skill +1.2%; d -0.0143 [-0.0364, +0.0021]: **undecided** | skill +3.2%; d -0.0129 [-0.0301, +0.0005]: **undecided** | skill +7.8%; d -0.0039 [-0.0101, +0.0009]: **undecided** | +12% |
| August | 885 | 177 | skill +1.5%; d -0.0158 [-0.0453, +0.0102]: **undecided** | skill +4.5%; d -0.0146 [-0.0383, +0.0060]: **undecided** | skill +15.3%; d -0.0040 [-0.0092, -0.0002]: **gain** | +17% |
| December | 830 | 168 | skill +1.6%; d -0.0298 [-0.0771, +0.0120]: **undecided** | skill +2.4%; d -0.0270 [-0.0690, +0.0090]: **undecided** | skill +6.8%; d -0.0050 [-0.0128, +0.0014]: **undecided** | +29% |
| February | 670 | 134 | skill +3.5%; d -0.0274 [-0.0695, +0.0049]: **undecided** | skill +3.9%; d -0.0094 [-0.0335, +0.0097]: **undecided** | skill +2.3%; d -0.0003 [-0.0019, +0.0009]: **undecided** | +22% |
| January | 715 | 143 | skill +0.3%; d -0.0059 [-0.0555, +0.0309]: **undecided** | skill +1.1%; d -0.0102 [-0.0578, +0.0243]: **undecided** | skill +18.2%; d -0.0053 [-0.0122, -0.0000]: **gain** | +5% |
| July | 775 | 157 | skill +0.2%; d -0.0028 [-0.0320, +0.0284]: **undecided** | skill +0.1%; d -0.0006 [-0.0323, +0.0318]: **undecided** | skill +2.5%; d -0.0010 [-0.0024, +0.0002]: **undecided** | +2% |
| June | 725 | 145 | skill +0.7%; d -0.0083 [-0.0291, +0.0081]: **undecided** | skill +6.3%; d -0.0166 [-0.0417, +0.0003]: **undecided** | skill +11.6%; d -0.0038 [-0.0084, -0.0001]: **gain** | +7% |
| March | 765 | 153 | skill -1.6%; d +0.0312 [-0.0243, +0.1044]: **undecided** | skill -3.4%; d +0.0302 [-0.0222, +0.1019]: **undecided** | skill +0.5%; d -0.0002 [-0.0051, +0.0047]: **undecided** | -28% |
| May | 740 | 148 | skill +1.2%; d -0.0111 [-0.0370, +0.0092]: **undecided** | skill +6.9%; d -0.0193 [-0.0449, +0.0003]: **undecided** | skill +4.0%; d -0.0014 [-0.0037, +0.0003]: **undecided** | +10% |
| November | 780 | 156 | skill +1.7%; d -0.0229 [-0.0549, +0.0053]: **undecided** | skill +3.1%; d -0.0278 [-0.0598, +0.0003]: **undecided** | skill +4.6%; d -0.0036 [-0.0090, +0.0015]: **undecided** | +21% |
| October | 850 | 170 | skill +2.4%; d -0.0435 [-0.0802, -0.0104]: **gain** | skill +3.4%; d -0.0380 [-0.0764, -0.0055]: **gain** | skill +2.4%; d -0.0020 [-0.0046, +0.0001]: **undecided** | +44% |
| September | 815 | 163 | skill -1.2%; d +0.0427 [-0.0010, +0.0981]: **undecided** | skill -1.2%; d +0.0347 [-0.0089, +0.0915]: **undecided** | skill -2.6%; d +0.0010 [-0.0008, +0.0035]: **undecided** | -41% |

**By the scarcity state of the decision day**

| state | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 0 (abundant) | 5,205 | 1,041 | skill +0.1%; d -0.0006 [-0.0031, +0.0020]: **undecided** | skill +0.0%; d -0.0000 [-0.0007, +0.0006]: **undecided** | skill +1.1%; d -0.0000 [-0.0001, +0.0000]: **undecided** | +4% |
| 1 to 2 | 1,765 | 353 | skill -0.9%; d +0.0107 [-0.0001, +0.0219]: **undecided** | skill +0.4%; d -0.0016 [-0.0087, +0.0070]: **undecided** | skill +0.8%; d -0.0002 [-0.0006, +0.0003]: **undecided** | -23% |
| 3 (scarce) | 2,305 | 461 | skill +1.2%; d -0.0433 [-0.0870, +0.0002]: **undecided** | skill +1.2%; d -0.0365 [-0.0759, +0.0031]: **undecided** | skill +6.1%; d -0.0097 [-0.0147, -0.0050]: **gain** | +119% |

**By realised event**

| set | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| event: spread above +5 bp | 680 | 138 | skill +1.5%; d -0.1117 [-0.2081, -0.0077]: **gain** | skill +1.4%; d -0.1077 [-0.2020, -0.0054]: **gain** | skill +8.9%; d -0.0272 [-0.0437, -0.0119]: **gain** | +91% |
| no event | 8,595 | 1,721 | skill +0.1%; d -0.0009 [-0.0112, +0.0104]: **undecided** | skill +0.5%; d -0.0016 [-0.0103, +0.0080]: **undecided** | skill +1.9%; d -0.0005 [-0.0012, +0.0003]: **undecided** | +9% |

**The probabilities and the Brier difference by realised event**

| set | cells | mean P(> +5 bp), arm | reference | Brier difference summed (arm less reference) |
|---|---|---|---|---|
| spread above +5 bp | 680 | 0.568 | 0.527 | -18.76 |
| no event | 8,595 | 0.059 | 0.061 | -4.01 |

Observed frequency of the event over these cells: 7.3%.

**Settlement-day cells against the rest, by regime**

*2018-19*

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 845 | 169 | skill +1.6%; d -0.0854 [-0.1793, +0.0076]: **undecided** | skill +1.0%; d -0.0467 [-0.1292, +0.0377]: **undecided** | skill +9.9%; d -0.0175 [-0.0300, -0.0052]: **gain** | +55% |
| neither settles | 950 | 192 | skill +2.8%; d -0.0621 [-0.1131, -0.0120]: **gain** | skill +4.5%; d -0.0783 [-0.1239, -0.0345]: **gain** | skill +5.3%; d -0.0081 [-0.0139, -0.0024]: **gain** | +45% |

*2020*

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 680 | 136 | skill -5.4%; d +0.0958 [+0.0101, +0.2197]: **loss** | skill -9.6%; d +0.0775 [+0.0060, +0.1764]: **loss** | skill -10.1%; d +0.0031 [-0.0004, +0.0089]: **undecided** | +110% |
| neither settles | 575 | 115 | skill +0.9%; d -0.0107 [-0.0506, +0.0224]: **undecided** | skill +8.6%; d -0.0263 [-0.0411, -0.0141]: **gain** | skill +8.5%; d -0.0011 [-0.0023, -0.0002]: **gain** | -10% |

*2021-23*

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 1,940 | 388 | skill -0.2%; d +0.0013 [-0.0030, +0.0064]: **undecided** | skill -5.4%; d +0.0004 [-0.0002, +0.0015]: **undecided** | skill -2.6%; d +0.0000 [-0.0000, +0.0000]: **undecided** | -66% |
| neither settles | 1,800 | 360 | skill +0.6%; d -0.0034 [-0.0074, -0.0002]: **gain** | skill +11.8%; d -0.0006 [-0.0015, -0.0000]: **gain** | skill +9.6%; d -0.0000 [-0.0000, -0.0000]: **gain** | +166% |

*2024*

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 630 | 126 | skill +0.0%; d -0.0003 [-0.0128, +0.0106]: **undecided** | skill -0.2%; d +0.0007 [-0.0009, +0.0023]: **undecided** | skill +0.3%; d -0.0001 [-0.0003, +0.0001]: **undecided** | +5% |
| neither settles | 620 | 124 | skill +0.7%; d -0.0065 [-0.0146, +0.0011]: **undecided** | skill +5.0%; d -0.0014 [-0.0029, -0.0002]: **gain** | skill +37.0%; d -0.0003 [-0.0007, -0.0000]: **gain** | +95% |

*2025-26*

| target day | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 627 | 127 | skill -0.4%; d +0.0095 [-0.0163, +0.0367]: **undecided** | skill +0.3%; d -0.0037 [-0.0191, +0.0103]: **undecided** | skill +1.5%; d -0.0009 [-0.0025, +0.0004]: **undecided** | -192% |
| neither settles | 608 | 122 | skill +0.7%; d -0.0162 [-0.0370, +0.0051]: **undecided** | skill +1.7%; d -0.0128 [-0.0273, -0.0014]: **gain** | skill +2.3%; d -0.0016 [-0.0036, -0.0000]: **gain** | +292% |

**Against (s3c-ann) (the flag) and (s3c-ann-net) against (s3c-ann), pooled and by regime**

(s3c-ann-flagnet) against (s3c-ann):

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| pooled | 9,275 | 1,855 | skill +0.7%; d -0.0105 [-0.0157, -0.0053]: **gain** | skill +0.4%; d -0.0032 [-0.0058, -0.0007]: **gain** | skill +1.0%; d -0.0005 [-0.0008, -0.0002]: **gain** | n/a |
| 2018-19 | 1,795 | 361 | skill +0.3%; d -0.0117 [-0.0190, -0.0051]: **gain** | skill +0.3%; d -0.0095 [-0.0169, -0.0027]: **gain** | skill +0.6%; d -0.0010 [-0.0019, -0.0000]: **gain** | +22% |
| 2020 | 1,255 | 251 | skill -1.0%; d +0.0160 [-0.0017, +0.0414]: **undecided** | skill -1.1%; d +0.0064 [-0.0014, +0.0160]: **undecided** | skill -0.1%; d +0.0000 [-0.0004, +0.0004]: **undecided** | -21% |
| 2021-23 | 3,740 | 748 | skill +0.6%; d -0.0041 [-0.0084, -0.0004]: **gain** | skill +2.2%; d -0.0002 [-0.0003, -0.0000]: **gain** | skill +2.6%; d -0.0000 [-0.0000, -0.0000]: **gain** | +16% |
| 2024 | 1,250 | 250 | skill +1.9%; d -0.0203 [-0.0339, -0.0073]: **gain** | skill +1.8%; d -0.0030 [-0.0076, -0.0001]: **gain** | skill +3.6%; d -0.0006 [-0.0017, -0.0000]: **gain** | +26% |
| 2025-26 | 1,235 | 249 | skill +2.0%; d -0.0443 [-0.0623, -0.0264]: **gain** | skill +1.4%; d -0.0128 [-0.0257, -0.0013]: **gain** | skill +1.8%; d -0.0012 [-0.0031, +0.0005]: **undecided** | +57% |

(s3c-ann-net) against (s3c-ann):

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| pooled | 9,275 | 1,855 | skill +0.1%; d -0.0014 [-0.0133, +0.0108]: **undecided** | skill -0.7%; d +0.0062 [-0.0043, +0.0164]: **undecided** | skill -4.5%; d +0.0020 [+0.0007, +0.0034]: **loss** | n/a |
| 2018-19 | 1,795 | 361 | skill -1.7%; d +0.0613 [+0.0071, +0.1130]: **loss** | skill -1.7%; d +0.0540 [+0.0034, +0.1031]: **loss** | skill -7.5%; d +0.0115 [+0.0057, +0.0175]: **loss** | -826% |
| 2020 | 1,255 | 251 | skill +2.0%; d -0.0311 [-0.0669, -0.0005]: **gain** | skill +3.9%; d -0.0236 [-0.0614, +0.0068]: **undecided** | skill +4.9%; d -0.0012 [-0.0037, +0.0006]: **undecided** | +292% |
| 2021-23 | 3,740 | 748 | skill +0.5%; d -0.0031 [-0.0071, +0.0003]: **undecided** | skill +1.1%; d -0.0001 [-0.0005, +0.0002]: **undecided** | skill -0.0%; d +0.0000 [-0.0000, +0.0000]: **undecided** | +88% |
| 2024 | 1,250 | 250 | skill +1.6%; d -0.0170 [-0.0321, -0.0023]: **gain** | skill +1.6%; d -0.0027 [-0.0070, +0.0005]: **undecided** | skill +2.6%; d -0.0005 [-0.0013, +0.0000]: **undecided** | +159% |
| 2025-26 | 1,235 | 249 | skill +1.8%; d -0.0412 [-0.0648, -0.0167]: **gain** | skill +0.5%; d -0.0047 [-0.0169, +0.0080]: **undecided** | skill -0.1%; d +0.0001 [-0.0019, +0.0021]: **undecided** | +389% |

## Table 2. The 2020 difference

### (s3c-ann-flagnet) against (s3c-ann-net)

**All of 2020, and March to June against the rest**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 2020 | 1,255 | 251 | skill -3.2%; d +0.0470 [+0.0096, +0.0956]: **loss** | skill -5.2%; d +0.0300 [-0.0037, +0.0720]: **undecided** | skill -5.3%; d +0.0012 [-0.0005, +0.0036]: **undecided** | n/a |
| March to June | 425 | 85 | skill -4.6%; d +0.1243 [+0.0299, +0.2420]: **loss** | skill -6.5%; d +0.0784 [-0.0093, +0.1879]: **undecided** | skill -5.8%; d +0.0034 [-0.0017, +0.0101]: **undecided** | +90% |
| rest of 2020 | 830 | 166 | skill -0.9%; d +0.0074 [-0.0077, +0.0225]: **undecided** | skill -2.0%; d +0.0052 [-0.0095, +0.0210]: **undecided** | skill -1.4%; d +0.0001 [-0.0003, +0.0004]: **undecided** | +10% |

**By month of the target day**

| month | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| April | 105 | 21 | skill +2.4%; d -0.0394 [-0.1050, +0.0234]: **undecided** | skill +8.3%; d -0.0146 [-0.0287, -0.0006]: **gain** | skill +12.4%; d -0.0014 [-0.0027, -0.0000]: **gain** | -7% |
| August | 105 | 21 | skill -0.2%; d +0.0017 [-0.0199, +0.0235]: **undecided** | skill +3.5%; d -0.0046 [-0.0120, +0.0027]: **undecided** | skill +11.7%; d -0.0000 [-0.0000, -0.0000]: **gain** | +0% |
| December | 110 | 22 | skill +3.7%; d -0.0334 [-0.0593, -0.0094]: **gain** | skill +12.3%; d -0.0277 [-0.0432, -0.0127]: **gain** | skill +11.1%; d -0.0005 [-0.0008, -0.0003]: **gain** | -6% |
| February | 95 | 19 | skill +1.4%; d -0.0083 no interval: **not read** | skill -32.4%; d +0.0414 no interval: **not read** | skill -12.8%; d +0.0003 no interval: **not read** | -1% |
| January | 105 | 21 | skill -5.2%; d +0.0453 [-0.0081, +0.1038]: **undecided** | skill -18.7%; d +0.0544 [+0.0039, +0.1077]: **loss** | skill -27.3%; d +0.0014 [+0.0002, +0.0026]: **loss** | +8% |
| July | 110 | 22 | skill +1.5%; d -0.0140 [-0.0411, +0.0127]: **undecided** | skill +4.4%; d -0.0259 [-0.0437, -0.0110]: **gain** | skill +10.2%; d -0.0005 [-0.0009, -0.0001]: **gain** | -3% |
| June | 110 | 22 | skill -8.3%; d +0.0789 [+0.0585, +0.1013]: **loss** | skill +0.7%; d -0.0010 [-0.0053, +0.0033]: **undecided** | skill +6.6%; d -0.0003 [-0.0004, -0.0001]: **gain** | +15% |
| March | 110 | 22 | skill -5.6%; d +0.3798 [-0.0820, +0.8621]: **undecided** | skill -7.3%; d +0.3180 [-0.0857, +0.7380]: **undecided** | skill -7.0%; d +0.0149 [-0.0088, +0.0397]: **undecided** | +71% |
| May | 100 | 20 | skill -4.7%; d +0.0653 [+0.0317, +0.1009]: **loss** | skill -0.3%; d +0.0000 [-0.0013, +0.0015]: **undecided** | skill +3.9%; d -0.0000 [-0.0000, +0.0000]: **undecided** | +11% |
| November | 95 | 19 | skill -1.5%; d +0.0185 no interval: **not read** | skill -1.6%; d +0.0065 no interval: **not read** | skill +3.4%; d -0.0003 no interval: **not read** | +3% |
| October | 105 | 21 | skill -5.5%; d +0.0382 [+0.0114, +0.0668]: **loss** | skill -9.1%; d +0.0161 [-0.0026, +0.0358]: **undecided** | skill -5.9%; d +0.0002 [-0.0001, +0.0007]: **undecided** | +7% |
| September | 105 | 21 | skill -1.7%; d +0.0137 [-0.0162, +0.0428]: **undecided** | skill +18.0%; d -0.0122 [-0.0246, -0.0003]: **gain** | skill +21.0%; d -0.0000 [-0.0001, -0.0000]: **gain** | +2% |

**By settlement-day type, by leg, and by the scarcity state of the decision day**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 680 | 136 | skill -5.4%; d +0.0958 [+0.0101, +0.2197]: **loss** | skill -9.6%; d +0.0775 [+0.0060, +0.1764]: **loss** | skill -10.1%; d +0.0031 [-0.0004, +0.0089]: **undecided** | +110% |
| neither settles | 575 | 115 | skill +0.9%; d -0.0107 [-0.0506, +0.0224]: **undecided** | skill +8.6%; d -0.0263 [-0.0411, -0.0141]: **gain** | skill +8.5%; d -0.0011 [-0.0023, -0.0002]: **gain** | -10% |
| bill settlement day | 560 | 112 | skill -1.6%; d +0.0281 [-0.0220, +0.0964]: **undecided** | skill -5.1%; d +0.0399 [-0.0026, +0.1094]: **undecided** | skill -2.8%; d +0.0008 [-0.0002, +0.0024]: **undecided** | +27% |
| bill settlement day with a cash management bill | 450 | 90 | skill -3.0%; d +0.0417 [-0.0121, +0.1113]: **undecided** | skill -12.3%; d +0.0446 [-0.0033, +0.1205]: **undecided** | skill -4.6%; d +0.0007 [-0.0002, +0.0021]: **undecided** | +32% |
| bill settlement day without one | 110 | 22 | skill +0.8%; d -0.0275 [-0.0728, +0.0217]: **undecided** | skill -0.8%; d +0.0205 [+0.0042, +0.0363]: **loss** | skill -1.5%; d +0.0013 [-0.0003, +0.0029]: **undecided** | -5% |
| coupon settlement day | 170 | 34 | skill -19.3%; d +0.4008 [+0.0862, +0.7435]: **loss** | skill -27.6%; d +0.3144 [+0.0339, +0.6120]: **loss** | skill -22.9%; d +0.0127 [+0.0004, +0.0264]: **loss** | +115% |
| bill only | 510 | 102 | skill +0.4%; d -0.0059 [-0.0168, +0.0035]: **undecided** | skill +0.2%; d -0.0014 [-0.0053, +0.0024]: **undecided** | skill +0.2%; d -0.0000 [-0.0004, +0.0004]: **undecided** | -5% |
| both legs | 50 | 10 | skill -11.7%; d +0.3749 no interval: **not read** | skill -27.5%; d +0.4608 no interval: **not read** | skill -10.0%; d +0.0097 no interval: **not read** | +32% |
| coupon only | 120 | 24 | skill -25.6%; d +0.4115 [+0.1017, +0.7263]: **loss** | skill -27.7%; d +0.2534 [+0.0264, +0.4891]: **loss** | skill -36.6%; d +0.0139 [+0.0002, +0.0292]: **loss** | +84% |
| neither | 575 | 115 | skill +0.9%; d -0.0107 [-0.0506, +0.0224]: **undecided** | skill +8.6%; d -0.0263 [-0.0411, -0.0141]: **gain** | skill +8.5%; d -0.0011 [-0.0023, -0.0002]: **gain** | -10% |
| state 0 (abundant) | 10 | 2 | skill -10.5%; d +0.1451 no interval: **not read** | skill -1.6%; d +0.0009 no interval: **not read** | skill -6.5%; d +0.0001 no interval: **not read** | +2% |
| state 1 to 2 | 935 | 189 | skill -1.5%; d +0.0154 [-0.0032, +0.0343]: **undecided** | skill +1.3%; d -0.0031 [-0.0115, +0.0055]: **undecided** | skill +0.4%; d -0.0000 [-0.0003, +0.0003]: **undecided** | +34% |
| state 3 (scarce) | 310 | 64 | skill -4.1%; d +0.1156 [+0.0167, +0.2373]: **loss** | skill -7.0%; d +0.1129 [+0.0346, +0.2091]: **loss** | skill -6.1%; d +0.0045 [-0.0006, +0.0110]: **undecided** | +64% |

**The immediate-release cash management bill days** (an auction with no stated release time settles on the target day, #1301)

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| in them | 345 | 69 | skill -3.3%; d +0.0497 [-0.0198, +0.1342]: **undecided** | skill -15.1%; d +0.0571 [-0.0047, +0.1281]: **undecided** | skill -5.0%; d +0.0009 [-0.0004, +0.0026]: **undecided** | +29% |
| 2020 with them left out | 910 | 182 | skill -3.1%; d +0.0460 [+0.0080, +0.0911]: **loss** | skill -3.0%; d +0.0197 [-0.0103, +0.0523]: **undecided** | skill -5.4%; d +0.0013 [-0.0009, +0.0041]: **undecided** | n/a |

Target days: 69.

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any immediate-release day | 345 | 69 | skill -3.3%; d +0.0497 [-0.0198, +0.1342]: **undecided** | skill -15.1%; d +0.0571 [-0.0047, +0.1281]: **undecided** | skill -5.0%; d +0.0009 [-0.0004, +0.0026]: **undecided** | +29% |
| 2020 with them all left out | 910 | 182 | skill -3.1%; d +0.0460 [+0.0080, +0.0911]: **loss** | skill -3.0%; d +0.0197 [-0.0103, +0.0523]: **undecided** | skill -5.4%; d +0.0013 [-0.0009, +0.0041]: **undecided** | n/a |

Target days: 69.

### (s3c-ann-flagnet) against (s3c-ann)

**All of 2020, and March to June against the rest**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 2020 | 1,255 | 251 | skill -1.0%; d +0.0160 [-0.0017, +0.0414]: **undecided** | skill -1.1%; d +0.0064 [-0.0014, +0.0160]: **undecided** | skill -0.1%; d +0.0000 [-0.0004, +0.0004]: **undecided** | n/a |
| March to June | 425 | 85 | skill -1.7%; d +0.0468 [-0.0038, +0.1081]: **undecided** | skill -1.6%; d +0.0202 [+0.0003, +0.0445]: **loss** | skill -0.3%; d +0.0002 [-0.0009, +0.0012]: **undecided** | +99% |
| rest of 2020 | 830 | 166 | skill -0.0%; d +0.0002 [-0.0051, +0.0053]: **undecided** | skill +0.2%; d -0.0006 [-0.0041, +0.0028]: **undecided** | skill +1.2%; d -0.0000 [-0.0002, +0.0001]: **undecided** | +1% |

**By month of the target day**

| month | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| April | 105 | 21 | skill -8.7%; d +0.1264 [-0.0148, +0.2732]: **undecided** | skill -13.6%; d +0.0195 [+0.0003, +0.0391]: **loss** | skill -13.5%; d +0.0012 [+0.0000, +0.0023]: **loss** | +66% |
| August | 105 | 21 | skill +0.6%; d -0.0048 [-0.0125, +0.0027]: **undecided** | skill +1.6%; d -0.0020 [-0.0075, +0.0035]: **undecided** | skill -2.9%; d +0.0000 [+0.0000, +0.0000]: **loss** | -3% |
| December | 110 | 22 | skill -0.6%; d +0.0053 [-0.0038, +0.0149]: **undecided** | skill -2.4%; d +0.0047 [-0.0024, +0.0120]: **undecided** | skill -3.4%; d +0.0001 [-0.0001, +0.0004]: **undecided** | +3% |
| February | 95 | 19 | skill +1.2%; d -0.0076 no interval: **not read** | skill +2.3%; d -0.0040 no interval: **not read** | skill +3.8%; d -0.0001 no interval: **not read** | -4% |
| January | 105 | 21 | skill +0.3%; d -0.0032 [-0.0155, +0.0089]: **undecided** | skill +2.6%; d -0.0090 [-0.0188, +0.0008]: **undecided** | skill +6.1%; d -0.0004 [-0.0009, +0.0000]: **undecided** | -2% |
| July | 110 | 22 | skill -0.9%; d +0.0086 [-0.0054, +0.0222]: **undecided** | skill +0.2%; d -0.0010 [-0.0100, +0.0076]: **undecided** | skill +3.7%; d -0.0002 [-0.0003, -0.0001]: **gain** | +5% |
| June | 110 | 22 | skill -1.0%; d +0.0099 [-0.0224, +0.0436]: **undecided** | skill -21.6%; d +0.0276 [+0.0109, +0.0445]: **loss** | skill -30.0%; d +0.0009 [+0.0002, +0.0016]: **loss** | +5% |
| March | 110 | 22 | skill -0.6%; d +0.0445 [-0.0200, +0.1122]: **undecided** | skill -0.7%; d +0.0313 [-0.0343, +0.0988]: **undecided** | skill +0.6%; d -0.0014 [-0.0050, +0.0020]: **undecided** | +24% |
| May | 100 | 20 | skill -0.4%; d +0.0062 [-0.0230, +0.0350]: **undecided** | skill -3.4%; d +0.0005 [+0.0002, +0.0008]: **loss** | skill -3.2%; d +0.0000 [+0.0000, +0.0000]: **loss** | +3% |
| November | 95 | 19 | skill +0.1%; d -0.0011 no interval: **not read** | skill -0.5%; d +0.0020 no interval: **not read** | skill -1.7%; d +0.0002 no interval: **not read** | -1% |
| October | 105 | 21 | skill +0.4%; d -0.0028 [-0.0164, +0.0113]: **undecided** | skill +1.0%; d -0.0019 [-0.0129, +0.0093]: **undecided** | skill +0.2%; d -0.0000 [-0.0003, +0.0003]: **undecided** | -1% |
| September | 105 | 21 | skill -0.7%; d +0.0055 [-0.0088, +0.0209]: **undecided** | skill -12.2%; d +0.0060 [+0.0005, +0.0117]: **loss** | skill -8.7%; d +0.0000 [+0.0000, +0.0000]: **loss** | +3% |

**By settlement-day type, by leg, and by the scarcity state of the decision day**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 680 | 136 | skill -1.6%; d +0.0296 [-0.0024, +0.0735]: **undecided** | skill -1.5%; d +0.0127 [-0.0007, +0.0282]: **undecided** | skill -0.2%; d +0.0001 [-0.0005, +0.0006]: **undecided** | +101% |
| neither settles | 575 | 115 | skill +0.0%; d -0.0002 [-0.0019, +0.0013]: **undecided** | skill +0.4%; d -0.0010 [-0.0019, -0.0003]: **gain** | skill +0.4%; d -0.0000 [-0.0001, +0.0000]: **undecided** | -1% |
| bill settlement day | 560 | 112 | skill -1.9%; d +0.0339 [-0.0129, +0.1023]: **undecided** | skill -2.1%; d +0.0170 [-0.0036, +0.0464]: **undecided** | skill -2.8%; d +0.0008 [+0.0000, +0.0021]: **loss** | +95% |
| bill settlement day with a cash management bill | 450 | 90 | skill -2.8%; d +0.0400 [-0.0187, +0.1179]: **undecided** | skill -5.3%; d +0.0205 [-0.0049, +0.0530]: **undecided** | skill -6.5%; d +0.0010 [+0.0000, +0.0024]: **loss** | +90% |
| bill settlement day without one | 110 | 22 | skill -0.3%; d +0.0089 [-0.0068, +0.0269]: **undecided** | skill -0.1%; d +0.0025 [-0.0061, +0.0124]: **undecided** | skill -0.1%; d +0.0001 [-0.0004, +0.0007]: **undecided** | +5% |
| coupon settlement day | 170 | 34 | skill -2.3%; d +0.0563 [+0.0117, +0.1015]: **loss** | skill -3.4%; d +0.0478 [+0.0083, +0.0870]: **loss** | skill +0.7%; d -0.0005 [-0.0033, +0.0017]: **undecided** | +48% |
| bill only | 510 | 102 | skill -1.3%; d +0.0207 [-0.0188, +0.0741]: **undecided** | skill -0.1%; d +0.0010 [-0.0092, +0.0128]: **undecided** | skill -1.2%; d +0.0003 [-0.0001, +0.0008]: **undecided** | +53% |
| both legs | 50 | 10 | skill -4.9%; d +0.1677 no interval: **not read** | skill -9.2%; d +0.1793 no interval: **not read** | skill -6.7%; d +0.0068 no interval: **not read** | +42% |
| coupon only | 120 | 24 | skill -0.5%; d +0.0098 [-0.0507, +0.0655]: **undecided** | skill +0.6%; d -0.0070 [-0.0606, +0.0423]: **undecided** | skill +6.3%; d -0.0035 [-0.0077, +0.0006]: **undecided** | +6% |
| neither | 575 | 115 | skill +0.0%; d -0.0002 [-0.0019, +0.0013]: **undecided** | skill +0.4%; d -0.0010 [-0.0019, -0.0003]: **gain** | skill +0.4%; d -0.0000 [-0.0001, +0.0000]: **undecided** | -1% |
| state 0 (abundant) | 10 | 2 | skill -11.7%; d +0.1601 no interval: **not read** | skill -4.2%; d +0.0023 no interval: **not read** | skill -0.6%; d +0.0000 no interval: **not read** | +8% |
| state 1 to 2 | 935 | 189 | skill -2.1%; d +0.0216 [-0.0000, +0.0525]: **undecided** | skill -5.2%; d +0.0115 [+0.0024, +0.0240]: **loss** | skill -9.4%; d +0.0005 [+0.0001, +0.0011]: **loss** | +98% |
| state 3 (scarce) | 310 | 64 | skill +0.1%; d -0.0040 [-0.0103, +0.0024]: **undecided** | skill +0.4%; d -0.0075 [-0.0131, -0.0021]: **gain** | skill +1.7%; d -0.0013 [-0.0026, -0.0002]: **gain** | -6% |

**The immediate-release cash management bill days** (an auction with no stated release time settles on the target day, #1301)

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| in them | 345 | 69 | skill -3.8%; d +0.0571 [-0.0169, +0.1510]: **undecided** | skill -7.6%; d +0.0307 [+0.0002, +0.0702]: **loss** | skill -7.6%; d +0.0014 [+0.0002, +0.0030]: **loss** | +98% |
| 2020 with them left out | 910 | 182 | skill -0.0%; d +0.0004 [-0.0098, +0.0094]: **undecided** | skill +0.4%; d -0.0028 [-0.0105, +0.0039]: **undecided** | skill +1.9%; d -0.0005 [-0.0013, +0.0000]: **undecided** | n/a |

Target days: 69.

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any immediate-release day | 345 | 69 | skill -3.8%; d +0.0571 [-0.0169, +0.1510]: **undecided** | skill -7.6%; d +0.0307 [+0.0002, +0.0702]: **loss** | skill -7.6%; d +0.0014 [+0.0002, +0.0030]: **loss** | +98% |
| 2020 with them all left out | 910 | 182 | skill -0.0%; d +0.0004 [-0.0098, +0.0094]: **undecided** | skill +0.4%; d -0.0028 [-0.0105, +0.0039]: **undecided** | skill +1.9%; d -0.0005 [-0.0013, +0.0000]: **undecided** | n/a |

Target days: 69.

### (s3c-ann-net) against (s3c-ann), as #1320 read it

**All of 2020, and March to June against the rest**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 2020 | 1,255 | 251 | skill +2.0%; d -0.0311 [-0.0669, -0.0005]: **gain** | skill +3.9%; d -0.0236 [-0.0614, +0.0068]: **undecided** | skill +4.9%; d -0.0012 [-0.0037, +0.0006]: **undecided** | n/a |
| March to June | 425 | 85 | skill +2.8%; d -0.0776 [-0.1703, +0.0036]: **undecided** | skill +4.6%; d -0.0583 [-0.1528, +0.0134]: **undecided** | skill +5.2%; d -0.0033 [-0.0105, +0.0019]: **undecided** | +85% |
| rest of 2020 | 830 | 166 | skill +0.8%; d -0.0072 [-0.0248, +0.0101]: **undecided** | skill +2.2%; d -0.0058 [-0.0239, +0.0113]: **undecided** | skill +2.6%; d -0.0001 [-0.0005, +0.0003]: **undecided** | +15% |

**By month of the target day**

| month | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| April | 105 | 21 | skill -11.4%; d +0.1658 [-0.0308, +0.3681]: **undecided** | skill -23.8%; d +0.0341 [+0.0010, +0.0681]: **loss** | skill -29.7%; d +0.0025 [+0.0000, +0.0051]: **loss** | -45% |
| August | 105 | 21 | skill +0.8%; d -0.0065 [-0.0294, +0.0161]: **undecided** | skill -2.0%; d +0.0026 [-0.0026, +0.0083]: **undecided** | skill -16.6%; d +0.0000 [+0.0000, +0.0000]: **loss** | +2% |
| December | 110 | 22 | skill -4.5%; d +0.0387 [+0.0107, +0.0683]: **loss** | skill -16.8%; d +0.0324 [+0.0145, +0.0502]: **loss** | skill -16.3%; d +0.0007 [+0.0002, +0.0011]: **loss** | -11% |
| February | 95 | 19 | skill -0.1%; d +0.0007 no interval: **not read** | skill +26.2%; d -0.0454 no interval: **not read** | skill +14.7%; d -0.0004 no interval: **not read** | -0% |
| January | 105 | 21 | skill +5.2%; d -0.0485 [-0.1156, +0.0128]: **undecided** | skill +17.9%; d -0.0634 [-0.1250, -0.0043]: **gain** | skill +26.2%; d -0.0018 [-0.0034, -0.0003]: **gain** | +13% |
| July | 110 | 22 | skill -2.4%; d +0.0226 [-0.0095, +0.0554]: **undecided** | skill -4.4%; d +0.0249 [+0.0087, +0.0414]: **loss** | skill -7.2%; d +0.0003 [-0.0000, +0.0007]: **undecided** | -6% |
| June | 110 | 22 | skill +6.8%; d -0.0690 [-0.0924, -0.0431]: **gain** | skill -22.4%; d +0.0286 [+0.0135, +0.0441]: **loss** | skill -39.2%; d +0.0012 [+0.0003, +0.0020]: **loss** | +19% |
| March | 110 | 22 | skill +4.7%; d -0.3353 [-0.7809, +0.0826]: **undecided** | skill +6.2%; d -0.2867 [-0.6545, +0.0670]: **undecided** | skill +7.1%; d -0.0163 [-0.0398, +0.0067]: **undecided** | +95% |
| May | 100 | 20 | skill +4.1%; d -0.0591 [-0.1209, -0.0002]: **gain** | skill -3.1%; d +0.0004 [-0.0012, +0.0020]: **undecided** | skill -7.4%; d +0.0000 [-0.0000, +0.0001]: **undecided** | +15% |
| November | 95 | 19 | skill +1.6%; d -0.0196 no interval: **not read** | skill +1.1%; d -0.0045 no interval: **not read** | skill -5.3%; d +0.0005 no interval: **not read** | +5% |
| October | 105 | 21 | skill +5.6%; d -0.0410 [-0.0753, -0.0075]: **gain** | skill +9.2%; d -0.0180 [-0.0414, +0.0051]: **undecided** | skill +5.8%; d -0.0003 [-0.0008, +0.0002]: **undecided** | +11% |
| September | 105 | 21 | skill +1.0%; d -0.0082 [-0.0463, +0.0315]: **undecided** | skill -36.8%; d +0.0182 [+0.0010, +0.0359]: **loss** | skill -37.6%; d +0.0001 [+0.0000, +0.0001]: **loss** | +2% |

**By settlement-day type, by leg, and by the scarcity state of the decision day**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 680 | 136 | skill +3.6%; d -0.0661 [-0.1615, +0.0037]: **undecided** | skill +7.4%; d -0.0648 [-0.1530, +0.0024]: **undecided** | skill +9.0%; d -0.0031 [-0.0090, +0.0005]: **undecided** | +115% |
| neither settles | 575 | 115 | skill -0.9%; d +0.0104 [-0.0213, +0.0485]: **undecided** | skill -9.0%; d +0.0252 [+0.0136, +0.0393]: **loss** | skill -8.9%; d +0.0010 [+0.0002, +0.0022]: **loss** | -15% |
| bill settlement day | 560 | 112 | skill -0.3%; d +0.0058 [-0.0339, +0.0463]: **undecided** | skill +2.8%; d -0.0229 [-0.0612, +0.0071]: **undecided** | skill -0.0%; d +0.0000 [-0.0006, +0.0006]: **undecided** | -8% |
| bill settlement day with a cash management bill | 450 | 90 | skill +0.1%; d -0.0017 [-0.0455, +0.0456]: **undecided** | skill +6.2%; d -0.0241 [-0.0642, +0.0100]: **undecided** | skill -1.8%; d +0.0003 [-0.0003, +0.0009]: **undecided** | +2% |
| bill settlement day without one | 110 | 22 | skill -1.1%; d +0.0364 [-0.0087, +0.0784]: **undecided** | skill +0.7%; d -0.0179 [-0.0376, +0.0023]: **undecided** | skill +1.3%; d -0.0011 [-0.0027, +0.0004]: **undecided** | -10% |
| coupon settlement day | 170 | 34 | skill +14.2%; d -0.3445 [-0.6832, -0.0215]: **gain** | skill +19.0%; d -0.2666 [-0.5670, +0.0236]: **undecided** | skill +19.1%; d -0.0131 [-0.0276, +0.0008]: **undecided** | +150% |
| bill only | 510 | 102 | skill -1.6%; d +0.0266 [-0.0168, +0.0836]: **undecided** | skill -0.4%; d +0.0025 [-0.0080, +0.0145]: **undecided** | skill -1.3%; d +0.0003 [-0.0002, +0.0009]: **undecided** | -35% |
| both legs | 50 | 10 | skill +6.1%; d -0.2072 no interval: **not read** | skill +14.4%; d -0.2816 no interval: **not read** | skill +3.0%; d -0.0030 no interval: **not read** | +27% |
| coupon only | 120 | 24 | skill +20.0%; d -0.4017 [-0.7732, -0.0448]: **gain** | skill +22.2%; d -0.2603 [-0.5483, +0.0133]: **undecided** | skill +31.4%; d -0.0173 [-0.0353, +0.0001]: **undecided** | +124% |
| neither | 575 | 115 | skill -0.9%; d +0.0104 [-0.0213, +0.0485]: **undecided** | skill -9.0%; d +0.0252 [+0.0136, +0.0393]: **loss** | skill -8.9%; d +0.0010 [+0.0002, +0.0022]: **loss** | -15% |
| state 0 (abundant) | 10 | 2 | skill -1.1%; d +0.0150 no interval: **not read** | skill -2.5%; d +0.0014 no interval: **not read** | skill +5.5%; d -0.0001 no interval: **not read** | -0% |
| state 1 to 2 | 935 | 189 | skill -0.6%; d +0.0062 [-0.0268, +0.0470]: **undecided** | skill -6.6%; d +0.0145 [+0.0037, +0.0269]: **loss** | skill -9.8%; d +0.0005 [+0.0002, +0.0009]: **loss** | +1% |
| state 3 (scarce) | 310 | 64 | skill +4.1%; d -0.1196 [-0.2388, -0.0214]: **gain** | skill +7.0%; d -0.1204 [-0.2156, -0.0420]: **gain** | skill +7.4%; d -0.0058 [-0.0131, -0.0001]: **gain** | +99% |

**The immediate-release cash management bill days** (an auction with no stated release time settles on the target day, #1301)

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| in them | 345 | 69 | skill -0.5%; d +0.0074 [-0.0415, +0.0620]: **undecided** | skill +6.5%; d -0.0264 [-0.0770, +0.0161]: **undecided** | skill -2.5%; d +0.0005 [-0.0002, +0.0012]: **undecided** | -7% |
| 2020 with them left out | 910 | 182 | skill +3.0%; d -0.0456 [-0.0950, -0.0041]: **gain** | skill +3.3%; d -0.0225 [-0.0609, +0.0121]: **undecided** | skill +7.0%; d -0.0018 [-0.0053, +0.0006]: **undecided** | n/a |

Target days: 69.

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any immediate-release day | 345 | 69 | skill -0.5%; d +0.0074 [-0.0415, +0.0620]: **undecided** | skill +6.5%; d -0.0264 [-0.0770, +0.0161]: **undecided** | skill -2.5%; d +0.0005 [-0.0002, +0.0012]: **undecided** | -7% |
| 2020 with them all left out | 910 | 182 | skill +3.0%; d -0.0456 [-0.0950, -0.0041]: **gain** | skill +3.3%; d -0.0225 [-0.0609, +0.0121]: **undecided** | skill +7.0%; d -0.0018 [-0.0053, +0.0006]: **undecided** | n/a |

Target days: 69.

### (s3c-ann-flagnet) against (s3c)

**All of 2020, and March to June against the rest**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| 2020 | 1,255 | 251 | skill -5.2%; d +0.0763 [+0.0191, +0.1505]: **loss** | skill -8.4%; d +0.0469 [+0.0053, +0.1014]: **loss** | skill -6.3%; d +0.0014 [-0.0005, +0.0038]: **undecided** | n/a |
| March to June | 425 | 85 | skill -7.2%; d +0.1922 [+0.0439, +0.3776]: **loss** | skill -9.4%; d +0.1107 [-0.0054, +0.2545]: **undecided** | skill -6.6%; d +0.0039 [-0.0019, +0.0109]: **undecided** | +85% |
| rest of 2020 | 830 | 166 | skill -2.0%; d +0.0169 [-0.0056, +0.0397]: **undecided** | skill -5.8%; d +0.0143 [-0.0022, +0.0297]: **undecided** | skill -3.6%; d +0.0001 [-0.0002, +0.0005]: **undecided** | +15% |

**By month of the target day**

| month | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| April | 105 | 21 | skill -3.7%; d +0.0568 [-0.0194, +0.1357]: **undecided** | skill +7.9%; d -0.0140 [-0.0298, +0.0002]: **undecided** | skill +15.4%; d -0.0018 [-0.0035, -0.0000]: **gain** | +6% |
| August | 105 | 21 | skill -0.1%; d +0.0005 [-0.0406, +0.0417]: **undecided** | skill +3.8%; d -0.0051 [-0.0197, +0.0097]: **undecided** | skill +13.5%; d -0.0000 [-0.0000, -0.0000]: **gain** | +0% |
| December | 110 | 22 | skill -5.7%; d +0.0459 [+0.0038, +0.0908]: **loss** | skill -11.8%; d +0.0208 [-0.0106, +0.0553]: **undecided** | skill -10.3%; d +0.0004 [-0.0003, +0.0012]: **undecided** | +5% |
| February | 95 | 19 | skill +7.2%; d -0.0473 no interval: **not read** | skill -19.0%; d +0.0270 no interval: **not read** | skill +4.9%; d -0.0001 no interval: **not read** | -5% |
| January | 105 | 21 | skill +0.6%; d -0.0058 [-0.0578, +0.0502]: **undecided** | skill -2.2%; d +0.0076 [-0.0297, +0.0503]: **undecided** | skill -0.7%; d +0.0000 [-0.0010, +0.0012]: **undecided** | -1% |
| July | 110 | 22 | skill +1.0%; d -0.0093 [-0.0643, +0.0418]: **undecided** | skill +6.2%; d -0.0371 [-0.0773, -0.0003]: **gain** | skill +18.1%; d -0.0010 [-0.0017, -0.0003]: **gain** | -1% |
| June | 110 | 22 | skill -10.8%; d +0.1004 [+0.0285, +0.1749]: **loss** | skill -53.4%; d +0.0540 [+0.0124, +0.0963]: **loss** | skill -53.8%; d +0.0014 [+0.0000, +0.0027]: **loss** | +12% |
| March | 110 | 22 | skill -7.8%; d +0.5152 [-0.0994, +1.1643]: **undecided** | skill -9.0%; d +0.3866 [-0.1386, +0.9401]: **undecided** | skill -7.2%; d +0.0153 [-0.0112, +0.0440]: **undecided** | +59% |
| May | 100 | 20 | skill -5.8%; d +0.0803 [+0.0577, +0.1018]: **loss** | skill -3.4%; d +0.0005 [-0.0010, +0.0021]: **undecided** | skill +1.7%; d -0.0000 [-0.0000, +0.0000]: **undecided** | +8% |
| November | 95 | 19 | skill -7.4%; d +0.0854 no interval: **not read** | skill -22.4%; d +0.0761 no interval: **not read** | skill -24.8%; d +0.0019 no interval: **not read** | +8% |
| October | 105 | 21 | skill -1.8%; d +0.0132 [-0.0108, +0.0410]: **undecided** | skill -10.4%; d +0.0182 [-0.0084, +0.0470]: **undecided** | skill -1.7%; d +0.0001 [-0.0005, +0.0007]: **undecided** | +1% |
| September | 105 | 21 | skill -6.7%; d +0.0529 [+0.0234, +0.0834]: **loss** | skill -40.0%; d +0.0159 [+0.0030, +0.0291]: **loss** | skill +2.3%; d -0.0000 [-0.0000, +0.0000]: **undecided** | +6% |

**By settlement-day type, by leg, and by the scarcity state of the decision day**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any settlement | 680 | 136 | skill -9.1%; d +0.1549 [+0.0330, +0.3338]: **loss** | skill -15.6%; d +0.1198 [+0.0344, +0.2424]: **loss** | skill -13.9%; d +0.0042 [-0.0000, +0.0105]: **undecided** | +110% |
| neither settles | 575 | 115 | skill +1.4%; d -0.0167 [-0.0639, +0.0227]: **undecided** | skill +12.4%; d -0.0393 [-0.0626, -0.0199]: **gain** | skill +13.9%; d -0.0019 [-0.0040, -0.0003]: **gain** | -10% |
| bill settlement day | 560 | 112 | skill -4.9%; d +0.0855 [-0.0172, +0.2442]: **undecided** | skill -10.6%; d +0.0793 [+0.0078, +0.1970]: **loss** | skill -7.8%; d +0.0022 [-0.0000, +0.0057]: **undecided** | +50% |
| bill settlement day with a cash management bill | 450 | 90 | skill -8.4%; d +0.1121 [-0.0170, +0.2871]: **undecided** | skill -30.4%; d +0.0951 [+0.0049, +0.2331]: **loss** | skill -17.9%; d +0.0025 [+0.0000, +0.0064]: **loss** | +53% |
| bill settlement day without one | 110 | 22 | skill +0.7%; d -0.0231 [-0.1005, +0.0558]: **undecided** | skill -0.6%; d +0.0148 [-0.0208, +0.0520]: **undecided** | skill -1.0%; d +0.0009 [-0.0015, +0.0033]: **undecided** | -3% |
| coupon settlement day | 170 | 34 | skill -32.4%; d +0.6066 [+0.2582, +0.9888]: **loss** | skill -55.0%; d +0.5154 [+0.2298, +0.8250]: **loss** | skill -35.9%; d +0.0180 [+0.0042, +0.0343]: **loss** | +108% |
| bill only | 510 | 102 | skill -0.3%; d +0.0043 [-0.0337, +0.0514]: **undecided** | skill +1.7%; d -0.0120 [-0.0238, +0.0011]: **undecided** | skill +1.8%; d -0.0004 [-0.0010, +0.0002]: **undecided** | +2% |
| both legs | 50 | 10 | skill -34.3%; d +0.9143 no interval: **not read** | skill -89.8%; d +1.0108 no interval: **not read** | skill -37.4%; d +0.0292 no interval: **not read** | +48% |
| coupon only | 120 | 24 | skill -31.0%; d +0.4784 [+0.2455, +0.7284]: **loss** | skill -36.0%; d +0.3090 [+0.1482, +0.4783]: **loss** | skill -34.7%; d +0.0133 [+0.0021, +0.0263]: **loss** | +60% |
| neither | 575 | 115 | skill +1.4%; d -0.0167 [-0.0639, +0.0227]: **undecided** | skill +12.4%; d -0.0393 [-0.0626, -0.0199]: **gain** | skill +13.9%; d -0.0019 [-0.0040, -0.0003]: **gain** | -10% |
| state 0 (abundant) | 10 | 2 | skill -27.0%; d +0.3260 no interval: **not read** | skill -6.3%; d +0.0034 no interval: **not read** | skill -10.6%; d +0.0002 no interval: **not read** | +3% |
| state 1 to 2 | 935 | 189 | skill -6.1%; d +0.0617 [+0.0284, +0.1022]: **loss** | skill -13.4%; d +0.0275 [+0.0071, +0.0510]: **loss** | skill -19.9%; d +0.0009 [+0.0001, +0.0020]: **loss** | +58% |
| state 3 (scarce) | 310 | 64 | skill -4.0%; d +0.1111 [-0.0238, +0.2798]: **undecided** | skill -6.3%; d +0.1015 [-0.0007, +0.2255]: **undecided** | skill -3.5%; d +0.0026 [-0.0021, +0.0085]: **undecided** | +39% |

**The immediate-release cash management bill days** (an auction with no stated release time settles on the target day, #1301)

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| in them | 345 | 69 | skill -8.4%; d +0.1215 [-0.0268, +0.3022]: **undecided** | skill -34.7%; d +0.1120 [-0.0004, +0.2461]: **undecided** | skill -18.6%; d +0.0031 [-0.0001, +0.0069]: **undecided** | +44% |
| 2020 with them left out | 910 | 182 | skill -4.0%; d +0.0591 [+0.0193, +0.1024]: **loss** | skill -3.4%; d +0.0223 [-0.0057, +0.0493]: **undecided** | skill -3.1%; d +0.0008 [-0.0012, +0.0029]: **undecided** | n/a |

Target days: 69.

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| any immediate-release day | 345 | 69 | skill -8.4%; d +0.1215 [-0.0268, +0.3022]: **undecided** | skill -34.7%; d +0.1120 [-0.0004, +0.2461]: **undecided** | skill -18.6%; d +0.0031 [-0.0001, +0.0069]: **undecided** | +44% |
| 2020 with them all left out | 910 | 182 | skill -4.0%; d +0.0591 [+0.0193, +0.1024]: **loss** | skill -3.4%; d +0.0223 [-0.0057, +0.0493]: **undecided** | skill -3.1%; d +0.0008 [-0.0012, +0.0029]: **undecided** | n/a |

Target days: 69.

## Table 3. The fitted settlement shift against the realised settlement-day premium (bp)

Called from #1321 as merged (decision-day bootstrap, seed 1321); the flag and net parts are added here and carry no interval.

**Leads 2 to 5**

| regime | decision days | realised premium (bp) | (s3c-ann) shift | (s3c-ann-net) shift | (s3c-ann-flagnet) shift | of it, flags | of it, nets | flagnet bias |
|---|---|---|---|---|---|---|---|---|
| all | 1,855 | +1.45 [+0.81, +2.24] | +1.06 [+0.85, +1.31] | +0.64 [+0.49, +0.80] | +1.09 [+0.87, +1.34] | +0.92 | +0.17 | +0.58 [+0.10, +1.21] |
| 2018-19 | 360 | +5.99 [+3.35, +9.38] | +2.72 [+2.05, +3.55] | +1.29 [+0.83, +1.86] | +2.76 [+2.08, +3.63] | +2.56 | +0.20 | +2.72 [+0.31, +5.73] |
| 2020 | 254 | +0.28 [-0.37, +1.16] | +1.31 [+0.86, +1.85] | +0.89 [+0.54, +1.31] | +1.38 [+0.89, +1.98] | +1.17 | +0.21 | -0.74 [-1.52, +0.13] |
| 2021-23 | 751 | +0.12 [-0.05, +0.28] | +0.14 [+0.09, +0.21] | +0.05 [+0.02, +0.09] | +0.12 [+0.08, +0.17] | +0.14 | -0.02 | +0.02 [-0.11, +0.14] |
| 2024 | 253 | +1.37 [+0.66, +2.27] | +0.74 [+0.54, +0.95] | +0.63 [+0.43, +0.85] | +0.81 [+0.59, +1.06] | +0.57 | +0.24 | +0.75 [+0.18, +1.45] |
| 2025-26 | 249 | +2.40 [+1.57, +3.19] | +1.75 [+1.35, +2.21] | +1.29 [+0.89, +1.70] | +1.81 [+1.38, +2.28] | +1.16 | +0.65 | +0.75 [+0.14, +1.36] |

**Lead 1**

| regime | decision days | realised premium (bp) | (s3c-ann) shift | (s3c-ann-net) shift | (s3c-ann-flagnet) shift | of it, flags | of it, nets | flagnet bias |
|---|---|---|---|---|---|---|---|---|
| all | 1,855 | +1.44 [+0.76, +2.28] | +0.97 [+0.77, +1.21] | +0.54 [+0.41, +0.70] | +1.00 [+0.79, +1.25] | +0.82 | +0.18 | +0.47 [+0.03, +1.04] |
| 2018-19 | 361 | +6.11 [+3.19, +9.80] | +2.59 [+1.97, +3.34] | +1.09 [+0.65, +1.68] | +2.63 [+1.99, +3.41] | +2.42 | +0.21 | +2.36 [+0.14, +5.09] |
| 2020 | 251 | +0.28 [-0.45, +1.24] | +1.27 [+0.86, +1.76] | +0.91 [+0.53, +1.36] | +1.41 [+0.90, +2.04] | +1.13 | +0.28 | -0.71 [-1.42, +0.14] |
| 2021-23 | 748 | +0.12 [-0.07, +0.30] | +0.14 [+0.08, +0.20] | +0.05 [+0.02, +0.08] | +0.11 [+0.07, +0.17] | +0.13 | -0.02 | -0.04 [-0.16, +0.08] |
| 2024 | 250 | +1.37 [+0.64, +2.28] | +0.50 [+0.32, +0.70] | +0.44 [+0.25, +0.65] | +0.56 [+0.35, +0.82] | +0.33 | +0.23 | +0.70 [+0.09, +1.47] |
| 2025-26 | 245 | +2.32 [+1.39, +3.30] | +1.52 [+1.20, +1.90] | +1.03 [+0.70, +1.36] | +1.56 [+1.20, +1.97] | +0.94 | +0.62 | +0.56 [-0.13, +1.26] |

## The 2026 development days (decide nothing; cells #1321 already scored, split further)

**Pooled, and by whether a leg settles**

| group | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| pooled | 825 | 165 | skill +0.4%; d -0.0065 [-0.0195, +0.0065]: **undecided** | skill +0.3%; d -0.0016 [-0.0129, +0.0085]: **undecided** | skill -2.5%; d +0.0009 [-0.0002, +0.0020]: **undecided** | n/a |
| any settlement | 442 | 91 | skill -1.3%; d +0.0210 [-0.0121, +0.0577]: **undecided** | skill -5.2%; d +0.0299 [+0.0051, +0.0538]: **loss** | skill -7.0%; d +0.0032 [+0.0007, +0.0058]: **loss** | -182% |
| neither settles | 383 | 78 | skill +2.4%; d -0.0403 [-0.0637, -0.0179]: **gain** | skill +7.9%; d -0.0400 [-0.0533, -0.0276]: **gain** | skill +6.8%; d -0.0021 [-0.0032, -0.0011]: **gain** | +282% |

**By settlement-day type**

| type | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| bill settlement day | 348 | 72 | skill -1.4%; d +0.0240 [-0.0062, +0.0558]: **undecided** | skill -5.9%; d +0.0316 [+0.0048, +0.0586]: **loss** | skill -9.9%; d +0.0037 [+0.0006, +0.0068]: **loss** | -165% |
| bill settlement day with a cash management bill | 5 | 1 | skill +4.0%; d -0.0579 no interval: **not read** | skill +12.5%; d -0.0003 no interval: **not read** | skill n/a; d +0.0000 no interval: **not read** | +5% |
| bill settlement day without one | 343 | 71 | skill -1.5%; d +0.0251 [-0.0050, +0.0586]: **undecided** | skill -5.9%; d +0.0320 [+0.0054, +0.0601]: **loss** | skill -9.9%; d +0.0038 [+0.0007, +0.0070]: **loss** | -170% |
| coupon settlement day | 119 | 24 | skill -3.7%; d +0.0586 [-0.0153, +0.1305]: **undecided** | skill -8.7%; d +0.0748 [+0.0138, +0.1349]: **loss** | skill -8.6%; d +0.0096 [+0.0034, +0.0157]: **loss** | -131% |
| neither settles | 383 | 78 | skill +2.4%; d -0.0403 [-0.0637, -0.0179]: **gain** | skill +7.9%; d -0.0400 [-0.0533, -0.0276]: **gain** | skill +6.8%; d -0.0021 [-0.0032, -0.0011]: **gain** | +282% |

**By lead**

| lead | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| h=1 | 165 | 165 | skill +0.6%; d -0.0088 [-0.0291, +0.0112]: **undecided** | skill +1.8%; d -0.0084 [-0.0259, +0.0073]: **undecided** | skill +0.6%; d -0.0002 [-0.0020, +0.0014]: **undecided** | +27% |
| h=2 | 165 | 165 | skill +0.3%; d -0.0045 [-0.0215, +0.0131]: **undecided** | skill -0.1%; d +0.0004 [-0.0131, +0.0133]: **undecided** | skill -3.4%; d +0.0012 [-0.0001, +0.0027]: **undecided** | +14% |
| h=3 | 165 | 165 | skill +0.7%; d -0.0117 [-0.0275, +0.0043]: **undecided** | skill +0.3%; d -0.0016 [-0.0133, +0.0091]: **undecided** | skill -3.6%; d +0.0013 [-0.0001, +0.0028]: **undecided** | +36% |
| h=4 | 165 | 165 | skill +0.4%; d -0.0067 [-0.0204, +0.0080]: **undecided** | skill +0.1%; d -0.0007 [-0.0117, +0.0106]: **undecided** | skill -2.7%; d +0.0009 [-0.0003, +0.0022]: **undecided** | +21% |
| h=5 | 165 | 165 | skill +0.0%; d -0.0007 [-0.0163, +0.0153]: **undecided** | skill -0.5%; d +0.0025 [-0.0094, +0.0136]: **undecided** | skill -3.1%; d +0.0011 [+0.0000, +0.0022]: **loss** | +2% |

**By realised event**

| set | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |
|---|---|---|---|---|---|---|
| event: spread above +5 bp | 21 | 5 | skill +6.0%; d -0.1991 no interval: **not read** | skill +5.7%; d -0.1796 no interval: **not read** | skill +4.8%; d -0.0321 no interval: **not read** | +78% |
| no event | 804 | 164 | skill +0.1%; d -0.0014 [-0.0154, +0.0130]: **undecided** | skill -0.7%; d +0.0030 [-0.0077, +0.0126]: **undecided** | skill -8.5%; d +0.0017 [+0.0008, +0.0028]: **loss** | +22% |

| set | cells | mean P(> +5 bp), arm | reference | Brier difference summed (arm less reference) |
|---|---|---|---|---|
| spread above +5 bp | 21 | 0.192 | 0.169 | -0.68 |
| no event | 804 | 0.090 | 0.087 | +1.39 |

Observed frequency of the event over these cells: 2.5%.

## Power of the prospective comparison (development series; descriptive)

d = score of (s3c-ann-net) less score of (s3c-ann-flagnet) per decision day, positive favouring the arm, from 2020-04-03; 40,000 windows of the look's length (circular blocks of 10, seed 1344), the protocol's Newey-West lag 10. Critical values are calibrated on this series at the nominal level of the look (`scoring_protocol.nominal_levels`, alpha 0.05 spent over 60, 125 and 250 days; look 60 checks futility only) and, for a family of m, at alpha/m. Each look is read on its own. The Monte Carlo error of a power is at most 0.2 points (the tail of the strictest level rests on a few dozen windows, so those are rougher).

**grid CRPS.** 1,429 decision days from 2020-04-03 to 2025-12-23; mean d -0.0008 (skill -0.08% of the candidate's mean score 1.021); long-run standard deviation of a daily difference 0.080.

| look (days) | family size | nominal level | critical value | power at observed | power at skill 0.5% | power at skill 1.0% | power at skill 3.0% | power at zero |
|---|---|---|---|---|---|---|---|---|
| 125 | 1 | 0.0056 | 3.19 | 0.3% | 7.1% | 23.2% | 86.4% | 0.6% |
| 125 | 2 | 0.0015 | 3.74 | 0.1% | 3.5% | 15.1% | 80.2% | 0.1% |
| 125 | 3 | 0.0007 | 4.05 | 0.0% | 2.3% | 11.7% | 76.2% | 0.1% |
| 250 | 1 | 0.0482 | 2.03 | 3.1% | 28.5% | 62.7% | 99.9% | 4.8% |
| 250 | 2 | 0.0245 | 2.38 | 1.4% | 20.3% | 53.4% | 99.7% | 2.4% |
| 250 | 3 | 0.0164 | 2.56 | 0.9% | 16.9% | 48.7% | 99.6% | 1.6% |

Days a one-sided test at the final look's level needs for 80% power (analytic, long-run variance), by effect:

| family size | observed | skill 0.5% | skill 1.0% | skill 3.0% |
|---|---|---|---|---|
| 1 | never (effect not positive) | 1,536 | 384 | 43 |
| 2 | never (effect not positive) | 1,935 | 484 | 54 |
| 3 | never (effect not positive) | 2,170 | 542 | 60 |

**upper-tail twCRPS.** 1,429 decision days from 2020-04-03 to 2025-12-23; mean d +0.0022 (skill +1.06% of the candidate's mean score 0.212); long-run standard deviation of a daily difference 0.038.

| look (days) | family size | nominal level | critical value | power at observed | power at skill 0.5% | power at skill 1.0% | power at skill 3.0% | power at zero |
|---|---|---|---|---|---|---|---|---|
| 125 | 1 | 0.0056 | 2.01 | 4.8% | 1.5% | 4.1% | 69.9% | 0.6% |
| 125 | 2 | 0.0015 | 2.32 | 1.6% | 0.4% | 1.3% | 59.9% | 0.1% |
| 125 | 3 | 0.0007 | 2.50 | 0.8% | 0.2% | 0.7% | 53.9% | 0.1% |
| 250 | 1 | 0.0482 | 1.43 | 32.4% | 12.6% | 29.5% | 95.2% | 4.8% |
| 250 | 2 | 0.0245 | 1.66 | 22.3% | 7.4% | 20.1% | 92.6% | 2.4% |
| 250 | 3 | 0.0164 | 1.78 | 17.7% | 5.4% | 15.6% | 90.6% | 1.6% |

Days a one-sided test at the final look's level needs for 80% power (analytic, long-run variance), by effect:

| family size | observed | skill 0.5% | skill 1.0% | skill 3.0% |
|---|---|---|---|---|
| 1 | 1,810 | 8,084 | 2,021 | 225 |
| 2 | 2,280 | 10,185 | 2,546 | 283 |
| 3 | 2,556 | 11,417 | 2,854 | 317 |

## The draft prospective declaration (drafted, not registered)

`metadata/s3c_flagnet_prospective_draft_1344.json`: DRAFT, not registered. Drafted by the pull request that closes #1344 for Eleonora to review. Registering it is her GitHub action (`GO #1344`, an entry in metadata/owner_attestations.json citing her own comment, and the file moved or copied to metadata/registrations/ by the registering change); a relayed ruling does not register it. Nothing here is scored, logged or published, and nothing is in force.

- **What it adds:** (s3c-ann) with #1273's announced net beside each announced 0/1 flag: per leg two settlement terms (the flag and the net in units of USD 100 bn), read from the auction announcements public at the decision instant (12:00 America/New_York on announcemt_date, the dating of metadata/settlement_announcement_dating.json), at every lead h = 1..5; everything else is (s3)'s, capped at the Standing Repo Facility line from full allotment as (s3c) is (repo_model.s3c_candidate, margin 0 bp); direct pairs, refit every 21 decision days, Huber fit and ridge as (s3c). Defined in metadata/s3c_flagnet_gross_1321.json and repo_model.s3c_announced.FLAGNET_ARM; frozen at registration by the hash of the code, configuration, inputs and training rule (scoring-protocol.md section 2).
- **The candidate:** The candidate (s3c-ann-net) does not change: docs/research/h5-candidate.json and its declaration are untouched. Whether and how it is registered is a separate act of hers; this draft only adds the arm beside whatever she registers.
- **Days:** Prospective confirmation days only (scoring-protocol.md section 1): the business days after the registration, the forecasts produced by the live pipeline at the decision instant and committed with hash and timestamp before the outcome is published. No 2018 to 2025 day and none of the 2026 days (all seen) is scored; the blind tier from 2026-09-04 stays locked until she opens it at a checkpoint, an attested action each time (scoring-protocol.md, item 3 of the amendments). Checkpoints at 60, 125 and 250 confirmation days, alpha spent by Lan-DeMets O'Brien-Fleming (nominal one-sided levels from scoring_protocol.nominal_levels).
- **Scoring:** Under scoring protocol v1: primary score grid CRPS (23 levels) averaged over h = 1..5, one number per decision day; key secondary upper-tail twCRPS (weight 1{z > 0 bp}); reported, not decision rules: Brier P(> +5 bp) and P(> +10 bp), coverage, PIT. d = S(benchmark) - S(arm), skill = mean(d)/mean(S(benchmark)), studentized stationary bootstrap, mean block 10, 10,000 draws (100,000 at interim checkpoints), one-sided 95% at the checkpoint's nominal level. The arm is tested against B1 and B2 exactly as a secondary candidate is (supported needs a win over both and the point skill at least the MME of 3% against B1). The comparison with the candidate (S(candidate) - S(arm), same machinery) is a reported comparison, no rule, printed beside the verdict as the protocol prints B3 (ruling of 19 October 2026, #768): it has no efficacy or futility rule and changes nothing registered.
- **Multiplicity:** Section 8: no correction for the primary candidate; Holm across the secondaries and the key secondary metric. With the arm registered as the one secondary, the Holm family of the hypothesis is the candidate's key secondary, the arm's primary score and the arm's key secondary: three tests (the arm against B1 and against B2 is one test per metric, as for the candidate: both legs must clear). The result page states the cost of the family: the critical value of each look at alpha/1, alpha/2 and alpha/3. The development variant count to date is published with the registration (#1321 tested two arms; #1319 none; #1288 two; #1273 one). The comparison with the candidate is outside the family (a reported comparison). Whether the family is these three is a reading of section 8 and is marked as a question on the page.
- **Power:** Stated on the result page (docs/research/s3c-flagnet-diagnosis-1344-result.md, section 'Power of the prospective comparison') from docs/research/s3c-flagnet-diagnosis-1344/result.json: the power of the arm against the candidate at 125 and 250 confirmation days, at the observed development effect and at skills of 0.5%, 1% and 3%, at family sizes 1, 2 and 3, and the days needed for 80%. It is a development estimate; no minimum power is set here. The protocol's own MME (3% against B1) and the power study for the candidate against B1 and B2 (#656, #886) are the candidate's and are not restated for the arm.
- **Registration:** Not registered. The registering change adds the declaration under metadata/registrations/, appends the owner attestation, and is hers; this draft changes no decision record, lockbox, live pin or published record.

## Questions for Eleonora (marked; defaults change no claim)

**Question 1. Register (s3c-ann-flagnet) beside the candidate for the prospective confirmation days?** The draft declaration (`metadata/s3c_flagnet_prospective_draft_1344.json`) is drafted, not registered. Registering it is her GitHub action, `GO #1344`; the candidate (s3c-ann-net) does not change.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **Do not register; keep the draft on file (default).** Nothing is scored on the confirmation days for the arm.
2. **Register the arm as a secondary candidate as drafted**, compared with the candidate head to head as a reported comparison with no rule, and tested against B1 and B2 under the protocol's rule with Holm across the secondaries and the key secondary metric.
3. **Register it, but read the comparison with the candidate on the Brier score of P(> +5 bp) as well**, as a further reported comparison (no decision rule), because that is where the development gain sits.

**Question 2 of #1326 (the announcement dating in published declarations)** keeps its default: off. Nothing here asks for it.

## What this does and does not show

It shows where, in the development data, the flagnet's differences from the candidate sit, and what a prospective comparison of the two could resolve. It does not show that either arm is better: the days were seen, the 2026 days were seen by #845, #151, #1229, #1255, #1273, #1288 and #1321, intervals of a group of target days keep the method that #1221 questions, and the bill leg and the net bill carry Lens E's caveat on the 12:00 announcement time of a cash management bill (item G). The mechanisms named are readings of the tables; no arm was run to test them. Nothing is a verdict.
