from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import copy_new, write_tsv


EXPECTED = {"Protein": 0.55, "RNA": 0.21, "DNA": 0.031, "Residual": 0.209}


def prepare_biomass_candidate(ctx: WorkflowContext) -> dict:
    source_root = ctx.path(ctx.project["release_review_root"]) / "reconstruction" / "biomass"
    evidence_root = ctx.root / "evidence" / "biomass"
    copies = {
        "BIOMASS_PROVENANCE.tsv": "BIOMASS_COMPOSITION.tsv",
        "BIOMASS_COEFFICIENTS.tsv": "BIOMASS_COEFFICIENTS.tsv",
        "BIOMASS_MASS_AUDIT.tsv": "BIOMASS_MASS_AUDIT.tsv",
    }
    for source_name, target_name in copies.items():
        source = source_root / source_name
        if source.exists():
            copy_new(source, evidence_root / target_name)
    provenance = pd.read_csv(evidence_root / "BIOMASS_COMPOSITION.tsv", sep="\t", dtype=str).fillna("")
    text = provenance.astype(str).to_string(index=False)
    checks = {name: (name in text and f"{value}" in text) for name, value in EXPECTED.items()}
    report = ctx.path(ctx.project["release_review_root"]) / "reconstruction" / "biomass" / "BIOMASS_V2_2_SAME_COMPONENTS_REPORT.md"
    report_text = report.read_text(encoding="utf-8", errors="replace") if report.exists() else ""
    checks.update({"GAM_53.95": "53.95" in report_text, "structural_mass_1.0": "1.0" in report_text or "1.000" in report_text})
    status = "PASS_REUSED_V2_2" if all(checks.values()) else "REVIEW_REQUIRED"
    source_model = ctx.path(ctx.project["source_model"])
    candidate = ctx.root / "models" / "candidates" / "LC1_BIOMASS_CANDIDATE.xml"
    copy_new(source_model, candidate)
    review_source = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE" / "CENTRAL_DECISION_QUEUE.tsv"
    queue = pd.read_csv(review_source, sep="\t", dtype=str).fillna("")
    review = queue[queue.category.eq("BIOMASS")].copy()
    review["component"] = review["object_id"]
    review["current_value"] = review["current_state"]
    review["estimated_value"] = review["proposed_state"]
    review["source"] = review["evidence_sources"]
    review["manual_decision"] = ""
    review["manual_notes"] = ""
    write_tsv(review, ctx.root / "review" / "candidates" / "BIOMASS_REVIEW.tsv")
    return {"status": status, "checks": checks, "model_biology_changed": False}
