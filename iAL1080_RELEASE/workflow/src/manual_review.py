from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from .config import WorkflowContext
from .io_utils import write_tsv


UNIFIED_COLUMNS = ["review_id", "module", "entity_id", "current_state", "candidate_state", "candidate_action", "evidence_summary", "confidence", "manual_decision", "manual_value", "manual_notes", "reviewer", "review_date"]
ALLOWED = {"APPROVE", "REJECT", "REVISE", "DEFER", "UNRESOLVED"}


def _value(frame: pd.DataFrame, choices: list[str]) -> pd.Series:
    for name in choices:
        if name in frame.columns:
            return frame[name].astype(str)
    return pd.Series([""] * len(frame), index=frame.index, dtype=str)


def _normalize(path: Path, module: str) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t", dtype=str).fillna("")
    return pd.DataFrame({
        "review_id": _value(frame, ["review_id"]), "module": module,
        "entity_id": _value(frame, ["reaction_id", "component", "entity_id", "object_id"]),
        "current_state": _value(frame, ["current_state", "current_gpr", "current_value"]),
        "candidate_state": _value(frame, ["candidate_state", "proposed_gpr", "estimated_value", "equation"]),
        "candidate_action": _value(frame, ["candidate_action", "recommendation"]),
        "evidence_summary": _value(frame, ["supporting_evidence", "evidence_summary", "reaction_evidence", "source"]),
        "confidence": _value(frame, ["confidence"]), "manual_decision": "", "manual_value": "",
        "manual_notes": "", "reviewer": "", "review_date": "",
    })


def build_review_package(ctx: WorkflowContext) -> dict[str, int | str]:
    candidates = ctx.root / "review" / "candidates"
    specs = [
        ("REACTION_GPR_REVIEW.tsv", "Reaction_GPR"), ("BIOMASS_REVIEW.tsv", "Biomass"),
        ("GAPFILL_REVIEW.tsv", "Gapfill"), ("DIRECTION_REVIEW.tsv", "Direction"),
        ("TRANSPORT_EXCHANGE_REVIEW.tsv", "Transport_Exchange"), ("QC_FLAG_REVIEW.tsv", "QC_Flags"),
    ]
    frames = [_normalize(candidates / name, module) for name, module in specs if (candidates / name).exists()]
    package = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=UNIFIED_COLUMNS)
    duplicates = package.review_id[package.review_id.duplicated()].tolist() if not package.empty else []
    if duplicates:
        raise ValueError(f"Duplicate review IDs: {duplicates[:10]}")
    tsv = ctx.root / "review" / "HUMAN_REVIEW_PACKAGE.tsv"
    write_tsv(package[UNIFIED_COLUMNS], tsv)
    source_workbook = ctx.path(ctx.project["legacy_workflow_root"]) / "FINAL_REVIEW_PACKAGE" / "HB_FINAL_REVIEW.xlsx"
    target_workbook = ctx.root / "review" / "HUMAN_REVIEW_PACKAGE.xlsx"
    workbook_status = "NOT_AVAILABLE"
    if source_workbook.exists():
        if not target_workbook.exists():
            shutil.copy2(source_workbook, target_workbook)
        workbook_status = "REUSED_EXISTING_RICH_REVIEW_WORKBOOK"
    return {"review_rows": len(package), "workbook_status": workbook_status, "automatic_decisions": 0}


def import_decisions(ctx: WorkflowContext) -> dict[str, int]:
    package_path = ctx.root / "review" / "HUMAN_REVIEW_PACKAGE.tsv"
    frame = pd.read_csv(package_path, sep="\t", dtype=str).fillna("")
    if frame.review_id.duplicated().any():
        raise ValueError("Duplicate review_id")
    invalid = sorted(set(frame.manual_decision) - ALLOWED - {""})
    if invalid:
        raise ValueError(f"Invalid decisions: {invalid}")
    revise_without_value = frame.manual_decision.eq("REVISE") & frame.manual_value.eq("")
    if revise_without_value.any():
        raise ValueError("REVISE requires manual_value")
    decisions = ctx.root / "review" / "decisions"
    approved = frame[frame.manual_decision.isin(["APPROVE", "REVISE"])].copy()
    rejected = frame[frame.manual_decision.eq("REJECT")].copy()
    deferred = frame[frame.manual_decision.isin(["DEFER", "UNRESOLVED", ""])].copy()
    write_tsv(approved, decisions / "APPROVED_DECISIONS.tsv")
    write_tsv(rejected, decisions / "REJECTED_DECISIONS.tsv")
    write_tsv(deferred, decisions / "DEFERRED_DECISIONS.tsv")
    report = ["# Decision validation report", "", f"- Total rows: {len(frame)}", f"- Approved/revised: {len(approved)}", f"- Rejected: {len(rejected)}", f"- Deferred/unresolved/blank: {len(deferred)}", "- Model modified: NO", "- Status: PASS"]
    (decisions / "DECISION_VALIDATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"approved": len(approved), "rejected": len(rejected), "deferred": len(deferred)}
