# Development history

Reconstructed from git history, file timestamps, and the project's own documents.
It exists so that the presence of [`../archive/legacy_three_ring/`](../archive/legacy_three_ring/)
is understandable rather than confusing.

## Timeline

| When | What |
|---|---|
| **2026-08-26** | "Photonic Reservoir" project started as a **SiN three-ring** temporal coupled-mode (TCMT) reservoir, targeting NARMA-3, with parameters seeded from an earlier `tidy3d_small_ring` FDTD study. |
| **2026-08-28** | Three-ring screening and delay-search runs (`archive/legacy_three_ring/runs/2026-08-28T17…`). |
| **2026-08-29** | Three-ring code and validation evidence committed. Claim level explicitly limited: the NARMA-3 metric comes from an **FDTD-spectrum-fitted TCMT surrogate**, not a direct temporal three-ring FDTD benchmark. |
| **late Aug – early Sep 2026** | Research line pivots. The three-ring topology is declared *not required*; what **is** required is a demonstrable physical contribution on a physically realizable core. NARMA-10 (harder, standard) replaces NARMA-3. |
| **2026-09-03** | **P0** benchmark & blind protocol frozen (`configs/p0_narma10_protocol_v2.json`). Development / blind seeds separated; 20 dataset commitments hash-locked. |
| **2026-09-03** | **P1** ideal coherent-delay + square-law hypothesis passes (median 0.022534). **P2** compresses 230 ideal channels to a 30-feature / 10-PD / 3-slot budget. **P3** adds realistic physics (nominal passes, stress fails). **P4** robust optimization passes across 5 hardware × 10 data seeds. |
| **2026-09-03** | Protocol **v1 retired unused** — its "beat your own lossless digital twin by 10 %" gate was logically impossible; **v2** makes the digital twin a reported upper bound. |
| **2026-09-03** | **P5** candidate + source locked; **one** blind run: median test NMSE 0.038705, 8/10 seeds, publication gate passed. |
| **2026-09-04 onward** | **P6** physical-validation campaign: G1 cross-section / `n_g`, G2 spiral layout, G3-A/B straight & bend EM (pass), G3-C tap/splitter and G3-D combiner (fail / redesign), G4 device inputs and G5 composition (open). PDK decision: keep a **custom 343 × 180 nm process**, do not migrate to a 220 nm PDK. |
| **2026-09** | G6 audit: `NOT_PHYSICALLY_ACCEPTED` (5/11 gates). Repository packaged for academic review. |

## Why the architecture changed

The three-ring line hit three limits that the documents record:

1. **Claim fragility.** A TCMT model fitted to a static FDTD spectrum is not an
   FDTD benchmark; the honest claim level was narrow.
2. **Silicon-specific memory.** Free-carrier and thermo-optic memory in silicon
   rings does not transfer to a SiN/Kerr or custom platform; a new memory
   mechanism would have to be designed and defended separately.
3. **Separability.** It was hard to cleanly separate the ring's contribution from
   the modulator/detector chain and from a digital equivalent.

The coherent-delay architecture keeps the transferable parts (masked input →
virtual nodes, linear-only readout, rigorous controls) and replaces the resonant
memory with an **explicit waveguide delay** whose behaviour is transparent and
whose digital twin is straightforward to build — which is exactly what the P5
control suite needs.

## Status of the legacy work

`archive/legacy_three_ring/` is **research history**, kept for reproducibility and
for its failure-mode lessons. Its run scores are **not** used for candidate
selection, success claims, or starting parameters in the current line. No current
code imports it. See [`../archive/legacy_three_ring/README.md`](../archive/legacy_three_ring/README.md).
