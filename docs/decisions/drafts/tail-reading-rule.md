# Draft: a tail is "in line" only when its ratio and its miss share both hold (#1592)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1592, from her ruling of 12
November 2026 (decision docket, card "should a tail that misses about twice its nominal rate count as in line?",
option "both"). It takes effect only when she merges it. Until then `repo_model.tail_reading` carries the rule and
nothing reads it.

## Why

#1547 called a tail "in line" when the 90% interval of its ratio held 1. On the post-month-end days its q05 was called in
line while its strict miss share was 9.1% [5.6%, 12.8%] against 5%. #1555 took that reading and widened only q95 there; the
arm lost on the group. A ratio that holds 1 does not show that the tail covers.

## The rule, as drafted

A tail (q01, q05, q95, q99) is called, in this order:

1. **too thin** when the 90% interval of its ratio lies wholly above 1;
2. **too wide** when that interval lies wholly below 1;
3. **in line** only when the ratio interval holds 1 **and** the 90% interval of its strict miss share holds the nominal
   rate (5% for q05 and q95, 1% for q01 and q99);
4. otherwise **miss share off**.

A tail whose miss share was not computed is never called in line; it is called "ratio holds 1, miss share not read". The
intervals are the study's own (same resamples as the ratio). The rule is in `repo_model.tail_reading.tail_call`.

## What it does not do

It does not re-run or edit #1547 or #1555 (their records stay as published; each page carries a dated note), and it does not
choose an arm. The next step on post-month-end days is a location or timing diagnostic, not a third width arm; it is
written after this pull request is reviewed.
