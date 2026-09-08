# Scientific background

## Reservoir computing in one paragraph

A reservoir is a **fixed** (untrained) dynamical system that maps an input
sequence into a high-dimensional set of features with two properties: **fading
memory** (features depend on recent inputs, with older inputs decaying) and
**nonlinearity** (features include products/nonlinear functions of past inputs).
Only a linear readout is trained. This makes temporal tasks cheap to learn, and
it puts all the modelling burden on the reservoir's dynamics rather than on
gradient training.

NARMA-10 is a standard reservoir benchmark precisely because it needs both
ingredients: its target depends on the last 10 inputs (memory) and on a bilinear
term (nonlinearity).

## Photonic memory and nonlinearity

In photonic implementations the memory can come from different physical
mechanisms, and the literature is explicit that they must not be conflated:

- **Delay-line / feedback memory** — an optical path length stores the signal for
  a fixed time. Long fiber loops (Donati et al. 2024) or on-chip waveguide
  provide broadband, low-power, well-understood delay.
- **Resonator dynamics** — a ring's photon lifetime and detuning response give a
  short intrinsic memory. A single silicon ring shows at most ~2 bits of
  intrinsic linear memory (Bazzanella et al. 2022).
- **Carrier / thermal dynamics** — in **silicon** rings, two-photon-absorption
  free carriers and thermo-optic heating add slow nonlinear memory. These are
  **platform-specific** and do not transfer to SiN/Kerr or a custom process
  (Giron Castro et al. 2024).

Nonlinearity likewise has several sources: material Kerr/TPA effects, resonant
detuning, or — the choice here — **square-law photodetection**, which turns a
coherent sum of fields `E_i + E_j` into an intensity containing the cross-term
`Re(E_i E_j*)`. That is an intrinsic, passive nonlinearity requiring no nonlinear
optical material.

## Why this project uses coherent delay + square-law detection

Given an input-modulated field `E_i ∝ u[t-i]`:

- `|E_i|²` gives `u[t-i]²` (self terms),
- `|LO + E_i|²` gives linear `u[t-i]` terms (LO-referenced),
- `|E_i + E_j|²` gives `u[t-i]·u[t-j]` (cross terms).

A linear readout over a sufficient set of such intensities spans exactly the
linear-lag and bilinear space NARMA-10 needs — which P1 confirms as an idealized
upper bound. The physical question the rest of the project addresses is whether a
*small, hardware-plausible* subset of these measurements, with real loss, noise,
phase error and bandwidth, still clears the benchmark.

## Relation to recurrent photonic computing

A programmable-weight-bank photonic system (Tait et al. 2017) implements a genuine
continuous-time RNN, `ds/dt = (W y − s)/τ + W_in u`, with trained weights. That is
a **different** architecture. This project does **not** train a physical recurrent
network; "reservoir" here means a fixed nonlinear temporal feature map followed by
a trained linear readout. Multi-ring "deep" reservoirs (Dong et al. 2026) and
hybrid nonlinear-ring + linear-ring-array memory (Ren et al. 2024) are relevant
context for the abandoned three-ring line, not for the current candidate.

## What is deliberately not claimed

- No energy-efficiency or throughput advantage over an electronic baseline (not
  quantified).
- No claim that the optical feature map is *more accurate* than its digital twin
  (it is 19.2 % worse on the blind test).
- No claim of a demonstrated physical device (P6 is incomplete).

References and per-entry roles: [`references/references.md`](references/references.md),
[`references/source_to_design_map.md`](references/source_to_design_map.md).
