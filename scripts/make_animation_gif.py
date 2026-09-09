"""Render docs/figures/system-animation.gif — a short looping animation of the
running system, for embedding directly in the README (GitHub autoplays GIFs).

A light pulse train crawls the spiral delay line past 20 taps; the electro-optic
block cycles 3 slots per 100 ps symbol; 10 photodiodes flash as they measure.
Concept only — drawn to the project's numbers, not a fabricated device.

    python scripts/make_animation_gif.py
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "figures" / "system-animation.gif"

INK, DIM, FAINT = "#e7edf2", "#9aa9b6", "#63727e"
BG, GOLD, CYAN, VIOLET, SEA, AMBER, RUST = (
    "#12181f", "#c9a24b", "#5fd6d2", "#b3a0e0", "#7cc6a6", "#d9903f", "#c9603f")

NTAP = 20
TURNS = 11
FRAMES_PER_SLOT = 9
SLOTS = 3
SYMBOLS = 4
FRAMES = FRAMES_PER_SLOT * SLOTS * SYMBOLS
FPS = 14

# ---- spiral geometry (outer entry -> centre), arc-length parametrised ----
_pts = []
r0 = 0.06
b = (1.0 - r0) / (TURNS * 2 * math.pi)
th = TURNS * 2 * math.pi
while th >= 0:
    r = r0 + b * th
    _pts.append((r * math.cos(th), r * math.sin(th)))
    th -= 0.05
_cum = [0.0]
for i in range(1, len(_pts)):
    _cum.append(_cum[-1] + math.hypot(_pts[i][0] - _pts[i - 1][0], _pts[i][1] - _pts[i - 1][1]))
_total = _cum[-1]


def on_spiral(s: float):
    s = max(0.0, min(1.0, s))
    target = s * _total
    lo, hi = 0, len(_cum) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if _cum[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    i = max(1, lo)
    seg = _cum[i] - _cum[i - 1] or 1.0
    f = (target - _cum[i - 1]) / seg
    return (_pts[i - 1][0] + (_pts[i][0] - _pts[i - 1][0]) * f,
            _pts[i - 1][1] + (_pts[i][1] - _pts[i - 1][1]) * f)


fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=110)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-1.15, 2.20)
ax.set_ylim(-1.52, 1.42)
ax.set_aspect("equal")
ax.axis("off")

# static spiral
sx = [p[0] for p in _pts]
sy = [p[1] for p in _pts]
ax.plot(sx, sy, color=GOLD, lw=0.8, alpha=0.55, solid_capstyle="round")

tap_s = [k / (NTAP - 1) for k in range(NTAP)]
tap_xy = [on_spiral(s) for s in tap_s]
ax.scatter([p[0] for p in tap_xy], [p[1] for p in tap_xy], s=26, color="#f0d9a0",
           edgecolors=BG, linewidths=0.6, zorder=4)

# EO block + PDs (to the right of the spiral)
EO_X, EO_W, EO_Y0, EO_Y1 = 1.30, 0.16, -0.95, 0.95
ax.add_patch(FancyBboxPatch((EO_X, EO_Y0), EO_W, EO_Y1 - EO_Y0,
                            boxstyle="round,pad=0.01", ec=VIOLET, fc="#b3a0e01a", lw=1.2))
PD_X, PD_W, PD_H = 1.62, 0.46, 0.14
pd_y = [EO_Y1 - 0.09 - i * ((EO_Y1 - EO_Y0 - 0.18) / 9) - PD_H for i in range(10)]
pd_patches = []
for y in pd_y:
    p = FancyBboxPatch((PD_X, y), PD_W, PD_H, boxstyle="round,pad=0.005",
                       ec=SEA, fc="#7cc6a614", lw=1.0)
    ax.add_patch(p)
    pd_patches.append(p)
    ax.text(PD_X + 0.03, y + PD_H / 2, "PD/TIA", color=DIM, fontsize=5.2,
            va="center", family="monospace")

# LO rail
ax.plot([EO_X + EO_W / 2, EO_X + EO_W / 2, PD_X + PD_W], [EO_Y0, EO_Y0 - 0.12, EO_Y0 - 0.12],
        color=AMBER, lw=1.1, alpha=0.8)
ax.text((EO_X + PD_X) / 2, EO_Y0 - 0.22, "LO + STATIC PHASE TRIM", color=AMBER,
        fontsize=5.2, ha="center", family="monospace")

# labels
ax.text(-1.1, 1.34, "Light Through the Spiral", color=INK, fontsize=13, fontweight="bold")
ax.text(-1.1, 1.18, "coherent delay reservoir  ·  10 GBd  ·  1 symbol = 100 ps = 3 slots",
        color=DIM, fontsize=6.5, family="monospace")
ax.text(-1.1, -1.30, "01 · SPIRAL DELAY — 20 taps — 14.24 cm  (turns drawn sparser than the real 93)",
        color=FAINT, fontsize=5.6, family="monospace")
ax.text(-1.1, -1.45, "P6: NOT PHYSICALLY ACCEPTED — this is the concept, not a fabricated device",
        color=RUST, fontsize=5.6, family="monospace")
ax.text(1.30, 1.16, "02 · EO", color=FAINT, fontsize=6.0, family="monospace")
ax.text(1.62, 1.16, "03 · 10 RECEIVERS   |E_i+E_j|² → u[t−i]·u[t−j]", color=FAINT,
        fontsize=5.6, family="monospace")

pulse_scat = ax.scatter([], [], s=[], color=CYAN, zorder=6)
flash_scat = ax.scatter([], [], s=[], facecolors="none", edgecolors=CYAN, zorder=5, lw=1.2)
slot_txt = ax.text(EO_X + EO_W / 2, 0, "", color=VIOLET, fontsize=6.5, rotation=90,
                   ha="center", va="center", family="monospace", fontweight="bold")
sym_txt = ax.text(-1.1, 0.86, "", color=CYAN, fontsize=7, family="monospace")
beam_lines = [ax.plot([], [], color=CYAN, lw=0.9, alpha=0.0)[0] for _ in range(10)]
slot_tick = ax.plot([], [], color=VIOLET, lw=3, solid_capstyle="round")[0]

tap_flash = [0.0] * NTAP


def frame(fi: int):
    global tap_flash
    within = fi % FRAMES_PER_SLOT
    slot = (fi // FRAMES_PER_SLOT) % SLOTS
    symbol = fi // (FRAMES_PER_SLOT * SLOTS)
    p = ((fi % (FRAMES_PER_SLOT * SLOTS)) / (FRAMES_PER_SLOT * SLOTS))  # 0..1 within symbol

    # pulses: age 0..NTAP-1 along the spiral
    px, py, ps = [], [], []
    for age in range(NTAP):
        s = (age + p) / (NTAP - 1)
        if s > 1.0:
            continue
        x, y = on_spiral(s)
        px.append(x); py.append(y); ps.append(70 if age == 0 else 26)
    pulse_scat.set_offsets(list(zip(px, py)))
    pulse_scat.set_sizes(ps)

    # tap hand-off flash at each new symbol (frame 0 of the symbol)
    if within == 0 and slot == 0:
        tap_flash = [1.0] * NTAP
    fx, fy, fs = [], [], []
    for k in range(NTAP):
        if tap_flash[k] > 0.03:
            fx.append(tap_xy[k][0]); fy.append(tap_xy[k][1])
            fs.append(40 + (1 - tap_flash[k]) * 260)
    flash_scat.set_offsets(list(zip(fx, fy)) if fx else [[0, 0]])
    flash_scat.set_sizes(fs if fs else [0])
    flash_scat.set_alpha(max(tap_flash) if fx else 0)
    tap_flash = [max(0.0, v - 1.0 / FRAMES_PER_SLOT) for v in tap_flash]

    # EO slot indicator
    yy = EO_Y0 + (EO_Y1 - EO_Y0) * (slot + 0.5) / 3
    slot_tick.set_data([EO_X + EO_W / 2 - 0.05, EO_X + EO_W / 2 + 0.05], [yy, yy])
    slot_txt.set_position((EO_X + EO_W / 2, yy))
    slot_txt.set_text(f"SLOT {slot + 1}/3")
    sym_txt.set_text(f"symbol {symbol}   slot {slot + 1}")

    # beams EO -> PD, brighten over the slot then fade
    glow = math.sin(min(1, within / FRAMES_PER_SLOT) * math.pi)
    for i, ln in enumerate(beam_lines):
        y0 = yy
        y1 = pd_y[i] + PD_H / 2
        ln.set_data([EO_X + EO_W, PD_X], [y0, y1])
        ln.set_alpha(0.10 + 0.55 * glow)
        pd_patches[i].set_alpha(0.4 + 0.6 * glow)
    for i in range(10):
        pass

    return [pulse_scat, flash_scat, slot_tick, slot_txt, sym_txt, *beam_lines, *pd_patches]


anim = FuncAnimation(fig, frame, frames=FRAMES, interval=1000 / FPS, blit=False)
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
OUT.parent.mkdir(parents=True, exist_ok=True)
anim.save(OUT, writer=PillowWriter(fps=FPS))
print("wrote", OUT.relative_to(ROOT), f"({OUT.stat().st_size/1e6:.1f} MB, {FRAMES} frames)")
plt.close(fig)
