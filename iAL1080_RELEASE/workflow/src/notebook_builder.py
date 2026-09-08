from __future__ import annotations

from pathlib import Path

import nbformat as nbf
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SETUP = """from pathlib import Path
import sys

ROOT = Path.cwd().resolve()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import load_context
ctx = load_context(ROOT)
"""

SPECS = [
    ("00_project_setup.ipynb", "Project setup and environment", "config/project.yaml; requirements.txt", "reports/00_environment_report.md; workflow_manifest.tsv", False, False, True,
     """import importlib.metadata as md
import platform, shutil, subprocess
from src.io_utils import ensure_directories, now_iso

ensure_directories(ctx.root)
packages = ['cobra', 'pandas', 'scipy', 'lxml', 'openpyxl', 'nbformat', 'nbclient']
versions = {name: (md.version(name) if name in {d.metadata['Name'].lower() for d in md.distributions() if d.metadata.get('Name')} else 'NOT_FOUND') for name in packages}
tools = {name: ('FOUND' if shutil.which(name) else 'NOT_FOUND') for name in ['diamond', 'memote', 'git']}
git_commit = 'NOT_A_GIT_REPOSITORY'
if (ctx.root / '.git').exists():
    git_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ctx.root, capture_output=True, text=True).stdout.strip()
lines = ['# Environment report', '', f'- Timestamp: {now_iso()}', f'- Project root: {ctx.root}', f'- Python: {platform.python_version()}', f'- Git commit: {git_commit}', '', '## Python packages']
lines += [f'- {k}: {v}' for k, v in versions.items()]
lines += ['', '## External tools'] + [f'- {k}: {v}' for k, v in tools.items()]
(ctx.root / 'reports' / '00_environment_report.md').write_text('\\n'.join(lines) + '\\n', encoding='utf-8')
print('ENVIRONMENT CHECK COMPLETE')
print(versions, tools)
"""),
    ("01_input_genome_proteome.ipynb", "Genome/proteome input registration", "config/project.yaml; input/genome; input/proteome", "evidence/input_manifest.tsv; evidence/genome_statistics.tsv; evidence/proteome_statistics.tsv", False, False, True,
     """from src.identifiers import scan_inputs
result = scan_inputs(ctx)
display(result['manifest'])
"""),
    ("02_functional_annotation_and_id_mapping.ipynb", "Functional annotation and protein ID mapping", "legacy workflow mapping; config/thresholds.yaml", "evidence/protein_mapping/*.tsv", False, True, True,
     """from src.protein_mapping import prepare_mapping
summary = prepare_mapping(ctx)
print(summary)
"""),
    ("03_draft_gem_reconstruction.ipynb", "Register or reconstruct draft GEM", "configured draft model or proteome", "models/draft/LC1_DRAFT.xml; reports/03_draft_statistics.tsv", False, False, True,
     """from src.draft_reconstruction import register_draft
result = register_draft(ctx)
print(result)
"""),
    ("04_evidence_integration.ipynb", "Integrate gene and reaction evidence", "existing evidence tables; protein mapping", "evidence/GENE_EVIDENCE.tsv; evidence/REACTION_EVIDENCE.tsv", False, False, True,
     """from src.evidence import integrate_existing_evidence
result = integrate_existing_evidence(ctx)
print(result)
"""),
    ("05_reaction_gpr_candidate_curation.ipynb", "Generate reaction/GPR candidates", "evidence tables; existing centralized review", "review/candidates/REACTION_GPR_REVIEW.tsv", False, True, True,
     """from src.gpr import generate_reaction_gpr_candidates
result = generate_reaction_gpr_candidates(ctx)
print(result)
"""),
    ("06_biomass_reconstruction.ipynb", "Reuse and audit LC1 Biomass V2.2", "final V2.2 biomass evidence; source model", "evidence/biomass/*.tsv; review/candidates/BIOMASS_REVIEW.tsv; models/candidates/LC1_BIOMASS_CANDIDATE.xml", False, True, True,
     """from src.biomass import prepare_biomass_candidate
result = prepare_biomass_candidate(ctx)
print(result)
if result['status'] == 'REVIEW_REQUIRED':
    print('STOP: BIOMASS REVIEW REQUIRED')
"""),
    ("07_precursor_gapfill.ipynb", "Prepare precursor-directed weighted-gapfill candidates", "candidate model; existing weighted-pFBA results", "evidence/gapfill/*.tsv; review/candidates/GAPFILL_REVIEW.tsv; models/candidates/LC1_GAPFILL_CANDIDATE.xml", False, True, True,
     """from src.gapfill import prepare_gapfill_candidates
result = prepare_gapfill_candidates(ctx)
print(result)
"""),
    ("08_direction_transport_exchange_qc.ipynb", "Generate direction, transport, exchange and QC review candidates", "candidate model; existing proposals", "review/candidates/DIRECTION_REVIEW.tsv; TRANSPORT_EXCHANGE_REVIEW.tsv; QC_FLAG_REVIEW.tsv", False, True, True,
     """from src.transport import generate_transport_review
from src.directionality import generate_direction_qc_review
print(generate_transport_review(ctx))
print(generate_direction_qc_review(ctx))
"""),
    ("09_generate_manual_review_package.ipynb", "Generate unified manual-review package", "review/candidates/*.tsv", "review/HUMAN_REVIEW_PACKAGE.tsv; review/HUMAN_REVIEW_PACKAGE.xlsx", False, True, True,
     """from src.manual_review import build_review_package
result = build_review_package(ctx)
print(result)
print('AUTOMATED PREPARATION COMPLETE')
print('MANUAL REVIEW REQUIRED')
"""),
    ("10_import_manual_decisions.ipynb", "Validate and import manual decisions", "review/HUMAN_REVIEW_PACKAGE.tsv", "review/decisions/APPROVED_DECISIONS.tsv; REJECTED_DECISIONS.tsv; DEFERRED_DECISIONS.tsv; DECISION_VALIDATION_REPORT.md", False, True, False,
     """from src.manual_review import import_decisions
result = import_decisions(ctx)
print(result)
"""),
    ("11_apply_manual_decisions.ipynb", "Atomically apply approved manual decisions", "last candidate model; review/decisions/APPROVED_DECISIONS.tsv", "models/reviewed/LC1_REVIEWED_MODEL.xml; review/decisions/DECISION_APPLICATION_LOG.tsv", True, True, False,
     """from src.decision_apply import apply_approved_decisions
result = apply_approved_decisions(ctx)
print(result)
"""),
    ("12_global_regression_and_memote_qc.ipynb", "Global regression and MEMOTE gate", "models/reviewed/LC1_REVIEWED_MODEL.xml; config/media.yaml", "qc/regression; qc/memote; qc/mass_charge; qc/blocked; qc/energy", False, False, False,
     """from src.regression import run_regression
result = run_regression(ctx)
print(result)
"""),
    ("13_phenotype_validation.ipynb", "Phenotype and essentiality validation", "reviewed model; existing final phenotype assets", "validation/carbon_sources/CARBON_PHENOTYPE_RESULTS.tsv; validation/essentiality/ESSENTIAL_GENES.tsv", False, False, False,
     """from src.phenotype import prepare_phenotype_results
result = prepare_phenotype_results(ctx)
print(result)
"""),
    ("14_finalize_release_model.ipynb", "Finalize gated release candidate", "reviewed model; decisions; regression; MEMOTE", "models/final/iAL1080_RELEASE_CANDIDATE.xml; MODEL_RELEASE_MANIFEST.tsv", True, False, False,
     """from src.export import finalize_release_candidate
result = finalize_release_candidate(ctx)
print(result)
"""),
    ("15_export_reproducibility_package.ipynb", "Export sanitized reproducibility package", "framework outputs", "GITHUB_RELEASE_REVIEW/reconstruction_framework", False, False, False,
     """from src.export import export_github_review
result = export_github_review(ctx)
print(result)
"""),
]


def build() -> None:
    notebooks = ROOT / "notebooks"
    notebooks.mkdir(exist_ok=True)
    manifest_rows = []
    io_rows = []
    for index, (name, title, inputs, outputs, modifies, manual, automatic, body) in enumerate(SPECS):
        notebook = nbf.v4.new_notebook()
        notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
        notebook.metadata.language_info = {"name": "python", "version": "3"}
        notebook.cells = [
            nbf.v4.new_markdown_cell(f"# {title}\n\n**Inputs:** {inputs}\n\n**Outputs:** {outputs}\n\nThis notebook orchestrates existing functions and does not infer unresolved biology."),
            nbf.v4.new_code_cell(SETUP),
            nbf.v4.new_code_cell(body),
        ]
        nbf.write(notebook, notebooks / name)
        manifest_rows.append({"step": index, "notebook": name, "main_input": inputs, "main_output": outputs, "status": "PREPARED", "timestamp": "", "notes": "Manual gate" if index == 9 else ""})
        io_rows.append({"notebook": name, "inputs": inputs, "outputs": outputs, "modifies_model": "YES" if modifies else "NO", "manual_review_required": "YES" if manual else "NO", "can_run_automatically": "YES" if automatic else "NO", "notes": "Does not overwrite existing outputs"})
    pd.DataFrame(manifest_rows).to_csv(ROOT / "workflow_manifest.tsv", sep="\t", index=False)
    pd.DataFrame(io_rows).to_csv(ROOT / "reports" / "NOTEBOOK_IO_MAP.tsv", sep="\t", index=False)


if __name__ == "__main__":
    build()
