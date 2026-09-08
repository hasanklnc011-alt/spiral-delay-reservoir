"""Local bent-mode screen for G3-B radius candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver

from g3_bend_preflight import G1_CONFIG, HERE, RADII_UM
from g3_straight_preflight_v2 import lossless_materials


def build_solver(radius_um: float, mesh: float = 25.0) -> ModeSolver:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width, height = float(accepted["width_um"]), float(accepted["height_um"])
    silicon, silica, _ = lossless_materials()
    core = td.Structure(
        geometry=td.Box(center=(0.0, 0.0, 0.0), size=(td.inf, width, height)),
        medium=silicon,
        name="g1_lossless_core",
    )
    simulation = td.Simulation(
        size=(2.0, 4.0, 3.0), center=(0.0, 0.0, 0.0), medium=silica,
        structures=(core,), sources=(), monitors=(),
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=1.55, min_steps_per_wvl=mesh),
        run_time=1e-12,
    )
    return ModeSolver(
        simulation=simulation,
        plane=td.Box(center=(0.0, 0.0, 0.0), size=(0.0, 3.0, 2.0)),
        mode_spec=td.ModeSpec(
            num_modes=1, target_neff=1.9, precision="double",
            bend_radius=radius_um, bend_axis=1, num_pml=(12, 12),
            sort_spec=td.ModeSortSpec(filter_key="TE_fraction", filter_reference=0.8, filter_order="over", keep_modes=1),
        ),
        freqs=td.C_0 / np.linspace(1.52, 1.58, 13),
    )


def screen() -> dict[str, Any]:
    wavelengths = np.linspace(1.52, 1.58, 13)
    cases = []
    for radius in RADII_UM:
        data = build_solver(radius).solve()
        n_complex = np.asarray(data.n_complex)
        fundamental = n_complex[:, 0]
        loss_db = 8.686 * (2.0 * np.pi / wavelengths) * np.abs(np.imag(fundamental)) * (np.pi * radius / 2.0)
        cases.append({
            "radius_um": radius,
            "n_complex": [{"real": float(v.real), "imag": float(v.imag)} for v in fundamental],
            "bend_loss_db_per_90deg": [float(v) for v in loss_db],
            "center_bend_loss_db_per_90deg": float(loss_db[6]),
            "worst_bend_loss_db_per_90deg": float(np.max(loss_db)),
        })
    return {
        "name": "p6-g3b-bent-mode-screen-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "g1_config_sha256": hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),
        "wavelengths_um": [float(v) for v in wavelengths],
        "cloud_called": False,
        "claim_level": "local bent-eigenmode radiation-loss upper-bound screen; imaginary-neff numerical floor and FDTD reflection remain separate",
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2))
