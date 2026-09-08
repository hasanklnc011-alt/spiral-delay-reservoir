"""Upload-only ID1 cost estimate for the hash-locked inverse-design seeds."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from tidy3d import web

from g3_straight_preflight import HERE
from g3d_mmi_fdtd import sha256
from inverse_design_preflight import CONFIG
from inverse_design_simulation_preflight import build_designs


PREFLIGHT_SOURCE = HERE / "inverse_design_simulation_preflight.py"
PREFLIGHT_RECORD = HERE / "runs" / "inverse-design-simulation-preflight-v1.json"
ID1_TOTAL_LIMIT_FC = 1.5


def serialized_sha(simulation: Any) -> str:
    return hashlib.sha256(simulation.model_dump_json().encode()).hexdigest()


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    locked = json.loads(PREFLIGHT_RECORD.read_text(encoding="utf-8"))
    if locked["source_sha256"] != sha256(PREFLIGHT_SOURCE):
        raise RuntimeError("Simulation source changed after preflight")
    if locked["config_sha256"] != sha256(CONFIG):
        raise RuntimeError("Inverse-design config changed after preflight")
    splitter, combiner = build_designs()
    splitter_sim = splitter.to_simulation(splitter.design_region.initial_parameters)
    combiner_sims = combiner.to_simulation(combiner.design_region.initial_parameters)
    payloads = [("g3c_splitter", splitter_sim)] + [
        (f"g3d_{index}", simulation)
        for index, simulation in enumerate(combiner_sims.values())
    ]
    tasks = []
    for label, simulation in payloads:
        task_name = f"p6_inverse_design_id1_estimate_{label}_v1"
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
                "label": label,
                "task_name": task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_simulation_sha256": serialized_sha(simulation),
                "estimated_forward_flexcredits": cost,
                "solve_started": False,
            }
        )
    splitter_forward = tasks[0]["estimated_forward_flexcredits"]
    combiner_forward = sum(
        item["estimated_forward_flexcredits"] for item in tasks[1:]
    )
    initial_forward_total = splitter_forward + combiner_forward
    # Conservative planning bound: one forward batch plus one adjoint batch per
    # optimization step, before any early shutoff discount.
    splitter_iteration = 2.0 * splitter_forward
    combiner_iteration = 2.0 * combiner_forward
    allocation = {"g3c_splitter": 0.5, "g3d_combiner": 1.0}
    max_steps = {
        "g3c_splitter": math.floor(allocation["g3c_splitter"] / splitter_iteration),
        "g3d_combiner": math.floor(allocation["g3d_combiner"] / combiner_iteration),
    }
    within_total_limit = initial_forward_total < ID1_TOTAL_LIMIT_FC
    return {
        "name": "p6-inverse-design-id1-estimate-v1",
        "source_sha256": sha256(Path(__file__)),
        "simulation_source_sha256": sha256(PREFLIGHT_SOURCE),
        "preflight_record_sha256": sha256(PREFLIGHT_RECORD),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "tasks": tasks,
        "planning_model": "2x forward-cost per optimization step (forward plus adjoint upper bound)",
        "estimated_iteration_flexcredits": {
            "g3c_splitter": splitter_iteration,
            "g3d_combiner": combiner_iteration,
        },
        "estimated_initial_forward_total_flexcredits": initial_forward_total,
        "id1_total_limit_flexcredits": ID1_TOTAL_LIMIT_FC,
        "provisional_allocation_flexcredits": allocation,
        "max_whole_steps_within_allocation": max_steps,
        "solve_started": False,
        "within_total_limit": within_total_limit,
        "optimization_allowed": within_total_limit
        and all(value >= 1 for value in max_steps.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-estimate", action="store_true", required=True)
    parser.add_argument("--user-credit-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(estimate(approved=args.user_credit_approval), indent=2))


if __name__ == "__main__":
    main()
