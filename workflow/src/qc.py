from __future__ import annotations

from pathlib import Path

import pandas as pd
from cobra.io import read_sbml_model

from .io_utils import sha256, write_tsv


def model_statistics(model_path: Path, output: Path | None = None) -> pd.DataFrame:
    model = read_sbml_model(str(model_path))
    objective = [r.id for r in model.reactions if abs(r.objective_coefficient) > 0]
    row = {
        "model": model_path.name,
        "genes": len(model.genes),
        "reactions": len(model.reactions),
        "metabolites": len(model.metabolites),
        "transport": sum(len(r.compartments) > 1 for r in model.reactions),
        "exchange": len(model.exchanges),
        "objective": ";".join(objective),
        "sha256": sha256(model_path),
    }
    frame = pd.DataFrame([row])
    if output:
        write_tsv(frame, output)
    return frame


def structural_flags(model_path: Path, output_root: Path) -> dict[str, int | bool]:
    model = read_sbml_model(str(model_path))
    blocked = []
    for reaction in model.reactions:
        if reaction.lower_bound == 0 and reaction.upper_bound == 0:
            blocked.append({"reaction_id": reaction.id, "reason": "ZERO_BOUNDS"})
    mass = []
    for reaction in model.reactions:
        imbalance = reaction.check_mass_balance()
        if imbalance:
            mass.append({"reaction_id": reaction.id, "imbalance": str(imbalance)})
    write_tsv(blocked, output_root / "blocked" / "BLOCKED_REACTIONS.tsv")
    write_tsv(mass, output_root / "mass_charge" / "MASS_CHARGE_FLAGS.tsv")
    return {"zero_bound_reactions": len(blocked), "mass_or_charge_flags": len(mass), "model_load": True}
