# Explainability & Its Critique

## Method
Same as the earlier version of this project: the scoring function
(`priority_score = pass_rate * (1 - 0.5*uncertainty_width)`) is fully
transparent and closed-form, so I use an exact decomposition rather than
an approximate method like SHAP/LIME — the same reasoning applies:
approximating a known formula would add noise to something already exact.

**Exact decomposition for `NewPilotLine_ProtoStation` (lowest-scoring,
completely excluded from allocation):**

| Component | Value |
|---|---|
| Units passed / failed | 288 / 58 (346 total) |
| Pass rate | 83.24% |
| Uncertainty width | 0.0786 (widest of any station type) |
| Discount | 1 − 0.5×0.0786 ≈ 0.9607 |
| **Priority score** | **0.7997 (lowest of 15, rank 15)** |
| **Allocated hours** | **0 — excluded from the top-10 cutoff entirely** |

**The explanation, stated plainly:** "The new pilot line receives zero
test-station-hours because it has both the lowest observed pass rate and
the least accumulated test history of any station category, making it the
statistically weakest candidate for additional capacity." **This is
completely accurate** — every number is exactly derivable from the data.

## The critique — where this explanation is accurate but misleading
The explanation says nothing about **what kind of jobs this station type
is actually running**, because the tool never looks at that field. Pulling
the real SLA-tier distribution from the source data:

```
NewPilotLine_ProtoStation:  41.7% Critical-tier jobs  (highest of all 15 station types)
Most other station types:   ~31-35% Critical-tier jobs
```

The pilot line isn't just another low-priority category — **it carries a
disproportionately large share of the floor's most urgent work**, and the
tool's score-based allocation would zero out its test capacity entirely
without ever surfacing that fact. A deployer reading "score: 0.7997, no
allocation" would reasonably conclude this station type is simply low
priority across the board. In reality, it's the station type most likely
to be sitting on a Critical-tier job when it gets starved of capacity.

This is the same shape of failure as the earlier project's Amgen case —
an explanation that is completely correct about the model's own inputs
and silent about a real-world dimension the model was never given
visibility into. The tool's own `objective_leaves_out` field names this
exact gap ("SLA-tier urgency") before this critique was written — the
gap was disclosed in advance, and this is what it looks like in practice
on a real station type.

**Counter-example, for honesty's sake:** not every excluded station has
this problem — `SoCFinalTester_GenA` (also excluded) has a Critical-tier
share of 31.1%, roughly in line with the floor average, so its exclusion
doesn't carry the same urgency-mismatch risk the pilot line's does. The
critique isn't "every low score is dangerous" — it's "the tool cannot
distinguish the two cases, and the pilot line proves that distinction
matters."
