# Reorganization report

Branch: **`docs/supervisor-cleanup`** (not merged to `main`).
Purpose: turn an internal research workspace into a clean, scientifically honest,
easy-to-follow academic repository **without changing the science**.

## Non-destructive guarantees

- No numerical result, benchmark definition, seed list, candidate lock, protocol
  hash, or provenance hash was modified.
- The P5 blind evaluation was **not** re-run. `p5-publication/runs/blind-v2.json`
  is untouched (SHA-256 `b263292f…`).
- No git history was rewritten; no force-push.
- Every phase folder keeps its **original name and internal layout**, so all
  provenance hash checks and unit tests still pass.
- Scientific evidence was preserved, including failed results and the legacy line.

## 1. Old structure (before)

The entire research project sat inside `archive/canonical-project-records/`
(≈ 317 files). The repository root exposed only prose docs (`docs/01…07_*.md`),
a `references/` folder, `provenance/`, a `blender/` folder, and a near-empty
`docs/index.html`. Raw HDF5 solver outputs were excluded. Obsidian `[[wikilinks]]`
and some local Windows paths were present throughout the archived snapshot.

## 2. New structure (after)

```
README.md  CITATION.cff  REORGANIZATION_REPORT.md
P0-BENCHMARK-AND-BLIND-PROTOCOL.md  MODEL-AND-ACCEPTANCE.md
requirements-lock.txt  pyproject.toml
src/photonic_reservoir/        (live)
scripts/                       (live: P0 verifier, P1–P5 workflows, make_figures.py)
tests/                         (live: 50 tests)
configs/                       (P0 protocol JSON)
p1-coherent-delay/ … p5-publication/    (per-phase README/RESULTS/configs/runs — unchanged internally)
p6-physical-validation/        (unchanged internally + new README landing + SCRIPT_INDEX.md)
  layout/*.{gds,csv,svg}       (Git LFS)
  runs/*.hdf5                  (Git LFS, 67 files)
  _unclassified_solver_scratch/*.hdf5   (Git LFS, 6 files, provenance unclear)
docs/
  PROJECT_OVERVIEW / SCIENTIFIC_BACKGROUND / METHODOLOGY / RESULTS_SUMMARY /
  PHYSICAL_VALIDATION / DEVELOPMENT_HISTORY / LIMITATIONS / REPRODUCIBILITY /
  DESIGN_RATIONALE .md
  figures/          (5 generated figures + 3 Blender renders)
  references/       (references.bib, references.md, source_to_design_map.md, glossary.md, literature_review.md)
  _source_records/  (original Turkish notes, verbatim)
  index.html
artifacts/
  blender/          (mcp.blend, spiral-reference-from-centerline.blend, build_spiral_reference.py)  [LFS]
  figures/          (mirror of the 5 generated figures)
provenance/         (manifest, environment, decisions, research log)
archive/
  legacy_three_ring/   (2026-08 SiN three-ring work)
```

## 3. Files moved

313 renames. The whole `archive/canonical-project-records/` tree was promoted:
`src/`, `tests/`, `configs/`, `scripts/*.py`, `pyproject.toml`,
`requirements-lock.txt`, `P0-BENCHMARK-AND-BLIND-PROTOCOL.md`,
`MODEL-AND-ACCEPTANCE.md`, and `p1-coherent-delay/ … p6-physical-validation/` all
moved to the repository root with `git mv` (history preserved).
`legacy-three-ring/` → `archive/legacy_three_ring/`.
`references/` → `docs/references/`.
`blender/` → `artifacts/blender/`.
`docs/01…07_*.md` → descriptive names (`PROJECT_OVERVIEW.md`, etc.).
`HANDOFF.md`, `Photonic-Reservoir.md`, original `README.md`,
`MRR-RNN-Literatur-Taramasi.md` → `docs/_source_records/` and
`docs/references/literature_review.md`.

## 4. Files newly created

101 additions, including: the root `README.md` (rewritten), all `docs/*.md`
narrative documents, `docs/references/{references.bib (expanded), references.md,
source_to_design_map.md, glossary.md}`, `docs/PHYSICAL_VALIDATION.md`,
`docs/DEVELOPMENT_HISTORY.md`, `p6-physical-validation/README.md` (verdict-first),
`p6-physical-validation/SCRIPT_INDEX.md`, `scripts/make_figures.py`,
`artifacts/blender/build_spiral_reference.py`, 5 figures + 2 data-derived Blender
renders, refreshed `provenance/*`, `archive/README.md`, `scripts/README.md`,
`results/README.md`, and this report.

## 5. Files intentionally preserved in place

`src/photonic_reservoir/**` and all `p*/` Python code, configs, `runs/*.json`,
and tests — byte-identical (only Obsidian links in `.md` files converted). The
per-phase folder names (`p1-coherent-delay`, …) were kept unchanged because
`p6-physical-validation` code resolves sibling paths and hash-checks
`configs/baseline-v1.json`; renaming them broke unit tests (see `provenance/design_decisions.md`
ADR-006).

## 6. Files removed

- `GITHUB_PREPARATION_REPORT.md` (superseded by this report).
- `archive/legacy_three_ring/gptpro/` and `gptpro-bundles/` (GPT-Pro handoff
  working artifacts + 5 zip files — not research results).
- `archive/canonical-project-records/.gitignore` (root `.gitignore` covers it).

No scientific evidence was removed.

## 7. Documentation

New English academic `README.md` (~10-minute read): research question → photonics
rationale → MRR-to-coherent-delay history → architecture (table + Mermaid signal
path) → P0–P6 pipeline table → key results → blind-test integrity → honest P6
status → repository map → reading order → reproducibility → limitations →
references → license/citation. `docs/` holds nine narrative documents; a
verdict-first P6 landing page opens with `NOT_PHYSICALLY_ACCEPTED`.

## 8. Bibliography

`docs/references/references.bib` expanded from 4 bare DOI stubs to 6 entries with
author/title/venue/year (each `note`-flagged as DOI-authoritative, metadata not
re-verified). `references.md` groups them by topic with a "used in this project
for…" note each. `source_to_design_map.md` links 14 design/methodology choices to
their support. `glossary.md` defines ~45 terms. The original Turkish literature
review is kept verbatim as `literature_review.md`. The 2026 "memory in integrated
photonic neural networks" review is **not** stored locally; it is cited by
description only (no PDF redistributed).

## 9. Broken links fixed

Every Obsidian `[[wikilink]]` in 41 Markdown files converted to plain text or a
relative Markdown link. Vault-external targets (`🧠 500-Knowledge/…`,
`🏰 300-Projects/3 halkalı Ring/…`) became plain text marked
"MayOS vault note, outside this repository". Post-audit: **0** wikilinks remain,
**0** broken relative Markdown links.

## 10. Local / private paths removed

- `C:\Users\hasan\OneDrive\Desktop\eski dosyalarım\…\.venv-tidy3d\…python.exe`
  interpreter paths in `p6-physical-validation/README.md` → `python`.
- `C:\Users\hasan\OneDrive\Desktop\MayOS\…` and `…\eski dosyalarım\…` paths in
  legacy notes → redacted placeholders.
- `legacy_tidy3d_manifest.json` `source_root` → `<local source path redacted
  during archival>` (SHA-256 values unchanged).
- Post-audit: no absolute Windows paths, user home directories, API keys, or
  Tidy3D credentials in supervisor-facing files.

## 11. Large files / Git LFS

`.gitattributes` now tracks `*.blend`, `*.hdf5`, `*.gds`, and the large
`spiral-centerline-v1.csv` with Git LFS: **71 LFS objects** total (67 P6 HDF5 +
6 scratch HDF5 − overlap, plus 2 `.blend` + 1 `.gds` + 1 `.csv`). Working tree
≈ 190 MB. A plain `git clone` fetches LFS pointers; `git lfs pull` fetches the
binaries. `.gitignore` blanket-ignores `*.hdf5` but re-includes
`p6-physical-validation/runs/**` and `.../_unclassified_solver_scratch/**`, so the
curated evidence is tracked at its original paths while stray scratch HDF5
elsewhere stays ignored.

## 12. Tests run

| Suite | Result |
|---|---|
| `python -m unittest discover -s tests` (package) | **50 / 50 pass** |
| `python scripts/verify_p0_protocol.py` | **20 datasets verified, `blind_test_authorized: false`** |
| `p6-physical-validation` `unittest discover -s tests` | **81 / 91 pass**; 10 errors are pre-existing missing-dependency (`tidy3d` / `autograd`) import failures in inverse-design tests — identical to the pre-reorganization baseline, not a regression |
| `python scripts/make_figures.py` | 5 figures generated |
| `blender --background … build_spiral_reference.py` | 2 renders + reference `.blend` generated |

No expensive cloud / FDTD job was run. The P5 blind evaluation was not run.

## 13. Current P5 scientific result

Blind median NARMA-10 **test** NMSE **0.0387049671**, 8/10 blind seeds `< 0.05`;
74.71 % better than the delayed-input baseline, 94.91 % better than the no-PIC
baseline; 19.20 % penalty vs. the lossless digital twin; paired 95 % bootstrap CI
upper bounds `< 0`. A physically parameterized **system-simulation** result, not
an experimental measurement.

## 14. Current P6 physical-validation verdict

**`NOT_PHYSICALLY_ACCEPTED`.** 5 of 11 gates PASS (G0 provenance, G1
cross-section/`n_g`, G2 layout route, G3-A straight, G3-B bend/crosstalk); G3-C
tap/splitter and G3-D 2×2 combiner are **FAIL / REDESIGN**; G4 (30 GHz switch,
50 GHz PD/TIA, thermal) and G5 (composition) are **OPEN**. This is a component
physical-evidence status, not a rejection of the P5 computational result.

## 15. Open decisions for the author

1. **License.** None chosen. `CITATION.cff` says "contact the author"; add a
   `LICENSE` file (e.g. CC BY 4.0 for text/data, MIT for code) before sharing
   widely.
2. **Repository name.** `07_hybrid_electro_photonic_pic_smoked_blue` is an
   internal codename; consider renaming the GitHub repo (e.g.
   `photonic-reservoir-coherent-delay`) before sending the link. Not done here —
   renaming the repo was out of scope for this reorganization.
3. **The Blender scene.** `artifacts/blender/scenes/mcp.blend` is near-empty; the
   hand-built geometry was never saved. Open it in Blender, rebuild/re-import the
   geometry, and `Save As` over that file.
4. **Unclassified HDF5.** `p6-physical-validation/_unclassified_solver_scratch/`
   holds 6 solver downloads with unclear provenance — confirm whether to keep,
   label, or drop them.
5. **The other repository.** `github.com/hasanklnc011-alt/Photonic_Resorvoir` (a
   raw earlier push of the same project) should be archived or deleted so there
   is a single canonical repository.
