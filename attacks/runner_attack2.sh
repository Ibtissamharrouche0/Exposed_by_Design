#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner for Attack 2 - Pairwise tail inference from Attack 1 scores
Runs all datasets (NELL, FB15, HealthKG) with their respective sensitive relations.
"""

import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION — update paths before running
# ─────────────────────────────────────────────────────────────────

SCRIPT = Path(__file__).parent / "attack2.py"

DATASETS = [
    {
        "name":               "NELL",
        "public":             "/path/to/NELL/global_kg_public_wo_sensitive.tsv",
        "public_has_header":  False,
        "sens":               "/path/to/NELL/sensitive/concept:teamplaysagainstteam.tsv",
        "sens_has_header":    False,
        "relation_name":      "concept:teamplaysagainstteam",
        "a1h_scores":         "/path/to/results/Attack1/NELL/attack1_head_scores.tsv",
        "a1t_scores":         "/path/to/results/Attack1/NELL/attack1_tail_scores.tsv",
        "a1h_thr":            0.5,
        "a1t_thr":            0.5,
    },
    {
        "name":               "FB15",
        "public":             "/path/to/FB15/global_kg_public_wo_sensitive.tsv",
        "public_has_header":  False,
        "sens":               "/path/to/FB15/sensitive/sports__sports_position__players.__sports__sports_team_roster__team.tsv",
        "sens_has_header":    False,
        "relation_name":      "sports__sports_position__players.__sports__sports_team_roster__team",
        "a1h_scores":         "/path/to/results/Attack1/FB15/attack1_head_scores.tsv",
        "a1t_scores":         "/path/to/results/Attack1/FB15/attack1_tail_scores.tsv",
        "a1h_thr":            0.0,
        "a1t_thr":            0.0,
    },
    {
        "name":               "HealthKG",
        "public":             "/path/to/HealthKG/global_kg_public.tsv",
        "public_has_header":  True,
        "sens":               "/path/to/HealthKG/sensitive/has_taxonomy.tsv",
        "sens_has_header":    False,
        "relation_name":      "has_taxonomy",
        "a1h_scores":         "/path/to/results/Attack1/HealthKG/attack1_head_scores.tsv",
        "a1t_scores":         "/path/to/results/Attack1/HealthKG/attack1_tail_scores.tsv",
        "a1h_thr":            0.3,
        "a1t_thr":            0.8,
    },
]

FEATURE_SETS = ["local", "proxies", "knn"]
OUTBASE      = Path("/path/to/results/Attack2")

# ─────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────

def run(cmd):
    print(f"\n{'='*60}")
    print(f"[RUN] {' '.join(cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"[WARNING] Command exited with code {result.returncode}")
    return result.returncode


def main():
    total   = len(DATASETS) * len(FEATURE_SETS)
    current = 0

    for ds in DATASETS:
        for feature_set in FEATURE_SETS:
            current += 1
            outdir = OUTBASE / ds["name"] / feature_set

            print(f"\n[{current}/{total}] {ds['name']} — feature_set={feature_set}")

            cmd = [
                sys.executable, str(SCRIPT),
                "--public-path",          ds["public"],
                "--sens-path",            ds["sens"],
                "--relation-name",        ds["relation_name"],
                "--attack1-head-scores",  ds["a1h_scores"],
                "--attack1-tail-scores",  ds["a1t_scores"],
                "--a1h-thr",              str(ds["a1h_thr"]),
                "--a1t-thr",              str(ds["a1t_thr"]),
                "--feature-set",          feature_set,
                "--outdir",               str(outdir),
            ]

            if ds["public_has_header"]:
                cmd.append("--public-has-header")
            if ds["sens_has_header"]:
                cmd.append("--sens-has-header")

            run(cmd)

    print(f"\n{'='*60}")
    print(f"[+] All {total} experiments completed.")
    print(f"[+] Results saved in: {OUTBASE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()