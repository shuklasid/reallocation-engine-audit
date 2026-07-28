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
