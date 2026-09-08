from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


STANDARD_COLUMNS = ["ncbi_id", "uniprot_id", "sequence_exact", "identity", "query_coverage", "subject_coverage", "evalue", "bitscore", "rbh", "mapping_class", "confidence", "manual_review_required"]


def prepare_mapping(ctx: WorkflowContext) -> dict[str, int]:
    legacy = ctx.path(ctx.project["legacy_workflow_root"]) / "results" / "03_mapping" / "PROTEIN_MAPPING.tsv"
    source = pd.read_csv(legacy, sep="\t", dtype=str).fillna("") if legacy.exists() else pd.DataFrame()
    aliases = {
        "ncbi_id": ["ncbi_id", "HB_NCBI_protein_raw", "query_id"],
        "uniprot_id": ["uniprot_id", "HB_UniProt", "subject_id"],
        "identity": ["identity", "Identity_pct"], "query_coverage": ["query_coverage", "HB_coverage_pct"],
        "subject_coverage": ["subject_coverage", "HC_coverage_pct"], "evalue": ["evalue", "Evalue"],
        "bitscore": ["bitscore", "Bitscore"], "rbh": ["rbh", "RBH"], "mapping_class": ["mapping_class", "Mapping_status"],
        "confidence": ["confidence", "mapping_confidence"],
    }
    out = pd.DataFrame(index=source.index)
    for target in STANDARD_COLUMNS:
        selected = next((name for name in aliases.get(target, [target]) if name in source.columns), None)
        out[target] = source[selected] if selected else ""
    out["sequence_exact"] = out["mapping_class"].str.contains("EXACT", case=False, na=False).map({True: "YES", False: "NO"})
    out["manual_review_required"] = (~out["confidence"].str.upper().isin(["HIGH", "VERY_HIGH"]) | out["uniprot_id"].eq("")).map({True: "YES", False: "NO"})
    rbh = out[out["rbh"].str.upper().isin(["YES", "TRUE", "1"])].copy()
    summary = pd.DataFrame([{"records": len(out), "exact_sequence": int(out.sequence_exact.eq("YES").sum()), "rbh": len(rbh), "manual_review_required": int(out.manual_review_required.eq("YES").sum())}])
    base = ctx.root / "evidence" / "protein_mapping"
    write_tsv(out, base / "PROTEIN_CROSSWALK.tsv")
    write_tsv(rbh, base / "RBH_RESULTS.tsv")
    write_tsv(summary, base / "PROTEIN_MAPPING_SUMMARY.tsv")
    return summary.iloc[0].to_dict()
