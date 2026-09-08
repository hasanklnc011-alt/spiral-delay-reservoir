"""No-cloud parity-mode screen for a physically targeted MMI/combiner redesign."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver

from g3_straight_preflight import G1_CONFIG, HERE, REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials


WAVELENGTH_UM = 1.55
WIDTHS_UM = (1.5, 1.75, 2.0, 2.25, 2.5)
MESHES = (20.0, 25.0)


def build_solver(width_um: float, mesh: float, parity: int) -> ModeSolver:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    height = float(accepted["height_um"])
    silicon, silica, _ = lossless_materials()
    core = td.Structure(
        geometry=td.Box(center=(0, 0, 0), size=(td.inf, width_um, height)),
        medium=silicon,
        name="mmi_uniform_section",
    )
    simulation = td.Simulation(
        size=(2.0, 5.0, 3.0),
        medium=silica,
        structures=(core,),
        sources=(),
        monitors=(),
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=WAVELENGTH_UM, min_steps_per_wvl=mesh),
        run_time=1e-12,
        symmetry=(0, parity, 0),
    )
    return ModeSolver(
        simulation=simulation,
        plane=td.Box(center=(0, 0, 0), size=(0, 4.0, 2.0)),
        mode_spec=td.ModeSpec(
            num_modes=5,
            target_neff=2.2,
            precision="double",
            sort_spec=td.ModeSortSpec(
                filter_key="TE_fraction",
                filter_reference=0.7,
                filter_order="over",
                keep_modes=3,
            ),
        ),
        freqs=[td.C_0 / WAVELENGTH_UM],
    )


def solve() -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    _, _, materials = lossless_materials()
    n_clad = math.sqrt(materials["silica_permittivity"])
    cases: list[dict[str, Any]] = []
    for mesh in MESHES:
        for width in WIDTHS_UM:
            parity_modes: dict[str, list[float]] = {}
            for parity, label in ((1, "symmetry_plus"), (-1, "symmetry_minus")):
                data = build_solver(width, mesh, parity).solve()
                values = np.atleast_1d(np.asarray(data.n_eff).real.squeeze())
                parity_modes[label] = [float(value) for value in values]
            even = parity_modes["symmetry_plus"]
            odd = parity_modes["symmetry_minus"]
            guided_even = [value for value in even if value > n_clad + 1e-3]
            guided_odd = [value for value in odd if value > n_clad + 1e-3]
            even_beat = WAVELENGTH_UM / abs(guided_even[0] - guided_even[1]) if len(guided_even) >= 2 else None
            eo_beat = WAVELENGTH_UM / abs(guided_even[0] - guided_odd[0]) if guided_even and guided_odd else None
            cases.append({
                "mesh": mesh,
                "mmi_width_um": width,
                "n_eff_even": even,
                "n_eff_odd": odd,
                "guided_even_count": len(guided_even),
                "guided_odd_count": len(guided_odd),
                "even_mode_2pi_beat_length_um": even_beat,
                "fundamental_symmetry_branch_2pi_beat_length_um": eo_beat,
            })
    convergence = []
    for width in WIDTHS_UM:
        coarse = next(x for x in cases if x["mesh"] == 20.0 and x["mmi_width_um"] == width)
        fine = next(x for x in cases if x["mesh"] == 25.0 and x["mmi_width_um"] == width)
        if coarse["fundamental_symmetry_branch_2pi_beat_length_um"] is None or fine["fundamental_symmetry_branch_2pi_beat_length_um"] is None:
            relative = None
        else:
            relative = abs(coarse["fundamental_symmetry_branch_2pi_beat_length_um"] - fine["fundamental_symmetry_branch_2pi_beat_length_um"]) / fine["fundamental_symmetry_branch_2pi_beat_length_um"]
        convergence.append({"mmi_width_um": width, "relative_fundamental_branch_beat_mesh_delta": relative})
    eligible = [
        x for x in cases
        if x["mesh"] == 25.0 and x["guided_even_count"] >= 2 and x["guided_odd_count"] >= 1
    ]
    selected = min(
        eligible,
        key=lambda x: next(c["relative_fundamental_branch_beat_mesh_delta"] for c in convergence if c["mmi_width_um"] == x["mmi_width_um"]),
    )
    beat = float(selected["fundamental_symmetry_branch_2pi_beat_length_um"])
    return {
        "name": "p6-g3cd-mmi-parity-mode-screen-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "g1_config_sha256": hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),
        "cloud_called": False,
        "material_policy": "lossless scattering screen; fabricated propagation remains external",
        "wavelength_um": WAVELENGTH_UM,
        "cases": cases,
        "mesh_convergence": convergence,
        "selected_width_um": float(selected["mmi_width_um"]),
        "selected_fundamental_branch_2pi_beat_length_um": beat,
        "targeted_length_fractions_um": {
            "three_eighths": 0.375 * beat,
            "one_half": 0.5 * beat,
            "five_eighths": 0.625 * beat,
        },
        "screen_passed": True,
        "claim_limit": "length seeds only; splitter/combiner S-matrix still requires EME/FDTD",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
