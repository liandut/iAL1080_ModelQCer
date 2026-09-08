from __future__ import annotations

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


def integrate_existing_evidence(ctx: WorkflowContext) -> dict[str, int]:
    base = ctx.path(ctx.project["legacy_workflow_root"]) / "results" / "04_evidence"
    results = {}
    for name in ("GENE_EVIDENCE.tsv", "REACTION_EVIDENCE.tsv"):
        source = base / name
        frame = pd.read_csv(source, sep="\t", dtype=str).fillna("") if source.exists() else pd.DataFrame()
        for column in frame.columns:
            frame[column] = frame[column].astype(str).str.replace(r"[A-Za-z]:\\[^\t;]+", "EXTERNAL_PROJECT_ASSET", regex=True)
        write_tsv(frame, ctx.root / "evidence" / name)
        results[name] = len(frame)
    return results
