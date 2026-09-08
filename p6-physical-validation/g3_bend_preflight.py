"""Local-only G3-B quarter-bend and adjacent-turn preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td

from g3_straight_preflight import G1_CONFIG, HERE, REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials


RADII_UM = (10.0, 20.0, 30.0, 50.0)
PITCH_UM = 5.0


def _mode_spec() -> td.ModeSpec:
    return td.ModeSpec(
        num_modes=3,
        target_neff=1.9,
        sort_spec=td.ModeSortSpec(
            filter_key="TE_fraction",
            filter_reference=0.8,
            filter_order="over",
            keep_modes=1,
        ),
    )


def _quarter_annulus(radius_um: float, width_um: float, height_um: float, arc_points: int = 97) -> td.PolySlab:
    angles = np.linspace(-np.pi / 2.0, 0.0, arc_points)
    outer = [
        ((radius_um + width_um / 2.0) * np.cos(a), (radius_um + width_um / 2.0) * np.sin(a))
        for a in angles
    ]
    inner = [
        ((radius_um - width_um / 2.0) * np.cos(a), (radius_um - width_um / 2.0) * np.sin(a))
        for a in angles[::-1]
    ]
    return td.PolySlab(vertices=outer + inner, slab_bounds=(-height_um / 2.0, height_um / 2.0), axis=2)


def build_bend(radius_um: float = 20.0, mesh: float = 15.0, arc_points: int = 97, run_time_s: float = 3e-12) -> td.Simulation:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width, height = float(accepted["width_um"]), float(accepted["height_um"])
    silicon, silica, _ = lossless_materials()
    wavelengths = np.linspace(1.52, 1.58, 13)
    freqs = td.C_0 / wavelengths
    freq0 = td.C_0 / 1.55
    fwidth = 1.5 * (max(freqs) - min(freqs))
    lead = 4.5
    structures = (
        td.Structure(
            geometry=td.Box(center=(-lead / 2.0, -radius_um, 0.0), size=(lead + 0.5, width, height)),
            medium=silicon,
            name="input_lead",
        ),
        td.Structure(
            geometry=_quarter_annulus(radius_um, width, height, arc_points=arc_points),
            medium=silicon,
            name="quarter_bend",
        ),
        td.Structure(
            geometry=td.Box(center=(radius_um, lead / 2.0, 0.0), size=(width, lead + 0.5, height)),
            medium=silicon,
            name="output_lead",
        ),
    )
    source = td.ModeSource(
        center=(-3.0, -radius_um, 0.0),
        size=(0.0, 2.0, 1.2),
        source_time=td.GaussianPulse(freq0=freq0, fwidth=fwidth),
        direction="+",
        mode_spec=_mode_spec(),
        mode_index=0,
        name="te0_source",
    )
    monitors = (
        td.ModeMonitor(center=(-2.2, -radius_um, 0.0), size=(0.0, 2.0, 1.2), freqs=freqs, mode_spec=_mode_spec(), name="input_port"),
        td.ModeMonitor(center=(radius_um, 2.2, 0.0), size=(2.0, 0.0, 1.2), freqs=freqs, mode_spec=_mode_spec(), name="output_port"),
    )
    center = (radius_um / 2.0, -radius_um / 2.0, 0.0)
    size = (radius_um + 8.0, radius_um + 8.0, 2.0)
    return td.Simulation(
        center=center,
        size=size,
        medium=silica,
        structures=structures,
        sources=(source,),
        monitors=monitors,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=1.55, min_steps_per_wvl=mesh),
        run_time=run_time_s,
        shutoff=1e-7,
        subpixel=True,
        symmetry=(0, 0, 1),
    )


def adjacent_turn_geometry(pitch_um: float = PITCH_UM) -> dict[str, float]:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width = float(accepted["width_um"])
    return {
        "pitch_um": pitch_um,
        "waveguide_width_um": width,
        "edge_gap_um": pitch_um - width,
        "screened_pitch_candidates_um": [3.0, 4.0, 5.0, 6.0],
    }


def preflight() -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required; found {td.__version__}")
    cases = []
    for radius in (20.0,):
        simulation = build_bend(radius, mesh=15.0)
        serialized = simulation.model_dump_json()
        cases.append(
            {
                "radius_um": radius,
                "mesh": 15.0,
                "simulation_cells": int(simulation.num_cells),
                "computational_grid_points": int(simulation.num_computational_grid_points),
                "serialized_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
            }
        )
    return {
        "name": "p6-g3b-bend-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "g1_config_sha256": hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),
        "material_policy": "lossless scattering reference; fabricated propagation loss external",
        "radius_screen_um": list(RADII_UM),
        "selected_nominal_radius_um": 20.0,
        "selection_basis": "P6 locked provisional layout; radius sweep is reserved for 2.5D screening and only selected R20 enters 3D pilot",
        "adjacent_turn": adjacent_turn_geometry(),
        "cloud_called": False,
        "cases": cases,
        "passed": True,
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
