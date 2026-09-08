from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import copy_new, write_tsv


def prepare_gapfill_candidates(ctx: WorkflowContext) -> dict[str, int | str]:
    source = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE" / "CENTRAL_DECISION_QUEUE.tsv"
    queue = pd.read_csv(source, sep="\t", dtype=str).fillna("")
    frame = queue[queue.category.eq("GAPFILL")].copy()
    review = pd.DataFrame({
        "review_id": frame["review_id"], "target_precursor": frame["dependency"],
        "reaction_id": frame["object_id"], "equation": frame["proposed_state"],
        "source": frame["evidence_sources"], "weight": 100.0, "required_flux": "NOT_RECOMPUTED",
        "reaction_evidence": frame["evidence_summary"], "candidate_gpr": "",
        "gpr_evidence": "NO_LC1_SPECIFIC_GPR_ASSIGNED", "foreign_gpr_added": "NO",
        "manual_decision": "", "manual_notes": "",
    })
    write_tsv(pd.DataFrame(columns=["precursor", "max_flux", "producible", "status"]), ctx.root / "evidence" / "gapfill" / "MISSING_PRECURSORS.tsv")
    write_tsv(review.drop(columns=["manual_decision", "manual_notes"]), ctx.root / "evidence" / "gapfill" / "GAPFILL_CANDIDATES.tsv")
    write_tsv(review, ctx.root / "review" / "candidates" / "GAPFILL_REVIEW.tsv")
    source_model = ctx.root / "models" / "candidates" / "LC1_BIOMASS_CANDIDATE.xml"
    if not source_model.exists():
        source_model = ctx.path(ctx.project["source_model"])
    copy_new(source_model, ctx.root / "models" / "candidates" / "LC1_GAPFILL_CANDIDATE.xml")
    return {"candidate_reactions": len(review), "foreign_gpr_added": "NO", "applied_to_final": 0}
