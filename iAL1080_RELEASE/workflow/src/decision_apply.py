from __future__ import annotations

import re

import pandas as pd
from cobra.io import read_sbml_model, write_sbml_model

from .config import WorkflowContext
from .io_utils import write_tsv


def _reaction_id(row: pd.Series) -> str:
    return str(row.get("entity_id", "")).strip()


def apply_approved_decisions(ctx: WorkflowContext) -> dict[str, int | str]:
    source = ctx.root / "models" / "candidates" / "LC1_GAPFILL_CANDIDATE.xml"
    if not source.exists():
        source = ctx.path(ctx.project["source_model"])
    decisions_path = ctx.root / "review" / "decisions" / "APPROVED_DECISIONS.tsv"
    decisions = pd.read_csv(decisions_path, sep="\t", dtype=str).fillna("") if decisions_path.exists() else pd.DataFrame()
    model = read_sbml_model(str(source))
    logs = []
    for _, row in decisions.iterrows():
        rid = _reaction_id(row)
        if not rid or rid not in model.reactions:
            raise ValueError(f"Unknown reaction for {row.review_id}: {rid}")
        reaction = model.reactions.get_by_id(rid)
        before = {"gpr": reaction.gene_reaction_rule, "bounds": list(reaction.bounds), "present": True}
        value = str(row.manual_value or row.candidate_state).strip()
        action = str(row.candidate_action).upper()
        if row.manual_decision == "REVISE" and re.fullmatch(r"-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?", value):
            lower, upper = (float(x.strip()) for x in value.split(","))
            if lower > upper:
                raise ValueError(f"Invalid bounds for {rid}: {value}")
            reaction.bounds = (lower, upper)
        elif value.upper() == "REMOVE" or "REMOVE_CANDIDATE" in action:
            model.remove_reactions([reaction], remove_orphans=False)
        elif "GPR" in action or row.module == "Reaction_GPR":
            if row.manual_decision == "REVISE":
                reaction.gene_reaction_rule = value
        after = {"gpr": reaction.gene_reaction_rule, "bounds": list(reaction.bounds), "present": rid in model.reactions} if rid in model.reactions else {"present": False}
        logs.append({"review_id": row.review_id, "entity_id": rid, "decision": row.manual_decision, "reviewer": row.reviewer, "before": str(before), "after": str(after), "evidence": row.evidence_summary})
    destination = ctx.root / "models" / "reviewed" / "LC1_REVIEWED_MODEL.xml"
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    write_sbml_model(model, str(destination))
    read_sbml_model(str(destination))
    write_tsv(logs, ctx.root / "review" / "decisions" / "DECISION_APPLICATION_LOG.tsv")
    return {"applied": len(logs), "output": destination.as_posix(), "atomic_write": "PASS"}
