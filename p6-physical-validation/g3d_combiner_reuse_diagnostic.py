"""Reuse a rejected 2x2 coupler solve to exercise G3-D coherent-combiner gates.

This is diagnostic evidence only: the second excitation is inferred from mirror
symmetry, and the source solve did not meet its field-decay threshold.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import tidy3d as td


HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
SOURCE_RECORD = RUNS / "g3c-coupler-fdtd-result-v2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complex_pair(value: complex) -> list[float]:
    return [float(np.real(value)), float(np.imag(value))]


def phase_error_deg(value: float, target_abs_deg: float = 90.0) -> float:
    wrapped = (value + 180.0) % 360.0 - 180.0
    return abs(abs(wrapped) - target_abs_deg)


def build_record() -> dict:
    source = json.loads(SOURCE_RECORD.read_text(encoding="utf-8"))
    result_path = RUNS / source["result_file"]
    data = td.SimulationData.from_file(result_path)
    center = len(data["input_top"].amps.f) // 2

    incident = np.asarray(
        data["input_top"].amps.sel(direction="+", mode_index=0)
    )[center]
    r_self = np.asarray(
        data["input_top"].amps.sel(direction="-", mode_index=0)
    )[center] / incident
    r_cross = np.asarray(
        data["input_bottom"].amps.sel(direction="-", mode_index=0)
    )[center] / incident
    bar = np.asarray(
        data["output_top"].amps.sel(direction="+", mode_index=0)
    )[center] / incident
    cross = np.asarray(
        data["output_bottom"].amps.sel(direction="+", mode_index=0)
    )[center] / incident

    # Mirror symmetry predicts the second columns; it does not replace the
    # independently excited solve required by the acceptance plan.
    forward = np.array([[bar, cross], [cross, bar]], dtype=complex)
    reflection = np.array([[r_self, r_cross], [r_cross, r_self]], dtype=complex)
    power_gram = forward.conj().T @ forward + reflection.conj().T @ reflection
    largest_power_eigenvalue = float(np.max(np.linalg.eigvalsh(power_gram)).real)
    singular_values = np.linalg.svd(forward, compute_uv=False)

    coherent = {}
    for phase_deg in (0, 90, 180, 270):
        inputs = np.array([1.0, np.exp(1j * np.deg2rad(phase_deg))])
        outputs = forward @ inputs
        reflected = reflection @ inputs
        coherent[str(phase_deg)] = {
            "output_power": [float(abs(x) ** 2) for x in outputs],
            "total_output_power": float(np.sum(abs(outputs) ** 2)),
            "total_reflected_power": float(np.sum(abs(reflected) ** 2)),
            "input_power": 2.0,
        }

    metrics = source["metrics"]
    relative_phase = float(metrics["center_relative_phase_deg"])
    gates = {
        "hard_excess_insertion_db_le_1p5": metrics["center_excess_loss_db"] <= 1.5,
        "imbalance_db_le_0p5": metrics["center_imbalance_db"] <= 0.5,
        "quadrature_error_deg_le_5": phase_error_deg(relative_phase) <= 5.0,
        "passive_power_operator_le_1p01": largest_power_eigenvalue <= 1.01,
        "field_decay_le_1e_7": source["final_field_decay"] <= 1e-7,
        "independent_two_port_excitations": False,
        "mesh_convergence_available": False,
    }
    return {
        "name": "p6-g3d-reused-coupler-diagnostic-v1",
        "source_sha256": sha256(Path(__file__)),
        "input_record_sha256": sha256(SOURCE_RECORD),
        "input_result_sha256": sha256(result_path),
        "p5_blind_rerun": False,
        "cloud_called": False,
        "evidence_class": "DIAGNOSTIC_ONLY_SYMMETRY_INFERRED_SECOND_EXCITATION",
        "forward_s_matrix_complex_ri": [
            [complex_pair(value) for value in row] for row in forward
        ],
        "reflection_s_matrix_complex_ri": [
            [complex_pair(value) for value in row] for row in reflection
        ],
        "forward_singular_values": [float(x) for x in singular_values],
        "largest_total_power_operator_eigenvalue": largest_power_eigenvalue,
        "center_relative_phase_deg": relative_phase,
        "quadrature_error_deg": phase_error_deg(relative_phase),
        "coherent_equal_input_transfer": coherent,
        "gates": gates,
        "diagnostic_passed": all(gates.values()),
        "g3d_accepted": False,
        "next_required_evidence": (
            "two independent port excitations on a redesigned/foundry-qualified "
            "2x2 cell, followed by m20/m25 complex-S convergence"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_record(), indent=2))
