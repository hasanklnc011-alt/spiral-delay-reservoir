"""P6 G1 cross-section mode solver.

The solver runs locally through Tidy3D's mode plugin and has no cloud path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver


REQUIRED_TIDY3D_VERSION = "2.12.0"
HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "configs" / "baseline-v1.json"


def load_seed(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    seed = config["platform_gate"]["cross_section_seed"]
    architecture = config["architecture"]
    return {
        "wavelength_um": float(config["platform_gate"]["wavelength_um"]),
        "width_um": float(seed["width_um"]),
        "height_um": float(seed["height_um"]),
        "group_index_target": float(config["platform_gate"]["required_group_index"]),
        "group_index_tolerance_fraction": float(architecture["group_index_tolerance_fraction"]),
        "locked_delay_length_cm": float(architecture["delay_length_cm_locked"]),
        "target_delay_s": (int(architecture["n_lags"]) - 1) / float(architecture["symbol_rate_hz"]),
    }


def build_mode_solver(
    seed: dict[str, Any],
    *,
    min_steps_per_wvl: float = 20.0,
    wavelengths_um: np.ndarray | None = None,
) -> ModeSolver:
    wavelength_um = float(seed["wavelength_um"])
    wavelengths = np.array([wavelength_um]) if wavelengths_um is None else np.asarray(wavelengths_um, dtype=float)
    if wavelengths.ndim != 1 or len(wavelengths) == 0 or np.any(wavelengths <= 0.0):
        raise ValueError("wavelengths_um must be a positive 1D array")
    silicon = td.material_library["cSi"]["Li1993_293K"]
    silica = td.material_library["SiO2"]["Horiba"]
    core = td.Structure(
        geometry=td.Box(center=(0.0, 0.0, 0.0), size=(td.inf, float(seed["width_um"]), float(seed["height_um"]))),
        medium=silicon,
        name="p6_seed_silicon_core",
    )
    simulation = td.Simulation(
        size=(2.0, 4.0, 3.0),
        center=(0.0, 0.0, 0.0),
        medium=silica,
        structures=(core,),
        sources=(),
        monitors=(),
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=wavelength_um, min_steps_per_wvl=min_steps_per_wvl),
        run_time=1e-12,
    )
    return ModeSolver(
        simulation=simulation,
        plane=td.Box(center=(0.0, 0.0, 0.0), size=(0.0, 3.0, 2.0)),
        mode_spec=td.ModeSpec(num_modes=3, target_neff=2.5, group_index_step=True),
        freqs=td.C_0 / wavelengths,
    )


def _mode_vector(value: Any) -> list[float]:
    array = np.asarray(value).real.squeeze()
    return [float(item) for item in np.atleast_1d(array)]


def _mode_matrix(value: Any) -> np.ndarray:
    array = np.asarray(value).real
    if array.ndim == 1:
        array = array[None, :]
    return array


def solve_local(
    seed: dict[str, Any],
    *,
    min_steps_per_wvl: float,
    wavelengths_um: np.ndarray | None = None,
) -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required; found {td.__version__}")
    wavelengths = np.array([float(seed["wavelength_um"])]) if wavelengths_um is None else np.asarray(wavelengths_um, dtype=float)
    solver = build_mode_solver(seed, min_steps_per_wvl=min_steps_per_wvl, wavelengths_um=wavelengths)
    data = solver.solve()
    n_eff_matrix = _mode_matrix(data.n_eff)
    n_group_matrix = _mode_matrix(data.n_group)
    mode_area_matrix = _mode_matrix(data.mode_area)
    center_index = int(np.argmin(np.abs(wavelengths - float(seed["wavelength_um"]))))
    n_eff = _mode_vector(n_eff_matrix[center_index])
    n_group = _mode_vector(n_group_matrix[center_index])
    mode_area = _mode_vector(mode_area_matrix[center_index])
    center_frequency = float(td.C_0 / wavelengths[center_index])
    silica = td.material_library["SiO2"]["Horiba"]
    n_cladding = float(np.sqrt(np.real(silica.eps_model(center_frequency))))
    guided_mode_count = sum(value > n_cladding + 1e-3 for value in n_eff)
    target_ng = float(seed["group_index_target"])
    target_tolerance = float(seed["group_index_tolerance_fraction"])
    ng_error = abs(n_group[0] - target_ng) / target_ng
    delay_s = n_group[0] * (float(seed["locked_delay_length_cm"]) / 100.0) / 299_792_458.0
    return {
        "claim_level": "local G1 seed cross-section result; not final platform acceptance",
        "tidy3d_version": str(td.__version__),
        "cloud_called": False,
        "seed": seed,
        "min_steps_per_wvl": min_steps_per_wvl,
        "wavelengths_um": [float(value) for value in wavelengths],
        "n_eff": n_eff,
        "n_group": n_group,
        "mode_area_um2": mode_area,
        "fundamental_mode": {"n_eff": n_eff[0], "n_group": n_group[0], "mode_area_um2": mode_area[0]},
        "higher_mode_margin": {
            "cladding_index": n_cladding,
            "guided_mode_count_by_index": guided_mode_count,
            "n_eff_mode0_minus_mode1": n_eff[0] - n_eff[1],
        },
        "delay_gate": {
            "group_index_target": target_ng,
            "relative_group_index_error": ng_error,
            "relative_group_index_error_limit": target_tolerance,
            "delay_at_locked_length_s": delay_s,
            "target_delay_s": float(seed["target_delay_s"]),
            "passed": ng_error <= target_tolerance,
        },
        "spectra": {
            "n_eff": n_eff_matrix.tolist(),
            "n_group": n_group_matrix.tolist(),
            "mode_area_um2": mode_area_matrix.tolist(),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--mesh", type=float, default=20.0)
    parser.add_argument("--solve-local", action="store_true")
    parser.add_argument("--spectral-sweep", action="store_true", help="Solve 13 points from 1.52 to 1.58 um locally.")
    args = parser.parse_args()
    seed = load_seed(args.config)
    wavelengths = np.linspace(1.52, 1.58, 13) if args.spectral_sweep else None
    if args.solve_local:
        output = solve_local(seed, min_steps_per_wvl=args.mesh, wavelengths_um=wavelengths)
    else:
        solver = build_mode_solver(seed, min_steps_per_wvl=args.mesh, wavelengths_um=wavelengths)
        output = {
            "claim_level": "local builder validation only",
            "tidy3d_version": str(td.__version__),
            "cloud_called": False,
            "seed": seed,
            "min_steps_per_wvl": args.mesh,
            "simulation_cells": int(solver.simulation.num_cells),
        }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
