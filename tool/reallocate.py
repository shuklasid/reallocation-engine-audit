#!/usr/bin/env python3
"""
Attention Reallocation Engine — job-search hour allocation.

Domain: an international MS student on STEM OPT has a fixed, scarce resource
and must reallocate it across candidate employers. Per Ch.2 ("The
Reallocation Principle") of The Reallocation Engine, effort should go where
the expected return is, not where the feedback feels good — that book
argues a 3-3-2 day (2hrs targeted applying / 3hrs networking / 3hrs
portfolio), with the "freed-hour rule" governing what happens when a role
is skipped. This tool operates WITHIN the targeted-applying sub-budget: it
does not decide the 3-3-2 split itself, it decides which companies that
applying time should go to, using historical H-1B approval rate as an
expected-return signal. This tool ingests SEC Form D x DOL H-1B mapped
company data, gates it for quality (per Ch.3's "Verified-Data Contract" —
verification comes from a script reading a public record, never from model
inference), scores candidates, and reallocates a fixed hour-budget
proportional to a priority score WITH an explicit uncertainty band on that
score.

STATED OBJECTIVE (one sentence): within a candidate's targeted-applying
hours, maximize expected interview-hours obtained per hour spent, using
each company's historical H-1B approval rate as a proxy for "will sponsor
me if I get an offer."

WHAT THIS OBJECTIVE LEAVES OUT: it says nothing about how many people are
competing for a given role, how hard that company's process actually is,
whether the company is even hiring for backend/infra roles right now, or
whether past approval rate predicts future sponsorship at all for a company
that has since changed policy, been acquired, or stopped filing. It also
treats "hours spent" as a free variable, when in reality some applications
take 20 minutes and others take a full day (referral hunting, take-home
tests). This is a REALLOCATION ON A PROXY, not a reallocation on hiring odds.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. INGEST
# ---------------------------------------------------------------------------
def load_rows(csv_path: str) -> list[dict]:
    with open(csv_path, encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# 2. GIGO GATE — a checkable quality standard, applied BEFORE any scoring
# ---------------------------------------------------------------------------
GATE_REQUIRED_FIELDS = ["company_name", "industry", "state"]


def passes_gate(row: dict) -> tuple[bool, str]:
    """Returns (passes, reason_if_rejected)."""
    for field in GATE_REQUIRED_FIELDS:
        if not (row.get(field) or "").strip():
            return False, f"missing required field: {field}"

    approvals = row.get("Total Approvals")
    denials = row.get("Total Denials")
    if not approvals and not denials:
        return False, "no H-1B record at all (approvals and denials both null)"

    try:
        a = float(approvals) if approvals else 0.0
        d = float(denials) if denials else 0.0
    except ValueError:
        return False, "non-numeric approvals/denials"

    if a < 0 or d < 0:
        return False, "negative approvals/denials (data corruption)"

    if a == 0 and d == 0:
        return False, "zero total H-1B decisions on record — no signal"

    return True, ""


def run_gigo_gate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    passed, rejected = [], []
    for r in rows:
        ok, reason = passes_gate(r)
        if ok:
            passed.append(r)
        else:
            rejected.append({"company_name": r.get("company_name", "?"), "reason": reason})
    return passed, rejected


# ---------------------------------------------------------------------------
# 3. SCORING — Wilson score interval for approval-rate uncertainty
# ---------------------------------------------------------------------------
def wilson_interval(successes: float, total: float, z: float = 1.96) -> tuple[float, float, float]:
    """Returns (point_estimate, low, high) — 95% Wilson score interval.
    Correctly widens the interval when total (n) is small, unlike a naive
    approvals/(approvals+denials) ratio, which reports 100% confidence off
    of e.g. a single approval and no denials."""
    if total == 0:
        return 0.0, 0.0, 0.0
    p = successes / total
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    half = (z * math.sqrt((p * (1 - p) / total) + (z**2 / (4 * total**2)))) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def score_company(row: dict) -> dict:
    a = float(row.get("Total Approvals") or 0)
    d = float(row.get("Total Denials") or 0)
    total = a + d
    p, lo, hi = wilson_interval(a, total)
    uncertainty_width = hi - lo  # wide interval = low confidence in the point estimate
    return {
        "company_name": row["company_name"],
        "industry": row.get("industry", ""),
        "state": row.get("state", ""),
        "n_decisions": total,
        "approval_rate_point": round(p, 4),
        "approval_rate_ci95": [round(lo, 4), round(hi, 4)],
        "uncertainty_width": round(uncertainty_width, 4),
        # priority score discounts by uncertainty: a 90% rate on n=2 is
        # trusted less than a 70% rate on n=200
        "priority_score": round(p * (1 - 0.5 * uncertainty_width), 4),
    }


# ---------------------------------------------------------------------------
# 4. REALLOCATION — allocate a fixed hour-budget proportional to priority
# ---------------------------------------------------------------------------
def reallocate_hours(scored: list[dict], total_hours: float, top_n: int) -> list[dict]:
    top = sorted(scored, key=lambda r: r["priority_score"], reverse=True)[:top_n]
    score_sum = sum(r["priority_score"] for r in top) or 1.0
    for r in top:
        share = r["priority_score"] / score_sum
        r["allocated_hours"] = round(share * total_hours, 2)
    return top


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--total-hours", type=float, default=40.0,
                     help="total scarce resource (application-hours) to reallocate")
    ap.add_argument("--top-n", type=int, default=15,
                     help="how many companies receive an allocation")
    ap.add_argument("--min-decisions", type=float, default=2.0,
                     help="floor on n_decisions to even be eligible (avoid n=1 flukes)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--human-approved", action="store_true",
                     help="HARD STOP: without this flag, output is marked DRAFT and unusable. "
                          "This tool never contacts a company, submits an application, or takes "
                          "any action on the candidate's behalf — it only ever produces a "
                          "recommendation. A human must explicitly pass this flag after reviewing "
                          "the allocation (including checking each company's actual open roles, "
                          "per the explainability report's Amgen finding) before treating this "
                          "output as an actual plan.")
    args = ap.parse_args()

    rows = load_rows(args.csv)
    passed, rejected = run_gigo_gate(rows)

    scored = [score_company(r) for r in passed]
    scored = [s for s in scored if s["n_decisions"] >= args.min_decisions]

    allocation = reallocate_hours(scored, args.total_hours, args.top_n)

    out = {
        "status": ("HUMAN-APPROVED — reviewed and cleared for use" if args.human_approved
                    else "DRAFT — NOT APPROVED. Do not act on this allocation (do not contact "
                         "any company, submit any application, or spend any hours based on this "
                         "output) until a human has reviewed it, including checking each "
                         "company's actual open roles, and re-run with --human-approved."),
        "objective_stated": ("Within a candidate's targeted-applying hours (per the book's 3-3-2 "
                              "day, Ch.2), maximize expected interview-hours obtained per hour "
                              "spent, using historical H-1B approval rate as a proxy for "
                              "sponsorship likelihood."),
        "objective_leaves_out": ("Competition per role, per-application time variance, whether "
                                  "the company is currently hiring for this candidate's target "
                                  "role, and whether past approval behavior predicts future "
                                  "sponsorship policy."),
        "gate": {
            "rows_in": len(rows),
            "rows_passed": len(passed),
            "rows_rejected": len(rejected),
            "rejection_reasons_sample": rejected[:10],
        },
        "eligible_after_min_decisions_filter": len(scored),
        "total_hours_reallocated": args.total_hours,
        "allocation": allocation,
    }

    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"gate: {len(rows)} in -> {len(passed)} passed -> {len(scored)} eligible "
          f"(min_decisions={args.min_decisions})")
    print(f"reallocated {args.total_hours} hours across top {len(allocation)} companies -> {args.out}")


if __name__ == "__main__":
    main()
