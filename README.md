# Hybrid Electro-Photonic PIC / Photonic Reservoir

Academic archive of a reservoir-computing-inspired integrated photonics study. The repository combines a Blender presentation model with a traceable Python research record.

> **Evidence boundary.** The reported NARMA-10 result is from a physically parameterized system simulation. It is **not** a fabricated PIC, a foundry-ready layout, or experimental device validation.

![P6 architecture overview](docs/figures/p6_overview_session_render.png)

## 1. Overview

The project investigates a recurrent photonic architecture in which coherent delay, optical interference, photodetection, and a linear readout are used to form memory-like temporal features for NARMA-10. The current presentation model depicts the P6 architecture and its 20 delay taps, 10 receiver branches, and electro-optic routing concept.

## 2. Research objective

The objective is to assess whether a physically motivated, on-chip photonic architecture can support reservoir-computing-inspired temporal processing. The work uses the careful terms *RNN-like dynamics*, *memory-like temporal response*, and *recurrent photonic architecture*; it does not claim a trained physical RNN demonstration.

## 3. Scientific motivation

Microring resonators, coherent delay, and photodetection can provide useful nonlinear and temporal feature mechanisms in photonic computing [@donati2024; @bazzanella2022; @gironcastro2024]. The precise memory mechanism and its physical implementation must be demonstrated for the specific platform; literature mechanisms are not automatically transferable.

## 4. Architecture

The model shows a presentation-level P6 architecture: a spiral delay path with 20 labelled taps, routing into 10 receiver branches, local-oscillator branches, combiners, and PD/TIA blocks. The Blender file is a **conceptual presentation model**, not a fabrication layout or simulation geometry. See [design rationale](docs/03_design_rationale.md).

## 5. Why this design

The chain is: temporal-processing problem → coherent delayed features and quadratic detection → tapped delay and receiver architecture → linear readout. P5 evaluates the resulting system model; P6 tests whether required physical components have sufficient evidence. The latter is not yet accepted.

## 6. Repository structure

- `blender/` — authoritative copied Blender scene and documentation render.
- `docs/` — academic overview, methods, results, limitations, and a static navigation interface.
- `scripts/` — staging notes; the canonical source snapshot is under `archive/`.
- `results/` — human-readable result pointers; raw HDF5 outputs are intentionally excluded.
- `references/` — verified identifier-based bibliography and decision mapping.
- `provenance/` — inventory, environment, and evidence log.
- `archive/` — non-destructive snapshot of the source project excluding large HDF5 binaries and Python caches.

## 7. Final Blender model

The copied canonical file is [mcp.blend](blender/scenes/mcp.blend). Its SHA-256 is `cfc4a2951aa98e53c902452a81a85f0a464dbfff2f2e5a853f21c755c998dd96` and matches the local source at archival time. The included render was produced from the connected Blender P6 session; its association with the copied on-disk file is **unverified** because the session had no saved filepath.

## 8. Scripts

The canonical record contains benchmark, model, screening, optimization, and protocol-checking scripts. See [implementation](docs/04_implementation.md). No script was re-run for this archive.

## 9. Results

**Implemented:** locked P0–P5 protocol and P6 physical-validation record.  
**Observed / calculated:** P5 blind median NARMA-10 NMSE `0.0387049671` (8/10 seeds below `0.05`).  
**Not yet validated:** fabricated component performance, foundry layout, PD/TIA/switch evidence, and final physical acceptance.

## 10. Reproduction / usage

Use Python 3.11+ and the dependencies named in the archived `pyproject.toml`. First inspect `archive/canonical-project-records/README.md`, then run only the documented protocol checks. Do not re-run the locked P5 blind suite. Blender 5.2.1 LTS was the connected-session version used to inspect the scene; compatibility of the copied `mcp.blend` with other versions is unverified.

## 11. Limitations

The Blender geometry is not a foundry-ready PIC layout. P6 currently reports `NOT_PHYSICALLY_ACCEPTED`; splitter/combiner, PDK/cutback loss, 30 GHz selector, 50 GHz PD/TIA, and thermal evidence remain open or require redesign. See [limitations](docs/06_limitations.md).

## 12. References

See [references.md](references/references.md) and [references.bib](references/references.bib).
