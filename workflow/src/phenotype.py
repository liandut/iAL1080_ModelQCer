from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


def prepare_phenotype_results(ctx: WorkflowContext) -> dict[str, int]:
    legacy = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE"
    phenotype_path = legacy / "PHENOTYPE_REPORT.tsv"
    phenotype = pd.read_csv(phenotype_path, sep="\t", dtype=str).fillna("") if phenotype_path.exists() else pd.DataFrame()
    expected = ["carbon_source", "experimental_state", "evidence_source", "model_prediction", "growth_rate", "TP/TN/FP/FN", "notes"]
    out = pd.DataFrame(columns=expected)
    for column in expected:
        if column in phenotype.columns:
            out[column] = phenotype[column]
    if out.empty and not phenotype.empty:
        out = phenotype.copy()
        for column in expected:
            if column not in out.columns:
                out[column] = ""
        out = out[expected]
    write_tsv(out, ctx.root / "validation" / "carbon_sources" / "CARBON_PHENOTYPE_RESULTS.tsv")
    essential_source = ctx.path(ctx.project["release_review_root"]) / "analysis" / "essentiality" / "HB_FINAL_ESSENTIAL_GENES.tsv"
    essential = pd.read_csv(essential_source, sep="\t", dtype=str).fillna("") if essential_source.exists() else pd.DataFrame()
    write_tsv(essential, ctx.root / "validation" / "essentiality" / "ESSENTIAL_GENES.tsv")
    return {"carbon_rows": len(out), "essential_gene_rows": len(essential), "mixed_substrate_as_negative": 0}
