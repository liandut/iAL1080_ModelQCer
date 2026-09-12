#!/usr/bin/env python3
"""Validate source tables and reproduce the iAL1080 N–O2/FVA figure."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PACKAGE_ROOT / "data"
FIGURE_DIR = PACKAGE_ROOT / "figures"
EXPECTED_MODEL_SHA256 = "42db34aeab6fc710202d47a917b8703d92565f47f0fc10346d79e10e7ffd1f7d"

DATA_FILES = {
    "phase": "HB_N_O2_PHASE_PLANE_DATA.csv",
    "states": "HB_FOUR_STATE_SUMMARY.csv",
    "fva": "HB_FVA_GROWTH_TO_STORAGE_SHIFT.csv",
    "crosscheck": "HB_FVA_FSEOF_CROSSCHECK.csv",
}
EXPECTED_STATES = {"Control", "N-limited", "O2-limited", "N + low O2"}
EXPECTED_FVA_REACTIONS = {
    "R_PHB_SYN_HB", "R_CS", "R_MDH", "R_CYO1_KT",
    "R_CYTCAA3pp", "R_ATPS4rpp", "R_EX_co2_e",
}
REACTION_LABELS = {
    "R_PHB_SYN_HB": "PHB synthase",
    "R_CS": "Citrate synthase",
    "R_MDH": "Malate dehydrogenase",
    "R_CYO1_KT": "Ubiquinol–cytochrome c reductase",
    "R_CYTCAA3pp": "Cytochrome c oxidase aa3",
    "R_ATPS4rpp": "ATP synthase",
    "R_EX_co2_e": "CO$_2$ release",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_repository_model() -> Path | None:
    """Locate the canonical model when this package is inside the repository."""
    for parent in (PACKAGE_ROOT, *PACKAGE_ROOT.parents):
        candidate = parent / "model" / "iAL1080.xml"
        if candidate.is_file():
            return candidate
    return None


def require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {sorted(missing)}")


def validate_numeric(frame: pd.DataFrame, name: str) -> None:
    numeric = frame.select_dtypes(include=[np.number])
    if numeric.empty or not np.isfinite(numeric.to_numpy()).all():
        raise ValueError(f"{name} contains missing or non-finite numerical values")


def load_and_validate() -> dict[str, pd.DataFrame]:
    tables = {key: pd.read_csv(DATA_DIR / filename) for key, filename in DATA_FILES.items()}
    for key, frame in tables.items():
        validate_numeric(frame, DATA_FILES[key])

    phase, states, fva, crosscheck = (
        tables["phase"], tables["states"], tables["fva"], tables["crosscheck"]
    )
    require_columns(phase, {
        "N_fraction_qNref", "O2_fraction_qO2ref", "mu_max_h-1",
        "PHB_flux_mmol_gDW_h", "PHB_capacity_g_gDW_h",
    }, DATA_FILES["phase"])
    require_columns(states, {
        "State", "N_fraction", "O2_fraction", "mu_max_h-1",
        "PHB_flux_mmol_gDW_h", "PHB_capacity_g_gDW_h",
    }, DATA_FILES["states"])
    require_columns(fva, {
        "reaction_id", "reference_min", "reference_max", "storage_min", "storage_max",
        "classification", "reference_min_norm", "reference_max_norm",
        "storage_min_norm", "storage_max_norm",
    }, DATA_FILES["fva"])
    require_columns(crosscheck, {
        "reaction_id", "reference_min", "reference_max", "storage_min", "storage_max",
        "FVA_nonoverlap_class",
    }, DATA_FILES["crosscheck"])

    if set(states["State"]) != EXPECTED_STATES or len(states) != 4:
        raise ValueError("The four predefined manuscript states are incomplete or duplicated")
    if set(fva["reaction_id"]) != EXPECTED_FVA_REACTIONS:
        raise ValueError("The main FVA table does not contain the validated seven-reaction set")
    if phase.duplicated(["N_fraction_qNref", "O2_fraction_qO2ref"]).any():
        raise ValueError("The N–O2 phase plane contains duplicate coordinates")
    expected_grid_size = phase["N_fraction_qNref"].nunique() * phase["O2_fraction_qO2ref"].nunique()
    if len(phase) != expected_grid_size:
        raise ValueError("The N–O2 phase plane is not a complete rectangular grid")

    indexed = states.set_index("State")
    combined, n_only = indexed.loc["N + low O2"], indexed.loc["N-limited"]
    if not np.isclose(combined["N_fraction"], 0.5) or not np.isclose(combined["O2_fraction"], 0.25):
        raise ValueError("The predefined combined coordinate is not N=0.5/O2=0.25")
    if not np.isclose(combined["mu_max_h-1"], n_only["mu_max_h-1"], atol=1e-10):
        raise ValueError("Combined-state growth is inconsistent with the N-limited reference")
    if combined["PHB_capacity_g_gDW_h"] > n_only["PHB_capacity_g_gDW_h"] + 1e-6:
        raise ValueError("Combined-state PHB exceeds the N-only state by a meaningful amount")

    checked = crosscheck.set_index("reaction_id")
    for reaction_id in ("R_PDH", "R_ACACT1r"):
        if checked.loc[reaction_id, "FVA_nonoverlap_class"] != "overlapping ranges":
            raise ValueError(f"{reaction_id} must remain an overlapping-range cross-check")
    return tables


def configure_style() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "iAL1080-N-O2-FVA",
    })


def clean_axis(axis: plt.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(length=3.5, width=0.8, colors="#34424A")


def add_state_markers(axis: plt.Axes, states: pd.DataFrame) -> None:
    display = {
        "Control": "Control",
        "N-limited": "N-limited",
        "O2-limited": "O$_2$-limited",
        "N + low O2": "N + low O$_2$",
    }
    offsets = {
        "Control": (0.025, 0.018),
        "N-limited": (0.025, 0.018),
        "O2-limited": (0.025, 0.018),
        "N + low O2": (0.025, 0.018),
    }
    for row in states.itertuples(index=False):
        dx, dy = offsets[row.State]
        axis.scatter(row.O2_fraction, row.N_fraction, s=32, facecolor="white",
                     edgecolor="#34424A", linewidth=1.0, zorder=5)
        axis.text(row.O2_fraction + dx, row.N_fraction + dy, display[row.State],
                  fontsize=7.3, color="#34424A", zorder=6)


def make_figure(tables: dict[str, pd.DataFrame]) -> plt.Figure:
    phase = tables["phase"]
    states = tables["states"]
    fva = tables["fva"].copy()
    growth = phase.pivot(index="N_fraction_qNref", columns="O2_fraction_qO2ref",
                         values="mu_max_h-1").sort_index().sort_index(axis=1)
    phb = phase.pivot(index="N_fraction_qNref", columns="O2_fraction_qO2ref",
                      values="PHB_capacity_g_gDW_h").sort_index().sort_index(axis=1)
    x, y = np.meshgrid(growth.columns.to_numpy(float), growth.index.to_numpy(float))

    growth_cmap = LinearSegmentedColormap.from_list(
        "growth_light", ["#F8FBFD", "#E3EFF6", "#BDD6E6", "#83AEC9", "#5F91B1"]
    )
    phb_cmap = LinearSegmentedColormap.from_list(
        "phb_light", ["#FBF8F0", "#EEE8CF", "#C8DDD6", "#91BFB4", "#6CA297"]
    )

    fig = plt.figure(figsize=(11.0, 9.0))
    grid = GridSpec(2, 2, figure=fig, height_ratios=[1.0, 0.95], hspace=0.34, wspace=0.28)
    ax_a, ax_b, ax_c = fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, :])

    levels_a = np.linspace(float(np.nanmin(growth)), float(np.nanmax(growth)), 18)
    image_a = ax_a.contourf(x, y, growth.to_numpy(), levels=levels_a, cmap=growth_cmap)
    color_a = fig.colorbar(image_a, ax=ax_a, pad=0.025, shrink=0.92)
    color_a.set_label("Maximum growth rate (h$^{-1}$)")
    ax_a.set_xlabel(r"Relative oxygen uptake constraint ($q_{O_2}/q_{O_2,ref}$)")
    ax_a.set_ylabel(r"Relative ammonium uptake constraint ($q_N/q_{N,ref}$)")
    ax_a.set_title("Maximum growth capacity across the N–O$_2$ plane", pad=8)

    levels_b = np.linspace(float(np.nanmin(phb)), float(np.nanmax(phb)), 18)
    image_b = ax_b.contourf(x, y, phb.to_numpy(), levels=levels_b, cmap=phb_cmap)
    color_b = fig.colorbar(image_b, ax=ax_b, pad=0.025, shrink=0.92)
    color_b.set_label("Maximum feasible PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)")
    ax_b.set_xlabel(r"Relative oxygen uptake constraint ($q_{O_2}/q_{O_2,ref}$)")
    ax_b.set_ylabel(r"Relative ammonium uptake constraint ($q_N/q_{N,ref}$)")
    ax_b.set_title("Maximum PHB storage capacity across the N–O$_2$ plane", pad=8)
    for axis in (ax_a, ax_b):
        add_state_markers(axis, states)
        clean_axis(axis)

    positions = np.arange(len(fva))[::-1]
    for position, row in zip(positions, fva.itertuples(index=False)):
        ax_c.plot([row.reference_min_norm, row.reference_max_norm],
                  [position + 0.13, position + 0.13], linewidth=5.2,
                  solid_capstyle="round", color="#7FA9C9")
        ax_c.plot([row.storage_min_norm, row.storage_max_norm],
                  [position - 0.13, position - 0.13], linewidth=5.2,
                  solid_capstyle="round", color="#D79A84")
        marker = r"$\uparrow$" if row.classification == "required upward shift" else r"$\downarrow$"
        marker_color = "#B85F55" if row.classification == "required upward shift" else "#567FA0"
        ax_c.text(1.045, position, marker, va="center", ha="left", fontsize=12,
                  color=marker_color, fontweight="bold")
    ax_c.axvline(0, color="#CDD5DA", linewidth=1)
    ax_c.set_yticks(positions, [REACTION_LABELS[x] for x in fva["reaction_id"]])
    ax_c.set_xlim(-1.08, 1.13)
    ax_c.set_xlabel("Feasible flux interval (normalized within each reaction)")
    ax_c.set_title("FVA-supported shift in feasible flux space between defined states", pad=8)
    ax_c.plot([], [], linewidth=5.2, color="#7FA9C9", label="Growth-dominant control state")
    ax_c.plot([], [], linewidth=5.2, color="#D79A84", label="Defined dual-limitation storage state")
    ax_c.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.65, 1.0), ncol=2)
    ax_c.grid(axis="x", color="#E9EEF1", linewidth=0.8)
    clean_axis(ax_c)

    for axis, letter in ((ax_a, "A"), (ax_b, "B"), (ax_c, "C")):
        axis.text(-0.18, 1.08, letter, transform=axis.transAxes, fontsize=15,
                  fontweight="bold", va="top", ha="left", color="#26343B")
    return fig


def _phase_grids(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    phase = tables["phase"]
    growth = phase.pivot(index="N_fraction_qNref", columns="O2_fraction_qO2ref",
                         values="mu_max_h-1").sort_index().sort_index(axis=1)
    phb = phase.pivot(index="N_fraction_qNref", columns="O2_fraction_qO2ref",
                      values="PHB_capacity_g_gDW_h").sort_index().sort_index(axis=1)
    x, y = np.meshgrid(growth.columns.to_numpy(float), growth.index.to_numpy(float))
    return growth, phb, x, y


def make_growth_phase_plane(tables: dict[str, pd.DataFrame]) -> plt.Figure:
    """Create the standalone growth-capacity phase plane."""
    growth, _, x, y = _phase_grids(tables)
    cmap = LinearSegmentedColormap.from_list(
        "growth_light_single", ["#F8FBFD", "#E3EFF6", "#BDD6E6", "#83AEC9", "#5F91B1"]
    )
    figure, axis = plt.subplots(figsize=(5.8, 4.8))
    levels = np.linspace(float(np.nanmin(growth)), float(np.nanmax(growth)), 18)
    image = axis.contourf(x, y, growth.to_numpy(), levels=levels, cmap=cmap)
    colorbar = figure.colorbar(image, ax=axis, pad=0.025, shrink=0.92)
    colorbar.set_label("Maximum growth rate (h$^{-1}$)")
    axis.set_xlabel(r"Relative oxygen uptake constraint ($q_{O_2}/q_{O_2,ref}$)")
    axis.set_ylabel(r"Relative ammonium uptake constraint ($q_N/q_{N,ref}$)")
    axis.set_title("Maximum growth capacity across the N–O$_2$ plane", pad=8)
    add_state_markers(axis, tables["states"])
    clean_axis(axis)
    figure.tight_layout()
    return figure


def make_phb_phase_plane(tables: dict[str, pd.DataFrame]) -> plt.Figure:
    """Create the standalone PHB-capacity phase plane."""
    _, phb, x, y = _phase_grids(tables)
    cmap = LinearSegmentedColormap.from_list(
        "phb_light_single", ["#FBF8F0", "#EEE8CF", "#C8DDD6", "#91BFB4", "#6CA297"]
    )
    figure, axis = plt.subplots(figsize=(5.8, 4.8))
    levels = np.linspace(float(np.nanmin(phb)), float(np.nanmax(phb)), 18)
    image = axis.contourf(x, y, phb.to_numpy(), levels=levels, cmap=cmap)
    colorbar = figure.colorbar(image, ax=axis, pad=0.025, shrink=0.92)
    colorbar.set_label("Maximum feasible PHB synthesis rate (g gDW$^{-1}$ h$^{-1}$)")
    axis.set_xlabel(r"Relative oxygen uptake constraint ($q_{O_2}/q_{O_2,ref}$)")
    axis.set_ylabel(r"Relative ammonium uptake constraint ($q_N/q_{N,ref}$)")
    axis.set_title("Maximum PHB storage capacity across the N–O$_2$ plane", pad=8)
    add_state_markers(axis, tables["states"])
    clean_axis(axis)
    figure.tight_layout()
    return figure


def make_fva_shift(tables: dict[str, pd.DataFrame]) -> plt.Figure:
    """Create the standalone normalized FVA interval comparison."""
    fva = tables["fva"].copy()
    figure, axis = plt.subplots(figsize=(9.0, 5.2))
    positions = np.arange(len(fva))[::-1]
    for position, row in zip(positions, fva.itertuples(index=False)):
        axis.plot([row.reference_min_norm, row.reference_max_norm],
                  [position + 0.13, position + 0.13], linewidth=5.2,
                  solid_capstyle="round", color="#7FA9C9")
        axis.plot([row.storage_min_norm, row.storage_max_norm],
                  [position - 0.13, position - 0.13], linewidth=5.2,
                  solid_capstyle="round", color="#D79A84")
        marker = r"$\uparrow$" if row.classification == "required upward shift" else r"$\downarrow$"
        marker_color = "#B85F55" if row.classification == "required upward shift" else "#567FA0"
        axis.text(1.045, position, marker, va="center", ha="left", fontsize=12,
                  color=marker_color, fontweight="bold")
    axis.axvline(0, color="#CDD5DA", linewidth=1)
    axis.set_yticks(positions, [REACTION_LABELS[x] for x in fva["reaction_id"]])
    axis.set_xlim(-1.08, 1.13)
    axis.set_xlabel("Feasible flux interval (normalized within each reaction)")
    axis.set_title("FVA-supported shift in feasible flux space between defined states", pad=8)
    axis.plot([], [], linewidth=5.2, color="#7FA9C9", label="Growth-dominant control state")
    axis.plot([], [], linewidth=5.2, color="#D79A84", label="Defined dual-limitation storage state")
    axis.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.65, 1.0), ncol=2)
    axis.grid(axis="x", color="#E9EEF1", linewidth=0.8)
    clean_axis(axis)
    figure.tight_layout()
    return figure


def make_all_figures(tables: dict[str, pd.DataFrame]) -> dict[str, plt.Figure]:
    """Build three independent figures; no combined canvas is generated."""
    return {
        "Fig4A_N_O2_Growth_PhasePlane": make_growth_phase_plane(tables),
        "Fig4B_N_O2_PHB_PhasePlane": make_phb_phase_plane(tables),
        "Fig4C_FVA_Growth_to_Storage_Shift": make_fva_shift(tables),
    }


def save_figure(figure: plt.Figure, stem: str, output_dir: Path = FIGURE_DIR) -> None:
    """Export reproducible raster and vector variants of one figure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    common = {"bbox_inches": "tight", "pad_inches": 0.06}
    figure.savefig(output_dir / f"{stem}.png", dpi=600, **common)
    figure.savefig(
        output_dir / f"{stem}.pdf",
        metadata={"Creator": "iAL1080 reproducible figure script", "CreationDate": None, "ModDate": None},
        **common,
    )
    figure.savefig(
        output_dir / f"{stem}.svg",
        metadata={"Creator": "iAL1080 reproducible figure script", "Date": None},
        **common,
    )


def print_summary(tables: dict[str, pd.DataFrame]) -> None:
    states = tables["states"].set_index("State")
    combined, n_only = states.loc["N + low O2"], states.loc["N-limited"]
    model = find_repository_model()
    print("=== iAL1080 N–O2 phase-plane/FVA reproduction ===")
    print(f"Phase-plane rows: {len(tables['phase'])}")
    print(f"Four manuscript states: {len(states)}")
    print(f"Combined-state mu_max: {combined['mu_max_h-1']:.15g} h^-1")
    print(f"Combined minus N-only PHB rate: {combined['PHB_capacity_g_gDW_h'] - n_only['PHB_capacity_g_gDW_h']:.3e} g gDW^-1 h^-1")
    print("PDH FVA classification: overlapping ranges")
    print("ACACT1r FVA classification: overlapping ranges")
    if model is None:
        print("Repository model: not found from this package location")
    else:
        digest = sha256(model)
        if digest != EXPECTED_MODEL_SHA256:
            raise ValueError(f"Repository model SHA256 mismatch: {digest}")
        print(f"Repository model: {model}")
        print(f"Model SHA256: {digest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true",
                        help="validate inputs and print the numerical summary without writing figures")
    args = parser.parse_args()
    configure_style()
    tables = load_and_validate()
    print_summary(tables)
    if args.validate_only:
        return
    figures = make_all_figures(tables)
    for stem, figure in figures.items():
        save_figure(figure, stem)
        plt.close(figure)
    print(f"Figures written to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
