from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


def generate_transport_review(ctx: WorkflowContext) -> dict[str, int]:
    source = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE" / "CENTRAL_DECISION_QUEUE.tsv"
    queue = pd.read_csv(source, sep="\t", dtype=str).fillna("")
    frame = queue[queue.category.isin(["TRANSPORT", "EXCHANGE"])].copy()
    out = pd.DataFrame({
        "review_id": frame["review_id"], "reaction_id": frame["object_id"], "current_state": frame["current_state"],
        "candidate_state": frame["proposed_state"], "candidate_action": "TRANSPORT_REVIEW",
        "evidence_summary": frame["evidence_summary"],
        "confidence": frame["confidence"], "manual_decision": "", "manual_notes": "",
    })
    write_tsv(out, ctx.root / "review" / "candidates" / "TRANSPORT_EXCHANGE_REVIEW.tsv")
    return {"review_rows": len(out)}
