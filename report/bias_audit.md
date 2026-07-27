# Bias Audit (Data → Output)

## Where bias enters
Not in the labels (approval/denial outcomes are objective DOL records) and
not obviously in sampling (the CSV covers a broad cross-section of Form D
filers). It enters at the **objective/scoring stage**: the tool's uncertainty
discount (`priority_score = rate * (1 - 0.5*uncertainty_width)`) treats
"few recorded decisions" as a penalty, which mechanically disadvantages
newer, smaller companies regardless of their true sponsorship rate — this
is the same mechanism identified in the causal reasoning section, now
showing up as a fairness harm rather than a purely statistical one.

## Who is systematically advantaged / starved
**Group A — early-stage** (funding stage: Pre-Seed, Seed, Series A), n=659 eligible
**Group B — late-stage** (funding stage: Series C, Series D+), n=514 eligible

| Metric | Early-stage | Late-stage |
|---|---|---|
| Mean approval rate (true quality) | 97.50% | 97.98% |
| Mean n_decisions (filing volume) | 23.93 | 151.81 |
| Mean priority_score (what the tool actually ranks on) | 0.7812 | 0.8653 |
| Selected into top-15 hour allocation | 1 / 659 | 11 / 514 |
| **Selection rate** | **0.15%** | **2.14%** |

**Quantitative fairness metric applied — four-fifths (disparate impact) rule:**
selection-rate ratio = 0.15% / 2.14% = **0.070** (7%). The four-fifths rule
(a common employment-law adverse-impact threshold) considers a selection
ratio below 80% evidence of disparate impact. This tool's ratio is **more
than 11x below that threshold**, despite the two groups having almost
identical true approval rates (97.5% vs 98.0% — a 0.48-point gap that in no
way justifies a 14x selection-rate gap).

## Two competing fairness definitions, in tension
**Definition 1 — Demographic parity / four-fifths rule:** early-stage and
late-stage companies should be selected at comparable rates. **Violated**
(ratio = 0.07, far below 0.80).

**Definition 2 — Calibration (sufficiency):** companies with equal true
approval rate should receive statistically equal treatment. Since the two
groups' true rates are nearly identical (97.5% vs 98.0%), calibration
implies they should score similarly. **Also violated** — but fixing it
isn't free.

**The actual tradeoff:** the reason small-n companies score lower isn't
arbitrary — it's the Wilson interval correctly expressing that a 100%
approval rate on 2 decisions is genuinely less certain than 100% on 610
decisions. **Removing the uncertainty discount to satisfy calibration/parity
would mean treating a company we've seen twice as equally trustworthy as
one we've seen 610 times** — which is statistically dishonest in the
opposite direction: it would overstate confidence in small, thin-history
companies, not just correct an unfair penalty.

**What I chose, and what it costs:** I'd keep some uncertainty discount
(statistical honesty matters — a truly unproven company shouldn't be
scored as confidently as a proven one) but shrink its weight sharply (e.g.
from a 0.5 coefficient to something like 0.15), and add a **guaranteed
minimum-exploration-hours floor** — every company clearing the GIGO gate
gets at least some nonzero allocation regardless of score, so early-stage
companies are never fully zeroed out by a mechanical sample-size penalty
alone. **Cost:** this deliberately sacrifices some of the score's raw
statistical rigor (a low-n company that's a genuine fluke will still get
some hours) to buy back real access for otherwise-qualified small
companies — a considered choice, not a free win.

## Highest-leverage intervention point
The `0.5` coefficient in `priority_score = rate * (1 - 0.5*uncertainty_width)`
is the single mechanical lever responsible for **both** the causal confound
(Rung 2) and this fairness violation. It's the cheapest, most targeted fix
available — changing it doesn't touch the GIGO gate, the data ingestion, or
the underlying approval-rate estimates, all of which are working as
intended.
