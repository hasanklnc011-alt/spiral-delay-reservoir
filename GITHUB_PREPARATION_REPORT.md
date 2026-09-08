# GitHub preparation report

## Scope and integrity

- Source project: MayOS Photonic-Reservoir record (copied, never modified).
- Canonical Blender file: `blender/scenes/mcp.blend`.
- Source/copy SHA-256: `cfc4a2951aa98e53c902452a81a85f0a464dbfff2f2e5a853f21c755c998dd96`.
- Generated documentation figure: `blender/renders/p6_overview_session_render.png` (also selected under `docs/figures/`).

## Included

- Python source, phase configuration, JSON result records, protocol documents, tests, and historical documentation in `archive/canonical-project-records/`.
- New academic README, evidence-boundary documentation, bibliography, provenance files, and static yellow-green documentation interface.

## Intentionally excluded

- HDF5 solver outputs, Python caches, virtual environments, temporary folders, Blender backups, and secret-bearing environment files.
- Literature PDFs: citations/links are retained; redistribution rights were not verified.

## Audit

- Python AST syntax validation: passed for 123 archived Python files.
- Secret-pattern scan: no secret found. Three test files were pattern-only false positives.
- Absolute local path scan: one legacy manifest path was redacted in the staging copy.
- Git LFS: not used; `mcp.blend` is approximately 98 KB and the archive excludes large raw binaries.

## Unresolved issues

- Blender-session render provenance is unverified relative to the copied on-disk `mcp.blend`.
- P6 physical acceptance remains `NOT_PHYSICALLY_ACCEPTED`.
- GitHub CLI is unavailable; repository publication will use the connected GitHub service if its final audit succeeds.
