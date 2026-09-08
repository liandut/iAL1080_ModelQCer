from __future__ import annotations

from .config import WorkflowContext
from .io_utils import copy_new
from .qc import model_statistics


def register_draft(ctx: WorkflowContext) -> dict:
    source = ctx.path(ctx.project["draft_model"])
    if source is None or not source.exists():
        return {"status": "DRAFT_INPUT_REQUIRED"}
    destination = ctx.root / "models" / "draft" / "LC1_DRAFT.xml"
    copy_new(source, destination)
    stats = model_statistics(destination, ctx.root / "reports" / "03_draft_statistics.tsv")
    return {"status": "REGISTERED_EXISTING_DRAFT", **stats.iloc[0].to_dict()}
