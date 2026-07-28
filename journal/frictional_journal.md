# Frictional Journal (v2 — pivoted domain: ATE test-station capacity reallocation)

**Note:** the original H-1B/job-search domain was abandoned mid-assignment
in favor of this domain, for reasons of personal domain fit (backend/
distributed-systems + semiconductor test background). This is a fresh
pre-registered prediction for the new domain, made before any script was
run against the synthetic dataset.

## Prediction (before building)
**Timestamp:** 2026-07-27 23:55 UTC

I expect the hardest failure in this engine to be the mirror image of what
I found in the H-1B version, but with the opposite-favored group: newer or
pilot test stations will get unfairly buried by the scoring formula even if
their true reliability is fine, simply because they haven't logged enough
completed tests yet for the uncertainty band to narrow. A brand-new station
type with a genuinely strong pass rate will look "unproven" next to an
old, high-volume station with a similar or even worse true rate, purely
because of how much history exists — not because of any real difference
in quality.

I expect the engine's causal validity to be moderate: historical pass-rate
probably carries some real signal about a station's reliability, but I
expect at least one confounder — most likely station age/volume, possibly
also which test program is running — to meaningfully break the "pass rate
predicts future reliability" claim once I actually check it against the
data.

**Confidence in these two guesses: ~50-60%.** I'm fairly confident the
volume/uncertainty mechanism will show up here again since it's a
structural property of the scoring formula itself, not something specific
to H-1B data — but I'm less sure whether station age or test-program type
ends up being the dominant confounder.

## Reflection (after building)
**Timestamp:** 2026-07-28 00:01 UTC

What surprised me most was that sample size mattered way less here than I
expected. I predicted the same story from the earlier project would
repeat — a new, low-volume station getting unfairly buried purely because
it hadn't accumulated enough history yet. Instead, even giving the pilot
line unlimited hypothetical volume at its same observed rate barely moved
its score, and it still couldn't have escaped last place. Most of its low
ranking was a genuine difference in observed reliability, not a
sample-size artifact at all.

Being wrong here taught me not to assume a finding generalizes across
domains just because the tool's underlying math is identical. The scoring
formula — pass rate discounted by a Wilson-interval uncertainty term — is
exactly the same code in both projects. But whether the "confound" that
shows up is mostly artificial (like the H-1B case) or partly reflects a
real underlying process (yield ramp, in this case) depends entirely on the
domain the formula is applied to, not on the formula itself. I carried
over a conclusion from one domain into my prediction for a structurally
different one, and that's exactly the kind of transfer that doesn't
actually hold up without checking.

If I kept working on this, the first thing I'd fix is the feedback loop
identified in the bias audit: stations that get zero hours this cycle can
never accumulate the data needed to prove they've improved, regardless of
whether they actually have. A small guaranteed exploration floor — routing
a modest, fixed share of hours to zero-allocation stations regardless of
score — would let the tool eventually detect a real yield-ramp
improvement instead of permanently locking a station out based on one
historical snapshot.

