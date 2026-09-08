"""Cost-gated selected 3D FDTD validation for the G3-B R=20 um bend."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from tidy3d import web

from g3_bend_preflight import HERE, build_bend
from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC, _sparams


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3b-bend-r20-estimate-v1.json"


def build_case(mesh: float = 15.0) -> tuple[Any, str]:
    simulation = build_bend(radius_um=20.0, mesh=mesh)
    digest = hashlib.sha256(simulation.model_dump_json().encode("utf-8")).hexdigest()
    return simulation, digest


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    simulation, digest = build_case()
    task_name = "p6_g3b_bend_r20_m15"
    job = web.Job(simulation=simulation, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
    job.upload()
    estimated = float(job.estimate_cost(verbose=False))
    return {
        "name": "p6-g3b-bend-r20-estimate-v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "task_name": task_name,
        "task_id": str(job.task_id),
        "task_status": str(job.get_info().status),
        "serialized_simulation_sha256": digest,
        "estimated_flexcredits": estimated,
        "solve_started": False,
        "within_limits": estimated < PER_SOURCE_LIMIT_FC and estimated < TOTAL_LIMIT_FC,
    }


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    locked = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    simulation, digest = build_case()
    if not locked["within_limits"] or locked["solve_started"]:
        raise RuntimeError("G3-B task is not eligible for execution")
    if digest != locked["serialized_simulation_sha256"]:
        raise RuntimeError("Locked G3-B simulation mismatch")
    path = RUNS / "g3b-bend-r20_m15-result-v1.hdf5"
    job = web.Job(
        simulation=simulation,
        task_name=locked["task_name"],
        folder_name="P6 Physical Validation",
        task_id_cached=locked["task_id"],
        verbose=False,
    )
    data = job.run(path=path)
    metrics = _sparams(data)
    passed = metrics["max_abs_energy_residual"] < 0.01 and metrics["worst_reflection_db"] < -30.0
    return {
        "name": "p6-g3b-bend-r20-result-v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "task_id": locked["task_id"],
        "task_status": str(job.get_info().status),
        "result_file": path.name,
        "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "actual_flexcredits": float(job.real_cost(verbose=False)),
        "metrics": metrics,
        "pilot_passed": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--upload-estimate", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--user-credit-approval", action="store_true")
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    result = estimate(approved=args.user_credit_approval) if args.upload_estimate else execute(approved=args.user_solve_approval)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
