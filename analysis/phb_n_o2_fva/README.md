# iAL1080 N–O2 phase-plane and FVA analysis

## Purpose

This directory contains the numerical source data and reproducible Python code for the N–O2 phase-plane and flux variability analysis (FVA) used in the manuscript.

## Main analyses

- N–O2 maximum-growth-capacity phase plane.
- N–O2 maximum-PHB-storage-capacity phase plane.
- FVA comparison of defined growth-dominant and dual-limitation storage states.

## Important interpretation

- Phase-plane PHB calculations use a relative residual-growth constraint (`alpha = 0.1`) based on the condition-specific maximum growth rate.
- The `N = 0.5 qN,ref` and `O2 = 0.25 qO2,ref` coordinate is one predefined combined condition, not a data-fitted global optimum.
- The near-zero instantaneous PHB difference between the combined and N-only states at this coordinate is not a statement about the entire N–O2 plane.
- FVA compares two author-defined feasible regions. Non-overlapping intervals indicate a constraint-robust shift across alternative feasible optima under those definitions.
- These results are model-derived feasible flux ranges, not direct experimental flux measurements and not an independent mechanism discovery.
- PDH and ACACT1r have overlapping FVA intervals and therefore are retained only in the cross-check table, not presented as required shifts.

## Reproduction

```bash
pip install numpy pandas matplotlib scipy
python analysis/phb_n_o2_fva/scripts/run_fva_phaseplane_figures.py
```

The script validates all four source tables and writes three independent figures to `figures/`, each as a 600-dpi PNG, PDF, and SVG. No combined canvas is generated, so the panels can be assembled during manuscript layout.

## Model version

- Canonical model: `../../model/iAL1080.xml`
- Model SHA256: `42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d`
- Model repository commit available before this analysis package: `3fa8b3d63e6c9507c7337f62b2ee26a78386c644`
- Repository: <https://github.com/liandut/iAL1080_ModelQCer>

The model is referenced from the repository root and is not duplicated in this analysis directory.

## Directory contents

```text
phb_n_o2_fva/
├── data/          # four machine-readable source tables
├── figures/       # three standalone figures, each in PNG/PDF/SVG
├── scripts/       # validated Python reproducer
├── notebooks/     # clean notebook using the same CSV files
├── README.md
├── METHODS_AND_ASSUMPTIONS.md
└── FILE_MANIFEST.tsv
```
