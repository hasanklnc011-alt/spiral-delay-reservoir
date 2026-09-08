"""No-cloud ID0 preflight for custom-process splitter and combiner design regions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import tidy3d as td
import tidy3d.plugins.invdes as tdi

from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION


CONFIG = HERE / "configs" / "inverse-design-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_region(size: list[float], config: dict[str, Any]) -> tdi.TopologyDesignRegion:
    fabrication = config["fabrication_constraints"]
    silica = 1.45**2
    silicon = 3.47**2
    return tdi.TopologyDesignRegion(
        center=(0.0, 0.0, 0.0),
        size=tuple(size),
        eps_bounds=(silica, silicon),
        pixel_size=float(fabrication["pixel_size_um"]),
        uniform=(False, False, True),
        transformations=(
            tdi.FilterProject(
                radius=float(fabrication["filter_radius_um"]),
                beta=1.0,
                eta=0.5,
            ),
        ),
        penalties=(
            tdi.ErosionDilationPenalty(
                length_scale=float(
                    fabrication["erosion_dilation_length_scale_um"]
                ),
                weight=1.0,
            ),
        ),
        initialization_spec=tdi.UniformInitializationSpec(value=0.5),
    )


def preflight() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    regions = {
        name: build_region(device["design_region_um"], config)
        for name, device in config["devices"].items()
    }
    summaries = {}
    for name, region in regions.items():
        nx = round(region.size[0] / region.pixel_size)
        ny = round(region.size[1] / region.pixel_size)
        summaries[name] = {
            "size_um": list(region.size),
            "pixel_size_um": region.pixel_size,
            "parameter_grid": [nx, ny, 1],
            "parameter_count": nx * ny,
            "serialized_region_sha256": hashlib.sha256(
                region.model_dump_json().encode()
            ).hexdigest(),
            "transformations": [item.type for item in region.transformations],
            "penalties": [item.type for item in region.penalties],
        }
    required_api = (
        "TopologyDesignRegion",
        "InverseDesign",
        "InverseDesignMulti",
        "AdamOptimizer",
        "FilterProject",
        "ErosionDilationPenalty",
    )
    api_available = {name: hasattr(tdi, name) for name in required_api}
    return {
        "name": "p6-custom-process-inverse-design-id0-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "cloud_called": False,
        "api_available": api_available,
        "wavelengths_um": config["wavelengths_um"],
        "regions": summaries,
        "separate_device_optimizations": True,
        "multi_source_combiner_required": config["devices"]["g3d_combiner"][
            "independent_sources"
        ] == 2,
        "preflight_passed": all(api_available.values())
        and len(regions) == 2
        and all(item["parameter_count"] > 0 for item in summaries.values()),
        "next_gate": "construct source/monitor/objective simulations, then upload estimate only",
        "id0_can_accept_device": False,
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
