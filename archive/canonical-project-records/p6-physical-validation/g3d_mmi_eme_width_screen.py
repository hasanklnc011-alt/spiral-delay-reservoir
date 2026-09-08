"""Physics-guided G3-D MMI width+length EME screen.

Only the 1.2 and 1.4 um body widths selected by the local mode diagnosis are
evaluated.  The center-wavelength screen may nominate one geometry for the
required two-source broadband FDTD pilot, but cannot accept G3-D by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d import web

from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC
from g3_straight_preflight import G1_CONFIG, HERE, REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials
from g3d_mmi_fdtd import _path_structure, sha256


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3d-mmi-eme-width-estimate-v1.json"
WIDTHS_UM = (1.2, 1.4)
LENGTHS_UM = np.linspace(3.0, 24.0, 85)
REFERENCE_LENGTH_UM = 12.0
MMI_CELL_INDEX = 9
S_BEND_LENGTH_UM = 3.43
S_BEND_OFFSET_UM = 0.8575


def serialized_sha(simulation: td.EMESimulation) -> str:
    return hashlib.sha256(simulation.model_dump_json().encode()).hexdigest()


def geometry_parameters(mmi_width_um: float) -> dict[str, float]:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width = float(accepted["width_um"])
    height = float(accepted["height_um"])
    near_y = mmi_width_um / 2 - width / 2
    far_y = near_y + S_BEND_OFFSET_UM
    return {
        "waveguide_width_um": width,
        "waveguide_height_um": height,
        "mmi_width_um": float(mmi_width_um),
        "reference_mmi_length_um": REFERENCE_LENGTH_UM,
        "s_bend_length_um": S_BEND_LENGTH_UM,
        "s_bend_offset_um": S_BEND_OFFSET_UM,
        "near_port_center_um": near_y,
        "far_port_center_um": far_y,
        "near_guide_gap_um": 2 * near_y - width,
    }


def build(mmi_width_um: float) -> td.EMESimulation:
    if mmi_width_um not in WIDTHS_UM:
        raise ValueError(f"width must be one of {WIDTHS_UM}")
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")

    p = geometry_parameters(mmi_width_um)
    width = p["waveguide_width_um"]
    height = p["waveguide_height_um"]
    near_y = p["near_port_center_um"]
    far_y = p["far_port_center_um"]
    lead = 3.0
    silicon, silica, _ = lossless_materials()
    left_body = -REFERENCE_LENGTH_UM / 2
    right_body = REFERENCE_LENGTH_UM / 2
    left_far = left_body - S_BEND_LENGTH_UM
    right_far = right_body + S_BEND_LENGTH_UM

    count = 161
    x_left = np.linspace(left_far, left_body, count)
    fraction = (x_left - left_far) / S_BEND_LENGTH_UM
    y_left = far_y + (near_y - far_y) * (
        0.5 - 0.5 * np.cos(np.pi * fraction)
    )
    upper_left = [(left_far - lead, far_y)] + list(zip(x_left, y_left))
    upper_right = [(-x, y) for x, y in reversed(upper_left)]
    lower_left = [(x, -y) for x, y in upper_left]
    lower_right = [(x, -y) for x, y in upper_right]
    structures = (
        td.Structure(
            geometry=td.Box(
                center=(0, 0, 0),
                size=(REFERENCE_LENGTH_UM, mmi_width_um, height),
            ),
            medium=silicon,
            name="mmi_body",
        ),
        _path_structure(upper_left, width, height, silicon, "upper_input"),
        _path_structure(lower_left, width, height, silicon, "lower_input"),
        _path_structure(upper_right, width, height, silicon, "upper_output"),
        _path_structure(lower_right, width, height, silicon, "lower_output"),
    )

    left_taper_internal = np.linspace(left_far, left_body, 9)[1:-1]
    right_taper_internal = np.linspace(right_body, right_far, 9)[1:-1]
    boundaries = np.concatenate(
        (
            [left_far],
            left_taper_internal,
            [left_body, right_body],
            right_taper_internal,
            [right_far],
        )
    )
    te_sort = td.ModeSortSpec(
        filter_key="TE_fraction", filter_reference=0.5, filter_order="over"
    )
    port_modes = td.EMEModeSpec(num_modes=4, target_neff=1.87, sort_spec=te_sort)
    device_modes = td.EMEModeSpec(
        num_modes=20, target_neff=1.87, sort_spec=te_sort
    )
    mode_specs = (
        [port_modes]
        + [device_modes] * 8
        + [device_modes]
        + [device_modes] * 8
        + [port_modes]
    )
    if len(mode_specs) != len(boundaries) + 1:
        raise RuntimeError("EME cell construction mismatch")
    scale_factors = np.ones((len(LENGTHS_UM), len(mode_specs)))
    scale_factors[:, MMI_CELL_INDEX] = LENGTHS_UM / REFERENCE_LENGTH_UM
    x_min = left_far - lead
    x_max = right_far + lead
    return td.EMESimulation(
        center=(0, 0, 0),
        size=(x_max - x_min - 0.2, 2 * (far_y + 1.5), 2.0),
        medium=silica,
        structures=structures,
        grid_spec=td.GridSpec.auto(wavelength=1.55, min_steps_per_wvl=15),
        eme_grid_spec=td.EMEExplicitGrid(
            boundaries=boundaries, mode_specs=mode_specs
        ),
        freqs=[td.C_0 / 1.55],
        axis=0,
        port_offsets=(0.4, 0.4),
        sweep_spec=td.EMELengthSweep(scale_factors=scale_factors),
        symmetry=(0, 0, 1),
        store_port_modes=True,
    )


def preflight() -> dict[str, Any]:
    simulations = {str(width): build(width) for width in WIDTHS_UM}
    return {
        "name": "p6-g3d-mmi-eme-width-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "g1_config_sha256": sha256(G1_CONFIG),
        "cloud_called": False,
        "p5_blind_rerun": False,
        "selection_basis": "local mode diagnosis selected only 1.2 and 1.4 um bodies",
        "widths_um": list(WIDTHS_UM),
        "geometries": {
            key: geometry_parameters(float(key)) for key in simulations
        },
        "length_sweep_um": {
            "start": float(LENGTHS_UM[0]),
            "stop": float(LENGTHS_UM[-1]),
            "step": float(LENGTHS_UM[1] - LENGTHS_UM[0]),
            "points": len(LENGTHS_UM),
        },
        "eme_cells": {key: len(sim.eme_grid.cells) for key, sim in simulations.items()},
        "mmi_cell_index": MMI_CELL_INDEX,
        "port_modes": 4,
        "device_modes": 20,
        "serialized_simulation_sha256": {
            key: serialized_sha(sim) for key, sim in simulations.items()
        },
        "cloud_status": "NOT_SUBMITTED",
        "preflight_passed": all(
            len(sim.eme_grid.cells) == 19 for sim in simulations.values()
        ),
        "claim_limit": "center-wavelength physics-guided seed; passing candidate still requires broadband two-source FDTD",
    }


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    tasks = []
    for width in WIDTHS_UM:
        simulation = build(width)
        tag = str(width).replace(".", "p")
        task_name = f"p6_g3d_mmi_eme_width_{tag}_v1"
        job = web.Job(
            simulation=simulation,
            task_name=task_name,
            folder_name="P6 Physical Validation",
            verbose=False,
        )
        job.upload()
        cost = float(job.estimate_cost(verbose=False))
        tasks.append(
            {
                "mmi_width_um": width,
                "task_name": task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_simulation_sha256": serialized_sha(simulation),
                "estimated_flexcredits": cost,
                "solve_started": False,
                "within_per_source_limit": cost < PER_SOURCE_LIMIT_FC,
            }
        )
    total = sum(task["estimated_flexcredits"] for task in tasks)
    return {
        "name": "p6-g3d-mmi-eme-width-estimate-v1",
        "source_sha256": sha256(Path(__file__)),
        "tasks": tasks,
        "estimated_total_flexcredits": total,
        "within_limits": all(x["within_per_source_limit"] for x in tasks)
        and total < TOTAL_LIMIT_FC,
        "solve_started": False,
    }


def _physical_basis(block: np.ndarray) -> np.ndarray:
    hadamard = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    return hadamard @ block @ hadamard


def _extract_block(array: Any, sweep_index: int) -> np.ndarray:
    selected = array.isel(
        sweep_index=sweep_index,
        f=0,
        mode_index_out=slice(0, 2),
        mode_index_in=slice(0, 2),
    )
    return np.asarray(selected.transpose("mode_index_out", "mode_index_in"))


def analyze(data: td.EMESimulationData, mmi_width_um: float) -> dict[str, Any]:
    records = []
    for index, length in enumerate(LENGTHS_UM):
        s11 = _physical_basis(_extract_block(data.smatrix.S11, index))
        s21 = _physical_basis(_extract_block(data.smatrix.S21, index))
        s12 = _physical_basis(_extract_block(data.smatrix.S12, index))
        s22 = _physical_basis(_extract_block(data.smatrix.S22, index))
        full_s = np.block([[s11, s12], [s21, s22]])
        input_metrics = []
        for source in range(2):
            powers = np.abs(s21[:, source]) ** 2
            total = float(np.sum(powers))
            phase = float(np.angle(s21[0, source] / s21[1, source], deg=True))
            wrapped = (phase + 180) % 360 - 180
            input_metrics.append(
                {
                    "source_port": "upper" if source == 0 else "lower",
                    "output_powers": [float(x) for x in powers],
                    "excess_insertion_loss_db": float(-10 * np.log10(total)),
                    "imbalance_db": float(abs(10 * np.log10(powers[0] / powers[1]))),
                    "quadrature_error_deg": float(abs(abs(wrapped) - 90)),
                    "reflection_db": float(
                        10 * np.log10(np.sum(np.abs(s11[:, source]) ** 2))
                    ),
                }
            )
        worst_excess = max(x["excess_insertion_loss_db"] for x in input_metrics)
        worst_imbalance = max(x["imbalance_db"] for x in input_metrics)
        worst_phase = max(x["quadrature_error_deg"] for x in input_metrics)
        worst_reflection = max(x["reflection_db"] for x in input_metrics)
        singular = float(np.max(np.linalg.svd(full_s, compute_uv=False)))
        score = (
            max(worst_excess - 0.5, 0) / 0.5
            + max(worst_imbalance - 0.5, 0) / 0.5
            + max(worst_phase - 5.0, 0) / 5.0
            + max(worst_reflection + 30.0, 0) / 10.0
            + max(singular - 1.000001, 0) * 100
        )
        records.append(
            {
                "mmi_width_um": mmi_width_um,
                "length_um": float(length),
                "inputs": input_metrics,
                "worst_excess_insertion_loss_db": worst_excess,
                "worst_imbalance_db": worst_imbalance,
                "worst_quadrature_error_deg": worst_phase,
                "worst_reflection_db": worst_reflection,
                "full_s_max_singular_value": singular,
                "selection_score": float(score),
            }
        )
    selected = min(records, key=lambda item: item["selection_score"])
    passed = (
        selected["worst_excess_insertion_loss_db"] <= 0.5
        and selected["worst_imbalance_db"] <= 0.5
        and selected["worst_quadrature_error_deg"] <= 5.0
        and selected["worst_reflection_db"] < -30.0
        and selected["full_s_max_singular_value"] <= 1.000001
    )
    return {
        "mmi_width_um": mmi_width_um,
        "selected_length_um": selected["length_um"],
        "selected_metrics": selected,
        "sweep_sha256": hashlib.sha256(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "sweep_points": len(records),
        "screen_passed": passed,
    }


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    locked = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if locked["source_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("Source changed after estimate")
    if not locked["within_limits"] or locked["solve_started"]:
        raise RuntimeError("Estimate record is not eligible for execution")
    task_records = []
    analyses = []
    for item in locked["tasks"]:
        width = float(item["mmi_width_um"])
        simulation = build(width)
        if serialized_sha(simulation) != item["serialized_simulation_sha256"]:
            raise RuntimeError(f"Locked simulation mismatch for width {width}")
        tag = str(width).replace(".", "p")
        path = RUNS / f"g3d-mmi-eme-width-{tag}-result-v1.hdf5"
        job = web.Job(
            simulation=simulation,
            task_name=item["task_name"],
            folder_name="P6 Physical Validation",
            task_id_cached=item["task_id"],
            verbose=False,
        )
        data = job.run(path=path)
        task_records.append(
            {
                "mmi_width_um": width,
                "task_id": item["task_id"],
                "task_status": str(job.get_info().status),
                "result_file": path.name,
                "result_sha256": sha256(path),
                "actual_flexcredits": float(job.real_cost(verbose=False) or 0),
            }
        )
        analyses.append(analyze(data, width))
    selected = min(
        (analysis["selected_metrics"] for analysis in analyses),
        key=lambda item: item["selection_score"],
    )
    return {
        "name": "p6-g3d-mmi-eme-width-screen-result-v1",
        "source_sha256": sha256(Path(__file__)),
        "estimate_sha256": sha256(ESTIMATE_RECORD),
        "p5_blind_rerun": False,
        "tasks": task_records,
        "actual_total_flexcredits": sum(
            item["actual_flexcredits"] for item in task_records
        ),
        "width_analyses": analyses,
        "selected_candidate": selected,
        "screen_passed": any(item["screen_passed"] for item in analyses),
        "g3d_accepted": False,
        "claim_limit": "EME center-wavelength seed only; selected candidate requires broadband two-source FDTD",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--upload-estimate", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--user-credit-approval", action="store_true")
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        record = preflight()
    elif args.upload_estimate:
        record = estimate(approved=args.user_credit_approval)
    else:
        record = execute(approved=args.user_solve_approval)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
