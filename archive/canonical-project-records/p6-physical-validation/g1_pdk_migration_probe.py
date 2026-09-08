"""No-cloud 220 nm PDK migration impact probe for the G1 delay gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from g1_candidate_probe import probe


HEIGHT_UM = 0.22
WIDTHS_UM = (0.30, 0.31, 0.35, 0.40, 0.45, 0.50)
SCREEN_MESH = 20.0
CONVERGENCE_MESHES = (15.0, 20.0, 25.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, Any]:
    screen = [probe(width, HEIGHT_UM, SCREEN_MESH) for width in WIDTHS_UM]
    selected = min(screen, key=lambda item: item["relative_group_index_error"])
    convergence = [
        probe(float(selected["width_um"]), HEIGHT_UM, mesh)
        for mesh in CONVERGENCE_MESHES
    ]
    n_groups = [float(item["fundamental_n_group"]) for item in convergence]
    relative_span = (max(n_groups) - min(n_groups)) / float(np.mean(n_groups))
    convergence_passed = relative_span <= 0.005
    return {
        "name": "p6-g1-220nm-pdk-migration-local-probe-v1",
        "source_sha256": sha256(Path(__file__)),
        "p5_blind_rerun": False,
        "cloud_called": False,
        "height_um": HEIGHT_UM,
        "screen_mesh": SCREEN_MESH,
        "screen": screen,
        "selected_width_um": float(selected["width_um"]),
        "convergence": convergence,
        "relative_group_index_span": relative_span,
        "local_convergence_threshold": 0.005,
        "local_convergence_passed": convergence_passed,
        "migration_g1_accepted": False,
        "claim_limit": "local no-subpixel impact probe only; PDK selection and remote subpixel corners required",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
