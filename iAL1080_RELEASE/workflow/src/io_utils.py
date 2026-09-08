from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


STANDARD_DIRS = [
    "evidence/protein_mapping", "evidence/reaction", "evidence/gpr", "evidence/biomass", "evidence/gapfill",
    "review/candidates", "review/templates", "review/decisions", "models/draft", "models/candidates",
    "models/reviewed", "models/final", "qc/regression", "qc/memote", "qc/mass_charge", "qc/blocked",
    "qc/energy", "validation/media", "validation/carbon_sources", "validation/essentiality", "logs", "reports",
]


def ensure_directories(root: Path) -> None:
    for relative in STANDARD_DIRS:
        (root / relative).mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_new(source: Path, destination: Path) -> Path:
    if not source.exists():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha256(source) == sha256(destination):
            return destination
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    shutil.copy2(source, destination)
    return destination


def write_tsv(rows: pd.DataFrame | Iterable[dict], path: Path) -> Path:
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(list(rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, sep="\t", index=False)
    return path


def write_json(data: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def relative_display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "EXTERNAL_PROJECT_ASSET/" + path.name


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
