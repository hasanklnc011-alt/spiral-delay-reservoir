"""Machine-readable P6 EM plan and no-cost local Tidy3D version gate."""

from __future__ import annotations

import argparse
import json
from typing import Any


REQUIRED_TIDY3D_VERSION = "2.12.0"


def budget_policy() -> dict[str, Any]:
    return {
        "user_credit_approval": False,
        "upload_allowed": False,
        "solve_allowed": False,
        "pilot_flexcredit_per_source_max": 0.5,
        "nominal_suite_flexcredit_max": 3.0,
        "convergence_and_corners_flexcredit_max": 10.0,
        "standard_cell_count_max": 20_000_000,
        "bend_cell_count_max": 40_000_000,
    }


def selected_cases() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G1",
            "case": "cross_section_mode",
            "solver": "ModeSolver",
            "depends_on": [],
            "seed_geometry": {"core": "silicon", "cladding": "silica", "width_um": 0.45, "height_um": 0.22},
            "sweep": {"wavelength_um": {"start": 1.52, "stop": 1.58, "points": 13}, "width_um": [0.43, 0.45, 0.47], "height_um": [0.21, 0.22, 0.23]},
            "outputs": ["n_eff", "n_group", "mode_area", "higher_mode_margin"],
            "acceptance": {"group_index_target": 4.0, "group_index_target_tolerance_fraction": 0.02, "delay_at_locked_length_s": 1.9e-9, "delay_tolerance_fraction": 0.02, "relative_n_group_mesh_delta_max": 0.005, "absolute_n_eff_mesh_delta_max": 0.001},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-A",
            "case": "straight_deembedding",
            "solver": "3D_FDTD",
            "depends_on": ["cross_section_mode"],
            "simulation_envelope": {"size_um": [16.0, 4.0, 3.0], "target_cells": [2000000, 6000000]},
            "outputs": ["complex_s21", "complex_s11", "phase_per_length"],
            "acceptance": {"energy_residual_max": 0.01, "reflection_db_max": -30.0, "mesh_loss_delta_db_max": 0.02, "mesh_phase_delta_deg_max": 0.5},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-B",
            "case": "bend_90deg",
            "solver": "2.5D_or_EME_then_selected_3D_FDTD",
            "depends_on": ["cross_section_mode", "straight_deembedding"],
            "sweep": {"radius_um": [10.0, 20.0, 30.0, 50.0], "pitch_um": [3.0, 4.0, 5.0, 6.0]},
            "outputs": ["loss_db_per_90deg", "reflection", "mode_conversion", "phase"],
            "acceptance": {"composed_propagation_plus_bend_db_per_cm_max": 1.0, "mesh_loss_delta_db_max": 0.02, "mesh_phase_delta_deg_max": 0.5},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-B",
            "case": "adjacent_spiral_turn_coupling",
            "solver": "EME_or_selected_3D_FDTD",
            "depends_on": ["cross_section_mode", "straight_deembedding"],
            "outputs": ["coupling_per_length", "crosstalk", "supermode_split"],
            "acceptance": {"full_parallel_length_crosstalk_reported": True},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-C",
            "case": "progressive_signal_tap",
            "solver": "3D_FDTD",
            "depends_on": ["cross_section_mode", "straight_deembedding"],
            "outputs": ["complex_3port_s_matrix", "target_kappa_error", "excess_loss", "reflection", "phase"],
            "acceptance": {"target_kappa_power_absolute_error_max": 0.01, "target_kappa_power_relative_error_max": 0.05, "excess_loss_db_per_cell_max": 0.2, "reflection_db_max": -30.0, "mesh_loss_delta_db_max": 0.02, "mesh_phase_delta_deg_max": 0.5},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-C",
            "case": "lo_1x2_splitter",
            "solver": "3D_FDTD",
            "depends_on": ["cross_section_mode", "straight_deembedding"],
            "outputs": ["complex_3port_s_matrix", "excess_loss", "imbalance", "reflection", "phase_mismatch"],
            "acceptance": {"target_kappa_power": 0.5, "excess_loss_db_per_stage_max": 0.2, "imbalance_db_max": 0.5, "phase_mismatch_deg_max": 2.0, "reflection_db_max": -30.0, "mesh_loss_delta_db_max": 0.02, "mesh_phase_delta_deg_max": 0.5},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G3-D",
            "case": "coherent_2x2_mmi",
            "solver": "3D_FDTD_two_single_port_excitations",
            "depends_on": ["cross_section_mode", "straight_deembedding"],
            "outputs": ["complex_4port_s_matrix", "excess_insertion_loss", "ideal_division", "imbalance", "quadrature_error", "coherent_transfer"],
            "acceptance": {"target_excess_insertion_loss_db_max": 0.5, "hard_excess_insertion_loss_db_max": 1.5, "ideal_single_output_division_db": 3.01029995664, "imbalance_db_max": 0.5, "phase_error_deg_max": 5.0, "passive_s_matrix_max_singular_value": 1.000001, "mesh_loss_delta_db_max": 0.02, "mesh_phase_delta_deg_max": 0.5},
            "cloud_status": "NOT_SUBMITTED",
        },
        {
            "gate": "G4",
            "case": "phase_pd_thermal_compact_evidence",
            "solver": "mode_perturbation_plus_PDK_or_measurement",
            "depends_on": ["cross_section_mode", "coherent_2x2_mmi"],
            "outputs": ["p_pi_l", "heater_time_constant", "thermal_crosstalk", "pd_responsivity", "pd_bandwidth", "pd_noise", "pd_saturation"],
            "acceptance": {"system_pd_bandwidth_hz_min": 15e9, "p5_compatibility_pd_bandwidth_hz_min": 50e9, "pd_responsivity_a_per_w_min": 0.8, "pd_noise_a_per_sqrt_hz_max": 2e-11, "pd_saturation": "REQUIRED"},
            "cloud_status": "NOT_APPLICABLE_UNTIL_PDK_DEFINED",
        },
    ]


def validate_plan(cases: list[dict[str, Any]] | None = None, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    cases = selected_cases() if cases is None else cases
    policy = budget_policy() if policy is None else policy
    names = [case["case"] for case in cases]
    unique = len(names) == len(set(names))
    known: set[str] = set()
    dag_ordered = True
    for case in cases:
        if any(dependency not in known for dependency in case["depends_on"]):
            dag_ordered = False
        known.add(case["case"])
    all_unsubmitted = all(case["cloud_status"] in {"NOT_SUBMITTED", "NOT_APPLICABLE_UNTIL_PDK_DEFINED"} for case in cases)
    no_spend_authority = not policy["user_credit_approval"] and not policy["upload_allowed"] and not policy["solve_allowed"]
    return {
        "unique_case_names": unique,
        "dependency_order_valid": dag_ordered,
        "all_cloud_work_unsubmitted": all_unsubmitted,
        "no_spend_authority": no_spend_authority,
        "passed": unique and dag_ordered and all_unsubmitted and no_spend_authority,
    }


def local_tidy3d_check() -> dict[str, Any]:
    try:
        import tidy3d as td
    except Exception as exc:  # pragma: no cover - depends on optional environment
        return {"passed": False, "required": REQUIRED_TIDY3D_VERSION, "error": repr(exc), "cloud_called": False}
    version = str(td.__version__)
    # Construct a minimal in-memory object. No web API or filesystem call occurs.
    sim = td.Simulation(
        size=(2.0, 2.0, 2.0),
        medium=td.Medium(permittivity=1.0),
        grid_spec=td.GridSpec.uniform(dl=0.2),
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        run_time=1e-15,
    )
    return {
        "passed": version == REQUIRED_TIDY3D_VERSION,
        "required": REQUIRED_TIDY3D_VERSION,
        "installed": version,
        "local_simulation_cells": int(sim.num_cells),
        "cloud_called": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-local", action="store_true", help="Import Tidy3D and build an in-memory simulation; never calls web.")
    args = parser.parse_args()
    cases = selected_cases()
    output: dict[str, Any] = {"required_tidy3d_version": REQUIRED_TIDY3D_VERSION, "budget_policy": budget_policy(), "plan_validation": validate_plan(cases), "cases": cases}
    if args.check_local:
        output["local_check"] = local_tidy3d_check()
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
