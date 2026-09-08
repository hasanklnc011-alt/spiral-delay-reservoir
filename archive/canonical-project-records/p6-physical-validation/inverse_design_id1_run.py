"""Budget-gated ID1 seed optimization for the custom-process devices."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import autograd.numpy as anp
import numpy as np
import tidy3d as td
import tidy3d.plugins.invdes as tdi

from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION
from g3d_mmi_fdtd import sha256
from inverse_design_preflight import CONFIG
from inverse_design_simulation_preflight import (
    build_designs,
    phase_invariant_column_objective,
)


SIMULATION_SOURCE = HERE / "inverse_design_simulation_preflight.py"
ESTIMATE_SOURCE = HERE / "inverse_design_estimate.py"
ESTIMATE_RECORD = HERE / "runs" / "inverse-design-id1-estimate-v1.json"
RUNS = HERE / "runs"
DEVICE_PLAN = {
    "splitter": {
        "steps": 3,
        "learning_rate": 0.3,
        "allocation_fc": 0.5,
        "estimate_key": "g3c_splitter",
        "failed_forward_reserve_fc": 0.14347139240602655,
        "cache": RUNS / "inverse-design-id1-splitter-v1.hdf5",
    },
    "combiner": {
        "steps": 3,
        "learning_rate": 0.3,
        "allocation_fc": 1.0,
        "estimate_key": "g3d_combiner",
        "failed_forward_reserve_fc": 0.12137693447015209,
        "cache": RUNS / "inverse-design-id1-combiner-v1.hdf5",
    },
}


def validate_gate(device: str, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    if device not in DEVICE_PLAN:
        raise ValueError(f"Unknown device: {device}")
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    estimate = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if estimate["source_sha256"] != sha256(ESTIMATE_SOURCE):
        raise RuntimeError("Estimate source changed after the cost lock")
    if estimate["simulation_source_sha256"] != sha256(SIMULATION_SOURCE):
        raise RuntimeError("Simulation source changed after the cost lock")
    if estimate["config_sha256"] != sha256(CONFIG):
        raise RuntimeError("Inverse-design config changed after the cost lock")
    if estimate["solve_started"] or not estimate["optimization_allowed"]:
        raise RuntimeError("Estimate record does not authorize ID1 optimization")
    plan = DEVICE_PLAN[device]
    estimated_optimization_cost = (
        plan["steps"]
        * estimate["estimated_iteration_flexcredits"][plan["estimate_key"]]
    )
    estimated_cost = estimated_optimization_cost + plan["failed_forward_reserve_fc"]
    if estimated_cost > plan["allocation_fc"]:
        raise RuntimeError("Planned optimization exceeds its device allocation")
    return {
        "device": device,
        "steps": plan["steps"],
        "learning_rate": plan["learning_rate"],
        "allocation_fc": plan["allocation_fc"],
        "estimated_cost_fc": estimated_cost,
        "failed_forward_reserve_fc": plan["failed_forward_reserve_fc"],
        "estimate_record_sha256": sha256(ESTIMATE_RECORD),
    }


def _amp_values(data: td.SimulationData, name: str, direction: str) -> Any:
    amps = tdi.utils.get_amps(
        data, monitor_name=name, direction=direction, mode_index=0
    )
    return anp.array(amps.values)


def splitter_post_process(data: td.SimulationData, **_: Any) -> Any:
    return phase_invariant_column_objective(
        _amp_values(data, "right_0", "+"),
        _amp_values(data, "right_1", "+"),
        _amp_values(data, "left_0", "-"),
        0.0,
    )


def _combiner_column_objective(
    out0: Any, out1: Any, reflections: tuple[Any, Any], target_phase_deg: float
) -> Any:
    column = anp.stack((out0, out1), axis=0)
    target = anp.array(
        [1.0, anp.exp(1j * anp.deg2rad(target_phase_deg))]
    ) / anp.sqrt(2.0)
    overlap = anp.sum(anp.conj(target)[:, None] * column, axis=0)
    reflected_power = sum(anp.abs(item) ** 2 for item in reflections)
    return anp.mean(anp.abs(overlap) ** 2 - reflected_power)


def combiner_post_process(batch_data: dict[str, td.SimulationData], **_: Any) -> Any:
    if len(batch_data) != 2:
        raise ValueError("G3-D objective requires exactly two source simulations")
    upper, lower = tuple(batch_data.values())
    upper_score = _combiner_column_objective(
        _amp_values(upper, "right_0", "+"),
        _amp_values(upper, "right_1", "+"),
        (
            _amp_values(upper, "left_0", "-"),
            _amp_values(upper, "left_1", "-"),
        ),
        -90.0,
    )
    lower_score = _combiner_column_objective(
        _amp_values(lower, "right_0", "+"),
        _amp_values(lower, "right_1", "+"),
        (
            _amp_values(lower, "left_0", "-"),
            _amp_values(lower, "left_1", "-"),
        ),
        90.0,
    )
    return 0.5 * (upper_score + lower_score)


def summarize_result(device: str, gate: dict[str, Any], result: Any) -> dict[str, Any]:
    final_params = np.asarray(result.params[-1])
    return {
        "name": f"p6-inverse-design-id1-{device}-v1",
        "device": device,
        "source_sha256": sha256(Path(__file__)),
        "simulation_source_sha256": sha256(SIMULATION_SOURCE),
        "config_sha256": sha256(CONFIG),
        "estimate_record_sha256": gate["estimate_record_sha256"],
        "p5_blind_rerun": False,
        "planned_steps": gate["steps"],
        "completed_steps": len(result.objective_fn_val),
        "learning_rate": gate["learning_rate"],
        "allocation_fc": gate["allocation_fc"],
        "estimated_cost_fc": gate["estimated_cost_fc"],
        "objective_history": [float(value) for value in result.objective_fn_val],
        "post_process_history": [float(value) for value in result.post_process_val],
        "penalty_history": [float(value) for value in result.penalty],
        "final_parameter_shape": list(final_params.shape),
        "final_parameter_min": float(np.min(final_params)),
        "final_parameter_max": float(np.max(final_params)),
        "cache_file": str(DEVICE_PLAN[device]["cache"].relative_to(HERE)),
        "id1_can_accept_device": False,
        "next_gate": "binary ID2 broadband two-source 3D FDTD estimate",
    }


def execute(device: str, approved: bool) -> dict[str, Any]:
    gate = validate_gate(device, approved)
    splitter, combiner = build_designs()
    design = splitter if device == "splitter" else combiner
    post_process = splitter_post_process if device == "splitter" else combiner_post_process
    plan = DEVICE_PLAN[device]
    optimizer = tdi.AdamOptimizer(
        design=design,
        num_steps=plan["steps"],
        learning_rate=plan["learning_rate"],
        results_cache_fname=str(plan["cache"]),
        store_full_results=False,
    )
    result = optimizer.run(post_process_fn=post_process)
    return summarize_result(device, gate, result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=tuple(DEVICE_PLAN), required=True)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--user-credit-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(args.device, args.user_credit_approval), indent=2))


if __name__ == "__main__":
    main()
