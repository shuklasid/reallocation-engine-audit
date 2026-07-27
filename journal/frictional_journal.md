# Frictional Journal

## Prediction (before building)
**Timestamp:** 2026-07-27 21:16 UTC

I expect the hardest failure in this engine to be confounding by company size:
big companies file more LCAs, so they accumulate more approvals and a
tighter, more trustworthy-looking confidence interval — but that says
something about their filing *volume*, not necessarily about how easy they
actually are to get sponsored by as a candidate. I'm worried the tool will
end up ranking "companies that do a lot of H-1B paperwork" above "companies
that are actually a good sponsorship bet for someone like me."

I expect the engine's causal validity to be moderate: there's probably some
real signal in historical approval behavior, but I think at least one
confounder (most likely company size, possibly also industry-level
base rates) will meaningfully break the "approval rate causes/predicts
sponsorship likelihood" claim once I actually check for it.

**Confidence in these two guesses: ~50-60%.** I'm not certain size is *the*
confound — it could turn out to be something else entirely (e.g., industry,
or filing recency) — but I'm fairly confident *some* confound will show up,
because the dataset only tracks outcomes, not the reasons behind them.

## Reflection (after building)
**Timestamp:** 2026-07-27 22:57 UTC

What surprised me most wasn't that a size bias existed — I predicted that
much correctly. It was *where* it turned out to live. I expected the bias
to be baked into the historical H-1B data itself: that big companies would
simply look "safer" because they file more paperwork. When the actual
correlation between company size and raw approval rate came back at 0.003,
essentially zero, I had to sit with the fact that my prediction was
right about the *symptom* but wrong about the *cause*. The bias was real,
but I had built it myself — my own uncertainty-discount formula was the
thing manufacturing a size penalty that the underlying data never had.

That's the part worth being honest about for calibration purposes: I had
implicitly assumed "the data" and "the tool's treatment of the data" were
the same thing, and they weren't. Getting the direction right made it easy
to feel like I'd basically nailed the prediction, but the more useful
lesson is that I should have tested the raw signal and my own scoring
formula as two separate things from the start, instead of treating a
confirmed hunch as confirmation of the whole mechanism behind it. Being
right about *that* a bias exists told me nothing about *where* to actually
go fix it — I only found that by decomposing the formula and checking each
piece against the data independently.

If I kept working on this, the first concrete thing I'd do is reduce the
uncertainty-penalty coefficient (currently 0.5 in the priority score
formula) and re-run the bias audit numbers to see how much of the
14x selection-rate gap between early- and late-stage companies actually
closes. That's the most direct, testable fix given what the causal and
bias sections both point at as the same root cause.

