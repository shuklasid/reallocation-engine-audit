#!/usr/bin/env python3
"""
Test-Capacity Reallocation Engine.

Domain: a semiconductor back-end test floor has a fixed, scarce resource —
available test-station-hours — and must reallocate queued test jobs across
station types. This tool ingests a SYNTHETIC dataset modeling generic ATE
(automated test equipment) station archetypes, gates it for quality, scores
station types by historical pass rate with an explicit uncertainty band,
and reallocates a fixed hour-budget proportional to that score.

DATA NOTE: this dataset is entirely synthetic, generated to model realistic
structure (uneven record volume across station types, pass-rate noise,
varied test-program mix) — it contains no real company, product, or
customer data. What it captures: the *statistical shape* of an uneven,
real-world-plausible test-floor dataset (some station types logged 30
completions, others 400+; pass rates cluster realistically by station
category). What it does NOT capture: real yield economics, real SLA
penalty costs, real test-program dependencies, or any actual employer's
production data.

STATED OBJECTIVE (one sentence): maximize expected passing-unit throughput
per test-station-hour spent, using each station type's historical pass
rate as a proxy for "will this station reliably pass units if given more
time."

WHAT THIS OBJECTIVE LEAVES OUT: it says nothing about SLA tier urgency
(a Critical-tier job may need to jump the queue regardless of station
pass-rate), test-program-specific yield differences, station calibration
schedules, or whether a station's historical pass rate reflects its
current hardware state versus a stale, superseded configuration.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# 1. INGEST
# ---------------------------------------------------------------------------
def load_rows(csv_path: str) -> list[dict]:
    with open(csv_path, encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# 2. GIGO GATE
# ---------------------------------------------------------------------------
GATE_REQUIRED_FIELDS = ["station_type", "sla_tier"]


def passes_gate(row: dict) -> tuple[bool, str]:
    for field in GATE_REQUIRED_FIELDS:
        if not (row.get(field) or "").strip():
            return False, f"missing required field: {field}"
    try:
        passed = float(row.get("units_passed") or 0)
        failed = float(row.get("units_failed") or 0)
    except ValueError:
        return False, "non-numeric units_passed/units_failed"
    if passed < 0 or failed < 0:
        return False, "negative unit counts (data corruption)"
    if passed + failed == 0:
        return False, "zero total units tested on record — no signal"
    return True, ""


def run_gigo_gate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    passed_rows, rejected = [], []
    for r in rows:
        ok, reason = passes_gate(r)
        if ok:
            passed_rows.append(r)
        else:
            rejected.append({"station_instance_id": r.get("station_instance_id", "?"), "reason": reason})
    return passed_rows, rejected


# ---------------------------------------------------------------------------
# 3. AGGREGATE PER STATION TYPE + WILSON SCORE
# ---------------------------------------------------------------------------
def wilson_interval(successes: float, total: float, z: float = 1.96) -> tuple[float, float, float]:
    if total == 0:
        return 0.0, 0.0, 0.0
    p = successes / total
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    half = (z * math.sqrt((p * (1 - p) / total) + (z**2 / (4 * total**2)))) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def aggregate_by_station_type(rows: list[dict]) -> list[dict]:
    agg = defaultdict(lambda: {"passed": 0.0, "failed": 0.0, "n_records": 0, "ages": []})
    for r in rows:
        st = r["station_type"]
        agg[st]["passed"] += float(r.get("units_passed") or 0)
        agg[st]["failed"] += float(r.get("units_failed") or 0)
        agg[st]["n_records"] += 1
        try:
            agg[st]["ages"].append(float(r.get("station_age_years")))
        except (TypeError, ValueError):
            pass

    out = []
    for st, d in agg.items():
        total = d["passed"] + d["failed"]
        p, lo, hi = wilson_interval(d["passed"], total)
        width = hi - lo
        priority = p * (1 - 0.5 * width)
        out.append({
            "station_type": st,
            "n_records": d["n_records"],
            "total_units": total,
            "pass_rate_point": round(p, 4),
            "pass_rate_ci95": [round(lo, 4), round(hi, 4)],
            "uncertainty_width": round(width, 4),
            "priority_score": round(priority, 4),
            "mean_station_age_years": round(sum(d["ages"]) / len(d["ages"]), 2) if d["ages"] else None,
        })
    return out


# ---------------------------------------------------------------------------
# 4. REALLOCATION
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
    ap.add_argument("--total-hours", type=float, default=200.0,
                     help="total scarce resource (test-station-hours) to reallocate")
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--min-records", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--human-approved", action="store_true",
                     help="HARD STOP: without this flag, output is DRAFT and unusable. "
                          "This tool never reconfigures a station or reroutes a real job — "
                          "it only produces a recommendation. A human must review (including "
                          "checking SLA-tier urgency, which this tool ignores) before treating "
                          "this as an actual capacity plan.")
    args = ap.parse_args()

    rows = load_rows(args.csv)
    passed_rows, rejected = run_gigo_gate(rows)
    scored = aggregate_by_station_type(passed_rows)
    scored = [s for s in scored if s["n_records"] >= args.min_records]
    allocation = reallocate_hours(scored, args.total_hours, args.top_n)

    out = {
        "status": ("HUMAN-APPROVED — reviewed and cleared for use" if args.human_approved
                    else "DRAFT — NOT APPROVED. Do not act on this allocation until a human "
                         "has reviewed it, including checking SLA-tier urgency for queued jobs, "
                         "and re-run with --human-approved."),
        "objective_stated": ("Maximize expected passing-unit throughput per test-station-hour "
                              "spent, using historical pass rate as a proxy for station "
                              "reliability."),
        "objective_leaves_out": ("SLA-tier urgency, test-program-specific yield differences, "
                                  "calibration schedules, and whether historical pass rate "
                                  "reflects current hardware state."),
        "data_note": "SYNTHETIC dataset — see tool docstring for what it does/doesn't capture.",
        "gate": {
            "rows_in": len(rows),
            "rows_passed": len(passed_rows),
            "rows_rejected": len(rejected),
            "rejection_reasons_sample": rejected[:10],
        },
        "station_types_eligible": len(scored),
        "total_hours_reallocated": args.total_hours,
        "allocation": allocation,
    }

    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"gate: {len(rows)} in -> {len(passed_rows)} passed -> {len(scored)} eligible station types")
    print(f"reallocated {args.total_hours} hours across top {len(allocation)} station types -> {args.out}")


if __name__ == "__main__":
    main()
