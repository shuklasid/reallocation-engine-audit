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
