"""Execute the explicitly approved, already-uploaded P6 G1 task exactly once."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d import web
from tidy3d.plugins.mode import ModeSolverData

from g1_cloud_gate import HERE, build_locked_solver


ESTIMATE_RECORD = HERE / "runs" / "g1-upload-estimate-v1.json"
RESULT_FILE = HERE / "runs" / "g1-remote-subpixel-result-v1.hdf5"


def _matrix(value: Any) -> np.ndarray:
    array = np.asarray(value).real
    return array[None, :] if array.ndim == 1 else array


def analyze(data: ModeSolverData, solver: Any) -> dict[str, Any]:
    n_eff = _matrix(data.n_eff)
    n_group = _matrix(data.n_group)
    mode_area = _matrix(data.mode_area)
    te_fraction = _matrix(data.pol_fraction.te)
    tm_fraction = _matrix(data.pol_fraction.tm)
    frequencies = np.asarray(solver.freqs, dtype=float)
    wavelengths = td.C_0 / frequencies
    center_index = int(np.argmin(np.abs(wavelengths - 1.55)))
    center_frequency = float(frequencies[center_index])
    silica = td.material_library["SiO2"]["Horiba"]
    n_cladding = float(np.sqrt(np.real(silica.eps_model(center_frequency))))
    center_neff = [float(value) for value in n_eff[center_index]]
    center_ng = [float(value) for value in n_group[center_index]]
    center_area = [float(value) for value in mode_area[center_index]]
    center_te_fraction = [float(value) for value in te_fraction[center_index]]
    center_tm_fraction = [float(value) for value in tm_fraction[center_index]]
    guided_count = sum(value > n_cladding + 1e-3 for value in center_neff)
    guided_te_like_count = sum(
        neff > n_cladding + 1e-3 and te >= 0.8
        for neff, te in zip(center_neff, center_te_fraction, strict=True)
    )
    ng_error = abs(center_ng[0] - 4.0) / 4.0
    delay_s = center_ng[0] * (14.240141755 / 100.0) / 299_792_458.0
    return {
        "center_wavelength_um": float(wavelengths[center_index]),
        "fundamental_n_eff": center_neff[0],
        "fundamental_n_group": center_ng[0],
        "fundamental_mode_area_um2": center_area[0],
        "cladding_index": n_cladding,
        "guided_mode_count_by_index": guided_count,
        "guided_te_like_mode_count": guided_te_like_count,
        "center_te_fraction": center_te_fraction,
        "center_tm_fraction": center_tm_fraction,
        "n_eff_mode0_minus_mode1": center_neff[0] - center_neff[1],
        "relative_group_index_error": ng_error,
        "delay_at_locked_length_s": delay_s,
        "symbols_at_10_gbd": delay_s * 10e9,
        "group_index_and_delay_gate_passed": ng_error <= 0.02,
        "wavelengths_um": [float(value) for value in wavelengths],
        "fundamental_n_eff_spectrum": [float(value) for value in n_eff[:, 0]],
        "fundamental_n_group_spectrum": [float(value) for value in n_group[:, 0]],
        "fundamental_mode_area_um2_spectrum": [float(value) for value in mode_area[:, 0]],
    }


def execute(*, user_solve_approval: bool) -> dict[str, Any]:
    if not user_solve_approval:
        raise PermissionError("Explicit user solve approval is required")
    record = json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if record["solve_started"] or record["task_status"] != "draft":
        raise RuntimeError("Estimate record is not an approved unsolved draft")
    if not record["within_pilot_limit"]:
        raise RuntimeError("Estimated cost exceeds the approved pilot threshold")

    solver, lock = build_locked_solver()
    task_id = str(record["task_id"])
    job = web.Job(
        simulation=solver,
        task_name=record["task_name"],
        folder_name=record["folder_name_requested"],
        task_id_cached=task_id,
        verbose=False,
    )
    if RESULT_FILE.exists():
        data = ModeSolverData.from_file(RESULT_FILE)
        resumed_local_result = True
    else:
        data = job.run(path=RESULT_FILE)
        resumed_local_result = False
    info = job.get_info()
    actual_cost = job.real_cost(verbose=False)
    result = {
        "name": "p6-g1-remote-subpixel-result-v1",
        "claim_level": "single approved G1 remote mode solve; not full P6 acceptance",
        "task_id": task_id,
        "task_status": str(info.status),
        "tidy3d_version": lock["tidy3d_version"],
        "config_sha256": lock["config_sha256"],
        "serialized_mode_solver_sha256": lock["serialized_mode_solver_sha256"],
        "result_file": RESULT_FILE.name,
        "result_sha256": hashlib.sha256(RESULT_FILE.read_bytes()).hexdigest(),
        "estimated_flexcredits": float(record["estimated_flexcredits"]),
        "actual_flexcredits": None if actual_cost is None else float(actual_cost),
        "user_solve_approval": True,
        "resumed_local_result": resumed_local_result,
        "analysis": analyze(data, solver),
    }
    result["g1_nominal_passed"] = (
        result["task_status"] == "success"
        and result["analysis"]["group_index_and_delay_gate_passed"]
        and result["analysis"]["guided_te_like_mode_count"] == 1
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-solve-approval", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(user_solve_approval=args.user_solve_approval), indent=2))


if __name__ == "__main__":
    main()
