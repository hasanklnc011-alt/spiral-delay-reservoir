# Glossary

| Term | Meaning in this project |
|---|---|
| **NARMA-10** | 10th-order Nonlinear AutoRegressive Moving Average sequence; the benchmark. Target at time `t` depends on the last 10 inputs and a bilinear term — needs memory *and* nonlinearity. |
| **NMSE** | Normalized Mean-Square Error between prediction and target. Lower is better; the project target is a blind median `< 0.05`. |
| **Reservoir computing** | A fixed (untrained) nonlinear dynamical system maps an input sequence to many temporal features; only a linear readout is trained. |
| **Reservoir (as used here)** | Loosely: a fixed nonlinear temporal feature map + trained linear readout. **Not** a trained physical recurrent network. |
| **Fading memory** | Property that features depend on recent inputs, with older inputs decaying. |
| **Ridge / linear readout** | The only trained component: linear regression with L2 regularization, fit on training data only ("leakage-safe"). |
| **Virtual node / time-multiplexed slot** | One measurement in a sequence of per-symbol readings from the same detector; `N` slots emulate `N` parallel detectors. |
| **Blind test / blind gate** | A one-shot evaluation on held-out seeds whose datasets were hash-committed before modelling. Cannot be re-run or tuned from. |
| **Candidate lock** | A frozen (config + source) hash bundle; the blind evaluator refuses to run without a match. |
| **Development / validation split** | Data used for all model choices (P1–P4). Disjoint from the blind test seeds. |
| **Digital twin (`same_delay_digital`)** | A lossless, noiseless numerical model of the exact same 30 features; reported as an accuracy upper bound, not a target. |
| **Delayed-input baseline** | Linear model with the same tapped-delay memory but no optical nonlinearity — a control. |
| **No-PIC baseline** | Memoryless control (no photonic core). |
| **Coherent combiner** | Optical element that adds field amplitudes (not powers) before detection, enabling interference cross-terms. |
| **LO (local oscillator)** | A reference optical field mixed with a delayed copy so `|LO + E_i|²` exposes linear `u[t-i]` terms. |
| **Square-law detection** | A photodiode outputs power ∝ `|E|²`; the squaring is the nonlinearity used here. |
| **TCMT** | Temporal Coupled-Mode Theory; reduced-order ODE model of a resonator's field, used in the archived three-ring line. |
| **Kerr nonlinearity** | Intensity-dependent refractive index (χ³); relevant to SiN platforms; not the nonlinearity used by the current candidate. |
| **FDTD** | Finite-Difference Time-Domain electromagnetic simulation; used in P6 for short component cells only. |
| **EME** | Eigenmode Expansion; a faster frequency-domain method used to screen combiner/MMI lengths in P6. |
| **Mode solver** | Computes waveguide eigenmodes (effective index `n_eff`, group index `n_g`). |
| **`n_g` (group index)** | Sets the optical delay per unit length: `τ = n_g · L / c`. `n_g ≈ 4` is required so 19 symbols fit in ~14.24 cm. |
| **`n_eff` (effective index)** | Mode phase index; used for phase/de-embedding checks. |
| **PD / TIA** | Photodiode / Trans-Impedance Amplifier — the detector + first electronic amplifier. |
| **Propagation loss** | Waveguide attenuation in dB/cm; needs fabricated cutback or PDK data (assumption-only in P6). |
| **MMI** | Multi-Mode Interference coupler; a candidate splitter/combiner geometry (rejected so far in G3-C/G3-D). |
| **Directional coupler (DC)** | Two waveguides coupling over a gap; a candidate splitter geometry (rejected in G3-C). |
| **Extinction ratio** | Ratio of "on" to "off" optical power through a switch/modulator. |
| **Quadrature error** | Deviation from the ideal 90° phase relationship at a 2×2 combiner's outputs. |
| **PDK** | Process Design Kit — a foundry's qualified device models and design rules. |
| **DRC** | Design Rule Check — geometric manufacturability checks (min width, gap, radius). |
| **GDS / GDSII** | Standard layout file format for the spiral centerline. |
| **FlexCredit (FC)** | Tidy3D's cloud-compute billing unit; P6 jobs are cost-gated and approved before submission. |
| **G0…G6** | P6 acceptance gates: provenance, cross-section/delay, layout, straight/bend/splitter/combiner EM, compact model, composition, final audit. |
| **`NOT_PHYSICALLY_ACCEPTED`** | The current G6 verdict: the component physical-evidence chain is incomplete (not a rejection of the P5 computational result). |
