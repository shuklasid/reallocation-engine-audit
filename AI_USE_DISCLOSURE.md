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
