"""Resume the hash-locked G3-D pilot after a post-processing-only failure."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import tidy3d as td
from tidy3d import web

from g3d_mmi_fdtd import (
    ESTIMATE_RECORD,
    RUNS,
    build,
    geometry_parameters,
    metrics,
    serialized_sha,
    sha256,
)


BUILDER = Path(__file__).resolve().with_name("g3d_mmi_fdtd.py")


def final_decay(data: td.SimulationData) -> float:
    values = re.findall(r"field decay:\s*([0-9.eE+-]+)", str(data.log))
    if not values:
        raise RuntimeError("Final field decay missing from solver log")
    return float(values[-1])


def resume(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    locked = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not locked["within_limits"] or locked["solve_started"]:
        raise RuntimeError("Estimate record is not eligible for execution")
    if locked["source_sha256"] != sha256(BUILDER):
        raise RuntimeError("Locked builder changed after estimate")

    data_by_port: dict[str, td.SimulationData] = {}
    task_records = []
    for item in locked["tasks"]:
        port = item["source_port"]
        simulation = build(port)
        if serialized_sha(simulation) != item["serialized_simulation_sha256"]:
            raise RuntimeError(f"Locked simulation mismatch for {port}")
        path = RUNS / f"g3d-mmi-{port}_m15-result-v1.hdf5"
        job = web.Job(
            simulation=simulation,
            task_name=item["task_name"],
            folder_name="P6 Physical Validation",
            task_id_cached=item["task_id"],
            verbose=False,
        )
        initial_status = str(job.get_info().status)
        data = job.run(path=path)
        data_by_port[port] = data
        task_records.append(
            {
                "source_port": port,
                "task_id": item["task_id"],
                "initial_status_on_resume": initial_status,
                "task_status": str(job.get_info().status),
                "result_file": path.name,
                "result_sha256": sha256(path),
                "actual_flexcredits": float(job.real_cost(verbose=False) or 0),
                "final_decay": final_decay(data),
            }
        )

    measured_full = metrics(data_by_port)
    spectral_digest = hashlib.sha256(
        json.dumps(
            measured_full["per_wavelength"], sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    measured = {
        key: value
        for key, value in measured_full.items()
        if key != "per_wavelength"
    }
    measured["per_wavelength_sha256"] = spectral_digest
    measured["per_wavelength_points"] = len(measured_full["per_wavelength"])
    decay = max(item["final_decay"] for item in task_records)
    gates = {
        "target_excess_le_0p5_db": measured["worst_excess_insertion_loss_db"] <= 0.5,
        "hard_excess_le_1p5_db": measured["worst_excess_insertion_loss_db"] <= 1.5,
        "imbalance_le_0p5_db": measured["worst_imbalance_db"] <= 0.5,
        "quadrature_error_le_5_deg": measured["worst_quadrature_error_deg"] <= 5.0,
        "reflection_below_minus_30_db": measured["worst_total_reflection_db"] < -30.0,
        "passive_singular_value_le_1p000001": measured["worst_full_s_max_singular_value"] <= 1.000001,
        "final_decay_le_1e_7": decay <= 1e-7,
        "two_independent_excitations": len(data_by_port) == 2,
    }
    return {
        "name": "p6-g3d-mmi-result-v1",
        "builder_source_sha256": sha256(BUILDER),
        "postprocessor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "estimate_sha256": sha256(ESTIMATE_RECORD),
        "p5_blind_rerun": False,
        "resume_reason": "first source completed; original runner failed only while parsing string solver log; second source remained draft",
        "solve_restarted": False,
        "geometry": geometry_parameters(),
        "tasks": task_records,
        "actual_total_flexcredits": sum(
            item["actual_flexcredits"] for item in task_records
        ),
        "metrics": measured,
        "gates": gates,
        "pilot_passed": all(gates.values()),
        "g3d_accepted": False,
        "claim_limit": "m15 pilot only; acceptance requires passing m20/m25 convergence",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", required=True)
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(resume(approved=args.user_solve_approval), indent=2))


if __name__ == "__main__":
    main()
