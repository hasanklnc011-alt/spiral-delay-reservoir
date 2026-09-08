"""Selected G3-D 2x2 MMI pilot with two independent FDTD excitations.

The topology is scaled from Flexcompute's official 2x2 SOI MMI example to the
accepted 343 x 180 nm P6 cross-section.  Upload, estimate, and solve remain
separate, hash-locked actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from shapely.geometry import LineString
from tidy3d import web

from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC
from g3_straight_preflight import G1_CONFIG, HERE, REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3d-mmi-estimate-v1.json"
WAVELENGTHS_UM = np.linspace(1.52, 1.58, 13)
MESH = 15.0
RUN_TIME_S = 3e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complex_record(value: complex) -> dict[str, float]:
    return {"real": float(np.real(value)), "imag": float(np.imag(value))}


def _path_structure(points: list[tuple[float, float]], width: float, height: float, medium: td.Medium, name: str) -> td.Structure:
    polygon = LineString(points).buffer(
        width / 2, cap_style=2, join_style=2, quad_segs=24
    )
    return td.Structure(
        geometry=td.PolySlab(
            vertices=list(polygon.exterior.coords)[:-1],
            slab_bounds=(-height / 2, height / 2),
            axis=2,
        ),
        medium=medium,
        name=name,
    )


def geometry_parameters() -> dict[str, float]:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width = float(accepted["width_um"])
    height = float(accepted["height_um"])
    # Official seed: 400x220 nm guide, 1x3 um MMI, 4 um cosine S-bends,
    # 1 um lateral offset. Scale lateral/longitudinal dimensions by w/0.4.
    scale = width / 0.4
    mmi_width = 1.0 * scale
    mmi_length = 3.0 * scale
    s_bend_length = 4.0 * scale
    s_bend_offset = 1.0 * scale
    near_y = mmi_width / 2 - width / 2
    far_y = near_y + s_bend_offset
    return {
        "waveguide_width_um": width,
        "waveguide_height_um": height,
        "scale_from_official_400nm_seed": scale,
        "mmi_width_um": mmi_width,
        "mmi_length_um": mmi_length,
        "s_bend_length_um": s_bend_length,
        "s_bend_offset_um": s_bend_offset,
        "near_port_center_um": near_y,
        "far_port_center_um": far_y,
        "near_guide_gap_um": 2 * near_y - width,
    }


def build(source_port: str, mesh: float = MESH, run_time_s: float = RUN_TIME_S) -> td.Simulation:
    if source_port not in {"upper", "lower"}:
        raise ValueError("source_port must be 'upper' or 'lower'")
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")

    p = geometry_parameters()
    width = p["waveguide_width_um"]
    height = p["waveguide_height_um"]
    mmi_width = p["mmi_width_um"]
    mmi_length = p["mmi_length_um"]
    s_bend_length = p["s_bend_length_um"]
    near_y = p["near_port_center_um"]
    far_y = p["far_port_center_um"]
    lead = 3.0
    silicon, silica, _ = lossless_materials()

    left_body = -mmi_length / 2
    right_body = mmi_length / 2
    left_far = left_body - s_bend_length
    right_far = right_body + s_bend_length
    count = 161
    x_left = np.linspace(left_far, left_body, count)
    fraction = (x_left - left_far) / s_bend_length
    y_left = far_y + (near_y - far_y) * (0.5 - 0.5 * np.cos(np.pi * fraction))
    upper_left = [(left_far - lead, far_y)] + list(zip(x_left, y_left))
    upper_right = [(-x, y) for x, y in reversed(upper_left)]
    lower_left = [(x, -y) for x, y in upper_left]
    lower_right = [(x, -y) for x, y in upper_right]

    structures = (
        td.Structure(
            geometry=td.Box(
                center=(0, 0, 0), size=(mmi_length, mmi_width, height)
            ),
            medium=silicon,
            name="mmi_body",
        ),
        _path_structure(upper_left, width, height, silicon, "upper_input"),
        _path_structure(lower_left, width, height, silicon, "lower_input"),
        _path_structure(upper_right, width, height, silicon, "upper_output"),
        _path_structure(lower_right, width, height, silicon, "lower_output"),
    )

    source_x = left_far - lead + 0.65
    input_monitor_x = left_far - lead + 1.45
    output_monitor_x = right_far + lead - 1.45
    port_size = (0, 0.9, 1.2)
    freqs = td.C_0 / WAVELENGTHS_UM
    f0 = td.C_0 / 1.55
    fwidth = 1.5 * (max(freqs) - min(freqs))
    mode_spec = td.ModeSpec(
        num_modes=2,
        target_neff=1.87,
        sort_spec=td.ModeSortSpec(
            filter_key="TE_fraction",
            filter_reference=0.8,
            filter_order="over",
            keep_modes=1,
        ),
    )
    source_y = far_y if source_port == "upper" else -far_y
    source = td.ModeSource(
        center=(source_x, source_y, 0),
        size=port_size,
        source_time=td.GaussianPulse(freq0=f0, fwidth=fwidth),
        direction="+",
        mode_spec=mode_spec,
        mode_index=0,
        name=f"source_{source_port}",
    )
    monitors = tuple(
        td.ModeMonitor(
            center=(x, y, 0),
            size=port_size,
            freqs=freqs,
            mode_spec=mode_spec,
            name=name,
        )
        for name, x, y in (
            ("input_upper", input_monitor_x, far_y),
            ("input_lower", input_monitor_x, -far_y),
            ("output_upper", output_monitor_x, far_y),
            ("output_lower", output_monitor_x, -far_y),
        )
    )
    x_extent = 2 * (right_far + lead + 1.5)
    y_extent = 2 * (far_y + 1.5)
    return td.Simulation(
        center=(0, 0, 0),
        size=(x_extent, y_extent, 2.0),
        medium=silica,
        structures=structures,
        sources=(source,),
        monitors=monitors,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(
            wavelength=1.55, min_steps_per_wvl=mesh
        ),
        run_time=run_time_s,
        shutoff=1e-7,
        subpixel=True,
        symmetry=(0, 0, 1),
    )


def serialized_sha(simulation: td.Simulation) -> str:
    return hashlib.sha256(simulation.model_dump_json().encode()).hexdigest()


def preflight() -> dict[str, Any]:
    simulations = {port: build(port) for port in ("upper", "lower")}
    p = geometry_parameters()
    symmetric = (
        p["near_port_center_um"] > p["waveguide_width_um"] / 2
        and p["far_port_center_um"] > p["near_port_center_um"]
    )
    return {
        "name": "p6-g3d-mmi-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "g1_config_sha256": sha256(G1_CONFIG),
        "cloud_called": False,
        "p5_blind_rerun": False,
        "design_basis": "Flexcompute official 2x2 SOI MMI seed, uniformly scaled by accepted width / 0.4 um",
        "geometry": p,
        "independent_excitations": list(simulations),
        "serialized_simulation_sha256": {
            port: serialized_sha(sim) for port, sim in simulations.items()
        },
        "simulation_cells": {
            port: int(sim.num_cells) for port, sim in simulations.items()
        },
        "computational_grid_points": {
            port: int(sim.num_computational_grid_points)
            for port, sim in simulations.items()
        },
        "geometry_symmetry_preflight_passed": symmetric,
        "upload_allowed": False,
        "solve_allowed": False,
        "preflight_passed": symmetric,
    }


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    tasks = []
    for port in ("upper", "lower"):
        simulation = build(port)
        task_name = f"p6_g3d_mmi_{port}_m15"
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
                "source_port": port,
                "task_name": task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_simulation_sha256": serialized_sha(simulation),
                "simulation_cells": int(simulation.num_cells),
                "computational_grid_points": int(
                    simulation.num_computational_grid_points
                ),
                "estimated_flexcredits": cost,
                "solve_started": False,
                "within_per_source_limit": cost < PER_SOURCE_LIMIT_FC,
            }
        )
    total = sum(task["estimated_flexcredits"] for task in tasks)
    return {
        "name": "p6-g3d-mmi-estimate-v1",
        "source_sha256": sha256(Path(__file__)),
        "tasks": tasks,
        "estimated_total_flexcredits": total,
        "within_limits": all(x["within_per_source_limit"] for x in tasks)
        and total < TOTAL_LIMIT_FC,
        "solve_started": False,
    }


def _port_column(data: td.SimulationData, source_port: str) -> tuple[np.ndarray, np.ndarray]:
    incident_name = f"input_{source_port}"
    incident = np.asarray(
        data[incident_name].amps.sel(direction="+", mode_index=0)
    )
    transmitted = np.stack(
        [
            np.asarray(data[name].amps.sel(direction="+", mode_index=0))
            / incident
            for name in ("output_upper", "output_lower")
        ],
        axis=1,
    )
    reflected = np.stack(
        [
            np.asarray(data[name].amps.sel(direction="-", mode_index=0))
            / incident
            for name in ("input_upper", "input_lower")
        ],
        axis=1,
    )
    return transmitted, reflected


def metrics(data_by_port: dict[str, td.SimulationData]) -> dict[str, Any]:
    columns_t = []
    columns_r = []
    for port in ("upper", "lower"):
        transmitted, reflected = _port_column(data_by_port[port], port)
        columns_t.append(transmitted)
        columns_r.append(reflected)
    transmission = np.stack(columns_t, axis=2)
    reflection = np.stack(columns_r, axis=2)
    center = len(WAVELENGTHS_UM) // 2

    per_wavelength = []
    for index, wavelength in enumerate(WAVELENGTHS_UM):
        t_matrix = transmission[index]
        r_left = reflection[index]
        # The geometry is exactly mirror-symmetric along x. Reciprocity and
        # longitudinal symmetry complete the four-port matrix from two left
        # excitations without additional coherent-source jobs.
        full_s = np.block([[r_left, t_matrix.T], [t_matrix, r_left]])
        singular_max = float(np.max(np.linalg.svd(full_s, compute_uv=False)))
        inputs = []
        for source_index, source_port in enumerate(("upper", "lower")):
            powers = np.abs(t_matrix[:, source_index]) ** 2
            total = float(np.sum(powers))
            phase = float(
                np.angle(
                    t_matrix[0, source_index] / t_matrix[1, source_index],
                    deg=True,
                )
            )
            inputs.append(
                {
                    "source_port": source_port,
                    "output_powers": [float(x) for x in powers],
                    "total_output_power": total,
                    "excess_insertion_loss_db": float(-10 * np.log10(total)),
                    "imbalance_db": float(abs(10 * np.log10(powers[0] / powers[1]))),
                    "relative_output_phase_deg": phase,
                    "quadrature_error_deg": float(abs(abs((phase + 180) % 360 - 180) - 90)),
                    "total_reflection_power": float(
                        np.sum(np.abs(r_left[:, source_index]) ** 2)
                    ),
                }
            )
        per_wavelength.append(
            {
                "wavelength_um": float(wavelength),
                "transmission_complex": [
                    [complex_record(value) for value in row] for row in t_matrix
                ],
                "reflection_complex": [
                    [complex_record(value) for value in row] for row in r_left
                ],
                "full_s_max_singular_value": singular_max,
                "inputs": inputs,
            }
        )

    center_case = per_wavelength[center]
    all_inputs = [x for case in per_wavelength for x in case["inputs"]]
    coherent = {}
    t_center = transmission[center]
    for phase_deg in (0, 90, 180, 270):
        vector = np.array([1.0, np.exp(1j * np.deg2rad(phase_deg))])
        output = t_center @ vector
        coherent[str(phase_deg)] = {
            "output_power": [float(abs(x) ** 2) for x in output],
            "total_output_power": float(np.sum(abs(output) ** 2)),
            "input_power": 2.0,
        }
    return {
        "center_wavelength_um": float(WAVELENGTHS_UM[center]),
        "center": center_case,
        "worst_excess_insertion_loss_db": max(
            x["excess_insertion_loss_db"] for x in all_inputs
        ),
        "worst_imbalance_db": max(x["imbalance_db"] for x in all_inputs),
        "worst_quadrature_error_deg": max(
            x["quadrature_error_deg"] for x in all_inputs
        ),
        "worst_total_reflection_db": float(
            10 * np.log10(max(x["total_reflection_power"] for x in all_inputs))
        ),
        "worst_full_s_max_singular_value": max(
            x["full_s_max_singular_value"] for x in per_wavelength
        ),
        "coherent_equal_input_transfer_center": coherent,
        "per_wavelength": per_wavelength,
    }


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    locked = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not locked["within_limits"] or locked["solve_started"]:
        raise RuntimeError("Estimate record is not eligible for execution")
    if locked["source_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("Source changed after estimate")

    data_by_port: dict[str, td.SimulationData] = {}
    task_records = []
    for item in locked["tasks"]:
        port = item["source_port"]
        simulation = build(port)
        if serialized_sha(simulation) != item["serialized_simulation_sha256"]:
            raise RuntimeError(f"Locked simulation mismatch for {port}")
        path = RUNS / f"g3d-mmi-{port}_m15-result-v1.hdf5"
        job = web.Job(
            simulation=simulation,
            task_name=item["task_name"],
            folder_name="P6 Physical Validation",
            task_id_cached=item["task_id"],
            verbose=False,
        )
        data = job.run(path=path)
        data_by_port[port] = data
        task_records.append(
            {
                "source_port": port,
                "task_id": item["task_id"],
                "task_status": str(job.get_info().status),
                "result_file": path.name,
                "result_sha256": sha256(path),
                "actual_flexcredits": float(job.real_cost(verbose=False) or 0),
                "final_decay": float(data.log.final_decay_value),
            }
        )

    measured = metrics(data_by_port)
    final_decay = max(x["final_decay"] for x in task_records)
    gates = {
        "target_excess_le_0p5_db": measured["worst_excess_insertion_loss_db"] <= 0.5,
        "hard_excess_le_1p5_db": measured["worst_excess_insertion_loss_db"] <= 1.5,
        "imbalance_le_0p5_db": measured["worst_imbalance_db"] <= 0.5,
        "quadrature_error_le_5_deg": measured["worst_quadrature_error_deg"] <= 5.0,
        "reflection_below_minus_30_db": measured["worst_total_reflection_db"] < -30.0,
        "passive_singular_value_le_1p000001": measured["worst_full_s_max_singular_value"] <= 1.000001,
        "final_decay_le_1e_7": final_decay <= 1e-7,
        "two_independent_excitations": len(data_by_port) == 2,
    }
    return {
        "name": "p6-g3d-mmi-result-v1",
        "source_sha256": sha256(Path(__file__)),
        "estimate_sha256": sha256(ESTIMATE_RECORD),
        "p5_blind_rerun": False,
        "geometry": geometry_parameters(),
        "tasks": task_records,
        "actual_total_flexcredits": sum(
            x["actual_flexcredits"] for x in task_records
        ),
        "metrics": measured,
        "gates": gates,
        "pilot_passed": all(gates.values()),
        "g3d_accepted": False,
        "claim_limit": "m15 pilot only; acceptance requires passing m20/m25 convergence",
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
        result = preflight()
    elif args.upload_estimate:
        result = estimate(approved=args.user_credit_approval)
    else:
        result = execute(approved=args.user_solve_approval)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
