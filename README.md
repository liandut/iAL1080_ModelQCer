# iAL1080

Repository-ready release package for the genome-scale metabolic model of *Vreelandella boliviensis* LC1.

| Field | Value |
|---|---|
| Model | iAL1080 |
| Organism | *Vreelandella boliviensis* LC1 |
| NCBI Taxonomy | 1072583 |
| SBML geneProducts | 1080 |
| Biological loci | 1079 |
| Non-biological placeholder | 1 |
| Reactions | 2377 |
| Metabolites | 1662 |
| Exchanges | 235 |
| Transport reactions | 716 |
| MEMOTE | 93.045301% |
| Model SHA256 | `42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d` |

The iAL1080 identifier is retained as the model name and should not be interpreted as the exact number of biological loci.

The canonical model is `model/iAL1080.xml`; the SHA-bound existing MEMOTE snapshot is in `memote/`. COBRApy-compatible JSON, YAML, and MATLAB serializations are provided as `model/iAL1080.json`, `model/iAL1080.yaml`, and `model/iAL1080.mat`. They are generated directly from the canonical SBML file by `scripts/export_model_formats.py`, which reloads every format and verifies identifiers, bounds, stoichiometry, and objective coefficients. Final figure source tables and publication figures are in `source_data/` and `figures/`. Supplementary Figures S1–S4, their source tables, and portable plotting scripts are grouped under `figures/supplementary/`, `source_data/supplementary/`, and `scripts/supplementary/`. Journal-submission Word files, laboratory workspace outputs, and machine-specific provenance scripts are intentionally excluded from this public code/data release.

## Model formats

| Format | File | COBRApy loader |
|---|---|---|
| SBML Level 3 FBC | `model/iAL1080.xml` | `cobra.io.read_sbml_model` |
| JSON | `model/iAL1080.json` | `cobra.io.load_json_model` |
| YAML | `model/iAL1080.yaml` | `cobra.io.load_yaml_model` |
| MATLAB | `model/iAL1080.mat` | `cobra.io.load_matlab_model` |

The SBML file remains authoritative. Regenerate and verify the alternative formats with `python scripts/export_model_formats.py`.

All 30 retained publication source-data TSV files under `source_data/` are used by a final main figure, a final supplementary figure/table, or a directly relevant figure provenance audit. No raw laboratory workspace, temporary output, internal assistant report, or historical model copy is included.

## Supplementary figures and data

The public Supplementary package contains the seven final raster panels for Figures S1–S4, the complete plotting inputs, Table S1 source data, and the compact GAM/O2 source and audit tables required to trace the displayed panels. Existing canonical files are reused without duplicate copies: Figure S1 uses `source_data/S1_FINAL_SOURCE.tsv`, Figure S2 uses `source_data/HB_N_SCAN_QGLC2p8_ROUND2.tsv`, and Table S1 uses `source_data/PHB_SUPP_TABLE_S1_FINAL.tsv`. Figure S4A intentionally omits `R_GLCDpp` and `R_EX_glcn_e` from the displayed heatmap because both are numerical zero in the plotted states; the full flux source and gluconate FVA table remain public for auditability. Run `python scripts/supplementary/plot_all_supplementary_panels.py` from any location to reproduce the panel-wise plots.

## Reconstruction workflow

The complete human-in-the-loop reconstruction framework is provided in [`workflow/`](workflow/README.md). It contains 16 ordered notebooks covering the registered CarveMe draft, identifier and protein mapping, evidence integration, reaction/GPR review, Biomass reconstruction, weighted precursor gap filling, direction/transport/exchange QC, manual expert adjudication, regression/MEMOTE gates, phenotype validation, and controlled release export. The workflow uses paths relative to the repository and never overwrites the canonical model in `model/iAL1080.xml`.

Public repository status: **REPOSITORY_URL_REQUIRED_FROM_USER**. No repository URL or DOI has been fabricated. Author list, version, and release date require confirmation before publication.
