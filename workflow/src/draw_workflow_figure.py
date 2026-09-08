#!/usr/bin/env python3
"""Draw the publication-style human-in-the-loop HB GEM workflow figure."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "figures"

BLUE = "#DCECF4"
BLUE_DARK = "#4F7E96"
ORANGE = "#F9E9D2"
ORANGE_DARK = "#B67B3E"
GREEN = "#DDEFE6"
GREEN_DARK = "#4F876D"
RED = "#B66A6A"
TEXT = "#26343B"
MUTED = "#5F6F76"
BORDER = "#AAB8BE"
WHITE = "#FFFFFF"


def rounded(ax, x, y, w, h, face, edge, radius=0.015, lw=1.1, z=2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        linewidth=lw, edgecolor=edge, facecolor=face, zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, color=BORDER, style="-|>", lw=1.35, connection="arc3", z=3):
    patch = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=10,
        linewidth=lw, color=color, connectionstyle=connection,
        shrinkA=2, shrinkB=2, zorder=z,
    )
    ax.add_patch(patch)
    return patch


def step_node(ax, x, y, w, h, number, title, subtitle, face, edge):
    rounded(ax, x, y, w, h, face, edge, radius=0.012, lw=1.0)
    badge = Circle((x + 0.018, y + h - 0.020), 0.012, facecolor=edge, edgecolor="none", zorder=4)
    ax.add_patch(badge)
    ax.text(x + 0.018, y + h - 0.020, str(number), ha="center", va="center",
            fontsize=6.6, fontweight="bold", color=WHITE, zorder=5)
    ax.text(x + w / 2, y + h * 0.61, title, ha="center", va="center",
            fontsize=8.0, fontweight="semibold", color=TEXT, zorder=5, linespacing=1.12)
    ax.text(x + w / 2, y + h * 0.27, subtitle, ha="center", va="center",
            fontsize=6.6, color=MUTED, zorder=5, linespacing=1.10)


def phase_header(ax, y, label, description, color):
    ax.text(0.045, y, label, ha="left", va="center", fontsize=9.6,
            fontweight="bold", color=color)
    ax.text(0.16, y, description, ha="left", va="center", fontsize=7.6, color=MUTED)


def draw() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })
    fig, ax = plt.subplots(figsize=(15.2, 8.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.955, "Human-in-the-loop reconstruction and curation workflow for iAL1080",
            ha="center", va="center", fontsize=17, fontweight="semibold", color=TEXT)
    ax.text(0.5, 0.919,
            "Automated evidence preparation is separated from expert biological decisions and release qualification",
            ha="center", va="center", fontsize=9.2, color=MUTED)

    # Three pale workflow lanes.
    rounded(ax, 0.025, 0.655, 0.95, 0.225, "#F8FBFD", "#D7E4EA", radius=0.018, lw=0.9, z=0)
    rounded(ax, 0.025, 0.395, 0.95, 0.205, "#FEFBF6", "#EBDCC9", radius=0.018, lw=0.9, z=0)
    rounded(ax, 0.025, 0.105, 0.95, 0.235, "#F8FCFA", "#D4E6DC", radius=0.018, lw=0.9, z=0)

    phase_header(ax, 0.850, "PHASE I", "Automated preparation and candidate generation", BLUE_DARK)
    phase_header(ax, 0.570, "PHASE II", "Formal manual expert review — workflow stops here", ORANGE_DARK)
    phase_header(ax, 0.310, "PHASE III", "Decision-controlled reintegration, regression and release", GREEN_DARK)

    # Phase I, left to right.
    p1 = [
        ("Genome /\nproteome", "FASTA · GBFF · FAA"),
        ("Annotation &\nID mapping", "Exact sequence · RBH"),
        ("Draft GEM", "CarveMe registration"),
        ("Evidence\nintegration", "Gene · reaction · xrefs"),
        ("Reaction / GPR\ncandidates", "No automatic deletion"),
        ("Biomass V2.2", "LC1 composition audit"),
        ("Weighted gapfill\ncandidates", "No foreign GPR"),
        ("Direction · transport\n· QC flags", "Review candidates only"),
    ]
    x1 = [0.045 + i * 0.1165 for i in range(8)]
    w1, h1, y1 = 0.102, 0.113, 0.690
    for i, ((title, subtitle), x) in enumerate(zip(p1, x1), start=1):
        step_node(ax, x, y1, w1, h1, i, title, subtitle, BLUE, BLUE_DARK)
        if i > 1:
            arrow(ax, (x - 0.013, y1 + h1 / 2), (x, y1 + h1 / 2), color=BLUE_DARK)

    # Turn from Phase I to Phase II at the right edge; Phase II flows right to left.
    arrow(ax, (x1[-1] + w1 / 2, y1), (0.827, 0.530), color=ORANGE_DARK,
          connection="angle3,angleA=-90,angleB=0")

    p2 = [
        (0.735, "Machine-readable\nreview package", "111 stable review IDs\nTSV + human workbook"),
        (0.410, "Manual expert\nreview", "APPROVE · REJECT · REVISE\nDEFER · UNRESOLVED"),
        (0.085, "Validated decision\nset", "Blank/unresolved decisions\nare never applied"),
    ]
    w2, h2, y2 = 0.19, 0.110, 0.435
    for idx, (x, title, subtitle) in enumerate(p2, start=9):
        step_node(ax, x, y2, w2, h2, idx, title, subtitle, ORANGE, ORANGE_DARK)
    arrow(ax, (0.735, y2 + h2 / 2), (0.600, y2 + h2 / 2), color=ORANGE_DARK)
    arrow(ax, (0.410, y2 + h2 / 2), (0.275, y2 + h2 / 2), color=ORANGE_DARK)
    ax.text(0.505, 0.410, "AUTOMATED PREPARATION COMPLETE  ·  MANUAL REVIEW REQUIRED",
            ha="center", va="center", fontsize=7.4, fontweight="bold", color=ORANGE_DARK)

    # Turn from Phase II to Phase III; Phase III flows left to right.
    arrow(ax, (0.085 + w2 / 2, y2), (0.105, 0.265), color=GREEN_DARK,
          connection="angle3,angleA=-90,angleB=180")

    p3 = [
        ("Import\ndecisions", "Validate IDs & values"),
        ("Atomic\napplication", "Before/after audit log"),
        ("Regression &\nstructural QC", "Growth · nutrients · ATPM"),
        ("Phenotype\nretest", "Carbon · essentiality · PHB"),
        ("MEMOTE &\nrelease gate", "FAIL blocks release"),
        ("Final curated\nGEM", "iAL1080 candidate + SHA"),
    ]
    x3 = [0.045 + i * 0.155 for i in range(6)]
    w3, h3, y3 = 0.135, 0.120, 0.145
    for i, ((title, subtitle), x) in enumerate(zip(p3, x3), start=12):
        step_node(ax, x, y3, w3, h3, i, title, subtitle, GREEN, GREEN_DARK)
        if i > 12:
            arrow(ax, (x - 0.018, y3 + h3 / 2), (x, y3 + h3 / 2), color=GREEN_DARK)

    # Dashed feedback from failed regression to expert review.
    feedback = FancyArrowPatch(
        (x3[2] + w3 / 2, y3 + h3), (0.505, y2),
        arrowstyle="-|>", mutation_scale=10, linewidth=1.1,
        linestyle=(0, (4, 3)), color=RED,
        connectionstyle="arc3,rad=-0.23", shrinkA=3, shrinkB=4, zorder=3,
    )
    ax.add_patch(feedback)
    ax.text(0.545, 0.346, "FAIL / revision required", ha="center", va="center",
            fontsize=7.0, color=RED, fontweight="semibold")

    # Safety principles.
    ax.plot([0.045, 0.955], [0.075, 0.075], color="#D7DFE2", lw=0.8)
    safety = [
        "No unresolved reaction is auto-deleted",
        "No donor/universal GPR is transferred",
        "No formal model is overwritten",
        "Every structural edit triggers regression gates",
    ]
    positions = [0.055, 0.305, 0.560, 0.775]
    for x, label in zip(positions, safety):
        ax.add_patch(Circle((x, 0.045), 0.0055, facecolor=GREEN_DARK, edgecolor="none"))
        ax.text(x + 0.013, 0.045, label, ha="left", va="center", fontsize=6.9, color=MUTED)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "HB_GEM_HUMAN_IN_LOOP_WORKFLOW"
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.08)
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(stem)


if __name__ == "__main__":
    draw()
