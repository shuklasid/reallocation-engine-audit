# Reallocation Engine — Validation Report

**Siddharth Shukla**

## 1. Working Tool + Objective

See `tool/reallocate.py` in the repo. Stated objective: maximize expected
passing-unit throughput per test-station-hour spent, using historical pass
rate as a proxy for station reliability. What it leaves out: SLA-tier
urgency, test-program-specific yield differences, calibration schedules,
and whether historical pass rate reflects current hardware state.

## 2. Data Validation & the GIGO Gate

Ingested 3,823 synthetic records; 25 rejected on checkable criteria
(missing required fields, negative unit counts, non-numeric corruption,
zero total units) — deliberately injected to give the gate something
real to catch. 3,798 rows passed, all 15 station types remained eligible.


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


# Bias Audit (Data → Output)

## Where bias enters
Not primarily in sampling or labels (units passed/failed are objective
counts) — it enters at the **feedback loop**. This tool's own output
determines which station types get more test-station-hours *next cycle*,
which determines how much new data those stations accumulate, which
determines how much their uncertainty shrinks, which determines their
priority score next time. A station excluded this cycle is disadvantaged
in exactly the input the tool uses to decide next cycle's allocation.

## Who is systematically starved
Under the current run (200 hours, top-10 of 15 station types): **5 of 15
station types receive zero hours** — `SoCFinalTester_GenA/GenB`,
`RFTester_GenA/GenB`, and `NewPilotLine_ProtoStation`. Per the causal
reasoning section, the pilot line's exclusion is *mostly* explained by a
genuinely lower observed rate — but the mechanism that keeps it excluded
going forward is purely the feedback loop: zero hours this cycle means
zero new test volume, means its uncertainty stays wide, means it keeps
scoring low next cycle too, regardless of whether its true yield is
actually improving (yield ramp).

## Quantitative fairness framing
Group station types by maturity (mean station age, already computed):
- **Established** (mean age ≥ 6 years): BurnInSystem_GenA (6.5),
  LegacyMixedSignalTester_GenA/B (6.5, 6.3) — all three **selected**,
  receiving hours every cycle.
- **Emerging/new** (mean age < 6 years, includes the youngest categories):
  RFTester_GenA/B, SoCFinalTester_GenA/B, NewPilotLine — **0 of 5
  selected** in this run.

**Selection rate: established = 3/3 (100%); emerging = 0/5 (0%).** This is
a complete exclusion, not a disparity in degree — the four-fifths rule
doesn't even apply meaningfully here because the emerging group's
selection rate is zero, the most extreme possible violation.

## Two competing fairness definitions, in tension
**Definition 1 — Demographic parity:** emerging station types should
receive some non-zero share of hours proportional to their number, so the
floor doesn't structurally freeze out newer categories. **Violated
completely** (0% selection rate for the emerging group).

**Definition 2 — Calibration/merit:** hours should go to stations that
will produce the most passing units per hour, and if emerging stations
genuinely have lower yield right now, sending them hours is a real
efficiency cost, not a bias correction. **Also has a real claim here** —
unlike the H-1B case, some of this domain's disparity may reflect true
underlying differences (yield ramp), not just measurement noise.

**The actual tradeoff:** unlike the earlier project, where calibration and
parity pointed toward the same conclusion (the disparity there was
entirely artifact, so fixing it cost little), here they may genuinely
conflict. Guaranteeing emerging stations some minimum hours could mean
routing test capacity toward stations that currently produce more scrap —
a real throughput cost, not just an accounting correction. But refusing to
ever allocate them anything guarantees they can never generate the data
needed to prove a real yield improvement, which is arguably a worse
long-run cost: a genuinely improving pilot line could stay locked out
indefinitely by a scoring formula that only looks backward.

**What I'd choose, and what it costs:** a small guaranteed exploration
floor — e.g., 5% of total hours reserved and split evenly across
zero-allocation station types regardless of score — costing a modest,
bounded amount of throughput now, in exchange for the emerging categories
having *any* chance to demonstrate real improvement over time. This is a
deliberate, named cost, not a free fix.

## Highest-leverage intervention point
The feedback loop itself: allocation determines future data, which
determines future allocation. The cheapest fix isn't changing the scoring
formula — it's decoupling "gets hours this cycle" from "definitely locked
out of ever accumulating more data," via the exploration floor above. That
breaks the loop without requiring the formula to somehow already know
which stations are truly improving.


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


# Adversarial Robustness & Fragility

## Finding 1 — a small perturbation flips an internal ranking
Comparing the two closest-ranked station types (both currently receiving
hours, adjacent ranks 3 and 4):

| Rank | Station | Passed/Total | Score |
|---|---|---|---|
| 3 | LegacyMixedSignalTester_GenA | 7,275 / 7,718 | 0.9374 |
| 4 | PowerDeviceTester_GenA | 934 / 985 | 0.9350 |

Gap: **0.0024** — the tightest adjacent gap on the whole ranked list.
**Adding just 20 additional failed units** (out of 7,718 — a defect-rate
increase of about 0.26%, easily within one bad batch or a single
calibration drift event) drops LegacyMixedSignalTester_GenA's score to
0.9349, below PowerDeviceTester_GenA. A realistic, small, single-cycle
quality blip reorders which station type gets more hours, even though
neither station's *true* long-run reliability plausibly changed at all.

## Finding 2 — the actual inclusion/exclusion cutoff is comparatively more robust
At the harder boundary — rank 10 (last included) vs. rank 11 (first
excluded) — the gap is larger and the story is different:

| Rank | Station | Score |
|---|---|---|
| 10 (included) | MemoryTester_GenB | 0.8930 |
| 11 (excluded) | SoCFinalTester_GenB | 0.8762 |

Flipping this boundary requires **550 additional passed units** for
SoCFinalTester_GenB (out of its current 3,302 total) — a ~17% volume
increase, not a trivial data-entry blip. **This is a meaningfully more
robust boundary than the earlier project's equivalent finding** (there,
just 2 approvals out of 172 flipped a company in or out).

## Why both results matter together
Reporting only Finding 1 would overstate fragility; reporting only
Finding 2 would understate it. The honest picture is: **which** boundary
you're near matters a lot. A station sitting near an internal-ranking
boundary can flip on almost nothing. A station sitting near the hard
inclusion cutoff needs a real, sustained volume change to flip — which is
a meaningfully different risk profile than the first project's cutoff,
and worth stating precisely rather than reusing the earlier "everything
near a boundary is fragile" framing uncritically.

## Honest limits
I did not test a genuine process-shift scenario (e.g., an actual yield-ramp
improvement sustained over many cycles, which per the causal reasoning
section is the scenario this tool is least equipped to detect at all,
since it only sees a static historical average). That's a bigger, more
interesting robustness question than either finding above, and I didn't
have time to simulate it properly for this submission.


# Delegation Map + Hard-Stop Gate

## Delegation map

| Stage | Tool decides | Human decides | Override / handoff point |
|---|---|---|---|
| Data ingestion | Load CSV | — | — |
| GIGO gate | Reject rows failing checkable criteria | Confirm rejection rate looks sane | 25/3,823 rejected here — a human should sanity-check this stays low; a sudden spike would suggest a real upstream data problem, not just noise |
| Scoring | Exact pass-rate + Wilson interval per station type | Judge whether the formula's assumptions hold | Per causal reasoning: a human must know this tool assumes a stable historical rate, which breaks for a station undergoing real yield ramp |
| Ranking / cutoff | Sort, cut at top-N | Treat near-boundary rankings as provisional | Per adversarial finding 1, ranks 3-4 are separated by a gap a single bad batch could close — a human should not treat close rankings as decisively ordered |
| SLA-tier urgency | Nothing — the tool has no visibility into this | Manually check whether an excluded station type is carrying disproportionate Critical-tier work | Mandatory, per the explainability finding: `NewPilotLine_ProtoStation` has the highest Critical-tier share of any station type and would be silently zeroed out without this check |
| **Acting on the allocation** (actually reconfiguring a station, rerouting a real job) | **Never** | **Always** | Hard-stop gate below |

## The hard-stop gate — implemented
Same pattern as before, code-level not just documented:

```
$ python3 tool/reallocate.py ... --out allocation_draft.json
status: "DRAFT — NOT APPROVED. Do not act on this allocation until a
         human has reviewed it, including checking SLA-tier urgency for
         queued jobs, and re-run with --human-approved."

$ python3 tool/reallocate.py ... --human-approved --out allocation_approved.json
status: "HUMAN-APPROVED — reviewed and cleared for use"
```

**Why this gate is non-negotiable here:** this tool's recommendation
directly shapes which physical test stations get real work routed to
them. A wrong recommendation acted on blindly — for instance, starving the
one station type carrying the most Critical-tier jobs — has a real
operational cost (delayed shipment of urgent units), not an abstract one.

**Honest limit:** identical to the earlier project — the flag is a
boolean a single person controls, trivially bypassable by someone who
doesn't actually review anything before setting it. A real deployment
needs this enforced by a second reviewer or a workflow gate, not a CLI
flag alone.


# AI Use Disclosure

**Tool(s) used:** Claude (Anthropic)

**Portions assisted:** Tool code (`reallocate.py`, GIGO gate, Wilson-interval
scoring, hard-stop flag), synthetic dataset generation, and initial drafts
of the causal reasoning, bias audit, explainability, and adversarial
robustness write-ups, based on statistics computed against the generated
data.

**How used:** I directed the domain pivot (from job-search hours to
semiconductor test-station capacity), the pre-registered prediction before
any script was run on the new data, and reviewed every numerical claim
against real script output. Claude built the tool, generated the synthetic
data, and ran the analysis; I set the direction and chose which findings
went into my reflection.

**What I changed:** I made the substantive calls the AI couldn't make for
me: the decision to abandon the first domain and pivot mid-assignment, the
choice of the new domain based on my own professional background, and
selecting which finding and next-fix to write into my reflection from real
options rather than a generic default.

**What the AI could not do:** My pre-registered prediction for this domain
assumed the same failure mode from my first (abandoned) domain would
repeat here — a new, low-volume category getting unfairly penalized by
sample size alone. Claude could run the exact counterfactual test
instantly (what would this station's score be with hypothetically
unlimited volume at the same rate), and the answer showed my prediction
was mostly wrong: the pilot line's low ranking is mostly a real
difference in observed reliability, not a sample-size artifact. Claude
could compute that number, but it couldn't have flagged, on its own, that
I was implicitly assuming a finding from one domain would transfer
unchanged to a structurally different one. Catching that required me
holding my own prior conclusion in mind and noticing where my new
prediction was actually just a copy of the old one, rather than a fresh
hypothesis about this specific domain.

# Rep link
https://github.com/shuklasid/reallocation-engine-audit.git

# Video link
https://northeastern-my.sharepoint.com/:v:/r/personal/shukla_sid_northeastern_edu/Documents/Recordings/Meeting%20with%20Siddharth%20Shukla-20260727_201942-Meeting%20Recording.mp4?csf=1&web=1&e=maK8J9&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D