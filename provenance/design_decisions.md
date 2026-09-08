# Design decisions (ADRs)

## ADR-001 — Preserve the P5 / P6 separation
**Context:** a benchmark result and component physical evidence are different
claims. **Alternatives:** tune the architecture using blind outcomes; keep the
blind result locked. **Decision:** keep the blind result locked; never feed P6
findings back into P5. **Consequences:** P6 may stay `NOT_PHYSICALLY_ACCEPTED`
while P5 remains reported. **Status:** accepted.

## ADR-002 — Retire protocol v1 unused
**Context:** protocol v1 required the noisy physical candidate to beat its own
lossless digital twin by 10 %, which is logically impossible. **Decision:** retire
v1 with zero blind evaluations; in v2 the digital twin is a reported upper bound
and superiority is measured against `delayed_input` and `no_photonic_core`.
**Status:** accepted.

## ADR-003 — Coherent delay architecture over the three-ring line
**Context:** the three-ring TCMT line had a narrow claim level, platform-specific
memory, and poor separability from digital equivalents. **Decision:** move the
main line to an explicit coherent optical delay + square-law readout; archive the
three-ring work. **Status:** accepted. See `../docs/DEVELOPMENT_HISTORY.md`.

## ADR-004 — Custom 343 x 180 nm process, not a 220 nm PDK
**Context:** public 50G-class PDKs are 220 nm silicon, incompatible with the G1
`180 ± 5 nm` lock; a licensed active PDK would reopen G1-G4. **Decision:** keep a
custom-process pre-design and freeze a validation contract
(`../p6-physical-validation/CUSTOM-PROCESS-VALIDATION.md`). **Status:** accepted.

## ADR-005 — Blender scene is a presentation model
**Context:** the scene has labelled architectural elements but no verified
fabrication provenance, and the saved `mcp.blend` is near-empty. **Decision:**
label all Blender geometry as presentation-level; add a data-derived spiral
reference built from the committed centerline so the geometry is reproducible
from evidence. **Status:** accepted.

## ADR-006 — Reorganization keeps code paths unchanged
**Context:** the target information architecture would rename the phase folders,
but `p6-physical-validation` code and tests resolve sibling paths
(`p5-publication/…`, `configs/…`) and hash-check `configs/baseline-v1.json`.
**Decision:** promote the research code to the repository root but keep every
phase folder's name and internal layout byte-identical; deliver navigability
through `docs/`, the README, per-phase indices, and a P6 landing page.
**Consequences:** folder names stay Turkish-era (`p1-coherent-delay`, …) rather
than the prettier `studies/p1_ideal_coherent_delay`. **Status:** accepted.

## ADR-007 — Raw evidence via Git LFS, not exclusion
**Context:** the curated P6 HDF5 solver outputs (~169 MB, 59 files) are cited by the provenance
hash checks. **Decision:** track them (and the GDS + large centerline CSV + the
Blender files) with Git LFS under their original paths, rather than excluding
them. Eight unlabeled scratch HDF5 files are kept in a clearly named
`_unclassified_solver_scratch/` folder. **Status:** accepted.
