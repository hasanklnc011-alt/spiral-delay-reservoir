# Reproducibility

## Environment

- Python ≥ 3.11 (developed and tested on CPython 3.14).
- Dependencies: NumPy and Matplotlib only for the core package. Exact versions
  are pinned in [`../requirements-lock.txt`](../requirements-lock.txt).
- The `p6-physical-validation` EM scripts additionally need the **Tidy3D** SDK
  (and `autograd` for the inverse-design paths). Cloud solves need Tidy3D
  credentials and explicit cost approval.

## Setup

```bash
git clone <repo-url>
cd 07_hybrid_electro_photonic_pic_smoked_blue
git lfs install && git lfs pull          # fetch the 67 HDF5 + layout binaries

python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

## Safe commands

```bash
export PYTHONPATH="$PWD/src"               # Windows: $env:PYTHONPATH="$PWD\src"

# P0 integrity — expect datasets_verified: 20 and blind_test_authorized: false
python scripts/verify_p0_protocol.py

# Package test suite — 50 tests
python -m unittest discover -s tests -v

# Development-only phase workflows (no blind data touched)
python scripts/run_p1_ideal.py
python scripts/run_p2_screen.py
python scripts/run_p3_screen.py
python scripts/run_p4_optimization.py
python scripts/run_p5_preflight.py

# Regenerate figures from committed records
python scripts/make_figures.py

# P6 component budget (deterministic, no solver)
cd p6-physical-validation
python component_model.py --check-provenance
python -m unittest discover -s tests        # ~10 inverse-design tests need Tidy3D+autograd
```

## What must NOT be re-run

- **`scripts/run_p5_blind.py`** — the blind evaluation is a locked, one-shot
  result. `p5-publication/runs/blind-v2.json` is the authorized output; the
  protocol treats a second blind evaluation as invalid, and the candidate lock
  guard is designed to refuse casual re-runs. If a *new* hypothesis is needed, it
  requires a **new protocol version and a new, disjoint blind suite** — not a
  re-run of this one.
- Cloud FDTD jobs without a recorded credit estimate and explicit approval.
- Full 14.24 cm 3D FDTD (never attempted; only short-cell S-parameters feed the
  compact model).

## Immutable publication evidence vs. safe reproduction

| Immutable (do not regenerate) | Safe to reproduce |
|---|---|
| `p5-publication/runs/blind-v2.json` | `scripts/run_p5_preflight.py` (development) |
| `p5-publication/candidate-lock-v2.json` | `scripts/verify_p0_protocol.py` |
| `configs/p0_narma10_protocol_v2.json` | `python -m unittest discover -s tests` |
| P6 `runs/*.json` and `runs/*.hdf5` | `component_model.py --check-provenance` |
| candidate / protocol / source SHA-256 values | `scripts/make_figures.py` |

## Blender

- `artifacts/blender/scenes/mcp.blend` is the author's presentation-scene file. It
  is **near-empty** (the hand-built geometry lived in an unsaved live session);
  open it only for reference.
- `artifacts/blender/build_spiral_reference.py` rebuilds a **data-derived**
  spiral reference model and two renders from
  `p6-physical-validation/layout/spiral-centerline-v1.csv`:

  ```bash
  "<blender>/blender.exe" --background --factory-startup \
      --python artifacts/blender/build_spiral_reference.py
  ```

  Treat all Blender geometry as presentation-level.
