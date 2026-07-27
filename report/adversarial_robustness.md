# Adversarial Robustness & Fragility

## The perturbation
A small, entirely realistic change: **2 additional approved LCAs** for a
company already near the top-15 cutoff — well within normal year-to-year
filing noise, not an attack in any dramatic sense, just the kind of update
that would show up in next year's data refresh.

## Real case, exact numbers
| Rank | Company | Approvals | n | Rate | Score |
|---|---|---|---|---|---|
| 15 (last included) | ICON TECHNOLOGY INC | 2,200 | 2,216 | 99.28% | 0.98918 |
| 16 (just excluded) | TURO INC | 172 | 172 | 100% | 0.98908 |

The score gap between rank 15 and rank 16 is **0.0001** — a rounding error's
width. Adding 2 approvals to Turo's real record (172 → 174 approvals, same
100% rate) is enough to push its score to 0.9892, **flipping the ranking**
and bumping Icon Technology out of the top-15 entirely, with zero hours
allocated instead of its current 2.66.

## Condition under which the engine flips
Any company sitting within roughly 0.0001–0.001 priority-score units of the
cutoff boundary is one or two ordinary filings away from flipping in or out
— and there's no way to tell from the tool's output which companies are in
that fragile zone versus genuinely, robustly ranked. The engine gives no
signal that rank 15 and rank 16 are, for practical purposes, tied.

## Why this matters, not just as a math curiosity
This isn't really "gaming" in the adversarial-attacker sense — a company
doesn't need to try to manipulate this. **Ordinary data refresh noise**
(this quarter's filings versus last quarter's) could flip which companies
make a candidate's top-15 list, for reasons that have nothing to do with
which company is actually a better use of the candidate's next 40 hours.

## Honest limits of this test
I did not test a genuine distribution-shift scenario (e.g., an
across-the-board approval-rate drop from a policy change) — that would
require simulating a shifted dataset rather than perturbing one real row,
and I didn't have time to build that scenario for this submission. It's a
known gap, not a hidden one: a policy shift that raises denial rates
industry-wide would silently invalidate every score in this tool, since
nothing here is time-weighted or aware of recency.

## What the fix would actually be
The deeper issue isn't the scoring formula — it's the **hard top-N cutoff
itself**. Any hard cutoff creates a cliff at whatever score happens to sit
at position N, regardless of how close position N+1 is. A more honest
design would either (a) allocate hours continuously and proportionally
across all eligible companies rather than a hard top-15, or (b) explicitly
flag "near-boundary" companies (e.g., within some epsilon of the cutoff) as
statistically tied, rather than presenting a clean ordinal ranking that
implies more precision than the data supports.
