"""Physics-guided EME length screen for the rejected G3-D 2x2 MMI pilot."""
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
from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION
from g3d_mmi_fdtd import build as build_fdtd
from g3d_mmi_fdtd import geometry_parameters, sha256


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3d-mmi-eme-estimate-v1.json"
REFERENCE_LENGTH_UM = geometry_parameters()["mmi_length_um"]
LENGTHS_UM = np.linspace(2.0, 14.0, 49)
MMI_CELL_INDEX = 9


def serialized_sha(simulation: td.EMESimulation) -> str:
    return hashlib.sha256(simulation.model_dump_json().encode()).hexdigest()


def build() -> td.EMESimulation:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    fdtd = build_fdtd("upper")
    p = geometry_parameters()
    mmi_length = p["mmi_length_um"]
    taper_length = p["s_bend_length_um"]
    lead = 3.0
    left_body = -mmi_length / 2
    right_body = mmi_length / 2
    left_far = left_body - taper_length
    right_far = right_body + taper_length
    x_min = left_far - lead
    x_max = right_far + lead

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
    port_modes = td.EMEModeSpec(
        num_modes=4, target_neff=1.87, sort_spec=te_sort
    )
    device_modes = td.EMEModeSpec(
        num_modes=16, target_neff=1.87, sort_spec=te_sort
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
    return td.EMESimulation(
        center=(0, 0, 0),
        # Clip 0.1 um from each x edge so the straight guides cross the EME
        # port planes instead of terminating exactly on a simulation boundary.
        size=(x_max - x_min - 0.2, fdtd.size[1], fdtd.size[2]),
        medium=fdtd.medium,
        structures=fdtd.structures,
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
    simulation = build()
    return {
        "name": "p6-g3d-mmi-eme-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "fdtd_builder_sha256": sha256(
            Path(__file__).resolve().with_name("g3d_mmi_fdtd.py")
        ),
        "cloud_called": False,
        "p5_blind_rerun": False,
        "reference_length_um": REFERENCE_LENGTH_UM,
        "length_sweep_um": {
            "start": float(LENGTHS_UM[0]),
            "stop": float(LENGTHS_UM[-1]),
            "step": float(LENGTHS_UM[1] - LENGTHS_UM[0]),
        },
        "length_sweep_points": len(LENGTHS_UM),
        "eme_cells": len(simulation.eme_grid.cells),
        "mmi_cell_index": MMI_CELL_INDEX,
        "port_modes": 4,
        "device_modes": 16,
        "serialized_simulation_sha256": serialized_sha(simulation),
        "cloud_status": "NOT_SUBMITTED",
        "preflight_passed": len(simulation.eme_grid.cells) == 19,
        "claim_limit": "center-wavelength length seed only; selected geometry requires broadband two-source FDTD",
    }


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    simulation = build()
    task_name = "p6_g3d_mmi_eme_length_screen_v1"
    job = web.Job(
        simulation=simulation,
        task_name=task_name,
        folder_name="P6 Physical Validation",
        verbose=False,
    )
    job.upload()
    cost = float(job.estimate_cost(verbose=False))
    return {
        "name": "p6-g3d-mmi-eme-estimate-v1",
        "source_sha256": sha256(Path(__file__)),
        "task_name": task_name,
        "task_id": str(job.task_id),
        "task_status": str(job.get_info().status),
        "serialized_simulation_sha256": serialized_sha(simulation),
        "estimated_flexcredits": cost,
        "solve_started": False,
        "within_limits": cost < PER_SOURCE_LIMIT_FC and cost < TOTAL_LIMIT_FC,
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
    return np.asarray(
        selected.transpose("mode_index_out", "mode_index_in")
    )


def analyze(data: td.EMESimulationData) -> dict[str, Any]:
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
    return {
        "selected_length_um": selected["length_um"],
        "selected_metrics": selected,
        "sweep_sha256": hashlib.sha256(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "sweep_points": len(records),
        "screen_passed": (
            selected["worst_excess_insertion_loss_db"] <= 0.5
            and selected["worst_imbalance_db"] <= 0.5
            and selected["worst_quadrature_error_deg"] <= 5.0
            and selected["worst_reflection_db"] < -30.0
            and selected["full_s_max_singular_value"] <= 1.000001
        ),
        "claim_limit": "EME center-wavelength length seed; no G3-D acceptance",
    }


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    locked = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    simulation = build()
    if locked["source_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("Source changed after estimate")
    if serialized_sha(simulation) != locked["serialized_simulation_sha256"]:
        raise RuntimeError("Locked simulation mismatch")
    if not locked["within_limits"] or locked["solve_started"]:
        raise RuntimeError("Estimate record is not eligible for execution")
    path = RUNS / "g3d-mmi-eme-length-screen-v1.hdf5"
    job = web.Job(
        simulation=simulation,
        task_name=locked["task_name"],
        folder_name="P6 Physical Validation",
        task_id_cached=locked["task_id"],
        verbose=False,
    )
    data = job.run(path=path)
    return {
        "name": "p6-g3d-mmi-eme-screen-result-v1",
        "source_sha256": sha256(Path(__file__)),
        "estimate_sha256": sha256(ESTIMATE_RECORD),
        "task_id": locked["task_id"],
        "task_status": str(job.get_info().status),
        "result_file": path.name,
        "result_sha256": sha256(path),
        "actual_flexcredits": float(job.real_cost(verbose=False) or 0),
        "p5_blind_rerun": False,
        "analysis": analyze(data),
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
