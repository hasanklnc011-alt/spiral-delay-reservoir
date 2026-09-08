"""LEGACY: bounded search for the old three-ring NARMA-10 candidate."""

from __future__ import annotations

from dataclasses import asdict, replace
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

from .benchmark import generate_narma, validation_nmse
from .config import BenchmarkConfig, DriveConfig, SolverConfig, TopologyParams
from .model import simulate


def _candidate(topology: TopologyParams, drive: DriveConfig, n_virtual: int, symbol_time_ps: float, detuning_span: float, coupling: float) -> tuple[TopologyParams, DriveConfig]:
    rings = tuple(replace(ring, detuning_linewidths=value) for ring, value in zip(topology.rings, (-detuning_span, 0.0, detuning_span)))
    return (
        replace(topology, rings=rings, coupling_linewidths=(coupling, coupling), kerr_enabled=False),
        replace(drive, n_virtual=n_virtual, symbol_time_s=symbol_time_ps * 1e-12),
    )


def bounded_search(topology: TopologyParams, drive: DriveConfig, solver: SolverConfig, benchmark: BenchmarkConfig) -> dict[str, Any]:
    grid = list(itertools.product((10, 20), (0.2, 0.5, 1.0), (0.5, 1.5), (0.25, 0.45)))
    first_seed = benchmark.seeds[0]
    u, target = generate_narma(benchmark.n_total, benchmark.order, first_seed)
    stage_one = []
    for n_virtual, symbol_time_ps, detuning_span, coupling in grid:
        candidate_topology, candidate_drive = _candidate(topology, drive, n_virtual, symbol_time_ps, detuning_span, coupling)
        result = simulate(u, candidate_topology, candidate_drive, solver)
        score, alpha = validation_nmse(result.features, target, benchmark)
        stage_one.append({
            "n_virtual": n_virtual, "symbol_time_ps": symbol_time_ps, "detuning_span": detuning_span,
            "coupling_linewidths": coupling, "seed": first_seed, "validation_nmse": score,
            "best_alpha": alpha, "diverged": result.diverged,
        })
    finalists = sorted(stage_one, key=lambda row: row["validation_nmse"])[:3]
    stage_two = []
    for candidate in finalists:
        scores = []
        for seed in benchmark.seeds:
            u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
            candidate_topology, candidate_drive = _candidate(topology, drive, int(candidate["n_virtual"]), float(candidate["symbol_time_ps"]), float(candidate["detuning_span"]), float(candidate["coupling_linewidths"]))
            result = simulate(u, candidate_topology, candidate_drive, solver)
            score, alpha = validation_nmse(result.features, target, benchmark)
            scores.append({"seed": seed, "validation_nmse": score, "best_alpha": alpha})
        stage_two.append({**{key: candidate[key] for key in ("n_virtual", "symbol_time_ps", "detuning_span", "coupling_linewidths")}, "seed_scores": scores, "median_validation_nmse": float(np.median([row["validation_nmse"] for row in scores]))})
    selected = min(stage_two, key=lambda row: row["median_validation_nmse"])
    selected_topology, selected_drive = _candidate(topology, drive, int(selected["n_virtual"]), float(selected["symbol_time_ps"]), float(selected["detuning_span"]), float(selected["coupling_linewidths"]))
    return {
        "selection_metric": "median validation NMSE only",
        "test_set_evaluated": False,
        "grid_size": len(grid),
        "stage_one": stage_one,
        "stage_two": stage_two,
        "selected": selected,
        "selected_topology": asdict(selected_topology),
        "selected_drive": asdict(selected_drive),
    }


def write_search(result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
