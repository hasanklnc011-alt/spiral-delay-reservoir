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


# --- Figure 0: how the system works (end-to-end signal flow) ------------------
def fig_how_it_works() -> None:
    fig = plt.figure(figsize=(13.5, 7.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.0], hspace=0.30)
    ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 20); ax.set_ylim(1.0, 11.4); ax.axis("off")

    def box(x, w, y, h, text, fc, fs=8.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    linewidth=1.4, edgecolor=INK, facecolor=fc))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x0, y0, x1, y1, color=INK):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                     mutation_scale=15, color=color, linewidth=1.3))

    E, O, D = "#e9e9e9", GOLD + "2a", LIME + "2a"
    y0, h = 7.4, 2.35
    box(0.2, 2.5, y0, h, "NARMA-10\ninput  u[t]\n(electrical)", E)
    box(3.1, 2.2, y0, h, "Laser\n(CW, ~1550 nm)", E)
    box(5.8, 2.5, y0, h, "EO modulator\nwrites u[t] onto\nlight  (10 GBd)", E)
    box(8.7, 3.5, y0, h, "01 · Spiral delay line\nsingle waveguide, 14.24 cm,\n93 turns, n_g ≈ 4  →  ≤ 19 symbols\n20 taps:  tap k → u[t−k]", O, 7.4)
    box(12.7, 3.4, y0, h, "02 · EO routing + combine\n3 slots / symbol (30 GHz)\npick tap pairs, add fields:\nE_i + E_j   or   E_i + LO", O, 7.4)
    box(16.6, 3.2, y0, h, "03 · 10× photodiode + TIA\nsquare-law:  I ∝ |E_i + E_j|²\n→ cross term  u[t−i]·u[t−j]", O, 7.4)

    for x0, x1 in [(2.7, 3.1), (5.3, 5.8), (8.3, 8.7), (12.2, 12.7), (16.2, 16.6)]:
        arrow(x0, y0 + h / 2, x1, y0 + h / 2)
    # role labels just under the optical boxes
    for cx, txt in [(10.45, "memory"), (14.4, "routing / interference"), (18.2, "nonlinearity")]:
        ax.text(cx, y0 - 0.22, txt, ha="center", va="top", fontsize=7.4, style="italic", color="#55605a")
    # LO branch: laser -> down -> along (clear of the role labels) -> up into block 02
    lo_y = 6.35
    ax.add_patch(FancyArrowPatch((4.2, y0), (4.2, lo_y), arrowstyle="-", color=GOLD, linewidth=1.6))
    ax.add_patch(FancyArrowPatch((4.2, lo_y), (14.4, lo_y), arrowstyle="-", color=GOLD, linewidth=1.6))
    ax.add_patch(FancyArrowPatch((14.4, lo_y), (14.4, y0), arrowstyle="-|>", mutation_scale=14, color=GOLD, linewidth=1.6))
    ax.text(8.4, lo_y - 0.26, "LO reference (split from the same laser)", ha="center", fontsize=7, color=GOLD, style="italic")
    ax.plot([8.7, 19.8], [y0 + h + 0.3, y0 + h + 0.3], color=GOLD, linewidth=1.4)
    ax.text(14.25, y0 + h + 0.5, "on-chip optical core", ha="center", fontsize=8.5, color=GOLD, fontweight="bold")
    ax.text(10.0, 11.1, "How the system works — one laser beam carries the data; the spiral stores its "
            "recent history; interference + square-law detection make the features",
            ha="center", va="top", fontsize=10.2, fontweight="bold")

    # digital chain, its own clean row below the optical core
    yd, hd = 3.2, 1.95
    box(9.3, 3.0, yd, hd, "30 numbers\nper symbol\n(feature vector)", E, 7.8)
    box(13.0, 3.6, yd, hd, "trained linear\nridge readout\n(digital — the only\ntrained part)", D, 7.8)
    box(17.4, 2.5, yd, hd, "NARMA-10\nprediction", D)
    # 03 down into the digital row
    jy = yd + hd + 0.55
    ax.add_patch(FancyArrowPatch((18.2, y0), (18.2, jy), arrowstyle="-", color=INK, linewidth=1.3))
    ax.add_patch(FancyArrowPatch((18.2, jy), (10.8, jy), arrowstyle="-", color=INK, linewidth=1.3))
    ax.add_patch(FancyArrowPatch((10.8, jy), (10.8, yd + hd), arrowstyle="-|>", mutation_scale=14, color=INK, linewidth=1.3))
    arrow(12.3, yd + hd / 2, 13.0, yd + hd / 2)
    arrow(16.6, yd + hd / 2, 17.4, yd + hd / 2)
    ax.text(14.5, jy + 0.22, "10 PDs × 3 slots", ha="center", fontsize=7, color="#55605a", style="italic")

    ax.text(10.0, 1.2, "P6 note: the 02 combiner and the 01 tap splitters are not yet physically accepted "
            "(gates G3-C / G3-D). This diagram is the concept — not a fabricated device.",
            ha="center", va="bottom", fontsize=7.4, color=RED)

    # bottom: 100 ps timeline
    tl = fig.add_subplot(gs[1]); tl.set_xlim(0, 100); tl.set_ylim(0, 1); tl.set_yticks([])
    tl.set_xlabel("time within one symbol (picoseconds)", fontsize=8)
    for a, b, lab, feat in [(0, 33, "SLOT 1", "features 1–10"),
                            (33, 66, "SLOT 2", "features 11–20"),
                            (66, 100, "SLOT 3", "features 21–30")]:
        tl.add_patch(FancyBboxPatch((a + 1, 0.15), b - a - 2, 0.7, boxstyle="round,pad=0.02",
                                    edgecolor=INK, facecolor=GOLD + "26", linewidth=1.2))
        tl.text((a + b) / 2, 0.62, lab, ha="center", fontweight="bold", fontsize=8.5)
        tl.text((a + b) / 2, 0.35, f"EO reconfigures → 10 PDs measure → {feat}", ha="center", fontsize=7.3)
    tl.set_title("Inside one 100 ps symbol: the EO block runs 3 configurations; 10 PDs × 3 slots = 30 numbers",
                 fontsize=9, fontweight="bold")
    tl.tick_params(labelsize=7)
    save(fig, "fig0_how_it_works.png")


if __name__ == "__main__":
    fig_how_it_works()
    fig_pipeline()
    fig_architecture()
    fig_nmse()
    fig_blind_seeds()
    fig_gates()
    print("done")
