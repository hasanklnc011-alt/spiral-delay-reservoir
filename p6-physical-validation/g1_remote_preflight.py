"""Serialize and validate the P6 G1 remote/subpixel candidate without upload.

This module intentionally contains no cloud client path. It prepares a deterministic
13-point ModeSolver payload whose digest can be compared before any approved upload.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td

from em_plan import REQUIRED_TIDY3D_VERSION, budget_policy, selected_cases
from g1_mode_solver import DEFAULT_CONFIG, build_mode_solver, load_seed


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_preflight(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required; found {td.__version__}")

    case = next(item for item in selected_cases() if item["case"] == "cross_section_mode")
    sweep = case["sweep"]["wavelength_um"]
    wavelengths = np.linspace(float(sweep["start"]), float(sweep["stop"]), int(sweep["points"]))
    solver = build_mode_solver(load_seed(config_path), min_steps_per_wvl=20.0, wavelengths_um=wavelengths)
    serialized = solver.model_dump_json()
    policy = budget_policy()
    payload = {
        "name": "p6-g1-remote-subpixel-preflight-v1",
        "claim_level": "serialization/preflight only; no upload, solve, cost, or G1 acceptance",
        "tidy3d_version": str(td.__version__),
        "config_sha256": sha256_file(config_path),
        "source_sha256": sha256_file(Path(__file__)),
        "serialized_mode_solver_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "serialized_bytes": len(serialized.encode("utf-8")),
        "wavelengths_um": [float(value) for value in wavelengths],
        "frequency_count": len(solver.freqs),
        "min_steps_per_wvl": 20.0,
        "subpixel_spec_present": bool(solver.simulation.subpixel),
        "simulation_cells_before_remote_subpixel_discretization": int(solver.simulation.num_cells),
        "cloud_called": False,
        "upload_allowed": policy["upload_allowed"],
        "solve_allowed": policy["solve_allowed"],
        "cost_estimate_status": "BLOCKED_UNTIL_USER_CREDIT_APPROVAL_AND_UPLOAD",
    }
    payload["passed"] = (
        payload["tidy3d_version"] == REQUIRED_TIDY3D_VERSION
        and payload["frequency_count"] == int(sweep["points"])
        and payload["wavelengths_um"][0] == float(sweep["start"])
        and payload["wavelengths_um"][-1] == float(sweep["stop"])
        and payload["subpixel_spec_present"]
        and not payload["cloud_called"]
        and not payload["upload_allowed"]
        and not payload["solve_allowed"]
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build_preflight(), indent=2))
