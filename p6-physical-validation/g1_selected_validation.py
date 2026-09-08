"""Remote convergence and fabrication-corner validation for the selected G1 cross-section."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from tidy3d import web

from g1_execute import analyze
from g1_mode_solver import REQUIRED_TIDY3D_VERSION, build_mode_solver, load_seed


HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
SELECTED_CONFIG = HERE / "configs" / "g1-selected-v1.json"
ESTIMATE_RECORD = RUNS / "g1-selected-validation-estimate-v1.json"
PILOT_TOTAL_LIMIT_FC = 0.5


def cases() -> list[dict[str, Any]]:
    return [
        {"name": "nominal_m15", "width_um": 0.343, "height_um": 0.18, "mesh": 15.0},
        {"name": "nominal_m20", "width_um": 0.343, "height_um": 0.18, "mesh": 20.0},
        {"name": "nominal_m25", "width_um": 0.343, "height_um": 0.18, "mesh": 25.0},
        {"name": "width_low", "width_um": 0.333, "height_um": 0.18, "mesh": 20.0},
        {"name": "width_high", "width_um": 0.353, "height_um": 0.18, "mesh": 20.0},
        {"name": "height_low", "width_um": 0.343, "height_um": 0.17, "mesh": 20.0},
        {"name": "height_high", "width_um": 0.343, "height_um": 0.19, "mesh": 20.0},
    ]


def build_case(case: dict[str, Any]) -> tuple[Any, str]:
    seed = load_seed()
    seed["width_um"] = float(case["width_um"])
    seed["height_um"] = float(case["height_um"])
    wavelengths = np.linspace(1.52, 1.58, 13)
    solver = build_mode_solver(seed, min_steps_per_wvl=float(case["mesh"]), wavelengths_um=wavelengths)
    digest = hashlib.sha256(solver.model_dump_json().encode("utf-8")).hexdigest()
    return solver, digest


def upload_estimates(*, user_credit_approval: bool) -> dict[str, Any]:
    if not user_credit_approval:
        raise PermissionError("Explicit user approval is required")
    jobs = []
    for case in cases():
        solver, digest = build_case(case)
        task_name = f"p6_g1_selected_{case['name']}"
        job = web.Job(simulation=solver, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
        job.upload()
        jobs.append(
            {
                **case,
                "task_name": task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_mode_solver_sha256": digest,
                "estimated_flexcredits": float(job.estimate_cost(verbose=False)),
                "solve_started": False,
            }
        )
    total = sum(item["estimated_flexcredits"] for item in jobs)
    return {
        "name": "p6-g1-selected-validation-estimate-v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "selected_config_sha256": hashlib.sha256(SELECTED_CONFIG.read_bytes()).hexdigest(),
        "jobs": jobs,
        "estimated_total_flexcredits": total,
        "pilot_total_limit_flexcredits": PILOT_TOTAL_LIMIT_FC,
        "within_pilot_limit": total < PILOT_TOTAL_LIMIT_FC,
        "user_credit_approval": True,
    }


def execute(*, user_solve_approval: bool) -> dict[str, Any]:
    if not user_solve_approval:
        raise PermissionError("Explicit user solve approval is required")
    record = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not record["within_pilot_limit"] or record["estimated_total_flexcredits"] >= PILOT_TOTAL_LIMIT_FC:
        raise RuntimeError("Selected validation suite exceeds the pilot limit")
    case_by_name = {case["name"]: case for case in cases()}
    results = []
    for item in record["jobs"]:
        case = case_by_name[item["name"]]
        solver, digest = build_case(case)
        if digest != item["serialized_mode_solver_sha256"] or item["solve_started"]:
            raise RuntimeError(f"Locked case mismatch: {item['name']}")
        result_file = RUNS / f"g1-selected-{item['name']}-result-v1.hdf5"
        job = web.Job(
            simulation=solver,
            task_name=item["task_name"],
            folder_name="P6 Physical Validation",
            task_id_cached=item["task_id"],
            verbose=False,
        )
        data = job.run(path=result_file)
        metrics = analyze(data, solver)
        results.append(
            {
                **case,
                "task_id": item["task_id"],
                "task_status": str(job.get_info().status),
                "result_file": result_file.name,
                "result_sha256": hashlib.sha256(result_file.read_bytes()).hexdigest(),
                "actual_flexcredits": float(job.real_cost(verbose=False)),
                "analysis": metrics,
                "case_passed": metrics["group_index_and_delay_gate_passed"]
                and metrics["guided_te_like_mode_count"] == 1,
            }
        )

    result_by_name = {item["name"]: item for item in results}
    medium = result_by_name["nominal_m20"]["analysis"]
    fine = result_by_name["nominal_m25"]["analysis"]
    convergence = {
        "relative_n_group_delta": abs(medium["fundamental_n_group"] - fine["fundamental_n_group"])
        / abs(fine["fundamental_n_group"]),
        "absolute_n_eff_delta": abs(medium["fundamental_n_eff"] - fine["fundamental_n_eff"]),
    }
    convergence["passed"] = (
        convergence["relative_n_group_delta"] < 0.005 and convergence["absolute_n_eff_delta"] < 0.001
    )
    nominal_passed = result_by_name["nominal_m25"]["case_passed"] and convergence["passed"]
    corner_names = ("width_low", "width_high", "height_low", "height_high")
    corners_passed = all(result_by_name[name]["case_passed"] for name in corner_names)
    return {
        "name": "p6-g1-selected-validation-result-v1",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "selected_config_sha256": hashlib.sha256(SELECTED_CONFIG.read_bytes()).hexdigest(),
        "results": results,
        "convergence": convergence,
        "nominal_passed": nominal_passed,
        "fabrication_corners_passed": corners_passed,
        "g1_passed": nominal_passed and corners_passed,
        "actual_total_flexcredits": sum(item["actual_flexcredits"] for item in results),
        "user_solve_approval": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--upload-estimates", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--user-credit-approval", action="store_true")
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    output = (
        upload_estimates(user_credit_approval=args.user_credit_approval)
        if args.upload_estimates
        else execute(user_solve_approval=args.user_solve_approval)
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
