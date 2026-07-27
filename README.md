# Attention Reallocation Engine — H-1B Sponsorship Job-Search Hour Allocation

## What this is
A reallocation tool for an international MS student on STEM OPT: it takes a
fixed, scarce resource (job-search hours before the visa clock runs out) and
reallocates it across candidate employers, using historical H-1B approval
data as a sponsorship-likelihood proxy, with an explicit statistical
uncertainty band on every score.

## How to run it
```
python3 tool/reallocate.py \
  --csv <path-to-SEC_DOL_H1b_data_mapped.csv> \
  --total-hours 40 --top-n 15 --min-decisions 2 \
  --out report/allocation_output.json
```
Add `--human-approved` only after manually reviewing the output (see
`report/delegation_map.md`) — without it, the output is marked DRAFT and
should not be acted on.

## Repo structure
```
tool/reallocate.py                — the working engine (component 1 + GIGO gate)
report/causal_reasoning.md        — Pearl's three rungs (component 5, 15 pts)
report/bias_audit.md              — fairness metrics + tradeoff (component 3, 10 pts)
report/explainability.md          — score decomposition + critique (component 4, 10 pts)
report/adversarial_robustness.md  — real boundary-flip case (component 6, 8 pts)
report/delegation_map.md          — hard-stop gate, implemented (component 7, 10 pts)
report/allocation_draft.json      — real output, DRAFT state
report/allocation_approved.json   — real output, HUMAN-APPROVED state
journal/frictional_journal.md     — pre-registered prediction + reflection
AI_USE_DISCLOSURE.md              — required disclosure block
```

## Anchor to the book
This tool is anchored to two mechanisms from *The Reallocation Engine*:

- **Ch.2, "The Reallocation Principle":** effort should go where the
  expected return is, not where the feedback feels good. The book argues
  for a 3-3-2 day (2hrs targeted applying / 3hrs networking / 3hrs
  portfolio) and treats a skip as a first-class decision with an explicit
  "freed-hour rule." This tool does not decide the 3-3-2 split — it
  operates one level deeper, deciding which companies the targeted-applying
  hours should go to, using the same "return over feedback" logic.
- **Ch.3, "The Verified-Data Contract":** a verification field (the book
  names four: sponsorship status, funding recency, posting liveness, role
  quality) may only be filled by a script reading a real public record,
  never by model inference. This tool's GIGO gate follows that rule for
  sponsorship status — and, as the explainability section shows, the
  *absence* of the other three named columns (especially role quality) is
  exactly what let Amgen score 99% while barely sponsoring relevant roles.
  That's not a gap I discovered independently — the book's own framework
  names it as required, and this build only implements one of the four.

*(Cited by chapter/section name, not page number — the source file is an
EPUB with no fixed pagination; if a paginated edition exists on Canvas,
substitute the real page numbers there.)*

## Real findings, in one paragraph each

- **GIGO gate:** 94.9% of the 30,369-company dataset has no usable H-1B
  record at all — this tool only ever operates on the remaining 5%.
- **Causal reasoning:** raw approval rate is NOT confounded by company size
  (r=0.003) — but the tool's own uncertainty-discount formula manufactures
  a size bias that isn't in the underlying data (r=0.154 with n_decisions).
- **Bias audit:** early-stage companies (nearly identical true approval
  rate to late-stage: 97.5% vs 98.0%) are selected into the top-15 at 14x
  lower a rate (0.15% vs 2.14%) — a four-fifths-rule violation of 0.07.
- **Explainability:** Amgen scores 0.99 (exact, correct math) but its real
  sponsored titles are commercial/IT-support, not backend engineering — the
  explanation is accurate about the score and silent about fit.
- **Adversarial:** Turo Inc, real rank 16, flips into the top-15 with just
  2 additional approvals — the score gap at the cutoff is 0.0001.
- **Hard-stop:** implemented as a real `--human-approved` CLI flag; output
  is unusable (marked DRAFT) without it.
