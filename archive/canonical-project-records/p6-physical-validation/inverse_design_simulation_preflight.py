"""No-cloud source, port, and complex-objective preflight for P6 inverse design."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import autograd.numpy as anp
import numpy as np
import tidy3d as td
import tidy3d.plugins.invdes as tdi

from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials
from inverse_design_preflight import CONFIG, build_region, sha256


WAVELENGTHS_UM = np.array([1.53, 1.55, 1.575])
MESH = 15.0
RUN_TIME_S = 3e-12
PORT_OFFSET_UM = 0.9
LEAD_UM = 3.0


def _mode_spec() -> td.ModeSpec:
    return td.ModeSpec(
        num_modes=1,
        target_neff=1.87,
        sort_spec=td.ModeSortSpec(
            filter_key="TE_fraction",
            filter_reference=0.8,
            filter_order="over",
            keep_modes=1,
        ),
    )


def _guide(
    x0: float, x1: float, y: float, width: float, height: float, medium: td.Medium, name: str
) -> td.Structure:
    return td.Structure(
        geometry=td.Box(
            center=((x0 + x1) / 2, y, 0),
            size=(x1 - x0, width, height),
        ),
        medium=medium,
        name=name,
    )


def _source(x: float, y: float, direction: str, name: str) -> td.ModeSource:
    freqs = td.C_0 / WAVELENGTHS_UM
    return td.ModeSource(
        center=(x, y, 0),
        size=(0, 0.9, 1.2),
        source_time=td.GaussianPulse(
            freq0=td.C_0 / 1.55,
            fwidth=1.5 * (max(freqs) - min(freqs)),
        ),
        direction=direction,
        mode_spec=_mode_spec(),
        mode_index=0,
        name=name,
    )


def _monitor(x: float, y: float, name: str) -> td.ModeMonitor:
    return td.ModeMonitor(
        center=(x, y, 0),
        size=(0, 0.9, 1.2),
        freqs=td.C_0 / WAVELENGTHS_UM,
        mode_spec=_mode_spec(),
        name=name,
    )


def _base_simulation(
    region_size: list[float],
    source_y: float,
    input_ys: tuple[float, ...],
    output_ys: tuple[float, ...],
    source_name: str,
) -> td.Simulation:
    accepted = json.loads((HERE / "configs" / "g1-accepted-v1.json").read_text(encoding="utf-8"))
    width = float(accepted["width_um"])
    height = float(accepted["height_um"])
    region_x = float(region_size[0])
    region_y = float(region_size[1])
    half = region_x / 2
    x_min = -half - LEAD_UM
    x_max = half + LEAD_UM
    silicon, silica, _ = lossless_materials()
    structures = []
    for index, y in enumerate(input_ys):
        structures.append(
            _guide(x_min - 1.0, -half + 0.1, y, width, height, silicon, f"input_{index}")
        )
    for index, y in enumerate(output_ys):
        structures.append(
            _guide(half - 0.1, x_max + 1.0, y, width, height, silicon, f"output_{index}")
        )
    source_x = x_min + 0.7
    input_monitor_x = -half - 0.7
    output_monitor_x = half + 0.7
    monitors = tuple(
        [_monitor(input_monitor_x, y, f"left_{index}") for index, y in enumerate(input_ys)]
        + [_monitor(output_monitor_x, y, f"right_{index}") for index, y in enumerate(output_ys)]
    )
    return td.Simulation(
        center=(0, 0, 0),
        size=(x_max - x_min + 1.0, region_y + 3.0, 2.0),
        medium=silica,
        structures=tuple(structures),
        sources=(_source(source_x, source_y, "+", source_name),),
        monitors=monitors,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),
        grid_spec=td.GridSpec.auto(wavelength=1.55, min_steps_per_wvl=MESH),
        run_time=RUN_TIME_S,
        shutoff=1e-7,
        subpixel=True,
        symmetry=(0, 0, 1),
    )


def phase_invariant_column_objective(
    out0: Any, out1: Any, reflection: Any, target_phase_deg: float
) -> Any:
    """Power-weighted overlap with an ideal two-port complex column."""
    column = anp.stack((out0, out1), axis=0)
    target = anp.array(
        [1.0, anp.exp(1j * anp.deg2rad(target_phase_deg))]
    ) / anp.sqrt(2.0)
    overlap = anp.sum(anp.conj(target)[:, None] * column, axis=0)
    fidelity_power = anp.abs(overlap) ** 2
    reflected_power = anp.abs(reflection) ** 2
    return anp.mean(fidelity_power - reflected_power)


def _amp(data: td.SimulationData, name: str, direction: str) -> Any:
    return tdi.utils.get_amps(
        data, monitor_name=name, direction=direction, mode_index=0
    )


def splitter_post_process(data: td.SimulationData, **_: Any) -> Any:
    return phase_invariant_column_objective(
        _amp(data, "right_0", "+"),
        _amp(data, "right_1", "+"),
        _amp(data, "left_0", "-"),
        0.0,
    )


def combiner_post_process(batch_data: dict[str, td.SimulationData], **_: Any) -> Any:
    if len(batch_data) != 2:
        raise ValueError("G3-D objective requires exactly two source simulations")
    upper, lower = tuple(batch_data.values())
    upper_score = phase_invariant_column_objective(
        _amp(upper, "right_0", "+"),
        _amp(upper, "right_1", "+"),
        anp.concatenate(
            (_amp(upper, "left_0", "-"), _amp(upper, "left_1", "-"))
        ),
        -90.0,
    )
    lower_score = phase_invariant_column_objective(
        _amp(lower, "right_0", "+"),
        _amp(lower, "right_1", "+"),
        anp.concatenate(
            (_amp(lower, "left_0", "-"), _amp(lower, "left_1", "-"))
        ),
        90.0,
    )
    return 0.5 * (upper_score + lower_score)


def build_designs() -> tuple[tdi.InverseDesign, tdi.InverseDesignMulti]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    split_spec = config["devices"]["g3c_splitter"]
    comb_spec = config["devices"]["g3d_combiner"]
    splitter_region = build_region(split_spec["design_region_um"], config)
    combiner_region = build_region(comb_spec["design_region_um"], config)
    splitter_ports = (-PORT_OFFSET_UM, PORT_OFFSET_UM)
    splitter_sim = _base_simulation(
        split_spec["design_region_um"], 0.0, (0.0,), splitter_ports, "g3c_source"
    )
    combiner_ports = (-PORT_OFFSET_UM, PORT_OFFSET_UM)
    combiner_sims = {
        "g3d_upper": _base_simulation(
            comb_spec["design_region_um"], PORT_OFFSET_UM, combiner_ports, combiner_ports, "g3d_upper_source"
        ),
        "g3d_lower": _base_simulation(
            comb_spec["design_region_um"], -PORT_OFFSET_UM, combiner_ports, combiner_ports, "g3d_lower_source"
        ),
    }
    splitter = tdi.InverseDesign(
        design_region=splitter_region,
        simulation=splitter_sim,
        task_name="p6_g3c_inverse_design_v1",
        output_monitor_names=("left_0", "right_0", "right_1"),
        verbose=False,
    )
    combiner = tdi.InverseDesignMulti(
        design_region=combiner_region,
        simulations=tuple(combiner_sims.values()),
        task_name="p6_g3d_inverse_design_v1",
        output_monitor_names=(
            ("left_0", "right_0", "right_1"),
            ("left_1", "right_0", "right_1"),
        ),
        verbose=False,
    )
    return splitter, combiner


def preflight() -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    splitter, combiner = build_designs()
    splitter_sim = splitter.to_simulation(splitter.design_region.initial_parameters)
    combiner_sims = combiner.to_simulation(combiner.design_region.initial_parameters)
    perfect_splitter = float(
        phase_invariant_column_objective(
            anp.ones(3) / anp.sqrt(2),
            anp.ones(3) / anp.sqrt(2),
            anp.zeros(3),
            0.0,
        )
    )
    perfect_quadrature = float(
        phase_invariant_column_objective(
            anp.ones(3) / anp.sqrt(2),
            1j * anp.ones(3) / anp.sqrt(2),
            anp.zeros(3),
            90.0,
        )
    )
    return {
        "name": "p6-inverse-design-source-port-objective-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "cloud_called": False,
        "wavelengths_um": list(WAVELENGTHS_UM),
        "perfect_objective_checks": {
            "splitter": perfect_splitter,
            "quadrature_column": perfect_quadrature,
        },
        "splitter": {
            "source_count": len(splitter_sim.sources),
            "monitor_names": [monitor.name for monitor in splitter_sim.monitors],
            "computational_grid_points": int(splitter_sim.num_computational_grid_points),
            "serialized_simulation_sha256": hashlib.sha256(
                splitter_sim.model_dump_json().encode()
            ).hexdigest(),
        },
        "combiner": {
            "source_count": sum(len(sim.sources) for sim in combiner_sims.values()),
            "simulation_keys": list(combiner_sims),
            "monitor_names": {
                key: [monitor.name for monitor in sim.monitors]
                for key, sim in combiner_sims.items()
            },
            "computational_grid_points": {
                key: int(sim.num_computational_grid_points)
                for key, sim in combiner_sims.items()
            },
            "serialized_simulation_sha256": {
                key: hashlib.sha256(sim.model_dump_json().encode()).hexdigest()
                for key, sim in combiner_sims.items()
            },
        },
        "preflight_passed": abs(perfect_splitter - 1.0) < 1e-12
        and abs(perfect_quadrature - 1.0) < 1e-12
        and len(combiner_sims) == 2,
        "estimate_only_next": True,
        "id0_can_accept_device": False,
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
