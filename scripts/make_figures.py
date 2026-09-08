"""Generate supervisor-facing figures from repository data only.

Every number in these figures is copied from a committed result file
(``*/RESULTS.md`` and ``*/runs/*.json``). Nothing here re-runs a model or
invents a measurement. Run from the repository root:

    python scripts/make_figures.py

Outputs land in ``docs/figures/`` (referenced by the README and docs) and are
mirrored to ``artifacts/figures/``.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "docs" / "figures"
MIRROR = ROOT / "artifacts" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
MIRROR.mkdir(parents=True, exist_ok=True)

INK = "#1f2a24"
LIME = "#4c9a2a"
GOLD = "#c8912f"
GREY = "#9aa79a"
RED = "#b5462f"
PASS, FAILC, OPENC = "#4c9a2a", "#b5462f", "#c8912f"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, name: str) -> None:
    out = FIG / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    shutil.copyfile(out, MIRROR / name)
    plt.close(fig)
    print("wrote", out.relative_to(ROOT))


# --- Figure 1: research pipeline -------------------------------------------------
def fig_pipeline() -> None:
    phases = [
        ("P0", "Benchmark &\nblind protocol", "Protocol"),
        ("P1", "Ideal coherent-delay\n+ square-law", "Ideal model"),
        ("P2", "Architecture\ncompression", "Ideal architecture sim."),
        ("P3", "Physical-parameter\nsystem model", "System-level sim."),
        ("P4", "Robust\noptimization", "Monte-Carlo system sim."),
        ("P5", "Locked blind\nevaluation", "Blind system-sim. result"),
        ("P6", "Physical\nvalidation", "EM / component evidence"),
    ]
    fig, ax = plt.subplots(figsize=(11, 3.1))
    ax.set_xlim(0, len(phases))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, (tag, title, evidence) in enumerate(phases):
        colour = LIME if tag != "P6" else GOLD
        box = FancyBboxPatch((i + 0.08, 0.34), 0.84, 0.5,
                             boxstyle="round,pad=0.02", linewidth=1.4,
                             edgecolor=INK, facecolor=colour + "22")
        ax.add_patch(box)
        ax.text(i + 0.5, 0.72, tag, ha="center", va="center", fontweight="bold", fontsize=12)
        ax.text(i + 0.5, 0.50, title, ha="center", va="center", fontsize=8.3)
        ax.text(i + 0.5, 0.24, evidence, ha="center", va="top", fontsize=7.2, style="italic", color="#55605a")
        if i < len(phases) - 1:
            ax.add_patch(FancyArrowPatch((i + 0.93, 0.59), (i + 1.07, 0.59),
                                         arrowstyle="-|>", mutation_scale=14, color=INK))
    ax.text(len(phases) / 2, 0.98, "Research pipeline: increasing evidence strength, left to right",
            ha="center", va="top", fontsize=10, fontweight="bold")
    ax.text(6.5, 0.06, "P6 verdict: NOT_PHYSICALLY_ACCEPTED", ha="center", va="top",
            fontsize=8, color=RED, fontweight="bold")
    save(fig, "fig1_research_pipeline.png")


# --- Figure 2: architecture signal path ---------------------------------------
def fig_architecture() -> None:
    blocks = [
        "NARMA-10 input\nsequence u[t]",
        "Optical delay bank\n20 taps, ≤19 symbols\n(≈14.24 cm max route)",
        "Sparse coherent\nfeature selection\n30 channels",
        "Interference /\ncombiner + LO",
        "10 photodiodes\n× 3 time slots\n(30 GHz slot rate)",
        "Ridge linear\nreadout",
        "NARMA-10\nprediction",
    ]
    fig, ax = plt.subplots(figsize=(12, 2.6))
    ax.set_xlim(0, len(blocks))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, text in enumerate(blocks):
        optical = 1 <= i <= 4
        colour = GOLD if optical else LIME
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.28), 0.88, 0.5,
                                    boxstyle="round,pad=0.02", linewidth=1.3,
                                    edgecolor=INK, facecolor=colour + "26"))
        ax.text(i + 0.5, 0.53, text, ha="center", va="center", fontsize=7.6)
        if i < len(blocks) - 1:
            ax.add_patch(FancyArrowPatch((i + 0.95, 0.53), (i + 1.05, 0.53),
                                         arrowstyle="-|>", mutation_scale=13, color=INK))
    ax.text(0.5, 0.12, "electronic", ha="center", fontsize=7, color=LIME, fontweight="bold")
    ax.text(3.0, 0.12, "on-chip optical core", ha="center", fontsize=7, color=GOLD, fontweight="bold")
    ax.text(len(blocks) / 2, 0.96,
            "P4/P5 architecture (system model; not a fabricated device)",
            ha="center", va="top", fontsize=10, fontweight="bold")
    save(fig, "fig2_architecture.png")


# --- Figure 3: NMSE progression ---------------------------------------------
def fig_nmse() -> None:
    items = [
        ("P1 ideal\n(dev)", 0.022534, LIME),
        ("P2 30-slot\n(dev)", 0.026459, LIME),
        ("P3 nominal\n(dev)", 0.038246, LIME),
        ("P4 nominal\n(dev)", 0.027499, LIME),
        ("P4 stress\n(dev)", 0.033723, LIME),
        ("P5 blind\n(test)", 0.038705, GOLD),
        ("Same-delay\ndigital twin", 0.032471, GREY),
        ("Delayed-input\nbaseline", 0.153049, GREY),
        ("No-PIC\nbaseline", 0.760606, RED),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    xs = range(len(items))
    ax.bar(xs, [v for _, v, _ in items], color=[c for *_, c in items], edgecolor=INK, linewidth=1)
    ax.set_yscale("log")
    ax.axhline(0.05, color=RED, linestyle="--", linewidth=1.3)
    ax.text(len(items) - 0.5, 0.052, "NMSE = 0.05 target", ha="right", va="bottom", color=RED, fontsize=8)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([n for n, *_ in items], fontsize=8)
    ax.set_ylabel("Median NARMA-10 NMSE (log scale)")
    ax.set_title("NMSE across the pipeline and against controls", fontweight="bold")
    for x, (_, v, _) in zip(xs, items):
        ax.text(x, v * 1.08, f"{v:.4f}", ha="center", va="bottom", fontsize=7)
    save(fig, "fig3_nmse_progression.png")


# --- Figure 4: P5 blind seed distribution ----------------------------------
def fig_blind_seeds() -> None:
    seeds = [(179, 0.03560), (181, 0.04108), (191, 0.03266), (193, 0.03072),
             (197, 0.03942), (199, 0.04247), (211, 0.03753), (223, 0.03799),
             (227, 0.06360), (229, 0.12033)]
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = [str(s) for s, _ in seeds]
    vals = [v for _, v in seeds]
    colours = [LIME if v < 0.05 else RED for v in vals]
    ax.bar(labels, vals, color=colours, edgecolor=INK, linewidth=1)
    ax.axhline(0.05, color=RED, linestyle="--", linewidth=1.3)
    ax.axhline(0.038705, color=GOLD, linestyle=":", linewidth=1.4)
    ax.text(9.4, 0.0398, "median 0.03870", ha="right", va="bottom", color=GOLD, fontsize=8)
    ax.text(9.4, 0.051, "target 0.05", ha="right", va="bottom", color=RED, fontsize=8)
    ax.set_xlabel("Blind seed")
    ax.set_ylabel("Test NMSE")
    ax.set_title("P5 one-shot blind evaluation: 8 / 10 seeds below 0.05", fontweight="bold")
    ax.text(0.0, 0.125, "Seeds 227 and 229 failed the per-seed threshold and were kept in the record.",
            fontsize=7.5, style="italic")
    save(fig, "fig4_p5_blind_seeds.png")


# --- Figure 5: P6 gate status ---------------------------------------------
def fig_gates() -> None:
    gates = [
        ("G0 provenance", "PASS"), ("G1 cross-section / delay", "PASS"),
        ("G2 layout route", "PASS"), ("G3-A straight de-embed", "PASS"),
        ("G3-B bend / crosstalk", "PASS"), ("G3-C tap / splitter", "FAIL / REDESIGN"),
        ("G3-D 2x2 combiner", "FAIL / REDESIGN"), ("G4 fast switch S-params", "OPEN"),
        ("G4 PD / TIA chain", "OPEN"), ("G4 thermal budget", "OPEN"),
        ("G5 full-link composition", "OPEN"),
    ]
    cmap = {"PASS": PASS, "FAIL / REDESIGN": FAILC, "OPEN": OPENC}
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ys = range(len(gates))
    ax.barh(list(ys), [1] * len(gates), color=[cmap[s] for _, s in gates], edgecolor=INK, linewidth=1)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([g for g, _ in gates], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xticks([])
    for y, (_, s) in zip(ys, gates):
        ax.text(0.5, y, s, ha="center", va="center", color="white", fontweight="bold", fontsize=8)
    ax.set_title("P6 physical-acceptance audit (G6): 5 PASS, 2 FAIL/REDESIGN, 4 OPEN\n"
                 "Overall verdict: NOT_PHYSICALLY_ACCEPTED", fontweight="bold", fontsize=10)
    save(fig, "fig5_p6_gate_status.png")


if __name__ == "__main__":
    fig_pipeline()
    fig_architecture()
    fig_nmse()
    fig_blind_seeds()
    fig_gates()
    print("done")
