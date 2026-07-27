# Delegation Map + Hard-Stop Gate

## Delegation map

| Stage | Tool decides | Human decides | Override / handoff point |
|---|---|---|---|
| Data ingestion | Load CSV rows | — | — |
| GIGO gate | Reject rows failing checkable criteria (missing fields, no H-1B record, corrupt counts) | Review rejection rate if it looks abnormal | If >90% of rows are rejected (as happened here: 94.9%), a human must confirm this reflects real data sparsity, not a broken gate rule, before trusting the remaining sample |
| Scoring (approval rate + uncertainty) | Compute exact statistics | Judge whether the scoring formula itself is trustworthy | Per the causal-reasoning finding, a human must know the uncertainty-discount coefficient (0.5) injects a size bias — this is a permanent human-judgment override on how much to trust the score, not a one-time check |
| Ranking / cutoff | Sort and cut at top-N | Treat near-boundary companies as effectively tied | Per the adversarial-robustness finding, anything within ~0.001 score units of the cutoff (e.g., rank 15 vs 16 here) must be flagged and reviewed manually — the tool does not currently do this automatically, which is itself a named gap |
| Role/fit relevance | Nothing — the tool has no visibility into this at all | Manually check each recommended company's actual open roles | Mandatory, per the explainability finding (Amgen scores 0.99 but sponsors almost no backend-engineering roles) — this is not optional due diligence, it's compensating for a real blind spot |
| **Acting on the allocation** (contacting a company, submitting an application, spending real hours) | **Never** — the tool has no ability to contact anyone or submit anything | **Always** — 100% human action | **This is the hard-stop gate.** See below. |

## The hard-stop gate — implemented, not just specified
This tool never touches a real-world resource on its own: it doesn't email
companies, submit applications, or take any external action. But per the
assignment's own framing — "if it spends, commits, or changes access, it
stops and asks, every time" — the actual resource being reallocated here
(the candidate's job-search hours) still needs an explicit human checkpoint
before the recommendation is treated as a real plan, because acting on a
bad recommendation costs real time the candidate can't get back.

I implemented this as a code-level flag, not just a policy statement:

```
$ python3 tool/reallocate.py ... --out allocation_draft.json
status: "DRAFT — NOT APPROVED. Do not act on this allocation ... until a
         human has reviewed it, including checking each company's actual
         open roles, and re-run with --human-approved."

$ python3 tool/reallocate.py ... --human-approved --out allocation_approved.json
status: "HUMAN-APPROVED — reviewed and cleared for use"
```

**Why this gate is non-negotiable here:** this tool's outputs directly
shape where a real person spends scarce, non-refundable time during a
visa-constrained job search. A bad recommendation acted on blindly — e.g.
spending hours on Amgen expecting backend-engineering openings that don't
really exist there — is a real cost to the candidate, not an abstract risk.
The gate doesn't prevent the tool from being wrong; it prevents a wrong
recommendation from being acted on without a human actually looking at it
first.

**Honest limit:** the flag is trivially bypassable — nothing stops someone
from just adding `--human-approved` without actually reviewing anything.
A real deployment would need this enforced by a workflow (e.g., a second
person or a checklist UI) rather than a boolean CLI flag a single user
controls. Naming that gap is more honest than pretending the flag alone
solves the problem.
