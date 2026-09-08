"""Run and score binary broadband ID2 FDTD validations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d import web
import tidy3d.plugins.invdes as tdi

from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION
from g3d_mmi_fdtd import sha256
from inverse_design_preflight import CONFIG
from inverse_design_id2_preflight import load_binary_seed, serialized_sha


ESTIMATE_SOURCE = HERE / "inverse_design_id2_estimate.py"
ESTIMATE_RECORD = HERE / "runs" / "inverse-design-id2-estimate-v1.json"
RUNS = HERE / "runs"


def validate_gate(approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    estimate = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if estimate["source_sha256"] != sha256(ESTIMATE_SOURCE):
        raise RuntimeError("ID2 estimate source changed after cost lock")
    if estimate["config_sha256"] != sha256(CONFIG):
        raise RuntimeError("Inverse-design config changed after cost lock")
    if estimate["solve_started"] or not estimate["execution_allowed"]:
        raise RuntimeError("ID2 estimate does not authorize execution")
    if estimate["estimated_total_flexcredits"] >= estimate["id2_limit_flexcredits"]:
        raise RuntimeError("ID2 estimate exceeds the configured limit")
    return estimate


def _amp(data: td.SimulationData, monitor: str, direction: str) -> np.ndarray:
    return np.asarray(
        tdi.utils.get_amps(data, monitor_name=monitor, direction=direction, mode_index=0).values
    )


def _db(power: np.ndarray) -> np.ndarray:
    return 10.0 * np.log10(np.maximum(power, 1e-30))


def _phase_error(measured: np.ndarray, target_deg: float) -> np.ndarray:
    return np.abs((measured - target_deg + 180.0) % 360.0 - 180.0)


def score_splitter(data: td.SimulationData, targets: dict[str, float]) -> dict[str, Any]:
    out0 = _amp(data, "right_0", "+")
    out1 = _amp(data, "right_1", "+")
    reflection = _amp(data, "left_0", "-")
    p0, p1 = np.abs(out0) ** 2, np.abs(out1) ** 2
    excess = -_db(p0 + p1)
    imbalance = np.abs(_db(p0) - _db(p1))
    reflection_db = _db(np.abs(reflection) ** 2)
    phase = np.angle(out1 / out0, deg=True)
    passed = bool(
        np.max(excess) <= targets["excess_loss_db_max"]
        and np.max(imbalance) <= targets["imbalance_db_max"]
        and np.max(reflection_db) <= targets["reflection_db_max"]
    )
    return {
        "output_power_0": p0.tolist(),
        "output_power_1": p1.tolist(),
        "excess_loss_db": excess.tolist(),
        "imbalance_db": imbalance.tolist(),
        "reflection_db": reflection_db.tolist(),
        "relative_output_phase_deg": phase.tolist(),
        "worst_excess_loss_db": float(np.max(excess)),
        "worst_imbalance_db": float(np.max(imbalance)),
        "worst_reflection_db": float(np.max(reflection_db)),
        "id2_metric_pass": passed,
    }


def score_combiner(
    data_items: list[td.SimulationData], targets: dict[str, float]
) -> dict[str, Any]:
    columns = []
    reflection_powers = []
    phase_errors = []
    excesses = []
    imbalances = []
    target_phases = (-90.0, 90.0)
    for data, target_phase in zip(data_items, target_phases):
        out0 = _amp(data, "right_0", "+")
        out1 = _amp(data, "right_1", "+")
        columns.append(np.stack((out0, out1), axis=0))
        p0, p1 = np.abs(out0) ** 2, np.abs(out1) ** 2
        excesses.append(-_db(p0 + p1))
        imbalances.append(np.abs(_db(p0) - _db(p1)))
        phase_errors.append(_phase_error(np.angle(out1 / out0, deg=True), target_phase))
        reflection_powers.append(
            np.abs(_amp(data, "left_0", "-")) ** 2
            + np.abs(_amp(data, "left_1", "-")) ** 2
        )
    scattering = np.stack(columns, axis=2)  # output, frequency, source
    singular = [float(np.linalg.svd(scattering[:, index, :], compute_uv=False)[0]) for index in range(scattering.shape[1])]
    reflection_db = [_db(item) for item in reflection_powers]
    worst_excess = float(np.max(excesses))
    worst_imbalance = float(np.max(imbalances))
    worst_phase = float(np.max(phase_errors))
    worst_reflection = float(np.max(reflection_db))
    max_singular = float(np.max(singular))
    passed = bool(
        worst_excess <= targets["excess_loss_db_hard_max"]
        and worst_imbalance <= targets["imbalance_db_max"]
        and worst_phase <= targets["quadrature_error_deg_max"]
        and worst_reflection <= targets["reflection_db_max"]
        and max_singular <= targets["passivity_max_singular_value"]
    )
    return {
        "excess_loss_db_by_source": [item.tolist() for item in excesses],
        "imbalance_db_by_source": [item.tolist() for item in imbalances],
        "quadrature_error_deg_by_source": [item.tolist() for item in phase_errors],
        "reflection_db_by_source": [item.tolist() for item in reflection_db],
        "max_singular_value_by_wavelength": singular,
        "worst_excess_loss_db": worst_excess,
        "worst_imbalance_db": worst_imbalance,
        "worst_quadrature_error_deg": worst_phase,
        "worst_reflection_db": worst_reflection,
        "max_singular_value": max_singular,
        "id2_metric_pass": passed,
    }


def execute(approved: bool) -> dict[str, Any]:
    estimate = validate_gate(approved)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    results = {}
    data_by_device = {}
    for device in ("splitter", "combiner"):
        simulations, _, preflight = load_binary_seed(device)
        data_items = []
        task_items = []
        for index, (key, simulation) in enumerate(simulations.items()):
            expected = next(
                item for item in estimate["tasks"]
                if item["device"] == device and item["simulation_key"] == key
            )
            if serialized_sha(simulation) != expected["serialized_simulation_sha256"]:
                raise RuntimeError(f"{device}/{key} changed after estimate")
            path = RUNS / f"inverse-design-id2-{device}-{index}-v1.hdf5"
            data = web.run(
                simulation,
                task_name=f"p6_inverse_design_id2_run_{device}_{index}_v1",
                folder_name="P6 Physical Validation",
                path=str(path),
                verbose=False,
            )
            data_items.append(data)
            task_items.append({"simulation_key": key, "data_file": str(path.relative_to(HERE))})
        data_by_device[device] = data_items
        results[device] = {"preflight": preflight, "tasks": task_items}
    targets = config["devices"]
    results["splitter"]["metrics"] = score_splitter(
        data_by_device["splitter"][0], targets["g3c_splitter"]["targets"]
    )
    results["combiner"]["metrics"] = score_combiner(
        data_by_device["combiner"], targets["g3d_combiner"]["targets"]
    )
    return {
        "name": "p6-inverse-design-id2-binary-fdtd-v1",
        "source_sha256": sha256(Path(__file__)),
        "estimate_record_sha256": sha256(ESTIMATE_RECORD),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "wavelengths_um": config["wavelengths_um"],
        "estimated_total_flexcredits": estimate["estimated_total_flexcredits"],
        "devices": results,
        "id2_all_metric_pass": all(results[item]["metrics"]["id2_metric_pass"] for item in results),
        "devices_accepted": False,
        "acceptance_blocker": "ID3 convergence/corners and CP0 manufacturing-rule closure required",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--user-credit-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(args.user_credit_approval), indent=2))


if __name__ == "__main__":
    main()
