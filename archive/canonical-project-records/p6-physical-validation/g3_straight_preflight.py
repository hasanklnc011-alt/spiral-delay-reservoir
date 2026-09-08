"""Build the two-length G3-A straight-waveguide FDTD de-embedding suite locally."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td


REQUIRED_TIDY3D_VERSION = "2.12.0"
HERE = Path(__file__).resolve().parent
G1_CONFIG = HERE / "configs" / "g1-accepted-v1.json"


def build_straight(length_um: float, mesh: float = 15.0) -> td.Simulation:
    accepted = json.loads(G1_CONFIG.read_text(encoding="utf-8"))
    width = float(accepted["width_um"])
    height = float(accepted["height_um"])
    wavelength_min, wavelength_max = 1.52, 1.58
    wavelengths = np.linspace(wavelength_min, wavelength_max, 13)
    freqs = td.C_0 / wavelengths
    freq0 = td.C_0 / 1.55
    fwidth = 1.5 * (max(freqs) - min(freqs))
    source_x = -length_um / 2.0 - 0.75
    input_x = -length_um / 2.0
    output_x = length_um / 2.0
    domain_x = length_um + 4.0
    mode_spec = td.ModeSpec(
        num_modes=3,
        target_neff=1.9,
        sort_spec=td.ModeSortSpec(
            filter_key="TE_fraction",
            filter_reference=0.8,
            filter_order="over",
            keep_modes=1,
        ),
    )
    port_size = (0.0, 2.0, 1.5)
    silicon = td.material_library["cSi"]["Li1993_293K"]
    silica = td.material_library["SiO2"]["Horiba"]
    structure = td.Structure(
        geometry=td.Box(center=(0.0, 0.0, 0.0), size=(td.inf, width, height)),
        medium=silicon,
        name="g1_accepted_silicon_strip",
    )
    source = td.ModeSource(
        center=(source_x, 0.0, 0.0),
        size=port_size,
        source_time=td.GaussianPulse(freq0=freq0, fwidth=fwidth),
        direction="+",
        mode_spec=mode_spec,
        mode_index=0,
        name="te0_source",
    )
    monitors = (
        td.ModeMonitor(center=(input_x, 0.0, 0.0), size=port_size, freqs=freqs, mode_spec=mode_spec, name="input_port"),
        td.ModeMonitor(center=(output_x, 0.0, 0.0), size=port_size, freqs=freqs, mode_spec=mode_spec, name="output_port"),
        td.FluxMonitor(center=(input_x, 0.0, 0.0), size=port_size, freqs=freqs, name="input_flux"),
        td.FluxMonitor(center=(output_x, 0.0, 0.0), size=port_size, freqs=freqs, name="output_flux"),
    )
    return td.Simulation(
        center=(0.0, 0.0, 0.0),
        size=(domain_x, 3.0, 2.5),
        medium=silica,
        structures=(structure,),
        sources=(source,),
        monitors=monitors,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=1.55, min_steps_per_wvl=mesh),
        run_time=2e-12,
        shutoff=1e-7,
        subpixel=True,
    )


def preflight() -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required; found {td.__version__}")
    cases = []
    for length in (4.0, 8.0):
        simulation = build_straight(length)
        serialized = simulation.model_dump_json()
        cases.append(
            {
                "length_um": length,
                "simulation_cells": int(simulation.num_cells),
                "serialized_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
                "serialized_bytes": len(serialized.encode("utf-8")),
                "source_count": len(simulation.sources),
                "monitor_count": len(simulation.monitors),
                "subpixel_enabled": bool(simulation.subpixel),
            }
        )
    return {
        "name": "p6-g3a-straight-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "g1_config_sha256": hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),
        "cloud_called": False,
        "cases": cases,
        "passed": all(case["source_count"] == 1 and case["monitor_count"] == 4 and case["subpixel_enabled"] for case in cases),
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
