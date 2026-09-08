from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


REVIEW_COLUMNS = ["review_id", "reaction_id", "current_gpr", "proposed_gpr", "candidate_action", "confidence", "supporting_evidence", "conflicting_evidence", "reason", "manual_decision", "manual_notes"]


def generate_reaction_gpr_candidates(ctx: WorkflowContext) -> dict[str, int]:
    source_root = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE"
    queue = pd.read_csv(source_root / "CENTRAL_DECISION_QUEUE.tsv", sep="\t", dtype=str).fillna("")
    selected = queue[queue["category"].isin(["REACTION", "GPR"])].copy()
    action_map = {"REMOVE": "REMOVE_CANDIDATE", "REVISE_GPR": "REVISE_GPR_CANDIDATE"}
    rows = []
    for row in selected.itertuples(index=False):
        action = action_map.get(str(row.recommended_action).upper(), "MANUAL_REVIEW")
        if "GPR" in str(row.category).upper() and action == "MANUAL_REVIEW":
            action = "REACTION_SUPPORTED_GPR_UNKNOWN" if not row.proposed_state else "REVISE_GPR_CANDIDATE"
        rows.append({"review_id": row.review_id, "reaction_id": row.object_id, "current_gpr": row.current_state, "proposed_gpr": row.proposed_state, "candidate_action": action, "confidence": row.confidence, "supporting_evidence": row.evidence_summary, "conflicting_evidence": row.reason if "CONFLICT" in row.confidence.upper() else "", "reason": row.reason, "manual_decision": "", "manual_notes": ""})
    frame = pd.DataFrame(rows, columns=REVIEW_COLUMNS)
    write_tsv(frame, ctx.root / "review" / "candidates" / "REACTION_GPR_REVIEW.tsv")
    return {"candidate_rows": len(frame), "automatic_model_edits": 0}
