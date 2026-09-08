"""Upload-only cost estimate for ID2 binary broadband validation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tidy3d import web

from g3_straight_preflight import HERE
from g3d_mmi_fdtd import sha256
from inverse_design_preflight import CONFIG
from inverse_design_id2_preflight import load_binary_seed, serialized_sha


PREFLIGHT_SOURCE = HERE / "inverse_design_id2_preflight.py"
PREFLIGHT_RECORD = HERE / "runs" / "inverse-design-id2-binary-preflight-v1.json"
ID2_LIMIT_FC = 3.0


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    locked = json.loads(PREFLIGHT_RECORD.read_text(encoding="utf-8"))
    if locked["source_sha256"] != sha256(PREFLIGHT_SOURCE):
        raise RuntimeError("ID2 preflight source changed after lock")
    if locked["config_sha256"] != sha256(CONFIG):
        raise RuntimeError("Inverse-design config changed after ID2 preflight")
    payloads = []
    for device in ("splitter", "combiner"):
        simulations, _, record = load_binary_seed(device)
        if record["serialized_simulation_sha256"] != locked["devices"][device]["serialized_simulation_sha256"]:
            raise RuntimeError(f"{device} binary simulation changed after preflight")
        payloads.extend((device, key, sim) for key, sim in simulations.items())
    tasks = []
    for device, key, simulation in payloads:
        job = web.Job(
            simulation=simulation,
            task_name=f"p6_inverse_design_id2_{device}_{key}_v1",
            folder_name="P6 Physical Validation",
            verbose=False,
        )
        job.upload()
        tasks.append(
            {
                "device": device,
                "simulation_key": key,
                "task_name": job.task_name,
                "task_id": str(job.task_id),
                "task_status": str(job.get_info().status),
                "serialized_simulation_sha256": serialized_sha(simulation),
                "estimated_flexcredits": float(job.estimate_cost(verbose=False)),
                "solve_started": False,
            }
        )
    total = sum(item["estimated_flexcredits"] for item in tasks)
    within_limit = total < ID2_LIMIT_FC
    return {
        "name": "p6-inverse-design-id2-estimate-v1",
        "source_sha256": sha256(Path(__file__)),
        "preflight_source_sha256": sha256(PREFLIGHT_SOURCE),
        "preflight_record_sha256": sha256(PREFLIGHT_RECORD),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "tasks": tasks,
        "estimated_total_flexcredits": total,
        "id2_limit_flexcredits": ID2_LIMIT_FC,
        "within_limit": within_limit,
        "solve_started": False,
        "execution_allowed": within_limit,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-estimate", action="store_true", required=True)
    parser.add_argument("--user-credit-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(estimate(approved=args.user_credit_approval), indent=2))


if __name__ == "__main__":
    main()
