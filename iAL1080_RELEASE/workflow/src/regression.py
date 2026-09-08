from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
from cobra.io import read_sbml_model

from .config import WorkflowContext
from .io_utils import sha256, write_tsv
from .qc import structural_flags


def _optimize(model, objective: str) -> tuple[str, float]:
    model.objective = objective
    solution = model.optimize()
    return solution.status, float(solution.objective_value or 0.0)


def run_regression(ctx: WorkflowContext) -> dict[str, str | float]:
    reviewed = ctx.root / "models" / "reviewed" / "LC1_REVIEWED_MODEL.xml"
    if not reviewed.exists():
        raise FileNotFoundError("Reviewed model missing; run notebook 11 after manual review")
    model = read_sbml_model(str(reviewed))
    model.solver = ctx.project.get("solver", "glpk")
    biomass = ctx.project["biomass_reaction"]
    rows = []
    status, growth = _optimize(model, biomass)
    rows.append({"gate": "SBML_LOAD_AND_OBJECTIVE", "value": f"{status}; growth={growth:.12g}", "status": "PASS" if status == "optimal" else "FAIL"})
    medium_path = ctx.path(ctx.media["source"])
    medium = pd.read_csv(medium_path, sep="\t")
    with model:
        for reaction in model.exchanges:
            reaction.lower_bound = max(0.0, reaction.lower_bound)
        for row in medium.itertuples(index=False):
            if row.exchange_id in model.reactions:
                model.reactions.get_by_id(row.exchange_id).bounds = (float(row.lower_bound), float(row.upper_bound))
        m_status, m_growth = _optimize(model, biomass)
    rows.append({"gate": "GLUCOSE_MINIMAL_GROWTH", "value": m_growth, "status": "PASS" if m_status == "optimal" and m_growth > 1e-8 else "FAIL"})
    for label, exchange in (("NO_CARBON", "EX_glc__D_e"), ("NO_N", "EX_nh4_e"), ("NO_P", "EX_pi_e"), ("NO_S", "EX_so4_e")):
        with model:
            if exchange in model.reactions:
                model.reactions.get_by_id(exchange).lower_bound = 0
            _, value = _optimize(model, biomass)
        rows.append({"gate": label, "value": value, "status": "PASS" if value <= 1e-8 else "FAIL"})
    with model:
        for reaction in model.exchanges:
            reaction.lower_bound = 0
        atpm = ctx.media.get("closed_system_atpm", "ATPM")
        _, atpm_value = _optimize(model, atpm) if atpm in model.reactions else ("missing", float("nan"))
    rows.append({"gate": "CLOSED_ATPM", "value": atpm_value, "status": "PASS" if abs(atpm_value) <= 1e-8 else "FAIL"})
    flags = structural_flags(reviewed, ctx.root / "qc")
    rows.append({"gate": "STRUCTURAL_FLAGS_GENERATED", "value": str(flags), "status": "PASS_WITH_WARNINGS"})
    source = ctx.path(ctx.project["source_model"])
    memote_source = ctx.path(ctx.project["release_review_root"]) / "reports" / "memote" / "iAL1080_MEMOTE_FINAL.html"
    memote_status = "MEMOTE_REQUIRED"
    if source.exists() and sha256(source) == sha256(reviewed) and memote_source.exists():
        target = ctx.root / "qc" / "memote" / "iAL1080_MEMOTE_FINAL.html"
        if not target.exists():
            shutil.copy2(memote_source, target)
        memote_status = "REUSED_EXACT_SHA_MATCHED_REPORT"
    rows.append({"gate": "MEMOTE", "value": memote_status, "status": "PASS" if memote_status.startswith("REUSED") else "FAIL"})
    result = pd.DataFrame(rows)
    write_tsv(result, ctx.root / "qc" / "regression" / "REGRESSION_RESULTS.tsv")
    final_status = "FAIL" if result.status.eq("FAIL").any() else ("PASS_WITH_WARNINGS" if result.status.eq("PASS_WITH_WARNINGS").any() else "PASS")
    return {"regression_status": final_status, "default_growth": growth, "minimal_growth": m_growth, "memote": memote_status}
