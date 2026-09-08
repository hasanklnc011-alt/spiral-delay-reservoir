# archive/

Research history that is **not** part of the current research line but is kept
for reproducibility and for its lessons.

## `legacy_three_ring/`

The 2026-08 SiN three-ring temporal-coupled-mode-theory (TCMT) reservoir study.
This was the project's original direction (NARMA-3 on three coupled microrings,
parameters seeded from an earlier `tidy3d_small_ring` FDTD study). The main line
later moved to the coherent optical delay architecture; see
[`../docs/DEVELOPMENT_HISTORY.md`](../docs/DEVELOPMENT_HISTORY.md).

**Status:** read-only history.

- Its run scores are **not** used for candidate selection, success claims, or
  starting parameters in the current line.
- No current code imports it.
- Its central claim level is deliberately narrow: the NARMA-3 metric comes from a
  TCMT surrogate fitted to a static FDTD spectrum, **not** a direct temporal
  three-ring FDTD benchmark.
- The GPT-Pro handoff bundles and their zip artifacts that were present in the
  original workspace are **not** included here (working artifacts, not results).
- One local absolute path in `evidence/legacy_tidy3d_manifest.json` is redacted;
  the file SHA-256 values it records are unchanged.

See [`legacy_three_ring/README.md`](legacy_three_ring/README.md) and
[`legacy_three_ring/ARCHIVE.md`](legacy_three_ring/ARCHIVE.md).

## Note on the current project's own history

Earlier versions of this repository kept the *entire* current project inside
`archive/canonical-project-records/`. That snapshot has been **promoted to the
repository root** so the research code is live and navigable (`src/`, `tests/`,
`scripts/`, `p1-…`/`p6-…`). Nothing was lost; the per-phase folders keep their
original internal layout. The original Turkish project notes are preserved
verbatim in [`../docs/_source_records/`](../docs/_source_records/).
