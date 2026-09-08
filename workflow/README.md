# iAL1080 reconstruction workflow

This folder provides the documented, human-in-the-loop workflow used to organize the reconstruction and curation of the *Vreelandella boliviensis* LC1 genome-scale metabolic model. It starts from the bundled CarveMe draft snapshot and ends at controlled QC, phenotype-validation, and release gates. It does not modify the canonical release model at `../model/iAL1080.xml`.

## Workflow stages

1. Project and software setup.
2. Genome/proteome registration and identifier mapping.
3. Registration of the CarveMe draft GEM.
4. Gene and reaction evidence integration.
5. Reaction and GPR candidate curation.
6. Biomass composition reconstruction and mass audit.
7. Evidence-weighted biomass-precursor gap-fill candidate generation.
8. Direction, transport, exchange, and structural QC review.
9. Generation of the manual-review package.
10. Import of explicit expert decisions.
11. Atomic application of approved decisions.
12. Regression, mass/charge, blocked-reaction, energy, and MEMOTE gates.
13. Phenotype validation.
14. Release-candidate finalization.
15. Reproducibility-package export.

The exact notebook sequence and input/output contracts are listed in `workflow_manifest.tsv` and `reports/NOTEBOOK_IO_MAP.tsv`.

## Directory guide

- `notebooks/`: 16 ordered notebooks, `00` through `15`.
- `src/`: reusable workflow functions called by the notebooks.
- `config/`: project, threshold, and medium configuration.
- `models/draft/LC1_DRAFT.xml`: registered CarveMe draft snapshot.
- `legacy_assets/`: frozen LC1 mapping, evidence, phenotype, and review inputs used by the historical reconstruction.
- `release_assets/`: frozen Biomass, essentiality, and MEMOTE evidence used by the release gates.
- `evidence/`: compact evidence and audit tables distributed with the original framework.
- `review/`: canonical machine-readable human-review table and instructions.
- `reports/`: notebook I/O map, workflow summary, and workflow diagram.

Intermediate Biomass and gap-fill candidate XML files are intentionally not distributed because they are duplicate generated checkpoints. The notebooks create them under `models/candidates/` when the workflow is run.

## Run to the manual-review gate

Create the environment:

```bash
conda env create -f environment.yml
conda activate hb-gem-reconstruction
```

Run automated preparation through notebook 09:

```bash
python run_all.py --until manual_review
```

Review the canonical `review/HUMAN_REVIEW_PACKAGE.tsv`. Record only explicit `APPROVE`, `REJECT`, `REVISE`, `DEFER`, or `UNRESOLVED` decisions. Blank or unresolved decisions are never applied. The optional historical XLSX review workbook is not distributed because it contained a private machine path; the TSV contains the complete machine-readable review interface.

Resume only after expert review:

```bash
python run_all.py --resume
```

## Important scope notes

- This package registers the supplied CarveMe draft; it does not rerun the external CarveMe command.
- The included evidence files are frozen LC1 reconstruction inputs, not universal annotations for other organisms.
- Candidate generation is not equivalent to biological approval.
- No donor-model or universal-database GPR is transferred automatically.
- GPR-less and blocked reactions are not deleted automatically.
- The final model is written only after decision, objective, regression, energy, provenance, and MEMOTE gates pass.
- The canonical public model remains `../model/iAL1080.xml`, SHA256 `42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d`.
