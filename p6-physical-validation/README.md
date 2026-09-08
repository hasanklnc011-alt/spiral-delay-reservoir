# P6 — Physical validation

> ## CURRENT VERDICT: `NOT_PHYSICALLY_ACCEPTED`
>
> The P6 evidence chain was audited fail-closed (G6). **5 of 11** physical gates
> pass; **2** component families are a physical FAIL requiring redesign; **4**
> gates are OPEN pending external device / PDK evidence. The P5 blind result was
> **not** re-run and is **not** an optimization target for this phase.

This is a statement about *component physical evidence*, **not** about the P5
computational result. P5 is a valid, frozen system-simulation result. For the
full narrative see [`../docs/PHYSICAL_VALIDATION.md`](../docs/PHYSICAL_VALIDATION.md).

## Summary of the audit

| # | Gate | Status |
|---|---|---|
| G0 | Provenance (P5 blind + candidate-lock hashes) | **PASS** |
| G1 | Waveguide cross-section & delay (`n_g`) | **PASS** — 343 × 180 nm Si, `n_g = 4.01297` |
| G2 | Spiral delay route (GDS/DRC) | **PASS** — 142 400.6 µm, pitch 5 µm, R ≥ 10 µm |
| G3-A | Straight de-embedding reference | **PASS** |
| G3-B | Bend loss & adjacent-turn crosstalk | **PASS** — R10 `−0.0037 dB/90°`, crosstalk `< −124 dB` |
| G3-C | Progressive tap / LO splitter | **FAIL / REDESIGN** |
| G3-D | 2×2 coherent combiner | **FAIL / REDESIGN** |
| G4 | 30 GHz fast selector S-parameters | **OPEN** |
| G4 | 50 GHz PD / TIA chain | **OPEN** |
| G4 | Thermal budget (`Pπ`, crosstalk) | **OPEN** |
| G5 | Full-link loss / launch / thermal composition | **OPEN** |

### What passed and still stands
Delay cross-section, exact spiral route, R = 10 µm bend, adjacent-turn crosstalk.
Assumption-only propagation (`0.8 dB/cm`) + bends → `0.8974 dB/cm`, inside the P5
stress envelope but **not** a physical loss acceptance without cutback/PDK data.

### What failed and needs redesign
- **G3-C:** directional coupler, Y-splitter, five-point MMI sweep, slot-Y (v1–v3),
  taper-only, and union-branch Y — none cleared the imbalance / reflection /
  energy gates together. Next input: a foundry-qualified complex S-matrix or a
  dedicated EME / inverse-design cell.
- **G3-D:** two-source FDTD MMI (imbalance 20.7 dB), EME length screens, and
  custom inverse-design ID2 (both seeds failed) did not clear
  imbalance / excess / reflection / quadrature.

### What is still open
30 GHz switch S-parameters; a measured 50 GHz PD/TIA chain; a full thermal matrix;
and the G5 composition that depends on all of the above. The chosen route is a
**custom 343 × 180 nm process** — contract in
[`CUSTOM-PROCESS-VALIDATION.md`](CUSTOM-PROCESS-VALIDATION.md).

## Detailed documents (below the summary)

| Document | Contents |
|---|---|
| [`P6-PROTOCOL.md`](P6-PROTOCOL.md) | Scope, dependency graph, all 10 acceptance gates, stop conditions |
| [`COMPONENT-MODEL.md`](COMPONENT-MODEL.md) | Delay, spiral, loss, optical power, phase, thermal equations |
| [`EM-FDTD-PLAN.md`](EM-FDTD-PLAN.md) | Cost-gated Tidy3D EM work order |
| [`G1-ACCEPTANCE.md`](G1-ACCEPTANCE.md) | Accepted cross-section, convergence, process window |
| [`G2-LAYOUT-ACCEPTANCE.md`](G2-LAYOUT-ACCEPTANCE.md) | Spiral centerline / GDS / DRC acceptance |
| [`G3A-ACCEPTANCE.md`](G3A-ACCEPTANCE.md), [`G3B-ACCEPTANCE.md`](G3B-ACCEPTANCE.md) | Straight & bend EM acceptance |
| [`G3C-STATUS.md`](G3C-STATUS.md), [`G3C-SLOT-Y-DIAGNOSIS.md`](G3C-SLOT-Y-DIAGNOSIS.md) | Tap/splitter failure analysis |
| [`G3D-STATUS.md`](G3D-STATUS.md), [`INVERSE-DESIGN-PROTOCOL.md`](INVERSE-DESIGN-PROTOCOL.md) | Combiner failure analysis, inverse-design attempts |
| [`G4-STATUS.md`](G4-STATUS.md), [`G5-STATUS.md`](G5-STATUS.md) | Compact-model and composition status |
| [`G6-PHYSICAL-ACCEPTANCE.md`](G6-PHYSICAL-ACCEPTANCE.md) | The audit and verdict |
| [`PDK-SELECTION.md`](PDK-SELECTION.md), [`CUSTOM-PROCESS-VALIDATION.md`](CUSTOM-PROCESS-VALIDATION.md) | Platform decision & frozen validation contract |
| [`STATUS.md`](STATUS.md) | Running progress log |
| [`SCRIPT_INDEX.md`](SCRIPT_INDEX.md) | What every `.py` script here does |

## Layout and data

- `layout/spiral-centerline-v1.{gds,csv,svg}` — the accepted delay route (Git LFS).
- `runs/*.json` — machine-readable gate results, hash-locked.
- `runs/*.hdf5` — 59 curated FDTD / mode-solve outputs (Git LFS); `git lfs pull` to fetch.
- `_unclassified_solver_scratch/` — 8 unlabeled solver downloads, provenance
  unclear, kept for completeness, cited by nothing.
- `configs/baseline-v1.json` — P5 inputs frozen into P6 + P6's open assumptions.

## Local checks (no cloud job, no credits)

```powershell
python component_model.py --check-provenance
python -m unittest discover -s tests -v
```

`em_plan.py --check-local` checks the Tidy3D import/version and a minimal
in-memory simulation. `g1_mode_solver.py --solve-local` runs a real local
eigensolve. `g1_remote_preflight.py` serializes/hashes the 13-point payload in
memory only. None of these submit a cloud job or spend FlexCredits. They require
a Python environment with the Tidy3D SDK installed.

## Rules

- The P5 blind score is never re-run and never tuned from P6 outcomes.
- No cloud job without a recorded credit estimate and explicit user approval.
- Full 14.24 cm 3D FDTD is never attempted.
- If a physical penalty exceeds P5 assumptions, the *claim* is narrowed — the P5
  number is not re-fitted.
