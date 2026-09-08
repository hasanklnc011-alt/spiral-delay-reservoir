# Design rationale

Why each element of the P4/P5 architecture is there, and what evidence supports
it. "Evidence level" uses the ladder in [`RESULTS_SUMMARY.md`](RESULTS_SUMMARY.md).

| Element | What it does | Why this choice | Evidence level |
|---|---|---|---|
| **Coherent optical delay line** (20 taps, ≤ 19 symbols) | Stores the input for controlled times so past inputs are available for combination | A waveguide is a broadband, passive, low-power, transparent delay; a tapped line gives memory without active recurrence, and its digital twin is trivial to build for the P5 controls | P1 (ideal), P6 G1/G2 (cross-section + route EM-supported) |
| **`n_g ≈ 4` cross-section** (343 × 180 nm Si strip) | Makes 19 symbols of delay at 10 GBd fit in ~14.24 cm of on-chip routing | An 800 × 400 nm SiN section gives `n_g ≈ 2.1` → only ~10 symbols in the same length; a higher-index section is required to lock length and memory simultaneously | P6 G1 PASS (`n_g = 4.01297`, mesh-converged) |
| **Single-series Archimedean spiral** | Physically routes the 14.24 cm delay in a 0.98 × 0.98 mm die area | Chosen over a double spiral to avoid a central U-turn below the 10 µm minimum bend radius | P6 G2 PASS (GDS length error 5.7×10⁻⁶, DRC clean) |
| **Square-law photodetection** | Supplies the nonlinearity: `|E_i + E_j|²` → `u[t-i]·u[t-j]` | Intrinsic, passive nonlinearity; no nonlinear optical material or bias needed | P1 (ideal basis spans the bilinear space) |
| **Local-oscillator branch** | Recovers linear `u[t-i]` terms via `|LO + E_i|²` | Without an LO the basis loses 20 channels and NMSE degrades (0.025 vs 0.0225 ideal) | P1 (LO-vs-no-LO ablation) |
| **30 sparse, task-selected features** | The measurement budget actually read out | Train-only channel ranking; 40 channels add only 0.0003 NMSE at the same hardware cost, so 30 is the Pareto point; random `0/π` masks needed ~230 to pass | P2, P4 (Pareto justification) |
| **10 photodiodes** | Parallel detection of the 30 features across slots | The minimum PD count that passes the P3 nominal accuracy gate; fewer PDs fail at every port split | P3 |
| **3 time-multiplex slots / symbol** (30 GHz) | Reads 30 features with 10 PDs | Single-PD 30-slot would need 300 GHz slot rate / 150 GHz receiver bandwidth at 10 GBd — not realistic; 10 PD × 3 slot needs only ~15 GHz | P3 |
| **2×2 coherent combiner feeding 10 branches** | Forms the interference pairs before detection | Required to realize `|E_i + E_j|²` physically | **P6 G3-D FAIL/REDESIGN** — generic MMI/EME/inverse-design cells miss imbalance/quadrature gates |
| **Progressive signal taps + 50:50 LO splitter** | Distributes power to taps and the LO with balanced coupling | Power-balance design `κ_k = 1/(20−k)` before excess loss | **P6 G3-C FAIL/REDESIGN** — DC/Y/MMI/slot-Y/union-Y all miss reflection/energy gates |
| **Fast (30 GHz) electro-optic slot selector** | Switches which feature each PD reads per slot | Thermo-optic phase control cannot switch at 30 GHz; a separate fast EO layer is needed, distinct from the static thermal trim | **P6 G4 OPEN** — no device S-parameters |
| **Static thermal phase trim** (30 presets) | Sets per-channel phase once | Slow (~10 kHz) thermal layer for calibration only, not slot switching | **P6 G4 OPEN** — no `Pπ` / crosstalk solve |
| **Leakage-safe ridge readout** | The only trained part | Ridge parameter and normalization fit on training data only; the *same* readout is applied to controls and to the raw input, per Bazzanella et al. (2022) | P0 protocol, P5 controls |
| **Delayed-input / no-PIC / digital-twin controls** | Isolate the optical contribution | Beating a same-memory linear model and a memoryless model, with bootstrap CIs excluding zero, is the actual success criterion | P5 (74.7 % / 94.9 % gains; 19.2 % twin penalty) |

The Blender scene's colours, materials and exact placements are **presentation
choices**. They do not encode measured material stacks, dimensions, loss,
coupling, or fabrication rules.
