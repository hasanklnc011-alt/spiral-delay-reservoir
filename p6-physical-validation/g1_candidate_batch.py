"""Cost-gated remote G1 candidate search after the provisional seed failed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from tidy3d import web

from g1_execute import analyze
from g1_mode_solver import REQUIRED_TIDY3D_VERSION, build_mode_solver, load_seed


HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g1-candidate-batch-estimate-v1.json"
PILOT_TOTAL_LIMIT_FC = 0.5
CANDIDATES = (
    {"name": "w300_h220", "width_um": 0.30, "height_um": 0.22},
    {"name": "w320_h200", "width_um": 0.32, "height_um": 0.20},
    {"name": "w330_h180", "width_um": 0.33, "height_um": 0.18},
    {"name": "w350_h180", "width_um": 0.35, "height_um": 0.18},
)


def build_candidate(candidate: dict[str, Any]) -> tuple[Any, str]:
    seed = load_seed()
    seed["width_um"] = float(candidate["width_um"])
    seed["height_um"] = float(candidate["height_um"])
    solver = build_mode_solver(seed, min_steps_per_wvl=20.0)
    digest = hashlib.sha256(solver.model_dump_json().encode("utf-8")).hexdigest()
    return solver, digest


def upload_estimates(*, user_credit_approval: bool) -> dict[str, Any]:
    if not user_credit_approval:
        raise PermissionError("Explicit user approval is required")
    jobs = []
    for candidate in CANDIDATES:
        solver, digest = build_candidate(candidate)
        task_name = f"p6_g1_candidate_{candidate['name']}_mesh20"
        job = web.Job(simulation=solver, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
        job.upload()
        estimate = float(job.estimate_cost(verbose=False))
        jobs.append(
            {
                **candidate,
                "task_name": task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_mode_solver_sha256": digest,
                "estimated_flexcredits": estimate,
                "solve_started": False,
            }
        )
    total = sum(item["estimated_flexcredits"] for item in jobs)
    return {
        "name": "p6-g1-candidate-batch-estimate-v1",
        "tidy3d_version": REQUIRED_TIDY3D_VERSION,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
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
        raise RuntimeError("Candidate batch exceeds the pilot limit")
    by_name = {candidate["name"]: candidate for candidate in CANDIDATES}
    results = []
    for item in record["jobs"]:
        if item["solve_started"]:
            raise RuntimeError(f"Candidate {item['name']} is not an unsolved draft")
        candidate = by_name[item["name"]]
        solver, digest = build_candidate(candidate)
        if digest != item["serialized_mode_solver_sha256"]:
            raise RuntimeError(f"Candidate payload changed: {item['name']}")
        result_file = RUNS / f"g1-candidate-{item['name']}-result-v1.hdf5"
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
                **candidate,
                "task_id": item["task_id"],
                "task_status": str(job.get_info().status),
                "result_file": result_file.name,
                "result_sha256": hashlib.sha256(result_file.read_bytes()).hexdigest(),
                "estimated_flexcredits": item["estimated_flexcredits"],
                "actual_flexcredits": float(job.real_cost(verbose=False)),
                "analysis": metrics,
                "candidate_passed": metrics["group_index_and_delay_gate_passed"]
                and metrics["guided_te_like_mode_count"] == 1,
            }
        )
    return {
        "name": "p6-g1-candidate-batch-result-v1",
        "tidy3d_version": REQUIRED_TIDY3D_VERSION,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "results": results,
        "actual_total_flexcredits": sum(item["actual_flexcredits"] for item in results),
        "passing_candidates": [item["name"] for item in results if item["candidate_passed"]],
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
