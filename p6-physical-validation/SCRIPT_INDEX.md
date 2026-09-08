# P6 script index

Every executable script in `p6-physical-validation/`, grouped by the gate it serves.
Code paths are unchanged from the original project layout so that provenance hash
checks and unit tests keep passing. `estimate` / `preflight` scripts never spend
cloud credits; `cloud` / `execute` / `run` scripts submit Tidy3D jobs and require a
recorded FlexCredit estimate plus explicit approval.

## Component budget model

| Script | Purpose |
|---|---|
| `component_model.py` | Deterministic P6 component and budget model. |

## EM plan / version gate

| Script | Purpose |
|---|---|
| `em_plan.py` | Machine-readable P6 EM plan and no-cost local Tidy3D version gate. |

## G1 — cross-section & group index

| Script | Purpose |
|---|---|
| `g1_candidate_batch.py` | Cost-gated remote G1 candidate search after the provisional seed failed. |
| `g1_candidate_probe.py` | No-cloud cross-section probe used only to nominate remote G1 candidates. |
| `g1_cloud_gate.py` | Upload the locked G1 ModeSolver only to obtain a FlexCredit estimate. |
| `g1_execute.py` | Execute the explicitly approved, already-uploaded P6 G1 task exactly once. |
| `g1_mode_solver.py` | P6 G1 cross-section mode solver. |
| `g1_pdk_migration_probe.py` | No-cloud 220 nm PDK migration impact probe for the G1 delay gate. |
| `g1_remote_preflight.py` | Serialize and validate the P6 G1 remote/subpixel candidate without upload. |
| `g1_selected_validation.py` | Remote convergence and fabrication-corner validation for the selected G1 cross-section. |
| `g1_thickness_refinement.py` | Validate the explicit 180 +/- 5 nm G1 silicon device-layer requirement. |

## G2 — spiral layout

| Script | Purpose |
|---|---|
| `g2_spiral_layout.py` | Generate and independently re-read the exact P6 serial Archimedean spiral. |

## G3-A — straight de-embedding

| Script | Purpose |
|---|---|
| `g3_straight_cloud.py` | Cost-gated execution and analysis of the G3-A two-length straight FDTD pilot. |
| `g3_straight_cloud_v2.py` | Cost-gated lossless-equivalent G3-A convergence suite. |
| `g3_straight_convergence.py` | Cost-gated mesh convergence for the G3-A straight reference. |
| `g3_straight_m15_cloud.py` | Cost-gated missing m15 lossless straight references for bend de-embedding. |
| `g3_straight_preflight.py` | Build the two-length G3-A straight-waveguide FDTD de-embedding suite locally. |
| `g3_straight_preflight_v2.py` | Lossless-equivalent G3-A scattering reference; propagation loss stays external. |

## G3-B — bends & adjacent turns

| Script | Purpose |
|---|---|
| `g3_bend_cloud.py` | Cost-gated selected 3D FDTD validation for the G3-B R=20 um bend. |
| `g3_bend_cloud_v2.py` | Densely faceted, cost-gated G3-B R=20 um bend pilot. |
| `g3_bend_cloud_v3.py` | Cost-gated G3-B R=10 um bend pilot selected from the planned radius screen. |
| `g3_bend_convergence.py` | Cost-gated m20 convergence check for the selected R=10 um bend. |
| `g3_bend_convergence_m25.py` | Cost-gated m25 final convergence check for the selected R=10 um bend. |
| `g3_bend_deembed.py` | De-embed straight propagation phase from the selected bend mesh pair. |
| `g3_bend_deembed_fine.py` | Final m20/m25 straight-reference de-embedding for the selected bend. |
| `g3_bend_mode_screen.py` | Local bent-mode screen for G3-B radius candidates. |
| `g3_bend_preflight.py` | Local-only G3-B quarter-bend and adjacent-turn preflight. |

## G3-C — tap / directional-coupler splitter

| Script | Purpose |
|---|---|
| `g3_coupler_fdtd.py` | Selected 3D FDTD cell for a 50:50 directional coupler with symmetric S-bends. |
| `g3_coupler_fdtd_v2.py` | Redesigned 50:50 coupler pilot with wider isolated ports and calibrated phase. |
| `g3_coupler_mode.py` | Local even/odd supermode synthesis for progressive taps and LO/combiner cells. |
| `g3_coupler_remote.py` | Cost-gated remote/subpixel supermode validation for the selected 200 nm gap. |

## G3-C — MMI splitter

| Script | Purpose |
|---|---|
| `g3_mmi_mode_screen.py` | No-cloud parity-mode screen for a physically targeted MMI/combiner redesign. |
| `g3_mmi_sweep.py` | Cost-gated 3D FDTD length sweep for a symmetric 1x2 MMI splitter. |
| `g3_mmi_targeted.py` | Cost-gated FDTD refinement around the no-cloud MMI modal beat-length. |

## G3-C — slot / adiabatic Y splitter

| Script | Purpose |
|---|---|
| `g3_slot_y_postprocess_v2.py` | Post-process the completed slot-Y v2 HDF5 without starting another solve. |
| `g3_slot_y_splitter.py` | Cost-gated slot-opening adiabatic Y splitter with constant-width output rails. |
| `g3_slot_y_splitter_v2.py` | Corrected cost-gated slot-opening Y splitter; symmetric slot boundaries. |
| `g3_slot_y_splitter_v3.py` | Half-domain long-adiabatic slot-Y convergence candidate for G3-C. |
| `g3_slot_y_taper_diagnostic.py` | Cost-gated FDTD isolation of the slot-Y w-to-2w input taper. |

## G3-C — union-branch Y splitter

| Script | Purpose |
|---|---|
| `g3_union_y_splitter.py` | Cost-gated long union-branch Y splitter without a width-doubling taper. |

## G3-C — Y splitter

| Script | Purpose |
|---|---|
| `g3_y_splitter_fdtd.py` | Cost-gated symmetric adiabatic Y-splitter candidate for G3-C2. |

## G3-D — 2x2 coherent combiner

| Script | Purpose |
|---|---|
| `g3d_combiner_reuse_diagnostic.py` | Reuse a rejected 2x2 coupler solve to exercise G3-D coherent-combiner gates. |
| `g3d_mmi_eme_screen.py` | Physics-guided EME length screen for the rejected G3-D 2x2 MMI pilot. |
| `g3d_mmi_eme_width_screen.py` | Physics-guided G3-D MMI width+length EME screen. |
| `g3d_mmi_fdtd.py` | Selected G3-D 2x2 MMI pilot with two independent FDTD excitations. |
| `g3d_mmi_resume_v1.py` | Resume the hash-locked G3-D pilot after a post-processing-only failure. |

## G3-C/G3-D — inverse design

| Script | Purpose |
|---|---|
| `inverse_design_estimate.py` | Upload-only ID1 cost estimate for the hash-locked inverse-design seeds. |
| `inverse_design_id1_run.py` | Budget-gated ID1 seed optimization for the custom-process devices. |
| `inverse_design_id2_estimate.py` | Upload-only cost estimate for ID2 binary broadband validation. |
| `inverse_design_id2_preflight.py` | Local-only binary seed and simulation preflight for inverse-design ID2. |
| `inverse_design_id2_run.py` | Run and score binary broadband ID2 FDTD validations. |
| `inverse_design_preflight.py` | No-cloud ID0 preflight for custom-process splitter and combiner design regions. |
| `inverse_design_simulation_preflight.py` | No-cloud source, port, and complex-objective preflight for P6 inverse design. |

## G4 — compact model (phase/receiver/thermal)

| Script | Purpose |
|---|---|
| `g4_compact_validation.py` | Deterministic G4 phase-control, receiver, and thermal validation record. |

## G5 — full-link composition

| Script | Purpose |
|---|---|
| `g5_composition.py` | Fail-closed P6 full-link composition from accepted and open evidence. |

## G6 — acceptance audit

| Script | Purpose |
|---|---|
| `g6_acceptance_audit.py` | Machine-readable P6 requirement audit; negative/open evidence stays fail-closed. |
