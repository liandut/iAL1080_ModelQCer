from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import nbformat
import pandas as pd
from cobra.io import read_sbml_model

from .config import WorkflowContext
from .io_utils import copy_new, sha256, write_tsv


def finalize_release_candidate(ctx: WorkflowContext) -> dict[str, str | int]:
    decisions = ctx.root / "review" / "HUMAN_REVIEW_PACKAGE.tsv"
    decision_frame = pd.read_csv(decisions, sep="\t", dtype=str).fillna("")
    incomplete = int(decision_frame.manual_decision.isin(["", "DEFER", "UNRESOLVED"]).sum())
    regression_path = ctx.root / "qc" / "regression" / "REGRESSION_RESULTS.tsv"
    regression = pd.read_csv(regression_path, sep="\t", dtype=str).fillna("") if regression_path.exists() else pd.DataFrame()
    regression_fail = regression.empty or regression.status.eq("FAIL").any()
    reviewed = ctx.root / "models" / "reviewed" / "LC1_REVIEWED_MODEL.xml"
    memote = next((ctx.root / "qc" / "memote").glob("*.html"), None)
    if incomplete or regression_fail or not reviewed.exists() or memote is None:
        return {"status": "RELEASE_GATE_FAIL", "incomplete_decisions": incomplete, "regression_fail": int(regression_fail)}
    model = read_sbml_model(str(reviewed))
    objective = [r.id for r in model.reactions if abs(r.objective_coefficient) > 0]
    if not objective:
        return {"status": "RELEASE_GATE_FAIL_NO_OBJECTIVE", "incomplete_decisions": incomplete}
    destination = ctx.root / "models" / "final" / "iAL1080_RELEASE_CANDIDATE.xml"
    copy_new(reviewed, destination)
    manifest = pd.DataFrame([{
        "model_file": destination.name, "model_id": ctx.project["final_model_id"], "organism": ctx.project["organism"],
        "taxonomy": ctx.project["taxonomy_id"], "genes": len(model.genes), "reactions": len(model.reactions),
        "metabolites": len(model.metabolites), "objective": ";".join(objective), "biomass_reaction": ctx.project["biomass_reaction"],
        "phb_reaction": ctx.project["phb_reaction"], "sha256": sha256(destination), "workflow_version": ctx.project["workflow_version"],
        "date": date.today().isoformat(), "regression_status": "PASS_WITH_WARNINGS" if regression.status.eq("PASS_WITH_WARNINGS").any() else "PASS",
        "memote_report": memote.relative_to(ctx.root).as_posix(), "manual_review_package": "review/HUMAN_REVIEW_PACKAGE.tsv",
        "decision_file": "review/decisions/APPROVED_DECISIONS.tsv",
    }])
    write_tsv(manifest, ctx.root / "models" / "final" / "MODEL_RELEASE_MANIFEST.tsv")
    return {"status": "RELEASE_CANDIDATE_CREATED", "output": destination.as_posix(), "incomplete_decisions": 0}


def export_github_review(ctx: WorkflowContext) -> dict[str, str | int]:
    destination = ctx.path(ctx.project["github_export"])
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for relative in ("README.md", "requirements.txt", "environment.yml", "run_all.py", "workflow_manifest.tsv"):
        target = destination / relative
        if not target.exists():
            shutil.copy2(ctx.root / relative, target)
            copied += 1
    for folder in ("config", "src"):
        target = destination / folder
        target.mkdir(exist_ok=True)
        for source in (ctx.root / folder).glob("*"):
            if source.is_file() and source.suffix != ".pyc":
                shutil.copy2(source, target / source.name)
                copied += 1
    notebooks_out = destination / "notebooks"
    notebooks_out.mkdir(exist_ok=True)
    for source in sorted((ctx.root / "notebooks").glob("*.ipynb")):
        nb = nbformat.read(source, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        nbformat.write(nb, notebooks_out / source.name)
        copied += 1
    selections = [
        "models/final/iAL1080_RELEASE_CANDIDATE.xml", "models/final/MODEL_RELEASE_MANIFEST.tsv",
        "review/README.md", "review/HUMAN_REVIEW_PACKAGE.tsv", "review/decisions/DECISION_APPLICATION_LOG.tsv",
        "evidence/protein_mapping/PROTEIN_MAPPING_SUMMARY.tsv",
        "evidence/biomass/BIOMASS_MASS_AUDIT.tsv", "evidence/gapfill/GAPFILL_CANDIDATES.tsv",
        "qc/regression/REGRESSION_RESULTS.tsv", "validation/carbon_sources/CARBON_PHENOTYPE_RESULTS.tsv",
        "validation/essentiality/ESSENTIAL_GENES.tsv", "reports/FRAMEWORK_BUILD_REPORT.md", "reports/NOTEBOOK_IO_MAP.tsv",
        "reports/figures/HB_GEM_HUMAN_IN_LOOP_WORKFLOW.png",
    ]
    for relative in selections:
        source = ctx.root / relative
        if source.exists():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied += 1
    return {"status": "EXPORTED", "files_copied": copied, "destination": destination.as_posix()}
