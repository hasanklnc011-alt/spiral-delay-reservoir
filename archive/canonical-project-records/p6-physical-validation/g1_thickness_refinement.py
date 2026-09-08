"""Validate the explicit 180 +/- 5 nm G1 silicon device-layer requirement."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from tidy3d import web

from g1_execute import analyze
from g1_mode_solver import build_mode_solver, load_seed


HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g1-thickness-refinement-estimate-v1.json"
LIMIT_FC = 0.1
CASES = (
    {"name": "height_175nm", "width_um": 0.343, "height_um": 0.175, "mesh": 20.0},
    {"name": "height_185nm", "width_um": 0.343, "height_um": 0.185, "mesh": 20.0},
)


def build_case(case: dict[str, Any]) -> tuple[Any, str]:
    seed = load_seed()
    seed["width_um"] = case["width_um"]
    seed["height_um"] = case["height_um"]
    solver = build_mode_solver(seed, min_steps_per_wvl=case["mesh"], wavelengths_um=np.linspace(1.52, 1.58, 13))
    return solver, hashlib.sha256(solver.model_dump_json().encode("utf-8")).hexdigest()


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    jobs = []
    for case in CASES:
        solver, digest = build_case(case)
        task_name = f"p6_g1_selected_{case['name']}"
        job = web.Job(simulation=solver, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
        job.upload()
        jobs.append({**case, "task_name": task_name, "task_id": str(job.task_id), "task_status": str(job.get_info().status), "serialized_mode_solver_sha256": digest, "estimated_flexcredits": float(job.estimate_cost(verbose=False)), "solve_started": False})
    total = sum(job["estimated_flexcredits"] for job in jobs)
    return {"name": "p6-g1-thickness-refinement-estimate-v1", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "jobs": jobs, "estimated_total_flexcredits": total, "limit_flexcredits": LIMIT_FC, "within_limit": total < LIMIT_FC}


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    record = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not record["within_limit"] or record["estimated_total_flexcredits"] >= LIMIT_FC:
        raise RuntimeError("Thickness refinement exceeds limit")
    locked = {item["name"]: item for item in record["jobs"]}
    results = []
    for case in CASES:
        item = locked[case["name"]]
        solver, digest = build_case(case)
        if digest != item["serialized_mode_solver_sha256"] or item["solve_started"]:
            raise RuntimeError(f"Locked case mismatch: {case['name']}")
        result_file = RUNS / f"g1-selected-{case['name']}-result-v1.hdf5"
        job = web.Job(simulation=solver, task_name=item["task_name"], folder_name="P6 Physical Validation", task_id_cached=item["task_id"], verbose=False)
        data = job.run(path=result_file)
        metrics = analyze(data, solver)
        results.append({**case, "task_id": item["task_id"], "task_status": str(job.get_info().status), "result_file": result_file.name, "result_sha256": hashlib.sha256(result_file.read_bytes()).hexdigest(), "actual_flexcredits": float(job.real_cost(verbose=False)), "analysis": metrics, "case_passed": metrics["group_index_and_delay_gate_passed"] and metrics["guided_te_like_mode_count"] == 1})
    return {"name": "p6-g1-thickness-refinement-result-v1", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results, "thickness_plus_minus_5nm_passed": all(item["case_passed"] for item in results), "actual_total_flexcredits": sum(item["actual_flexcredits"] for item in results)}


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
