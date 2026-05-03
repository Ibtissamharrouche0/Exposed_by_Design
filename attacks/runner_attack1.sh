#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner for Attack 1 - ni_head + Ri features
Runs all datasets (NELL, FB15, HealthKG) across layers 1 and 2.
"""

import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION — update paths before running
# ─────────────────────────────────────────────────────────────────

SCRIPT = Path(__file__).parent / "attack1_ni_head_Ri.py"

DATASETS = [
    {
        "name":          "NELL",
        "public":        "/path/to/NELL/global_kg_public_wo_sensitive.tsv",
        "sens":          "/path/to/NELL/sensitive/concept:teamplaysagainstteam.tsv",
        "header":        False,
        "num_neg":       5000,
        "hard_neg_mode": "median_ge",
    },
    {
        "name":          "FB15",
        "public":        "/path/to/FB15/global_kg_public_wo_sensitive.tsv",
        "sens":          "/path/to/FB15/sensitive/sports__sports_position__players.__sports__sports_team_roster__team.tsv",
        "header":        False,
        "num_neg":       5000,
        "hard_neg_mode": "median_ge",
    },
    {
        "name":          "HealthKG",
        "public":        "/path/to/HealthKG/global_kg_public.tsv",
        "sens":          "/path/to/HealthKG/sensitive/has_taxonomy.tsv",
        "header":        True,
        "num_neg":       50000,
        "hard_neg_mode": "median_ge",
    },
]

LAYERS  = [2]
OUTBASE = Path("/path/to/results/Attack1_ni_head_Ri")

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
    total   = len(DATASETS) * len(LAYERS)
    current = 0

    for ds in DATASETS:
        for max_hop in LAYERS:
            current += 1
            outdir = OUTBASE / ds["name"] / f"L{max_hop}"

            print(f"\n[{current}/{total}] {ds['name']} — Layer {max_hop}")

            cmd = [
                sys.executable, str(SCRIPT),
                "--sens-path",     ds["sens"],
                "--public-path",   ds["public"],
                "--max-hop",       str(max_hop),
                "--num-neg",       str(ds["num_neg"]),
                "--hard-neg-mode", ds["hard_neg_mode"],
                "--outdir",        str(outdir),
            ]

            if ds["header"]:
                cmd.append("--public-has-header")

            run(cmd)

    print(f"\n{'='*60}")
    print(f"[+] All {total} experiments completed.")
    print(f"[+] Results saved in: {OUTBASE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()