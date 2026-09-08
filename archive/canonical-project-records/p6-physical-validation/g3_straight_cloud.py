"""Cost-gated execution and analysis of the G3-A two-length straight FDTD pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from tidy3d import web

from g3_straight_preflight import HERE, build_straight


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3a-straight-estimate-v1.json"
PER_SOURCE_LIMIT_FC = 0.5
TOTAL_LIMIT_FC = 3.0


def cases() -> list[dict[str, float]]:
    return [{"name": "length4_m15", "length_um": 4.0}, {"name": "length8_m15", "length_um": 8.0}]


def build_case(case: dict[str, float]) -> tuple[Any, str]:
    simulation = build_straight(case["length_um"], mesh=15.0)
    digest = hashlib.sha256(simulation.model_dump_json().encode("utf-8")).hexdigest()
    return simulation, digest


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    jobs = []
    for case in cases():
        simulation, digest = build_case(case)
        task_name = f"p6_g3a_straight_{case['name']}"
        job = web.Job(simulation=simulation, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
        job.upload()
        jobs.append({**case, "task_name": task_name, "task_id": str(job.task_id), "task_status": str(job.get_info().status), "serialized_simulation_sha256": digest, "estimated_flexcredits": float(job.estimate_cost(verbose=False)), "solve_started": False})
    total = sum(item["estimated_flexcredits"] for item in jobs)
    return {"name": "p6-g3a-straight-estimate-v1", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "jobs": jobs, "estimated_total_flexcredits": total, "per_source_limit_flexcredits": PER_SOURCE_LIMIT_FC, "total_limit_flexcredits": TOTAL_LIMIT_FC, "within_limits": total < TOTAL_LIMIT_FC and all(item["estimated_flexcredits"] < PER_SOURCE_LIMIT_FC for item in jobs)}


def _complex_list(values: np.ndarray) -> list[dict[str, float]]:
    return [{"real": float(value.real), "imag": float(value.imag)} for value in values]


def _sparams(data: Any) -> dict[str, Any]:
    input_amps = data["input_port"].amps
    output_amps = data["output_port"].amps
    incident = np.asarray(input_amps.sel(direction="+", mode_index=0))
    reflected = np.asarray(input_amps.sel(direction="-", mode_index=0))
    transmitted = np.asarray(output_amps.sel(direction="+", mode_index=0))
    s11 = reflected / incident
    s21 = transmitted / incident
    residual = 1.0 - np.abs(s11) ** 2 - np.abs(s21) ** 2
    return {
        "s11": _complex_list(s11),
        "s21": _complex_list(s21),
        "reflection_db": [float(20.0 * np.log10(max(abs(value), 1e-15))) for value in s11],
        "transmission_db": [float(20.0 * np.log10(max(abs(value), 1e-15))) for value in s21],
        "energy_residual": [float(value) for value in residual],
        "max_abs_energy_residual": float(np.max(np.abs(residual))),
        "worst_reflection_db": float(np.max(20.0 * np.log10(np.maximum(np.abs(s11), 1e-15)))),
    }


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    record = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not record["within_limits"]:
        raise RuntimeError("G3-A pilot exceeds cost limits")
    locked = {item["name"]: item for item in record["jobs"]}
    results = []
    for case in cases():
        item = locked[case["name"]]
        simulation, digest = build_case(case)
        if digest != item["serialized_simulation_sha256"] or item["solve_started"]:
            raise RuntimeError(f"Locked G3-A case mismatch: {case['name']}")
        result_file = RUNS / f"g3a-straight-{case['name']}-result-v1.hdf5"
        job = web.Job(simulation=simulation, task_name=item["task_name"], folder_name="P6 Physical Validation", task_id_cached=item["task_id"], verbose=False)
        data = job.run(path=result_file)
        metrics = _sparams(data)
        results.append({**case, "task_id": item["task_id"], "task_status": str(job.get_info().status), "result_file": result_file.name, "result_sha256": hashlib.sha256(result_file.read_bytes()).hexdigest(), "actual_flexcredits": float(job.real_cost(verbose=False)), "metrics": metrics, "pilot_case_passed": metrics["max_abs_energy_residual"] < 0.01 and metrics["worst_reflection_db"] < -30.0})
    return {"name": "p6-g3a-straight-result-v1", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results, "pilot_passed": all(item["pilot_case_passed"] for item in results), "actual_total_flexcredits": sum(item["actual_flexcredits"] for item in results)}


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--upload-estimates", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--user-credit-approval", action="store_true")
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    output = estimate(approved=args.user_credit_approval) if args.upload_estimates else execute(approved=args.user_solve_approval)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
