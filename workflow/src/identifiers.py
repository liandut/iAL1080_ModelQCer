from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import WorkflowContext
from .io_utils import sha256, write_tsv


FASTA_SUFFIXES = {".fa", ".fasta", ".fna", ".faa"}


def _fasta_records(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    name = ""
    sequence: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith(">"):
                if name:
                    records.append((name, "".join(sequence)))
                name, sequence = line[1:], []
            elif line:
                sequence.append(line)
    if name:
        records.append((name, "".join(sequence)))
    return records


def scan_inputs(ctx: WorkflowContext) -> dict[str, pd.DataFrame]:
    candidates = []
    for folder in (ctx.root / "input" / "genome", ctx.root / "input" / "proteome", ctx.root / "input" / "annotation"):
        candidates.extend(p for p in folder.rglob("*") if p.is_file())
    for key in ("genome", "proteome", "annotation"):
        configured = ctx.path(ctx.project.get(key))
        if configured and configured.exists() and configured not in candidates:
            candidates.append(configured)
    manifest = []
    genome_rows = []
    protein_rows = []
    for path in sorted(candidates):
        kind = "OTHER"
        if path.suffix.lower() in FASTA_SUFFIXES:
            records = _fasta_records(path)
            letters = "".join(sequence.upper() for _, sequence in records)
            if path.suffix.lower() == ".faa":
                kind = "PROTEOME"
                protein_rows.append({"file": path.name, "protein_count": len(records), "total_amino_acids": len(letters), "sha256": sha256(path)})
            else:
                kind = "GENOME"
                gc = (letters.count("G") + letters.count("C")) / len(letters) if letters else 0
                genome_rows.append({"file": path.name, "genome_length": len(letters), "gc_fraction": gc, "sequence_count": len(records), "cds_count": "NOT_AVAILABLE_FROM_FASTA", "sha256": sha256(path)})
        manifest.append({"file": path.name, "kind": kind, "identity_status": "REQUIRES_METADATA_CONFIRMATION", "sha256": sha256(path)})
    if not manifest:
        manifest.append({"file": "", "kind": "INPUT_REQUIRED", "identity_status": "NO_GENOME_OR_PROTEOME_CONFIGURED", "sha256": ""})
    outputs = {
        "manifest": pd.DataFrame(manifest),
        "genome": pd.DataFrame(genome_rows, columns=["file", "genome_length", "gc_fraction", "sequence_count", "cds_count", "sha256"]),
        "proteome": pd.DataFrame(protein_rows, columns=["file", "protein_count", "total_amino_acids", "sha256"]),
    }
    write_tsv(outputs["manifest"], ctx.root / "evidence" / "input_manifest.tsv")
    write_tsv(outputs["genome"], ctx.root / "evidence" / "genome_statistics.tsv")
    write_tsv(outputs["proteome"], ctx.root / "evidence" / "proteome_statistics.tsv")
    return outputs
