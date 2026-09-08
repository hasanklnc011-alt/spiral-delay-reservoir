# Results summary (P1–P6)

All numbers are copied verbatim from committed result records. This document does
not re-run anything. Where a phase reports several variants, the **canonical**
selected value is in bold.

## 1. Computational performance (development, validation split)

| Phase | Configuration | Median validation NMSE | Seeds `≤ 0.05` (of 10) | Record |
|---|---|---|---|---|
| P1 | Full-quadratic digital oracle, 230 ch | 0.022164 | 9 | [`p1-coherent-delay/RESULTS.md`](../p1-coherent-delay/RESULTS.md) |
| P1 | **Coherent field-`u` + PD square-law, 230 ch** | **0.022534** | 9 | " |
| P1 | Coherent `sqrt(power)` + PD square-law, 230 ch | 0.022450 | 9 | " |
| P1 | Coherent field-`u`, no LO, 210 ch | 0.025093 | 9 | " |
| P1 | Linear 20-lag control, 20 ch | 0.154694 | 0 | " |
| P2 | 20 time-mux slots (minimum) | 0.039716 | 8 | [`p2-architecture/RESULTS.md`](../p2-architecture/RESULTS.md) |
| P2 | **30 time-mux slots (selected)** | **0.026459** | 9 | " |
| P2 | 40 / 60 slots | 0.025559 / 0.023906 | 9 / 9 | " |
| P3 | **Nominal profile, 30 feat., 10 PD × 3 slot** | **0.038246** | 9 | [`p3-realistic/RESULTS.md`](../p3-realistic/RESULTS.md) |
| P3 | Stress profile (any port split) | did not pass (≥ 0.05356) | — | " |
| P4 | **Nominal, 5 hw × 10 data** | **0.027499** (P90 0.044108) | 9 data seeds; 45/50 runs | [`p4-optimization/RESULTS.md`](../p4-optimization/RESULTS.md) |
| P4 | Stress, 5 hw × 10 data | 0.033723 (P90 0.051650) | 9 data seeds; 45/50 runs | " |

Notes:
- P1's 230-channel basis is an **idealized upper bound**, not a PIC result.
- Seed 23 is a consistent outlier from P1 onward (a dataset-specific limit of the
  20-lag / quadratic hypothesis, not a hardware effect); all five failing P4 runs
  are seed 23.
- P3 rejected the single-PD 30-slot reading because at 10 GBd it demands a
  300 GHz slot rate / 150 GHz receiver bandwidth.

## 2. P5 locked blind evaluation (test split, one shot)

| Metric | Value |
|---|---|
| Blind median **test** NMSE (photonic candidate) | **0.0387049671** |
| Blind seeds with test NMSE `< 0.05` | **8 / 10** |
| Delayed-input baseline median | 0.1530487464 → candidate **74.71 %** better |
| No-photonic-core baseline median | 0.7606056879 → candidate **94.91 %** better |
| Lossless same-delay digital twin median | 0.0324712617 → candidate penalty **19.20 %** |
| Paired 95 % bootstrap CI upper bound (vs. each control) | `< 0` |
| Blind datasets evaluated | 10 |
| Total candidate + control test evaluations | 40 |
| `publication_passed` | `true` |

### Per-seed blind results

| Seed | Test NMSE | Result |
|---:|---:|:---:|
| 179 | 0.03560 | pass |
| 181 | 0.04108 | pass |
| 191 | 0.03266 | pass |
| 193 | 0.03072 | pass |
| 197 | 0.03942 | pass |
| 199 | 0.04247 | pass |
| 211 | 0.03753 | pass |
| 223 | 0.03799 | pass |
| 227 | 0.06360 | **fail (kept)** |
| 229 | 0.12033 | **fail (kept)** |

Source: [`p5-publication/RESULTS.md`](../p5-publication/RESULTS.md),
[`p5-publication/runs/blind-v2.json`](../p5-publication/runs/blind-v2.json).

## 3. Provenance (SHA-256)

| Artifact | SHA-256 |
|---|---|
| P0 protocol v1 (retired) | `2a66934d024178a15cacfccd282a3c27ca4d96a357b0820f3fcae59360ebc95a` |
| P0 protocol v2 (canonical, internal) | `e6cbd95e7aa6b5b3aae9f73172099e4c591db334b2a7f0497768f999c70073f8` |
| P1 result (`ideal-v1.json`) | `450aea478c75bdf0dc7d7efd0d4134336d49e1e4b5846b6e0b8069b1e6afd510` |
| P2 config (`screen-v4-pareto`) | `83db356d85026abb880a4338c222d62d80e3fba129f6884d9466f16e9e2fb2f7` |
| P2 result (`screen-v4-pareto.json`) | `9207253bd00634da699c6d13c82a8025977cef20d6e4bb530d0d165d6e87405d` |
| P3 result v2 (`screen-v2-receiver-bandwidth.json`) | `0f08e6291bde6ed26144a14e8ea7481f9e1e65939697d87a1db51eeb3095129f` |
| P4 discovery (`discovery-v1.json`) | `b7d9ae6f5af9c7f46ea477a96c5c639a72e662710fed6365c7463e7749e17f51` |
| P4 stress confirmation (`confirmation-v1.json`) | `44fa69e447ac10b1fd6564185eb30db7c9f8759b9b7758025d7c4a4a9a719a17` |
| P4 nominal confirmation (`confirmation-nominal-v1.json`) | `9de948e459f3f8f833a3da4a14d00fc0c09aea3e991823244468b0ba556e9416` |
| P5 candidate config (canonical) | `c7c36b289bf1bdc0689f45b280f807ceaed3c470690cfe36cfd21be023baaa3c` |
| P5 locked source | `a0e6561a726a6d17a31dd1bde37257435f857549cb726d711bea6e5c4a17a080` |
| P5 candidate lock | `664904b350efaa84a65e5f57a5119042f196753ccd4e7e6d11e851395e5c247d` |
| **P5 blind result** (`blind-v2.json`) | `b263292fd0226c10cc3b0096350176cb14771e258f2eacd89c2952ace9219028` |

`scripts/verify_p0_protocol.py` re-checks the P0 side of this chain;
`p6-physical-validation` tests re-check the P5→P6 hash locks
(`p6-physical-validation/configs/baseline-v1.json`).

## 4. Physical validation (P6, component / EM level)

| Gate | Status | Key evidence |
|---|---|---|
| G0 provenance | PASS | P5 blind + candidate-lock hashes match |
| G1 cross-section / delay | PASS | 343 × 180 nm Si strip, `n_g = 4.01297`, window `width 343 ± 10 nm`, `thickness 180 ± 5 nm` |
| G2 layout route | PASS | single-series Archimedean spiral, GDS 142 400.61 µm (rel. err 5.7×10⁻⁶), pitch 5 µm, min radius 10 µm, bbox 982.34 × 982.34 µm, 20 taps |
| G3-A straight de-embedding | PASS | m20/m25 mesh-converged lossless reference |
| G3-B bend & crosstalk | PASS | R = 10 µm bend `−0.00372 dB/90°`, worst reflection `−39.26 dB`; adjacent-turn coupling `< −124.6 dB` at 5 µm pitch |
| G3-C tap / splitter | **FAIL / REDESIGN** | DC, Y-splitter, 5-point MMI sweep, slot-Y (v1–v3), taper-only, union-Y — none cleared imbalance/reflection/energy gates; best MMI excess `0.991 dB`, best reflection `−17.6 dB` |
| G3-D 2×2 combiner | **FAIL / REDESIGN** | two-source FDTD MMI imbalance `20.7 dB`; EME length screen best excess `4.6 dB`, quadrature error `74–79°`; inverse-design ID2 seeds failed |
| G4 fast switch S-params | OPEN | no 30 GHz device S-parameters |
| G4 PD/TIA chain | OPEN | no measured 50 GHz responsivity / noise / saturation / linearity |
| G4 thermal | OPEN | no `Pπ`, time constant, or crosstalk solve |
| G5 full-link composition | OPEN | cannot compose with missing device losses |
| **G6 overall** | **`NOT_PHYSICALLY_ACCEPTED`** | 5 PASS / 2 FAIL-REDESIGN / 4 OPEN |

Sources: [`p6-physical-validation/G6-PHYSICAL-ACCEPTANCE.md`](../p6-physical-validation/G6-PHYSICAL-ACCEPTANCE.md),
[`p6-physical-validation/STATUS.md`](../p6-physical-validation/STATUS.md),
[`p6-physical-validation/runs/g6-acceptance-audit-v1.json`](../p6-physical-validation/runs/g6-acceptance-audit-v1.json).

## 5. Evidence-level ladder

| Level | Phases | Meaning |
|---|---|---|
| Protocol / integrity | P0 | Benchmark, splits, blind rules hash-locked |
| Idealized mathematical model | P1 | Upper bound; no loss/noise/geometry |
| Ideal architecture simulation | P2 | Measurement-budget reduction, still lossless |
| Physical-parameter system simulation | P3 | Loss, noise, phase error, bandwidth |
| Monte-Carlo system simulation | P4 | Robustness over hardware × data seeds |
| Locked blind system-simulation result | P5 | One-shot, immutable, controls with bootstrap CIs |
| Component / EM validation | P6 | Mode solving + selected FDTD; **incomplete** |
| Experimental / fabricated | — | **not reached** |
