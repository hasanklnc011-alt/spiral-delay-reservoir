"""No-cloud cross-section probe used only to nominate remote G1 candidates."""

from __future__ import annotations

import argparse
import json

import numpy as np
import tidy3d as td

from g1_mode_solver import REQUIRED_TIDY3D_VERSION, build_mode_solver, load_seed


def probe(width_um: float, height_um: float, mesh: float = 20.0) -> dict[str, object]:
    if str(td.__version__) != REQUIRED_TIDY3D_VERSION:
        raise RuntimeError(f"Tidy3D {REQUIRED_TIDY3D_VERSION} required; found {td.__version__}")
    seed = load_seed()
    seed["width_um"] = width_um
    seed["height_um"] = height_um
    solver = build_mode_solver(seed, min_steps_per_wvl=mesh)
    data = solver.solve()
    n_eff = np.asarray(data.n_eff).real.squeeze()
    n_group = np.asarray(data.n_group).real.squeeze()
    te = np.asarray(data.pol_fraction.te).real.squeeze()
    mode_area = np.asarray(data.mode_area).real.squeeze()
    target_error = abs(float(n_group[0]) - 4.0) / 4.0
    return {
        "claim_level": "local no-subpixel candidate nomination only",
        "cloud_called": False,
        "width_um": width_um,
        "height_um": height_um,
        "mesh": mesh,
        "fundamental_n_eff": float(n_eff[0]),
        "fundamental_n_group": float(n_group[0]),
        "fundamental_te_fraction": float(te[0]),
        "fundamental_mode_area_um2": float(mode_area[0]),
        "relative_group_index_error": target_error,
        "nomination_gate_passed": target_error <= 0.02 and float(te[0]) >= 0.8,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=float, required=True)
    parser.add_argument("--height", type=float, required=True)
    parser.add_argument("--mesh", type=float, default=20.0)
    args = parser.parse_args()
    print(json.dumps(probe(args.width, args.height, args.mesh), indent=2))


if __name__ == "__main__":
    main()
