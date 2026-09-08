"""LEGACY: audit of old three-ring FDTD and transient evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


def _read_complex_spectrum(path: Path) -> np.ndarray:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return np.array([complex(float(row["mode_amp_real"]), float(row["mode_amp_imag"])) for row in rows])


def validate_existing_fdtd(source_root: Path) -> dict[str, Any]:
    target = json.loads((source_root / "results/invdes_tcmt_narma3_target.json").read_text(encoding="utf-8"))
    measured = _read_complex_spectrum(source_root / "results/explicit_three_ring_spectrum_best.csv")
    expected = np.asarray(target["target_s21_real"]) + 1j * np.asarray(target["target_s21_imag"])
    if measured.shape != expected.shape:
        raise ValueError(f"spectrum length mismatch: {measured.shape} != {expected.shape}")
    measured_power = np.abs(measured) ** 2
    expected_power = np.abs(expected) ** 2
    power_nmse = float(np.mean((measured_power - expected_power) ** 2) / np.var(expected_power))
    power_corr = float(np.corrcoef(measured_power, expected_power)[0, 1])
    # Allow one global complex gain (calibration and propagation phase), no offset.
    scale = np.vdot(expected, measured) / np.vdot(expected, expected)
    aligned = scale * expected
    complex_nmse = float(np.mean(np.abs(measured - aligned) ** 2) / np.mean(np.abs(measured - np.mean(measured)) ** 2))
    static_passed = complex_nmse < 0.2 and power_corr > 0.95

    transient = json.loads((source_root / "results/fdtd_vs_tcmt_summary_w800_h400_r10_memory_t1ps.json").read_text(encoding="utf-8"))
    transient_passed = float(transient["aligned_nmse"]) < 0.2 and float(transient["aligned_cosine_similarity"]) > 0.95
    return {
        "claim_level": "legacy evidence audit",
        "three_ring_static_spectrum": {
            "power_nmse": power_nmse,
            "power_correlation": power_corr,
            "complex_nmse_after_global_gain": complex_nmse,
            "passed": static_passed,
            "note": "Static spectrum matching cannot validate temporal reservoir computation.",
        },
        "single_ring_transient": {
            "aligned_nmse": transient["aligned_nmse"],
            "aligned_cosine_similarity": transient["aligned_cosine_similarity"],
            "passed": transient_passed,
        },
        "dynamic_three_ring_fdtd_validated": False,
        "new_cloud_run_authorized": False,
    }


def write_validation(source_root: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(validate_existing_fdtd(source_root), indent=2), encoding="utf-8")
