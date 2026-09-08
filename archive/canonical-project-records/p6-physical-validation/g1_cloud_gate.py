"""Upload the locked G1 ModeSolver only to obtain a FlexCredit estimate.

There is intentionally no solve/start/run path in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from tidy3d import web

from em_plan import selected_cases
from g1_mode_solver import DEFAULT_CONFIG, build_mode_solver, load_seed


HERE = Path(__file__).resolve().parent
LOCK_RECORD = HERE / "runs" / "g1-remote-subpixel-preflight-v1.json"


def build_locked_solver(config_path: Path = DEFAULT_CONFIG) -> tuple[Any, dict[str, Any]]:
    lock = json.loads(LOCK_RECORD.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
    if config_hash != lock["config_sha256"]:
        raise RuntimeError("G1 config hash changed after preflight; refusing upload")

    case = next(item for item in selected_cases() if item["case"] == "cross_section_mode")
    sweep = case["sweep"]["wavelength_um"]
    wavelengths = np.linspace(float(sweep["start"]), float(sweep["stop"]), int(sweep["points"]))
    solver = build_mode_solver(load_seed(config_path), min_steps_per_wvl=20.0, wavelengths_um=wavelengths)
    serialized_hash = hashlib.sha256(solver.model_dump_json().encode("utf-8")).hexdigest()
    if serialized_hash != lock["serialized_mode_solver_sha256"]:
        raise RuntimeError("Serialized G1 payload differs from locked preflight; refusing upload")
    return solver, lock


def upload_and_estimate(*, user_credit_approval: bool, existing_task_id: str | None = None) -> dict[str, Any]:
    if not user_credit_approval:
        raise PermissionError("Explicit user credit approval is required for upload and estimate")
    solver, lock = build_locked_solver()
    job_kwargs: dict[str, Any] = {
        "simulation": solver,
        "task_name": "p6_g1_cross_section_mode_nominal_mesh20",
        "folder_name": "P6 Physical Validation",
        "verbose": False,
    }
    if existing_task_id is not None:
        job_kwargs["task_id_cached"] = existing_task_id
    job = web.Job(
        **job_kwargs,
    )
    if existing_task_id is None:
        job.upload()
    info = job.get_info()
    estimate = float(job.estimate_cost(verbose=False))
    return {
        "name": "p6-g1-upload-estimate-v1",
        "claim_level": "uploaded draft and cost estimate only; solver not started",
        "task_name": "p6_g1_cross_section_mode_nominal_mesh20",
        "folder_name": "P6 Physical Validation",
        "task_id": str(job.task_id),
        "task_status": str(info.status),
        "tidy3d_version": lock["tidy3d_version"],
        "config_sha256": lock["config_sha256"],
        "serialized_mode_solver_sha256": lock["serialized_mode_solver_sha256"],
        "estimated_flexcredits": estimate,
        "uploaded": True,
        "resumed_existing_draft": existing_task_id is not None,
        "solve_started": False,
        "user_credit_approval_for_upload_estimate": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-estimate", action="store_true")
    parser.add_argument("--user-credit-approval", action="store_true")
    parser.add_argument("--task-id", help="Resume an already-created draft without re-uploading")
    args = parser.parse_args()
    if not args.upload_estimate:
        raise SystemExit("Refusing cloud mutation without --upload-estimate")
    print(
        json.dumps(
            upload_and_estimate(
                user_credit_approval=args.user_credit_approval,
                existing_task_id=args.task_id,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
