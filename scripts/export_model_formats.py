#!/usr/bin/env python3
"""Export the canonical iAL1080 SBML model to COBRApy exchange formats.

The script writes JSON, YAML, and MATLAB files next to ``model/iAL1080.xml``
and verifies that each reloaded model preserves identifiers and mathematics.
"""

from __future__ import annotations

from pathlib import Path

from cobra.io import (
    load_json_model,
    load_matlab_model,
    load_yaml_model,
    read_sbml_model,
    save_json_model,
    save_matlab_model,
    save_yaml_model,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "model"
SBML = MODEL_DIR / "iAL1080.xml"


def objective_coefficients(model):
    return {
        reaction.id: float(reaction.objective_coefficient)
        for reaction in model.reactions
        if abs(reaction.objective_coefficient) > 1e-15
    }


def stoichiometry(reaction):
    return {metabolite.id: float(value) for metabolite, value in reaction.metabolites.items()}


def verify_equivalent(reference, candidate, label):
    reference_reactions = {reaction.id: reaction for reaction in reference.reactions}
    assert {gene.id for gene in candidate.genes} == {gene.id for gene in reference.genes}
    assert {reaction.id for reaction in candidate.reactions} == set(reference_reactions)
    assert {metabolite.id for metabolite in candidate.metabolites} == {
        metabolite.id for metabolite in reference.metabolites
    }
    assert candidate.objective.direction == reference.objective.direction
    assert objective_coefficients(candidate) == objective_coefficients(reference)
    for reaction in candidate.reactions:
        original = reference_reactions[reaction.id]
        assert abs(reaction.lower_bound - original.lower_bound) < 1e-12
        assert abs(reaction.upper_bound - original.upper_bound) < 1e-12
        assert stoichiometry(reaction) == stoichiometry(original)
    print(
        f"{label}: PASS "
        f"({len(candidate.genes)} genes, {len(candidate.reactions)} reactions, "
        f"{len(candidate.metabolites)} metabolites)"
    )


def main():
    model = read_sbml_model(str(SBML))
    json_path = MODEL_DIR / "iAL1080.json"
    yaml_path = MODEL_DIR / "iAL1080.yaml"
    mat_path = MODEL_DIR / "iAL1080.mat"

    save_json_model(model, str(json_path), sort=True, pretty=False)
    save_yaml_model(model, str(yaml_path), sort=True)
    save_matlab_model(model, str(mat_path), varname="iAL1080")

    verify_equivalent(model, load_json_model(str(json_path)), "JSON")
    verify_equivalent(model, load_yaml_model(str(yaml_path)), "YAML")
    verify_equivalent(
        model,
        load_matlab_model(str(mat_path), variable_name="iAL1080"),
        "MATLAB",
    )


if __name__ == "__main__":
    main()
