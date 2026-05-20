# Exposed by Design: Topology-based privacy attacks and mitigations for Knowledge Graphs

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/pytorch-2.4.1-red)](https://pytorch.org/)

This repository contains the code and resources to reproduce the main results of the paper **"Exposed by Design: Topology-based privacy attacks and mitigations for Knowledge Graphs"**.

---

## Requirements and Setup

To set up the environment and install all required libraries:

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. The main requirements include:
   - PyTorch 2.4.1
   - NetworkX 3.1
   - Scikit-learn 1.3.2
   - Pandas 2.0.3
   - NumPy 1.24.4
   - CUDA (optional, for GPU acceleration)

---

## Hardware Requirements

Our results were primarily produced using the following setup:

- NVIDIA GPU (RTX 3090 or A100, 24 GB VRAM)
- 16+ GB RAM
- 8-core CPU
- Ubuntu 20.04 or later

We have also tested the code on a smaller CPU-only setup:

- 8 GB RAM
- 4-core CPU
- Any OS with Python 3.7+

**Note:** Experiments on NELL and FB15K-237 can be run on CPU in approximately 1–2 hours. GPU acceleration is recommended for HealthKG.

---

## Data Preparation
 
We use three knowledge graphs: **NELL-995** (154K triples), **FB15k-237** (310K triples), and **HealthKG** (6M triples).
 
**See [data/README.md](data/README.md) for:**
- Download and preprocessing instructions
- Dataset statistics and characteristics
- Target relations for each attack
- Complete workflow examples

---

## Attacks
 
### Attack 1: Link Inference
Predicts if a vertex is involved in a sensitive relation using public graph topology.
 
```bash
python attacks/attack1_head.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --sens-path data/processed/NELL/sensitive/concept__teamplaysagainstteam.tsv \
  --outdir results/attack1/
```
 
### Attack 2: Triple Inference
Infers the most likely tail vertex for a confirmed head in a sensitive relation.
 
```bash
python attacks/attack2.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --sens-path data/processed/NELL/sensitive/concept__teamplaysagainstteam.tsv \
  --outdir results/attack2/
```
 
### Attack 3: Graph Reconstruction
Reconstructs sensitive subgraphs by propagating labels from seed nodes.
 
```bash
python attacks/attack3.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --sens-dir data/processed/NELL/sensitive/ \
  --outdir results/attack3/
```
 
**Batch execution:**
```bash
bash attacks/runner_attack1.sh
bash attacks/runner_attack2.sh
bash attacks/runner_attack3.sh
```
 
## Defenses
 
Three privacy-preserving mechanisms to protect against topology-based attacks.
 
### K-Anonymity
Groups entities with similar structural properties to prevent re-identification.
 
```bash
python defenses/defense_kanonymity.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --k 10 \
  --outdir results/defenses/kanon/
```
 
**Parameters:**
- `--k`: Anonymity parameter (higher = more privacy, lower utility)
### Randomized Response
Adds controlled noise to graph structure using differential privacy.
 
```bash
python defenses/defense_randomized_response.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --epsilon 1.0 \
  --outdir results/defenses/rr/
```
 
**Parameters:**
- `--epsilon`: Privacy budget (lower = more privacy, more noise)
### CHAMELEON
Adaptive defense that modifies graph structure to confuse attackers while preserving utility.
 
```bash
python defenses/chameleon_defense.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --budget 0.1 \
  --outdir results/defenses/chameleon/
```
 
**Parameters:**
- `--budget`: Modification budget (fraction of edges to modify)

**Batch execution:**
```bash
bash defenses/kanon_runner.sh
bash defenses/rr_runner.sh
bash defenses/chameleon_runner.sh
```
 
## Experiments
 
### Feature Ablation Studies
 
Evaluate the contribution of different topological features:
 
```bash
bash experiments/runner1.sh   # Attack 1 ablation
bash experiments/runner2.sh   # Attack 2 ablation
bash experiments/runner3.sh   # Attack 3 ablation
```
 
Or run individually:
```bash
python experiments/attack1_featuresstudy.py \
  --public-path data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --sens-path data/processed/NELL/sensitive/concept__teamplaysagainstteam.tsv
```
 
### Privacy-Utility Trade-off
 
Measure how defenses impact link prediction performance:
 
**Evaluation Setup:**
1. Split public graph randomly: 80% train, 20% test
2. Extract the 20% test set (same triples used for both evaluations)
3. **Baseline**: Train TransE on 80% of public graph → Test on fixed 20%
4. **Defended**: Train TransE on 80% of defended graph → Test on same fixed 20%
5. Compare Hits@10 and MRR to measure utility degradation
**Key insight:** Same test set for both models, only the training graph changes (public vs defended).
 
```bash
python experiments/utility_LinkPrediction.py \
  --baseline-graph data/processed/NELL/global_kg_public_wo_sensitive.tsv \
  --defended-graph results/defenses/kanon/defended_graph.tsv \
  --target-relation "concept:athleteplayssport" \
  --output results/utility_tradeoff.json

---

## License

This project is released under the [MIT License](LICENSE).

---

## Contact

For questions or issues related to this repository, please open a GitHub issue or contact the authors directly.

**Note:** Before running batch scripts (`runner_*.sh`), adapt the dataset paths in the scripts to match your directory structure.
 
