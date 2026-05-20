# Knowledge graphs

## Quick Start
 
```bash
cd data
 
# NELL + FB15k-237
pip install datasets
python download_datasets.py --all
python merge_files.py --all
 
# HealthKG
pip install rdflib
python preprocess_healthkg.py --download
 
# Validate
python validate_data.py --all
```
 
## Datasets
 
| Dataset | Entities | Relations | Triples | Domain |
|---------|----------|-----------|---------|--------|
| NELL-995 | 75K | 200 | 154K | General |
| FB15k-237 | 15K | 237 | 310K | Facts |
| HealthKG | 950K | 37 | 6M | Medical |
 
### Target Relations for Attacks
 
**NELL-995:**
- Attack 1 (Link Inference): `concept:teamplaysagainstteam`
- Attack 3 (Graph Reconstruction): `concept:atlocation`, `concept:proxyfor`, `concept:subpartof`, `concept:teamplaysagainstteam`
- Utility (Link Prediction): `concept:athleteplayssport`  

**FB15k-237:**
- Attack 1: `/sports/sports_position/players./sports/sports_team_roster/team`
- Attack 3: `/education/educational_institution/students_graduates./education/education/student`, `/film/film/genre`, `/people/person/profession`, `/sports/sports_position/players./sports/sports_team_roster/team`
- Utility: `/people/person/nationality`   

**HealthKG:**
- Attack 1: `has_taxonomy`
- Attack 3: `has_age_category`, `has_age_living_apart`, `has_family_ID`, `has_gender`, `has_is_westernized`, `has_is-from`, `has_zygosity`
- Utility: `has_age_category`
## Scripts
 
**`download_datasets.py`** - Downloads NELL + FB15k-237
```bash
python download_datasets.py --all
```
 
**`merge_kg_files.py`** - Merges splits, cleans NELL URIs
```bash
python merge_kg_files.py --all
```
 
**`preprocess_healthkg.py`** - Downloads & processes HealthKG, anonymizes persons
```bash
python preprocess_healthkg.py --download
```
 
**`validate_data.py`** - Validates datasets
```bash
python validate_data.py --all
```
 
## Output
 
```
data/raw/
├── NELL/full_kg.tsv         # 154K triples
├── FB15k-237/full_kg.tsv    # 310K triples
└── HealthKG/full_kg.tsv     # 6M triples
```
 
All files are tab-separated: `head \t relation \t tail`
 
## Workflow
 
1. Run scripts above
2. Use `split.py` for your experiments:

```bash
python ../scripts/split.py \
  --global_path raw/NELL/full_kg.tsv \
  --relation "concept:teamplaysagainstteam" \
  --outdir public/NELL/
```
 
**What it does:**
- Reads the full knowledge graph
- Separates triples by relation:
  - **Sensitive**: Relations you specify → saved in `sensitive/` directory
  - **Public**: Everything else → `global_kg_public_wo_sensitive.tsv`
**Output structure:**
```
public/NELL/
├── global_kg_public_wo_sensitive.tsv    # All triples except sensitive ones
├── sensitive/
│   └── concept__teamplaysagainstteam.tsv  # Only this relation
└── split_report_multi.txt               # Statistics report
```
 
**Multiple relations (for Attack 3):**
```bash
python ../scripts/split.py \
  --global_path raw/NELL/full_kg.tsv \
  --relation "concept:atlocation" \
  --relation "concept:proxyfor" \
  --relation "concept:subpartof" \
  --outdir public/NELL/
```
 
This creates separate files for each relation in `sensitive/`.
 

 
## Troubleshooting
 
**NELL URIs not cleaned?**
```bash
python merge_files.py --dataset NELL
```
 
**HealthKG download fails?**
```bash
git clone https://github.com/Boreico/KGE_QCB_Project.git
python preprocess_healthkg.py --input "KGE_QCB_Project/Phase 5 - Entity Definition/"
```
 
**Missing dependencies?**
```bash
pip install datasets rdflib
```
 
## Sources
 
- NELL-995: [HuggingFace](https://huggingface.co/datasets/CleverThis/nell-995)
- FB15k-237: [Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=52312)
- HealthKG: [GitHub](https://github.com/Boreico/KGE_QCB_Project)
 
