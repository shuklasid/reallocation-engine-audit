# Explainability & Its Critique

## Method
The engine's scoring function is fully known and simple:
`priority_score = approval_rate * (1 - 0.5 * uncertainty_width)`.

Because the function is transparent and closed-form, I use an **exact
additive/multiplicative decomposition** of each score into its two inputs,
rather than an approximate method like SHAP or LIME. Running a
sampling-based approximate explainer on a formula this simple would
re-derive, with noise, something I can already state exactly — that would
be theater, not rigor. (This is itself a small but real explainability
lesson: SHAP/LIME earn their keep on opaque models; applying them to a
white-box formula is the wrong tool for the job.)

**Exact decomposition for a real top-15 company (AMGEN INC):**

| Component | Value | Contribution |
|---|---|---|
| Approvals / Denials | 1,882 / 10 (n=1,892) | raw counts behind the rate |
| Approval rate | 99.47% | base term |
| uncertainty_width | 0.0068 (very narrow) | discount = 1 − 0.5×0.0068 ≈ 0.9966 |
| **priority_score** | **0.9913** | 0.9947 × 0.9966 |
| **Allocated hours** | **2.67 of 40** | proportional share of top-15 pool |

**The explanation, stated plainly:** "Amgen received 2.67 hours because it
has a high historical H-1B approval rate and a large enough filing history
that we're confident in that rate." This is **completely accurate** — every
number in it is exactly derivable from the formula and the underlying data.

## The critique — where this explanation is accurate but misleading
The explanation says nothing about **what kind of roles Amgen actually
sponsors**, because the tool never looks at that field. Pulling Amgen's real
`top_job_titles_sponsored` from the source CSV:

```
['Data Engineer', 'Strategy Sr. Manager', 'Commercial Leadership Program',
 'Principal IS Architect', 'Sr. Associate IS Engineer']
```

Amgen is a biotech/pharma company. Its H-1B history is dominated by
commercial, strategy, and IT-support roles — not backend or
distributed-systems software engineering, which is what this candidate is
actually searching for. **The explanation is silent on this entirely.** A
candidate reading "Amgen scored 0.99, spend 2.67 hours here" would
reasonably conclude Amgen is a strong use of their time — but if there is no
open backend-engineering role there at all, those hours could be a near-total
loss, and nothing in the score or its explanation would have warned them.

This is a misleading-by-omission case, not a misleading-by-error case: every
number the explanation reports is correct, and the explanation is complete
**with respect to the model's own inputs**. The gap is that the model's
inputs were never designed to capture role relevance — a dimension the
candidate cares about at least as much as sponsorship likelihood. This
exact gap was already named, honestly, in the tool's own
`objective_leaves_out` field before this critique was written — which is
itself worth stating plainly: the tool told you what it couldn't see, and
this is what that blind spot looks like when you go find a real company it
produces.

**Counter-example, for honesty's sake:** not every high scorer has this
problem — `AURIS HEALTH INC` (also top-15) sponsors genuine `Software
Engineer`, `Senior Software Engineer`, and `Senior Systems Integration
Engineer` titles alongside hardware/QA roles, so its high score is a
reasonably good match. The critique isn't "the tool is always wrong" — it's
"the tool cannot tell you which case you're in, and Amgen proves that gap is
real, not hypothetical."

**This gap was named in advance, not discovered independently.** The
book's Ch.2 exercises specify four required verification columns for any
target-list tool: sponsorship status, funding recency, posting liveness,
and role quality. This build implements exactly one of the four
(sponsorship status). The Amgen case is precisely what the book's own
framework predicts happens when "role quality" is left unverified — a
company can look statistically excellent on sponsorship grounds while
being a poor match on the dimension the tool never checked.

