"""Local-only binary seed and simulation preflight for inverse-design ID2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage
import tidy3d as td
import tidy3d.plugins.invdes as tdi

from g3_straight_preflight import HERE, REQUIRED_TIDY3D_VERSION
from g3d_mmi_fdtd import sha256
from inverse_design_preflight import CONFIG


RUNS = HERE / "runs"
CACHE_FILES = {
    "splitter": RUNS / "inverse-design-id1-splitter-v1.hdf5",
    "combiner": RUNS / "inverse-design-id1-combiner-v1.hdf5",
}
SUMMARY_FILES = {
    "splitter": RUNS / "inverse-design-id1-splitter-v1.json",
    "combiner": RUNS / "inverse-design-id1-combiner-v1.json",
}


def serialized_sha(simulation: Any) -> str:
    digest = hashlib.sha256(simulation.model_dump_json().encode())
    for structure in simulation.structures:
        medium = structure.medium
        if isinstance(medium, td.CustomMedium):
            values = np.asarray(medium.permittivity.values, dtype="<f8")
            digest.update(values.tobytes(order="C"))
    return digest.hexdigest()


def _disk(radius_pixels: int) -> np.ndarray:
    yy, xx = np.ogrid[-radius_pixels : radius_pixels + 1, -radius_pixels : radius_pixels + 1]
    return xx * xx + yy * yy <= radius_pixels * radius_pixels


def load_binary_seed(device: str) -> tuple[Any, np.ndarray, dict[str, Any]]:
    cache = CACHE_FILES[device]
    summary_path = SUMMARY_FILES[device]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary["cache_file"].replace("\\", "/") != str(cache.relative_to(HERE)).replace("\\", "/"):
        raise RuntimeError(f"{device} cache path does not match its summary")
    result = tdi.InverseDesignResult.from_file(str(cache))
    params = np.asarray(result.params[-1])
    density = np.asarray(result.design.design_region.material_density(params), dtype=float)
    binary = (density >= 0.5).astype(float)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    min_feature = float(config["fabrication_constraints"]["minimum_feature_um"])
    pixel = float(result.design.design_region.pixel_size)
    radius = max(1, int(np.ceil(0.5 * min_feature / pixel)))
    footprint = _disk(radius)
    mask = binary[:, :, 0].astype(bool)
    opened_core = ndimage.binary_opening(mask, structure=footprint)
    opened_clad = ndimage.binary_opening(~mask, structure=footprint)
    feature_proxy_violations = int(np.count_nonzero(mask & ~opened_core))
    gap_proxy_violations = int(np.count_nonzero((~mask) & ~opened_clad))
    binary_region = result.design.design_region.updated_copy(
        transformations=(), penalties=()
    )
    binary_design = result.design.updated_copy(design_region=binary_region)
    simulations = binary_design.to_simulation(binary)
    if not isinstance(simulations, dict):
        simulations = {device: simulations}
    record = {
        "summary_sha256": sha256(summary_path),
        "cache_sha256": sha256(cache),
        "parameter_shape": list(params.shape),
        "density_min": float(np.min(density)),
        "density_max": float(np.max(density)),
        "density_sha256": hashlib.sha256(
            np.asarray(density, dtype="<f8").tobytes(order="C")
        ).hexdigest(),
        "grey_fraction_0p05_to_0p95": float(np.mean((density > 0.05) & (density < 0.95))),
        "binary_fill_fraction": float(np.mean(binary)),
        "binary_seed_sha256": hashlib.sha256(
            np.asarray(binary, dtype="<f8").tobytes(order="C")
        ).hexdigest(),
        "minimum_feature_proxy_radius_pixels": radius,
        "core_feature_proxy_violation_pixels": feature_proxy_violations,
        "gap_feature_proxy_violation_pixels": gap_proxy_violations,
        "simulation_count": len(simulations),
        "serialized_simulation_sha256": {
            key: serialized_sha(sim) for key, sim in simulations.items()
        },
    }
    return simulations, binary, record


def preflight() -> dict[str, Any]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required")
    devices = {}
    for device in CACHE_FILES:
        _, _, devices[device] = load_binary_seed(device)
    return {
        "name": "p6-inverse-design-id2-binary-preflight-v1",
        "tidy3d_version": str(td.__version__),
        "source_sha256": sha256(Path(__file__)),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "cloud_called": False,
        "threshold": 0.5,
        "devices": devices,
        "preflight_passed": all(
            item["simulation_count"] >= 1
            and len(item["serialized_simulation_sha256"]) == item["simulation_count"]
            for item in devices.values()
        ),
        "feature_proxy_is_acceptance": False,
        "id2_can_accept_device": False,
        "next_gate": "upload binary broadband FDTD estimate only",
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), indent=2))
