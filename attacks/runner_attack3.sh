#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runner for Attack 3 - Structural kNN voting for link prediction
Runs all datasets (NELL, FB15, HealthKG) with their respective sensitive relations.
"""

import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION — update paths before running
# ─────────────────────────────────────────────────────────────────

SCRIPT = Path(__file__).parent / "attack3.py"

DATASETS = [
    {
        "name":            "NELL",
        "public":          "/path/to/NELL/global_kg_public_wo_sensitive.tsv",
        "sensitive_dir":   "/path/to/NELL/sensitive",
        "sensitive_files": "concept:atlocation.tsv,concept:proxyfor.tsv,concept:subpartof.tsv,concept:teamplaysagainstteam.tsv",
        "head_prefix":     "",
        "knn_k":           120,
    },
    {
        "name":            "FB15",
        "public":          "/path/to/FB15/global_kg_public_wo_sensitive.tsv",
        "sensitive_dir":   "/path/to/FB15/sensitive",
        "sensitive_files": "education__educational_institution__students_graduates.__education__education__student.tsv,film__film__genre.tsv,people__person__profession.tsv,sports__sports_position__players.__sports__sports_team_roster__team.tsv",
        "head_prefix":     "",
        "knn_k":           120,
    },
    {
        "name":            "HealthKG",
        "public":          "/path/to/HealthKG/global_kg_public.tsv",
        "sensitive_dir":   "/path/to/HealthKG/sensitive",
        "sensitive_files": "has_age_category.tsv,has_age_living_apart.tsv,has_family_ID.tsv,has_gender.tsv,has_is_westernized.tsv,has_is-from.tsv,has_zygosity.tsv",
        "head_prefix":     "",
        "knn_k":           120,
    },
]

OUTBASE = Path("/path/to/results/Attack3")

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
    total   = len(DATASETS)
    current = 0

    for ds in DATASETS:
        current += 1
        outdir = OUTBASE / ds["name"]

        print(f"\n[{current}/{total}] {ds['name']}")

        cmd = [
            sys.executable, str(SCRIPT),
            "--public_tsv",      ds["public"],
            "--sensitive_dir",   ds["sensitive_dir"],
            "--sensitive_files", ds["sensitive_files"],
            "--knn_k",           str(ds["knn_k"]),
            "--outdir",          str(outdir),
        ]

        if ds["head_prefix"]:
            cmd += ["--head_prefix", ds["head_prefix"]]

        run(cmd)

    print(f"\n{'='*60}")
    print(f"[+] All {total} experiments completed.")
    print(f"[+] Results saved in: {OUTBASE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()