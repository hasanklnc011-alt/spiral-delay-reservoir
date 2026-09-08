# Limitations

Stated explicitly, by category. In an academic repository, naming these increases
credibility rather than reducing it.

## Computational limitations

- The feature family is **linear + bilinear** (lags and pairwise products). Any
  NARMA-10 structure not captured by that family is out of reach; seed 23 is a
  consistent example — it is a dataset-specific hard case for this hypothesis,
  present from P1's ideal model onward, not a hardware artefact.
- The readout is linear ridge regression only. No nonlinear post-processing.
- Blind seeds 227 and 229 exceed the per-seed 0.05 threshold. They are kept in
  the record; the median and 8/10-seed gates still pass.
- The blind test is a **single** evaluation by design. It cannot be repeated, so
  there is no blind-set variance estimate beyond the within-run bootstrap.

## System-model limitations

- P3/P4 are **system-level simulations** with parameterized loss, noise, phase
  error and bandwidth — not a circuit or layout.
- The 100 mW "simultaneous optical budget" is a conservative constructed figure,
  **not** a laser wall-plug power or a single-launch power.
- Splitter-tree division loss and ideal fan-out penalty were not fully modelled
  inside P3/P5; P6 treats them as a separate, still-open budget item.
- The digital twin is lossless and noiseless; the 19.2 % penalty is the modelled
  cost of the physical implementation *as parameterized*, not a measured cost.

## Component-model limitations (P6)

- `n_g ≈ 4` is a **design input that P6 verifies**, not a platform that was
  selected up front. The chosen 343 × 180 nm cross-section is a **custom-process
  pre-design**, not a foundry PDK entry.
- The spiral layout is an EM-checked centerline/GDS with DRC, **not** a full
  mask with all routing, I/O, and metal.
- Propagation loss (`0.8 dB/cm`) is assumption-only; a physical loss acceptance
  needs fabricated cutback / PDK data.
- The progressive tap / LO splitter (G3-C) and the 2×2 coherent combiner (G3-D)
  **fail** their acceptance gates with every generic geometry tried; they require
  a foundry-qualified S-matrix or a dedicated optimized cell.
- 30 GHz fast switching, a measured 50 GHz PD/TIA chain, and a full thermal
  (`Pπ`, time constant, crosstalk) matrix are **not available** (G4 OPEN).
- The full-link composition (G5) cannot be completed while the above are missing.

## Fabrication / experimental limitations

- **Nothing has been fabricated.** There is no PIC, no wafer, no measurement.
- No foundry qualification, no tape-out, no experimental 30 GHz switching, no
  measured detector/TIA chain, no measured thermal matrix.
- The Blender scene [`../artifacts/blender/`](../artifacts/blender/) is a
  presentation/visualization aid, not a fabrication layout, not a GDS source, and
  not experimental geometry. The author's hand-built scene is not saved in
  `mcp.blend` (that file is near-empty); the committed renders are
  (a) a capture from the author's live Blender session and (b) a data-derived
  reconstruction of the spiral from `spiral-centerline-v1.csv`.

## Repository limitations

- The 67 P6 HDF5 files (59 curated solver outputs + 8 unclassified) are tracked with **Git LFS**; a plain `git clone`
  without LFS fetches pointer files only.
- Eight unlabeled solver-scratch HDF5 files are kept under
  `p6-physical-validation/_unclassified_solver_scratch/` with **unclear
  provenance** — they were preserved rather than deleted, but are not cited by any
  result.
- Some `p6-physical-validation` unit tests require the Tidy3D SDK and its
  `autograd` dependency; without them ~10 inverse-design tests error at import
  (pre-existing; unrelated to the reorganization). The 50-test package suite and
  the ~80 other P6 tests pass.
