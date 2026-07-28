# Test-Capacity Reallocation Engine — Semiconductor ATE Station Hours

## What this is
A reallocation tool for a semiconductor back-end test floor: it takes a
fixed, scarce resource (available test-station-hours) and reallocates it
across station types, using historical pass-rate as an expected-return
signal, with an explicit statistical uncertainty band on every score.

## Data note
**Data note:** the dataset (`data/synthetic_ate_test_capacity.csv`) is
entirely synthetic, generated to model realistic structure — uneven record
volume across station categories, pass-rate variation, a deliberately
injected batch of malformed rows to give the GIGO gate something real to
catch. It contains no real company, product, or customer data; see the
tool's docstring for exactly what it does and doesn't capture.

**Limit worth stating plainly:** the specific pass-rate values assigned to
each station type (e.g., RF testers lower, legacy testers higher) are
illustrative — chosen to produce a realistic, uneven pattern across
station categories, not derived from a verified industry source. The
general phenomenon they're modeling (newer production lines starting with
lower yield and improving over time — "yield ramp") is a real, well-known
concept in semiconductor manufacturing, but the exact numbers here are
mine, not sourced data.

## How to run it
```
python3 tool/reallocate.py \
  --csv data/synthetic_ate_test_capacity.csv \
  --total-hours 200 --top-n 10 --min-records 2 \
  --out report/allocation_output.json
```
Add `--human-approved` only after manually reviewing the output (see
`report/delegation_map.md`), including checking SLA-tier urgency — without
the flag, the output is marked DRAFT and should not be acted on.

## Repo structure
```
tool/reallocate.py                — the working engine (component 1 + GIGO gate)
data/synthetic_ate_test_capacity.csv — synthetic dataset, documented above
report/causal_reasoning.md        — Pearl's three rungs (component 5, 15 pts)
report/bias_audit.md              — fairness metrics + feedback-loop tradeoff (component 3, 10 pts)
report/explainability.md          — score decomposition + critique (component 4, 10 pts)
report/adversarial_robustness.md  — two contrasting boundary-flip cases (component 6, 8 pts)
report/delegation_map.md          — hard-stop gate, implemented (component 7, 10 pts)
report/allocation_draft.json      — real output, DRAFT state
report/allocation_approved.json   — real output, HUMAN-APPROVED state
journal/frictional_journal.md     — pre-registered prediction + reflection (this domain)
AI_USE_DISCLOSURE.md              — required disclosure block
```

## Anchor to the book — honest note on fit
*The Reallocation Engine* is written specifically about the job-search
domain (Ch.2's "reallocation principle," the 3-3-2 day, the freed-hour
rule). This project pivoted to a semiconductor test-capacity domain that
the book doesn't directly address, so the connection here is
**principle-level, not literal-mechanism-level**, and that's a real
difference in fit worth stating plainly rather than papering over.

The strongest genuine anchor is **Ch.3, "The Verified-Data Contract"**:
a verification field may only be filled by a script reading a real record,
never by model inference. This tool's GIGO gate follows that rule — every
rejected row is rejected by a checkable, mechanical criterion, not a
judgment call. The broader "reallocation principle" (spend a scarce
resource where the expected return is, not where the feedback feels good)
still applies as a general framework, but this project does not claim the
same close, chapter-specific fit that the original (abandoned) job-search
domain had.

## Real findings, in one paragraph each
- **GIGO gate:** 25 of 3,823 rows rejected on real, varied, checkable
  criteria (missing fields, negative counts, non-numeric corruption) —
  deliberately injected to test the gate, disclosed here rather than hidden.
- **Causal reasoning:** unlike the abandoned first domain, raw pass rate
  here correlates moderately with record volume (r=0.306) — but a
  counterfactual test shows even unlimited volume barely changes the
  lowest-scoring station's rank, meaning most of its exclusion is a real
  reliability difference, not a scoring artifact. My prediction assumed
  the opposite and was mostly wrong.
- **Bias audit:** 5 of 15 station types get zero hours; the real harm
  isn't the exclusion itself but the feedback loop — zero hours means zero
  new data, means the uncertainty never shrinks, means permanent exclusion
  regardless of real improvement.
- **Explainability:** the lowest-scoring, fully-excluded station type
  (`NewPilotLine_ProtoStation`) carries the *highest* share of Critical-SLA
  jobs of any station on the floor — a fact the score-based explanation
  never surfaces.
- **Adversarial:** an internal ranking (ranks 3-4) flips with just 20
  additional failed units out of 7,718 — but the actual inclusion cutoff
  (ranks 10-11) needs a much larger, ~17% volume change to flip, a more
  robust boundary than the earlier project's equivalent finding.
- **Hard-stop:** implemented as a real `--human-approved` CLI flag,
  identical mechanism to the earlier project.
