"""Render docs/figures/system-animation.gif — a short looping animation of the
whole running system, for embedding in the README (GitHub autoplays GIFs).

Top: a light-pulse train crawls the spiral delay line past 20 taps; the
electro-optic block cycles 3 slots per 100 ps symbol; 10 photodiodes flash as
they measure. Bottom: the symbol clock, the 30-value feature vector filling slot
by slot, and a small ridge read-out tracking the NARMA-10 target.

Concept only — drawn to the project's numbers, not a fabricated device.

    python scripts/make_animation_gif.py
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "figures" / "system-animation.gif"

INK, DIM, FAINT = "#e7edf2", "#9aa9b6", "#63727e"
BG, PANEL, GOLD, CYAN, VIOLET, SEA, AMBER, RUST = (
    "#12181f", "#171f28", "#c9a24b", "#5fd6d2", "#b3a0e0", "#7cc6a6", "#d9903f", "#c9603f")

NTAP = 20
TURNS = 11
FPS = 14
FRAMES_PER_SLOT = 9
SLOTS = 3
SYMBOLS = 4
FRAMES = FRAMES_PER_SLOT * SLOTS * SYMBOLS
FRAMES_PER_SYMBOL = FRAMES_PER_SLOT * SLOTS

# ---------------------------------------------------------------- NARMA-10 + read-out
rng = np.random.default_rng(20260909)
N = 900
u = 0.5 * rng.random(N)
y = np.zeros(N)
for t in range(10, N):
    s = y[t - 10:t].sum()
    y[t] = np.clip(0.3 * y[t - 1] + 0.05 * y[t - 1] * s + 1.5 * u[t - 10] * u[t - 1] + 0.1, 0, 2)

LO = 0.5
FEAT = ([(k, k + 9) for k in range(1, 11)] +                       # unrolled cross terms
        [(k, "LO") for k in (1, 2, 3, 4, 5, 6, 8, 10, 13, 16)] +   # LO-referenced linear
        [(1, 1), (2, 2), (5, 5), (10, 10), (1, 2), (1, 3), (2, 10), (3, 11), (1, 19), (19, "LO")])
NF = len(FEAT)


def feat_row(t):
    h = [u[t - k] if t - k >= 0 else 0.0 for k in range(NTAP)]
    r = np.empty(NF)
    for f, (a, b) in enumerate(FEAT):
        va = h[a]
        vb = LO if b == "LO" else h[b]
        r[f] = (va + vb) ** 2
    return r


X = np.array([feat_row(t) for t in range(NTAP, N)])
X = np.hstack([X, np.ones((len(X), 1))])
Y = y[NTAP:N]
fit = slice(0, 600)
A = X[fit].T @ X[fit] + 0.3 * np.eye(NF + 1)
w = np.linalg.solve(A, X[fit].T @ Y[fit])
pred = X @ w
# illustrative NMSE over a held-out stretch
hold = slice(620, 860)
demo_nmse = np.mean((pred[hold] - Y[hold]) ** 2) / np.var(Y[hold])
FEAT_VALS = X[700, :NF]                                    # a representative feature vector
V0 = 700                                                   # sparkline window start (in X index)
WIN = 90

# ---------------------------------------------------------------- spiral geometry
_pts = []
r0 = 0.06
b = (1.0 - r0) / (TURNS * 2 * math.pi)
th = TURNS * 2 * math.pi
while th >= 0:
    r = r0 + b * th
    _pts.append((r * math.cos(th), r * math.sin(th)))
    th -= 0.05
_cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff([p[0] for p in _pts]), np.diff([p[1] for p in _pts])))])
_total = _cum[-1]
_px = np.array([p[0] for p in _pts])
_py = np.array([p[1] for p in _pts])


def on_spiral(s):
    s = min(1.0, max(0.0, s))
    i = int(np.searchsorted(_cum, s * _total))
    i = max(1, min(i, len(_pts) - 1))
    seg = _cum[i] - _cum[i - 1] or 1.0
    f = (s * _total - _cum[i - 1]) / seg
    return (_px[i - 1] + (_px[i] - _px[i - 1]) * f, _py[i - 1] + (_py[i] - _py[i - 1]) * f)


# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(9.0, 6.4), dpi=112)
fig.patch.set_facecolor(BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1.62, 1.0], width_ratios=[0.9, 1.15, 1.5],
                      hspace=0.05, wspace=0.22, left=0.015, right=0.985, top=0.985, bottom=0.055)

ax = fig.add_subplot(gs[0, :]); ax.set_facecolor(BG)
ax.set_xlim(-1.15, 2.22); ax.set_ylim(-1.5, 1.42); ax.set_aspect("equal"); ax.axis("off")
ax.plot(_px, _py, color=GOLD, lw=0.8, alpha=0.55, solid_capstyle="round")
tap_xy = [on_spiral(k / (NTAP - 1)) for k in range(NTAP)]
ax.scatter([p[0] for p in tap_xy], [p[1] for p in tap_xy], s=24, color="#f0d9a0",
           edgecolors=BG, linewidths=0.6, zorder=4)

EO_X, EO_W, EO_Y0, EO_Y1 = 1.32, 0.16, -0.95, 0.95
ax.add_patch(FancyBboxPatch((EO_X, EO_Y0), EO_W, EO_Y1 - EO_Y0, boxstyle="round,pad=0.01",
                            ec=VIOLET, fc="#b3a0e01a", lw=1.2))
PD_X, PD_W, PD_H = 1.63, 0.46, 0.135
pd_y = [EO_Y1 - 0.09 - i * ((EO_Y1 - EO_Y0 - 0.18) / 9) - PD_H for i in range(10)]
pd_patches = []
for yv in pd_y:
    p = FancyBboxPatch((PD_X, yv), PD_W, PD_H, boxstyle="round,pad=0.005", ec=SEA, fc="#7cc6a614", lw=1.0)
    ax.add_patch(p); pd_patches.append(p)
    ax.text(PD_X + 0.03, yv + PD_H / 2, "PD/TIA", color=DIM, fontsize=5, va="center", family="monospace")
ax.plot([EO_X + EO_W / 2, EO_X + EO_W / 2, PD_X + PD_W], [EO_Y0, EO_Y0 - 0.12, EO_Y0 - 0.12],
        color=AMBER, lw=1.1, alpha=0.8)
ax.text((EO_X + PD_X) / 2, EO_Y0 - 0.22, "LO + STATIC PHASE TRIM", color=AMBER, fontsize=5, ha="center", family="monospace")
ax.text(-1.12, 1.34, "Light Through the Spiral", color=INK, fontsize=12.5, fontweight="bold")
ax.text(-1.12, 1.17, "coherent delay reservoir · 10 GBd · 1 symbol = 100 ps",
        color=DIM, fontsize=6, family="monospace")
ax.text(-1.12, -1.30, "01 · SPIRAL DELAY — 20 taps — 14.24 cm  (turns drawn sparser than the real 93)",
        color=FAINT, fontsize=5.4, family="monospace")
ax.text(-1.12, -1.44, "P6: NOT PHYSICALLY ACCEPTED — this is the concept, not a fabricated device",
        color=RUST, fontsize=5.4, family="monospace")
ax.text(1.32, 1.10, "02 · EO", color=FAINT, fontsize=5.8, family="monospace")
ax.text(1.63, 1.10, "03 · 10 RECEIVERS   |E_i+E_j|² → u[t−i]·u[t−j]", color=FAINT, fontsize=5.4, family="monospace")

pulse_scat = ax.scatter([], [], s=[], color=CYAN, zorder=6)
flash_scat = ax.scatter([], [], s=[], facecolors="none", edgecolors=CYAN, zorder=5, lw=1.1)
slot_tick = ax.plot([], [], color=VIOLET, lw=3, solid_capstyle="round")[0]
slot_txt = ax.text(EO_X + EO_W / 2, 0, "", color=VIOLET, fontsize=6, rotation=90, ha="center", va="center",
                   family="monospace", fontweight="bold")
sym_txt = ax.text(-1.1, 0.99, "", color=CYAN, fontsize=6.5, family="monospace")
beam_lines = [ax.plot([], [], color=CYAN, lw=0.9, alpha=0.0)[0] for _ in range(10)]
tap_flash = np.zeros(NTAP)

# --- bottom-left: symbol clock
axc = fig.add_subplot(gs[1, 0]); axc.set_facecolor(PANEL)
axc.set_xlim(0, 3); axc.set_ylim(0, 1.35); axc.axis("off")
axc.text(0.05, 1.16, "SYMBOL CLOCK — 100 ps", color=FAINT, fontsize=5.6, family="monospace")
slot_bg, slot_fill = [], []
for i in range(3):
    axc.add_patch(Rectangle((i + 0.06, 0.15), 0.88, 0.8, ec="#2a3642", fc=BG, lw=1))
    f = Rectangle((i + 0.06, 0.15), 0.0, 0.8, ec="none", fc="#b3a0e0", alpha=0.45)
    axc.add_patch(f); slot_fill.append(f)
    axc.text(i + 0.5, 0.55, f"SLOT {i+1}", color=DIM, fontsize=5.6, ha="center", va="center", family="monospace")

# --- bottom-middle: 30-value feature vector
axg = fig.add_subplot(gs[1, 1]); axg.set_facecolor(PANEL)
axg.set_xlim(0, 10); axg.set_ylim(-0.5, 3.4); axg.axis("off")
axg.text(0.0, 3.15, "FEATURE VECTOR — 10 PD × 3 slots", color=FAINT, fontsize=5.6, family="monospace")
cell_rects = []
for r in range(3):
    for c in range(10):
        rect = Rectangle((c + 0.08, (2 - r) + 0.08), 0.84, 0.84, ec="#2a3642", fc=BG, lw=0.7)
        axg.add_patch(rect); cell_rects.append(rect)

# --- bottom-right: read-out tracking NARMA-10
axr = fig.add_subplot(gs[1, 2]); axr.set_facecolor(PANEL)
tgt = Y[V0:V0 + WIN]; prd = pred[V0:V0 + WIN]
lo_v = min(tgt.min(), prd.min()); hi_v = max(tgt.max(), prd.max()); pad = (hi_v - lo_v) * 0.12
axr.set_xlim(0, WIN - 1); axr.set_ylim(lo_v - pad, hi_v + pad); axr.axis("off")
axr.text(0.0, hi_v + pad * 0.2, "READ-OUT — prediction vs NARMA-10 target", color=FAINT, fontsize=5.6,
         family="monospace", transform=axr.transData)
axr.plot(range(WIN), tgt, color=DIM, lw=1.3, alpha=0.75)
axr.plot(range(WIN), prd, color=CYAN, lw=1.4)
playhead = axr.axvline(0, color=VIOLET, lw=1.0, alpha=0.7)
head_dot = axr.plot([], [], "o", color=CYAN, ms=4)[0]
axr.text(WIN - 1, lo_v - pad * 0.55, f"demo NMSE ≈ {demo_nmse:.3f}   ·   locked blind result 0.0387",
         color=DIM, fontsize=5.3, ha="right", family="monospace")


def animate(fi):
    global tap_flash
    within = fi % FRAMES_PER_SLOT
    slot = (fi // FRAMES_PER_SLOT) % SLOTS
    symbol = fi // FRAMES_PER_SYMBOL
    p = (fi % FRAMES_PER_SYMBOL) / FRAMES_PER_SYMBOL

    # pulses on the spiral
    px, py, ps = [], [], []
    for age in range(NTAP):
        s = (age + p) / (NTAP - 1)
        if s > 1.0:
            continue
        x, yv = on_spiral(s)
        px.append(x); py.append(yv); ps.append(66 if age == 0 else 24)
    pulse_scat.set_offsets(np.c_[px, py]); pulse_scat.set_sizes(ps)

    if within == 0 and slot == 0:
        tap_flash[:] = 1.0
    fx = [tap_xy[k][0] for k in range(NTAP) if tap_flash[k] > 0.03]
    fy = [tap_xy[k][1] for k in range(NTAP) if tap_flash[k] > 0.03]
    fs = [40 + (1 - tap_flash[k]) * 240 for k in range(NTAP) if tap_flash[k] > 0.03]
    flash_scat.set_offsets(np.c_[fx, fy] if fx else np.empty((0, 2)))
    flash_scat.set_sizes(fs if fs else [])
    flash_scat.set_alpha(float(tap_flash.max()) if fx else 0.0)
    tap_flash[:] = np.maximum(0.0, tap_flash - 1.0 / FRAMES_PER_SLOT)

    yy = EO_Y0 + (EO_Y1 - EO_Y0) * (slot + 0.5) / 3
    slot_tick.set_data([EO_X + EO_W / 2 - 0.05, EO_X + EO_W / 2 + 0.05], [yy, yy])
    slot_txt.set_position((EO_X + EO_W / 2, yy)); slot_txt.set_text(f"SLOT {slot+1}/3")
    sym_txt.set_text(f"symbol {symbol}   ·   slot {slot+1} of 3")
    glow = math.sin(min(1, within / FRAMES_PER_SLOT) * math.pi)
    for i, ln in enumerate(beam_lines):
        ln.set_data([EO_X + EO_W, PD_X], [yy, pd_y[i] + PD_H / 2])
        ln.set_alpha(0.10 + 0.55 * glow)
        pd_patches[i].set_alpha(0.4 + 0.6 * glow)

    # clock fills
    for i, f in enumerate(slot_fill):
        local = min(1.0, max(0.0, p * 3 - i))
        f.set_width(0.88 * local)

    # feature cells: reveal slot's 10 as it completes
    revealed = slot * 10 + int(within / FRAMES_PER_SLOT * 10)
    for idx, rect in enumerate(cell_rects):
        if idx < revealed:
            v = FEAT_VALS[idx]
            rect.set_facecolor((0.486, 0.776, 0.651, min(1.0, 0.25 + v * 0.9)))
        else:
            rect.set_facecolor(BG)

    # read-out playhead sweeps the window, looping
    hp = (fi / FRAMES) * (WIN - 1)
    playhead.set_xdata([hp, hp])
    head_dot.set_data([hp], [np.interp(hp, range(WIN), prd)])

    return [pulse_scat, flash_scat, slot_tick, slot_txt, sym_txt, playhead, head_dot,
            *beam_lines, *pd_patches, *slot_fill, *cell_rects]


anim = FuncAnimation(fig, animate, frames=FRAMES, interval=1000 / FPS, blit=False)
OUT.parent.mkdir(parents=True, exist_ok=True)
anim.save(OUT, writer=PillowWriter(fps=FPS))
print("wrote", OUT.relative_to(ROOT), f"({OUT.stat().st_size/1e6:.1f} MB, {FRAMES} frames, demo NMSE {demo_nmse:.3f})")
plt.close(fig)
