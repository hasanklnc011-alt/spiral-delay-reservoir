# Methodology

How each phase was run, and why. Code lives at the repository root
(`src/photonic_reservoir/`, `scripts/`, `tests/`, and the `p1-…`/`p6-…` folders).

## Benchmark and metric

- **Task:** NARMA-10 — a 10th-order nonlinear autoregressive moving-average
  sequence. The target at time `t` depends on the last 10 inputs and on a product
  term, so a solver needs both memory and nonlinearity.
- **Metric:** normalized mean-square error (NMSE) between prediction and target,
  computed with a **leakage-safe** ridge readout (ridge parameter and
  normalization fit on training data only).
- **Split:** deterministic, finite datasets. Development seeds are used for all
  model choices; a disjoint set of **blind** seeds (179–229) is reserved and
  hash-committed before any modelling.
- **Target:** blind median test NMSE `< 0.05` with ≥ 8/10 blind seeds `< 0.05`,
  plus ≥ 10 % relative gain over each control and a paired bootstrap CI upper
  bound `< 0`.

Frozen in [`../P0-BENCHMARK-AND-BLIND-PROTOCOL.md`](../P0-BENCHMARK-AND-BLIND-PROTOCOL.md)
and [`../MODEL-AND-ACCEPTANCE.md`](../MODEL-AND-ACCEPTANCE.md); enforced by
`src/photonic_reservoir/protocol.py` and `scripts/verify_p0_protocol.py`.

## Producer / verifier separation

- The **producer** only ever touches development train/validation data during
  P1–P4.
- The **verifier** checks dataset hashes, candidate-config and source hashes, and
  the blind-test authorization flag.
- The blind test result is **not fed back** into any hyperparameter or
  architecture choice.

## Phase by phase

### P0 — protocol
Generate NARMA-10 deterministically; verify every value is finite; commit 20
dataset hashes; separate development and blind seeds; make the blind evaluator
refuse to run without a candidate lock. Correct output at this stage:
`blind_test_authorized: false`.

### P1 — ideal upper bound
Model the optical field as `E_i = u[t-i]` and form intensity channels `|E_i|²`,
`|LO + E_i|²`, `|E_i + E_j|²`. With a linear readout these span all linear lags
and cross-terms `u_i u_j`. Purpose: establish the **best achievable** NMSE for
this feature family (0.022534, 230 channels) and confirm a plain linear 20-lag
model cannot do it (0.154694). No loss, noise, geometry, or port budget.
Code: `src/photonic_reservoir/p1_coherent_delay/`.

### P2 — architecture compression
Rank channels on **training data only** and reduce 230 ideal channels to a
realizable measurement budget: 20 delay taps, a reconfigurable combiner (two
signal taps, or one tap + LO), one photodiode, and *N* time-multiplex slots per
symbol. 20 slots is the bare minimum (margin 0.0003); 30 slots is selected for
headroom (median 0.026459, 9/10). Random equal-amplitude `0/π` MZI masks were
inefficient (needed ~230 masks), so a task-focused sparse family was chosen.
Still lossless. Code: `src/photonic_reservoir/p2_architecture/`.

### P3 — realistic system model
Add splitter/combiner insertion loss, finite extinction, static and dynamic phase
error, LO amplitude drift, shot/thermal detector noise, detector bandwidth, and
slot timing. Two profiles: **nominal** (passes: 30 features, 10 PD × 3 slots,
median 0.038246, 9/10) and **stress** (fails, even at 30 PD). The single-PD
30-slot reading is rejected because at 10 GBd it needs a 300 GHz slot rate.
Code: `src/photonic_reservoir/p3_realistic/`.

### P4 — robust optimization
Validation-only optimization over 5 hardware realizations × 10 data seeds.
Selected: 30 channels, 10 PD × 3 slots, 5 mW signal + 5 mW LO per branch,
conservative 100 mW simultaneous optical budget. Nominal median 0.027499, stress
median 0.033723, 45/50 runs pass in each profile. 40 channels buy only 0.0003, so
30 is the Pareto choice. All 5 failing runs are seed 23.
Code: `src/photonic_reservoir/p4_optimization/`.

### P5 — locked blind evaluation
Run development-only publication preflights; only if the accuracy, ≥ 10 %-gain,
and bootstrap-CI gates all pass is a `candidate-lock` produced. Then run the
blind suite **once**. Controls: `delayed_input` (linear, same memory),
`no_photonic_core` (memoryless), `same_delay_digital` (lossless digital twin of
the same 30 features, reported as an upper bound). Result: median 0.038705, 8/10
seeds, gains 74.7 % / 94.9 %, digital-twin penalty 19.2 %. The authorized output
file makes a second blind run impossible by protocol.
Code: `src/photonic_reservoir/p5_publication/`; `scripts/run_p5_blind.py`
(**do not run**).

### P6 — physical validation
See [`PHYSICAL_VALIDATION.md`](PHYSICAL_VALIDATION.md). Mode solving + selected
short-cell FDTD (Tidy3D), cost-gated, never a full 14 cm 3D FDTD. Quantities that
need a real process (propagation loss, PD, heaters) are kept in a separate
evidence class. Code: `p6-physical-validation/*.py` (indexed in
[`../p6-physical-validation/SCRIPT_INDEX.md`](../p6-physical-validation/SCRIPT_INDEX.md)).

## Code entry points

| Script | Purpose | Safe to run? |
|---|---|---|
| `scripts/verify_p0_protocol.py` | Re-check P0 integrity (20 dataset commitments) | Yes |
| `scripts/run_p1_ideal.py` | P1 ideal model, development only | Yes |
| `scripts/run_p2_screen.py` | P2 architecture screen, development only | Yes |
| `scripts/run_p3_screen.py` | P3 realistic model, development only | Yes |
| `scripts/run_p4_optimization.py` | P4 robust optimization, development only | Yes |
| `scripts/run_p5_preflight.py` | P5 development preflight | Yes |
| `scripts/create_p5_candidate_lock.py` | Write the candidate lock | Only with intent |
| `scripts/run_p5_blind.py` | **Locked one-shot blind evaluation** | **No** |
| `scripts/make_figures.py` | Regenerate `docs/figures/fig*.png` from records | Yes |
| `p6-physical-validation/component_model.py` | Deterministic component/area/power budget | Yes (`--check-provenance`) |
| `p6-physical-validation/g*.py`, `inverse_design_*.py` | EM / mode-solve workflows | Needs Tidy3D SDK; cloud runs need approval |
