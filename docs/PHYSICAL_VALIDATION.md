# Physical validation (P6) — honest status

**Current verdict: `NOT_PHYSICALLY_ACCEPTED`.**

This is a statement about the *physical evidence chain for the components*, not
about the P5 computational result. P5 remains a valid, frozen system-simulation
result. P6 asks a different question: *can the optical parts that the P5
architecture assumes actually be built with the required loss, balance, phase and
bandwidth?* As of the latest G6 audit the answer is "not yet shown".

## What P6 is trying to prove

The P5 candidate assumes, among other things:
- a waveguide with group index `n_g ≈ 4` so that 19 symbols of delay at 10 GBd
  fit in a routable on-chip length;
- a ~14.24 cm low-loss spiral delay route with 20 taps;
- progressive signal taps and a 50:50 LO splitter with small excess loss and
  controlled reflection;
- a reciprocal 2×2 coherent combiner feeding 10 balanced photodiode branches;
- a fast (30 GHz) slot selector, a 50 GHz PD/TIA chain, and a static thermal
  phase-trim budget within a power ceiling.

P6 tests each of these at the component level with mode solving and **selected**
short-cell FDTD (never a brute-force 3D FDTD of the whole 14 cm structure), and
keeps quantities that need a real process (propagation loss, PD, heaters) in a
separate evidence class.

## Gate-by-gate

### Passing (5)

| Gate | Result |
|---|---|
| **G0 provenance** | P5 `blind-v2.json` and `candidate-lock-v2.json` SHA-256 values match the values frozen in `p6-physical-validation/configs/baseline-v1.json`. No blind re-run. |
| **G1 cross-section & delay** | A 343 × 180 nm silicon strip gives `n_g = 4.01297` (mesh-converged, remote sub-pixel ModeSolver). Mandatory process window: `width = 343 ± 10 nm`, `thickness = 180 ± 5 nm`. An earlier local 450 × 220 nm SiN seed gave `n_g ≈ 4.26` but failed the convergence gate and is recorded as `g1_passed = false`. |
| **G2 layout route** | A single-series Archimedean spiral (chosen over a double spiral to avoid a sub-radius central U-turn) with GDS polyline length **142 400.61 µm** vs. target 142 401.42 µm (relative error 5.7×10⁻⁶). Pitch 5 µm, minimum curvature radius 10 µm, edge gap 4.657 µm, die bounding box 982.34 × 982.34 µm, 20 taps, continuous GDS path. Files hash-locked. |
| **G3-A straight de-embedding** | Lossless 4/8 µm straight references converge at mesh levels m20/m25; used as the de-embedding baseline for bends. Fabricated propagation loss is deliberately left as an open PDK/cutback input. |
| **G3-B bend & adjacent-turn crosstalk** | R = 10 µm bend: fine-mesh transmission `−0.00372 dB / 90°`, worst reflection `−39.26 dB`, de-embedded phase convergence `0.446°`. Neighbouring-turn coupling at 5 µm pitch bounded `< −124.6 dB` over a conservative 2.99 mm parallel length (re-checked against the exact centerline). |

### Failing — redesign required (2)

| Gate | Why it fails |
|---|---|
| **G3-C progressive tap / LO splitter** | Every generic geometry tried missed the acceptance gates together: a uniform 200 nm-gap directional coupler (imbalance 7.85 dB, centre reflection `−11.83 dB`, energy residue 4.64 %); a symmetric Y-splitter (`−15.0 dB` centre / `−9.27 dB` worst reflection); a five-point 1×2 MMI length sweep (best 10 µm: excess 0.991 dB, reflection `−17.6 dB`); slot-opening Y redesigns v1–v3 (best excess 0.498 dB, reflection `−13.11 dB`, energy 6.68 %); an 80 µm adiabatic extension; and a width-doubling-free union-branch Y (excess 0.403 dB, reflection `−12.89 / −12.23 dB`, energy 5.14 %). A `w→2w` input transition was diagnosed as a `−9.58 dB` reflection source. Generic FDTD geometry scanning is stopped; the next input must be a foundry-qualified complex S-matrix or a dedicated EME/inverse-design cell. |
| **G3-D 2×2 coherent combiner** | A 0.8575 µm-wide 2×2 MMI in two-independent-source broadband FDTD: centre imbalance 20.73 dB, worst excess 1.584 dB, reflection `−11.61 dB`, quadrature error 74.41°. A 2–14 µm EME length screen (best 11.0 µm) and a physics-based 1.2/1.4 µm × 3–24 µm EME screen (best 1.4 × 23.75 µm: excess 4.57 dB, quadrature 17.89°) did not clear FDTD promotion. Custom inverse-design ID2 (binary, 0.169 FC total) produced splitter excess 3.49 dB / imbalance 0.35 dB and combiner excess 5.47 dB / imbalance 5.16 dB / max singular value 0.639 — both seeds failed; ID3 was not run. |

### Open — external evidence needed (4)

| Gate | Missing input |
|---|---|
| **G4 fast selector** | 30 GHz electro-optic switch/selector S-parameters and a bandwidth proof (thermo-optic phase control is explicitly *not* an option at 30 GHz). |
| **G4 PD/TIA** | A P5-compatible 50 GHz photodiode + TIA chain with measured responsivity ≥ 0.8 A/W, input noise ≤ 20 pA/√Hz, and reported saturation / dark current / capacitance / TIA swing. Required peak photocurrent ~4.5 mA must stay linear. |
| **G4 thermal** | Heater count, `Pπ` / `PπL`, mean and maximum trim power, control-electronics-in/out limits, and a thermal-crosstalk matrix. Assumption-only envelope: 395 mW mean / 770 mW max against an 800 mW ceiling. |
| **G5 composition** | The full-link loss / launch-power / thermal budget cannot be composed while G3-C, G3-D and the G4 inputs are missing. Assumption-only propagation (`0.8 dB/cm`) + bends give `0.8974 dB/cm` — inside the P5 stress envelope, but not a physical PASS. |

## What remains physically valid

- The delay-line cross-section (`n_g` and process window).
- The exact spiral centerline / GDS route and its DRC checks.
- The R = 10 µm bend loss and reflection.
- Adjacent-turn crosstalk at the selected 5 µm pitch.

These do not depend on the failed/open gates and stay valid within P6's
component-validation scope.

## Rules P6 follows

- The P5 blind score is **never** re-run and is **never** tuned from P6 outcomes.
- If a physical penalty exceeds the P5 assumptions, the *claim* is narrowed —
  the P5 number is not re-fitted.
- No cloud FDTD job is submitted without a recorded credit estimate and explicit
  user approval; non-finite or non-converged results reject the job.
- Full 14.24 cm 3D FDTD is never attempted; only short-cell S-parameters feed the
  compact model.

## Path forward (from the records)

1. Foundry-qualified complex S-matrices for the tap/splitter and the 2×2 combiner,
   **or** dedicated EME / inverse-design cells that pass the gates.
2. Fabricated cutback loss, a 30 GHz selector, a co-measured 50 GHz PD/TIA chain,
   and a 30 × 30 thermal test matrix for the chosen custom process
   ([`../p6-physical-validation/CUSTOM-PROCESS-VALIDATION.md`](../p6-physical-validation/CUSTOM-PROCESS-VALIDATION.md)).
3. Re-compose G5 once those inputs exist. The blind P5 result stays frozen.
