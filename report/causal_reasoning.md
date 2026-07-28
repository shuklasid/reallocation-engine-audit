# Causal & Counterfactual Reasoning (Pearl's Three Rungs)

## Rung 1 — Observation
Unlike the earlier version of this project (job-search hour allocation by
H-1B approval rate, since abandoned for this domain), **raw pass rate here
DOES correlate with record volume**: Pearson r(n_records, pass_rate) =
**0.306** — moderate, not zero. Mature, high-volume station types
(BurnInSystem_GenA, the Legacy testers) cluster at 92-98% pass rates;
low-volume, newer categories (RF testers, the pilot line) cluster at
83-87%.

## Rung 2 — Intervention
Is this a real causal relationship or an artifact worth distrusting? In
semiconductor manufacturing, a genuine phenomenon called **yield ramp**
means new production lines really do start with lower yield and improve as
process kinks get worked out — so *some* of this correlation may reflect
real physics/process reality, not just an artifact of how much data exists.
That's different from the H-1B case, where there was no equivalent
real-world mechanism connecting company size to true approval rate.

But the scoring formula still adds its own confound on top: the
uncertainty-discount term shrinks with volume regardless of whether a
station's true rate is stable or improving. Measured directly by
comparing the lowest-scoring station (`NewPilotLine_ProtoStation`, n=346,
observed rate 83.24%) against a counterfactual with the same rate but
progressively more accumulated volume:

| Hypothetical n | Uncertainty width | Score |
|---|---|---|
| 346 (actual) | 0.0786 | 0.7997 |
| 1,000 | 0.0463 | 0.8131 |
| 3,000 | 0.0267 | 0.8213 |
| 7,718 (matches the most mature station's volume) | 0.0167 | **0.8255** |

## Rung 3 — Counterfactual, and where my prediction was wrong
**Counterfactual claim:** even if `NewPilotLine_ProtoStation` had
accumulated as much test volume as the most mature station on the floor,
with its *same* observed 83.24% rate, its score would only rise to
**0.8255** — which is still below `RFTester_GenA`'s current score of
**0.8457**. **No realistic amount of additional volume would move it out
of last place**, given its current observed rate.

**This means my pre-registered prediction was mostly wrong.** I predicted
the pilot station would be "unfairly buried" by low sample size, expecting
a story similar to the earlier project's Turo/Icon finding, where sample
size alone flipped a ranking. Here, sample size only accounts for a small
slice of the gap (0.7997 → ~0.83 ceiling) — most of the low ranking is a
genuine, real difference in observed pass rate, not a scoring artifact.

**Assumption this rests on:** that the pilot station's currently observed
83.24% rate is a stable estimate of its true rate going forward. If yield
ramp is real and ongoing, its *true* rate may currently be increasing even
as the historical average sits at 83.24% — and this tool has no mechanism
to detect a trend, only a static historical average. That's a real,
separate causal problem this tool doesn't address at all: it cannot tell
the difference between "a station that's reliably mediocre" and "a station
that's improving but hasn't accumulated enough recent-only data to show it."

## Honest verdict
**Yes, this still reallocates on correlation dressed as causation — but
via a different mechanism than the earlier version of this project.** The
raw pass-rate signal here is a superficially more defensible proxy (yield
ramp is a real phenomenon, unlike company-size confounding in the H-1B
case), but the tool still can't distinguish a station that's *stably*
mediocre from one that's *improving*, and averaging all historical data
into one static rate silently assumes the underlying process hasn't
changed — the same static-history assumption that broke the H-1B version,
just manifesting differently here.

**On the prediction itself:** being wrong here was more informative than
being right would have been. I expected to find the same "the tool invents
a bias" story a second time, and reflexively assumed the *shape* of the
first project's finding would transfer to a new domain. It didn't — the
volume/quality relationship in this domain is at least partially grounded
in real physical behavior (yield ramp), which the H-1B data had no
equivalent of. That's a useful lesson about not assuming a validated
finding in one domain automatically generalizes to a structurally
different one, even when the tool's mathematical architecture is
identical.
