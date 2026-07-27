# Causal & Counterfactual Reasoning (Pearl's Three Rungs)

## Rung 1 — Observation
What correlates with a "good outcome" (a company scored as high-priority)?

In the raw data, **approval rate does not correlate with company size/filing
volume at all**: Pearson r(n_decisions, approval_rate) = **0.0033**. Small
filers (n = 2-4 decisions) average a 98.09% approval rate; large filers
(n = 50+) average 98.37% — essentially the same. This is consistent with
the well-known fact that H-1B approval rates are high industry-wide, so
there wasn't much room for company size to move the needle here.

This *contradicts* my pre-registered prediction that the raw approval-rate
signal itself would be confounded by company size. It wasn't.

## Rung 2 — Intervention
Here's where the tool's own math introduces a confound the data doesn't have.
The tool doesn't score on raw approval rate — it scores on
`priority_score = rate * (1 - 0.5 * uncertainty_width)`, where
`uncertainty_width` is a Wilson-interval width that shrinks mechanically as
`n_decisions` grows, independent of the true underlying rate.

Measured directly:
- Pearson r(n_decisions, uncertainty_width) = **-0.185**
- Pearson r(n_decisions, priority_score) = **+0.154**

So: **if you intervened on a company's `n_decisions`** — say, it simply had
50 more H-1B filings show up in next year's data, at the *same* true
approval rate — its `priority_score` would rise, and it would receive more
of the candidate's scarce hours, **with no change in its actual
sponsorship-friendliness**. The confounder here isn't a hidden third
variable in the usual sense; it's the tool's own uncertainty-discount
formula, which conflates "how much paperwork exists" with "how attractive
this company is as a sponsor."

## Rung 3 — Counterfactual
A real, exact case from the data: at **100% observed approval rate**,
compare:

| Company | n_decisions | Approval rate | Uncertainty width | Effect on score |
|---|---|---|---|---|
| 1LIFE HEALTHCARE INC | 2 | 100% | 0.658 (wide) | heavily discounted |
| 317 LABS INC | 2 | 100% | 0.658 (wide) | heavily discounted |
| CONFLUENT INC | 610 | 100% | 0.006 (narrow) | almost no discount |

**Counterfactual claim:** had 1LIFE HEALTHCARE's true sponsorship behavior
been identical to Confluent's (both 100% approval), but its *filing volume*
had also happened to be 610 instead of 2, it would have received nearly the
full, undiscounted priority score instead of being penalized to roughly a
third of it — a purely mechanical consequence of sample size, not of any
real difference in how likely either company is to sponsor a candidate.

**Assumption this rests on:** that a company's true approval rate is stable
regardless of how many decisions have been logged — i.e., that 1LIFE
HEALTHCARE isn't actually different from Confluent in some real way that
also happens to correlate with filing volume (e.g., maturity, HR
sophistication). I can't rule that out with this data; I can only show the
tool's formula would treat them identically-scored if that assumption
holds.

## Honest verdict
**Yes — this engine reallocates on correlation dressed as causation, and it
does so in two separate ways, not one:**

1. Even the "clean" raw signal (approval rate) is a proxy: it measures
   whether a company **has** sponsored someone before, not whether spending
   *this candidate's* additional hours applying there **causes** a higher
   probability of a sponsored offer. The causal quantity the tool actually
   needs — "does an extra hour of my effort at company X increase my odds
   of an offer there" — is never measured by this dataset at all. Historical
   institutional approval behavior and one candidate's marginal-hour payoff
   are different causal objects entirely.
2. On top of that unavoidable proxy problem, the tool's own scoring formula
   introduces a second, avoidable one: it lets statistical sample size
   masquerade as a signal about company quality, systematically favoring
   large, well-documented companies over small ones with identical true
   behavior.

My pre-registered prediction was **directionally right but located in the
wrong place** — I expected the confound in the data; it actually turned out
to live in the tool's own uncertainty-weighting design. That's a more
useful finding than if I'd been right in the way I expected, and it's the
kind of thing the reflection should say plainly rather than paper over.
