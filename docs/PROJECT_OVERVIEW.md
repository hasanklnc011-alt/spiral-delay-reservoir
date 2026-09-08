# Project overview

## In one paragraph

This project studies an integrated-photonic way to build the temporal nonlinear
feature map needed for the **NARMA-10** benchmark. An input sequence modulates an
optical field; the field is delayed by controlled amounts in on-chip waveguide;
selected delayed copies interfere and are detected by photodiodes whose
**square-law** response supplies the nonlinearity; and only a **linear ridge
readout** is trained. The work is organized as a chain of phases with rising
evidence strength (P0 protocol → P1 ideal model → P2 architecture → P3 realistic
system model → P4 robustness → P5 locked blind test → P6 physical validation).
The blind test (P5) reaches median NMSE **0.0387** (target `< 0.05`, 8/10 seeds),
and beats a same-memory linear baseline and a memory-free baseline with bootstrap
confidence intervals excluding zero. The physical-validation phase (P6) is
**incomplete**: the delay cross-section, route, and bends are EM-supported, but
the tap/splitter and 2×2 combiner cells need redesign and several device inputs
are still missing, so the current physical verdict is `NOT_PHYSICALLY_ACCEPTED`.

## What this is / is not

| It is | It is not |
|---|---|
| A physically parameterized **system-simulation** study with a locked blind test | An experimental / fabricated-PIC demonstration |
| A component-level EM **feasibility** campaign for the selected architecture | A foundry-qualified layout or tape-out |
| A careful separation of *optical contribution* from digital-equivalent baselines | A claim that the optical version is more accurate than digital |
| A "reservoir" in the loose sense (fixed nonlinear feature map + trained linear readout) | A trained physical recurrent neural network |

## Origin

The project grew out of interest in **microring-resonator reservoir computing**.
The main research line later moved to an explicit **coherent optical delay**
architecture because it is easier to reason about physically and to compare
against digital controls. The earlier three-ring work is kept as history in
[`../archive/legacy_three_ring/`](../archive/legacy_three_ring/); see
[`DEVELOPMENT_HISTORY.md`](DEVELOPMENT_HISTORY.md).

## Key numbers (from committed records)

- Blind median test NMSE: **0.0387049671** (8/10 blind seeds `< 0.05`)
- Improvement vs. delayed-input linear baseline: **74.7 %**
- Improvement vs. no-photonic-core baseline: **94.9 %**
- Penalty vs. lossless digital twin of the same features: **19.2 %**
- Longest optical delay route: **≈ 14.24 cm** (`n_g ≈ 4`, 19 symbols at 10 GBd)
- P6 physical acceptance: **5 / 11 gates PASS**, verdict `NOT_PHYSICALLY_ACCEPTED`

See [`RESULTS_SUMMARY.md`](RESULTS_SUMMARY.md) for the full table with SHA-256
provenance, and the root [`README.md`](../README.md) for the complete narrative.
