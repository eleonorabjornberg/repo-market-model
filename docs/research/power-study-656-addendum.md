# Power study (#656): a post-hoc check of the test's size

**This is post-hoc.** It was added after `docs/research/power-study-656.md` was run and its power figures were seen, and
it is labelled so wherever it is quoted. It changes none of that document's rule or results. It is a diagnostic of the
test the study rests on, not a part of the study's answer.

## Why

The power figures are the share of simulated paths in which the protocol's test says *Supported*. That figure is power
only if the test holds its size: under no true difference it must say *Supported* rarely. The protocol sets the overall
one-sided level at 5%, spent across the three checkpoints. The synthetic suite (H1) shows the test ranks forecasts of
known quality; it does not measure the test's size on daily score differences that are skewed and heavy-tailed, as a
spread's are.

## The check

The candidate of the rule (§3) with `DELTA` = 0, `NOISE` = 1: its daily difference against B1 is the centred
difference of B1 and B2, so the true mean difference is exactly zero. Paths as in the rule (§4), `REPLICATIONS` paths,
the protocol's 10,000 draws, mean block 10, the lower bound at each checkpoint's nominal level. A path is a **false
detection** if the lower bound of mean(d) against B1 is above zero at look 2 or look 3 (look 1 is unresolvable). The
point-skill condition (`MME`) is not applied, so this is the test's own size, before the MME gate. The same paths are
also reported with the MME gate applied.

`scripts/power_study.py null` writes `docs/research/power-study-656/null.json`.
