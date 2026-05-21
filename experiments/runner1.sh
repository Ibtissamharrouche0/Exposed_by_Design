#!/bin/bash
#
# Runner for Attack 1 Ablation Study
# Tests all feature groups on NELL, FB15k-237, and HealthKG
#


set -e

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

OUTDIR="./results/ablation_attack1"
DEVICE="cuda"  # Change to "cpu" if no GPU
EPOCHS=100
BATCH_SIZE=2048
MAX_LAYER=2

# Hard negative sampling (dataset-specific, set in each loop below)
# - NELL & FB15k-237: 5,000 hard negatives
# - HealthKG: 50,000 hard negatives (larger dataset)

# Feature groups to test
FEATURES=("ni_head" "ni_tail" "Ii_head" "Ei_head" "Ri")

echo "════════════════════════════════════════════════════════════"
echo "  ATTACK 1 ABLATION STUDY - ALL DATASETS"
echo "════════════════════════════════════════════════════════════"
echo "Output directory: $OUTDIR"
echo "Device: $DEVICE"
echo "Features: ${FEATURES[@]}"
echo "Max layer: $MAX_LAYER"
echo ""

# ═══════════════════════════════════════════════════════════════
# NELL-995
# ═══════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────"
echo "  NELL-995"
echo "─────────────────────────────────────────────────────────────"

PUBLIC_NELL="data/processed/NELL/global_kg_public_wo_sensitive.tsv"
SENS_NELL="data/processed/NELL/sensitive/concept__teamplaysagainstteam.tsv"

if [ ! -f "$PUBLIC_NELL" ]; then
    echo "❌ Public graph not found: $PUBLIC_NELL"
    echo "   Run: python scripts/split.py first"
    exit 1
fi

if [ ! -f "$SENS_NELL" ]; then
    echo " Sensitive file not found: $SENS_NELL"
    exit 1
fi

for FEAT in "${FEATURES[@]}"; do
    echo ""
    echo "Running NELL with feature: $FEAT"
    python experiments/ablation_attack1.py \
        --public-path "$PUBLIC_NELL" \
        --sens-path "$SENS_NELL" \
        --feature-group "$FEAT" \
        --max-layer $MAX_LAYER \
        --outdir "$OUTDIR" \
        --device "$DEVICE" \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --train-neg-sample 5000 \
        --test-neg-sample 5000 \
        --hardneg-mode median_ge \
        --seed 42
done

# ═══════════════════════════════════════════════════════════════
# FB15k-237
# ═══════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "  FB15k-237"
echo "─────────────────────────────────────────────────────────────"

PUBLIC_FB="data/processed/FB15k-237/global_kg_public_wo_sensitive.tsv"
SENS_FB="data/processed/FB15k-237/sensitive/sports__sports_position__players.__sports__sports_team_roster__team.tsv"

if [ ! -f "$PUBLIC_FB" ]; then
    echo " Public graph not found: $PUBLIC_FB"
    exit 1
fi

if [ ! -f "$SENS_FB" ]; then
    echo " Sensitive file not found: $SENS_FB"
    exit 1
fi

for FEAT in "${FEATURES[@]}"; do
    echo ""
    echo "Running FB15k-237 with feature: $FEAT"
    python experiments/ablation_attack1.py \
        --public-path "$PUBLIC_FB" \
        --sens-path "$SENS_FB" \
        --feature-group "$FEAT" \
        --max-layer $MAX_LAYER \
        --outdir "$OUTDIR" \
        --device "$DEVICE" \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --train-neg-sample 5000 \
        --test-neg-sample 5000 \
        --hardneg-mode median_ge \
        --seed 42
done

# ═══════════════════════════════════════════════════════════════
# HealthKG
# ═══════════════════════════════════════════════════════════════

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "  HealthKG"
echo "─────────────────────────────────────────────────────────────"

PUBLIC_HKG="data/processed/HealthKG/global_kg_public_wo_sensitive.tsv"
SENS_HKG="data/processed/HealthKG/sensitive/has_taxonomy.tsv"

if [ ! -f "$PUBLIC_HKG" ]; then
    echo " Public graph not found: $PUBLIC_HKG"
    exit 1
fi

if [ ! -f "$SENS_HKG" ]; then
    echo " Sensitive file not found: $SENS_HKG"
    exit 1
fi

for FEAT in "${FEATURES[@]}"; do
    echo ""
    echo "Running HealthKG with feature: $FEAT"
    python experiments/ablation_attack1.py \
        --public-path "$PUBLIC_HKG" \
        --sens-path "$SENS_HKG" \
        --feature-group "$FEAT" \
        --max-layer $MAX_LAYER \
        --outdir "$OUTDIR" \
        --device "$DEVICE" \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --train-neg-sample 50000 \
        --test-neg-sample 50000 \
        --hardneg-mode median_ge \
        --seed 42
done

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

echo ""
echo "════════════════════════════════════════════════════════════"
echo "   ABLATION STUDY COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Results saved to: $OUTDIR"
echo ""
echo "Directory structure:"
echo "  $OUTDIR/"
echo "    ├── ni_head/metrics/*.json"
echo "    ├── ni_tail/metrics/*.json"
echo "    ├── Ii_head/metrics/*.json"
echo "    ├── Ei_head/metrics/*.json"
echo "    └── Ri/metrics/*.json"
echo ""
echo "To analyze results:"
echo "  python experiments/analyze_ablation.py --indir $OUTDIR"
echo ""