# Source-to-design map

Each row links a concrete design or methodological choice to its support. A
source is only listed where the project documents actually rely on it; "project
record" means an internal document rather than an external paper.

| Design / methodological choice | Supporting source | Role in this project |
|---|---|---|
| **Use NARMA-10 as the benchmark** | Bazzanella et al. 2022; Giron Castro et al. 2024; Dong et al. 2026 (all report NARMA on rings); project P0 | Standard photonic-reservoir task needing both memory and bilinear nonlinearity; lets results be compared to the literature. |
| **Train only a linear ridge readout** | Donati et al. 2024; Bazzanella et al. 2022; Giron Castro et al. 2024 | Defines "reservoir" for this project: fixed nonlinear feature map + trained linear readout. |
| **Delay-line memory instead of resonator memory** | Donati et al. 2024 (external delay supplies memory a bare ring lacks); Bazzanella et al. 2022 (single-ring intrinsic memory ≈ 2 bits) | A tapped waveguide gives transparent, broadband, low-power memory whose digital twin is easy to build for controls. |
| **Do not transfer silicon carrier/thermal memory** | Bazzanella et al. 2022; Giron Castro et al. 2024; project literature review | TPA/FCD/thermo-optic memory is silicon-specific; a custom / SiN-Kerr platform needs its own mechanism — here, explicit delay. |
| **Square-law photodetection as the nonlinearity** | Project P1 (ideal basis derivation); general coherent-detection physics | `|E_i + E_j|²` yields `u[t-i]·u[t-j]`; an intrinsic passive nonlinearity, no nonlinear material. |
| **Local-oscillator branch** | Project P1 LO ablation | Recovers linear `u[t-i]` terms via `|LO + E_i|²`; removing it costs ~0.003 NMSE at the ideal level. |
| **Compare against delayed-input and no-PIC baselines** | Bazzanella et al. 2022 (readout must be applied to the input; guard against artefacts); project P0/MODEL-AND-ACCEPTANCE | Isolates the optical contribution; beating a same-memory linear model and a memoryless model (bootstrap CI < 0) is the real success criterion. |
| **Report a lossless digital twin as an upper bound** | Project P5 protocol correction (v1 → v2) | Requiring a noisy physical model to beat its own lossless twin is logically impossible; the twin is an upper bound, not a target. |
| **TCMT + RK4 modelling style (legacy line)** | Giron Castro et al. 2024; Dong et al. 2026 | Template for the archived three-ring TCMT work; superseded by the delay architecture. |
| **`n_g ≈ 4` cross-section requirement** | Project P6 G1; legacy `tidy3d_small_ring` (`n_g ≈ 2.1` for 800×400 nm SiN) | A higher-index section is needed so 19 symbols of delay fit in ~14 cm of routing. |
| **Single-series Archimedean spiral delay route** | Project P6 G2 | Routes 14.24 cm in ~1 mm² without a sub-radius central U-turn. |
| **Custom 343 × 180 nm process, not a 220 nm PDK** | Project P6 PDK-SELECTION | Public 50G-class PDKs (imec iSiPP50G, Tower PH18) are 220 nm Si, incompatible with the G1 `180 ± 5 nm` lock; a licensed active PDK would reopen G1–G4. |
| **Keep the three-ring work as archive only** | Project HANDOFF / MODEL-AND-ACCEPTANCE; Dong et al. 2026 (architectural context) | Historical evidence and failure-mode lessons; never a source of candidate parameters or success claims. |
| **Do not claim a trained physical RNN** | Tait et al. 2017 | A weight-bank continuous-time RNN is a separate architecture; this project's "reservoir" is not that. |

Open questions this map does **not** yet answer (evidence missing):

- Which real component realizes the 2×2 coherent combiner (G3-D FAIL/REDESIGN).
- Which real component realizes the progressive tap / LO splitter (G3-C FAIL/REDESIGN).
- Measured propagation loss, 30 GHz switching, 50 GHz PD/TIA, thermal matrix (G4 OPEN).
