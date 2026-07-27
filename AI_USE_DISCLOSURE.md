# AI Use Disclosure

**Tool(s) used:** Claude (Anthropic)

**Portions assisted:** Tool code (`reallocate.py`, GIGO gate, Wilson-interval
scoring, hard-stop flag), initial drafts of the causal reasoning, bias
audit, explainability, and adversarial robustness write-ups, based on
statistics computed against the real dataset.

**How used:** I directed the domain choice, the pre-registered prediction
(before any data was touched), and reviewed/confirmed every numerical claim
against real script output before it was written into the report. Claude
built the tool and ran the analysis; I set the direction and checked the
results.

**What I changed:** I didn't edit the wording or code directly, but I made
the substantive calls the AI couldn't make for me: choosing the specific
domain framing (job-search hours as the reallocated resource), committing
to a specific pre-registered failure hypothesis before any data was run,
and selecting which finding and next-step to write into my reflection
rather than accepting a generic default.

**What the AI could not do:** My pre-registered prediction guessed the
confound would live in the raw H-1B approval-rate data itself (company size
biasing the historical rate). When Claude ran the actual correlation, it
came back essentially zero (r=0.003) — the raw data wasn't confounded by
size at all. Recognizing that my prediction was wrong required checking a
second, less obvious location: the tool's *own scoring formula* was where
the size bias actually lived (r=0.154 between company size and the final
priority score), because the uncertainty-discount term shrinks
mechanically with sample size regardless of true quality. Claude could
compute both correlations instantly, but it couldn't have known which
alternative hypothesis to test next, or that the interesting story wasn't
"is there a confound" but "which of two very different places is the
confound actually hiding in" — that required me holding my own prediction
in mind and treating its failure as a lead to chase, not a dead end to
report. That's the specific judgment call an AI running statistics on
demand doesn't make on its own.
