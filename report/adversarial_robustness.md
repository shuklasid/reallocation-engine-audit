# Adversarial Robustness & Fragility

## Finding 1 — a small perturbation flips an internal ranking
Comparing the two closest-ranked station types (both currently receiving
hours, adjacent ranks 3 and 4):

| Rank | Station | Passed/Total | Score |
|---|---|---|---|
| 3 | LegacyMixedSignalTester_GenA | 7,275 / 7,718 | 0.9374 |
| 4 | PowerDeviceTester_GenA | 934 / 985 | 0.9350 |

Gap: **0.0024** — the tightest adjacent gap on the whole ranked list.
**Adding just 20 additional failed units** (out of 7,718 — a defect-rate
increase of about 0.26%, easily within one bad batch or a single
calibration drift event) drops LegacyMixedSignalTester_GenA's score to
0.9349, below PowerDeviceTester_GenA. A realistic, small, single-cycle
quality blip reorders which station type gets more hours, even though
neither station's *true* long-run reliability plausibly changed at all.

## Finding 2 — the actual inclusion/exclusion cutoff is comparatively more robust
At the harder boundary — rank 10 (last included) vs. rank 11 (first
excluded) — the gap is larger and the story is different:

| Rank | Station | Score |
|---|---|---|
| 10 (included) | MemoryTester_GenB | 0.8930 |
| 11 (excluded) | SoCFinalTester_GenB | 0.8762 |

Flipping this boundary requires **550 additional passed units** for
SoCFinalTester_GenB (out of its current 3,302 total) — a ~17% volume
increase, not a trivial data-entry blip. **This is a meaningfully more
robust boundary than the earlier project's equivalent finding** (there,
just 2 approvals out of 172 flipped a company in or out).

## Why both results matter together
Reporting only Finding 1 would overstate fragility; reporting only
Finding 2 would understate it. The honest picture is: **which** boundary
you're near matters a lot. A station sitting near an internal-ranking
boundary can flip on almost nothing. A station sitting near the hard
inclusion cutoff needs a real, sustained volume change to flip — which is
a meaningfully different risk profile than the first project's cutoff,
and worth stating precisely rather than reusing the earlier "everything
near a boundary is fragile" framing uncritically.

## Honest limits
I did not test a genuine process-shift scenario (e.g., an actual yield-ramp
improvement sustained over many cycles, which per the causal reasoning
section is the scenario this tool is least equipped to detect at all,
since it only sees a static historical average). That's a bigger, more
interesting robustness question than either finding above, and I didn't
have time to simulate it properly for this submission.
