from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


def generate_direction_qc_review(ctx: WorkflowContext) -> dict[str, int]:
    source_root = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE"
    queue = pd.read_csv(source_root / "CENTRAL_DECISION_QUEUE.tsv", sep="\t", dtype=str).fillna("")
    direction = queue[queue.category.eq("DIRECTION_CHEMISTRY")].copy()
    d = pd.DataFrame({
        "review_id": direction["review_id"], "reaction_id": direction["object_id"], "current_state": direction["current_state"],
        "candidate_state": direction["proposed_state"], "candidate_action": "DIRECTION_REVIEW",
        "evidence_summary": direction["evidence_summary"], "confidence": direction["confidence"],
        "manual_decision": "", "manual_notes": "",
    })
    write_tsv(d, ctx.root / "review" / "candidates" / "DIRECTION_REVIEW.tsv")
    q = pd.DataFrame(columns=["review_id", "entity_id", "flag", "candidate_action", "evidence_summary", "confidence", "manual_decision", "manual_notes"])
    write_tsv(q, ctx.root / "review" / "candidates" / "QC_FLAG_REVIEW.tsv")
    return {"direction_rows": len(d), "qc_flag_rows": len(q)}
