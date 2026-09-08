# Software environment

## Research code

- Python `>= 3.11` required; developed and tested on CPython `3.14.7` (Windows).
- Runtime dependencies (pinned in `requirements-lock.txt`, verified 2026-08-29):
  NumPy `2.5.2`, Matplotlib `3.11.1`, and their transitive dependencies.
- Test runner: standard-library `unittest` (no pytest). 50 package tests pass.
- `p6-physical-validation` electromagnetic scripts additionally require the
  **Tidy3D** SDK (`2.12.0` referenced in the records) and, for inverse design,
  `autograd`. Without them ~10 P6 inverse-design tests error at import
  (pre-existing). Cloud solves need Tidy3D credentials and explicit cost
  approval; none are stored in this repository.

## Blender

- Author session: Blender `5.2.1 LTS`, metric units, scale length 1, EEVEE.
- Data-derived reference renders produced with the same Blender `5.2.1 LTS` via
  `artifacts/blender/build_spiral_reference.py` (`--background --factory-startup`).

## Provenance hygiene

- All local absolute paths have been removed or made repository-relative.
- One local path in `archive/legacy_three_ring/evidence/legacy_tidy3d_manifest.json`
  is redacted; the SHA-256 values it records are unchanged.
- No credentials, API tokens, or `.env` files are committed.
- Large binaries (`*.hdf5`, `*.blend`, `*.gds`, the large centerline `*.csv`) are
  tracked with Git LFS.
