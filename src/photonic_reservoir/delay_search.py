"""LEGACY: search for the old three-ring explicit-feedback pivot."""

from __future__ import annotations

from dataclasses import asdict, replace
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

from .benchmark import generate_narma, validation_nmse
from .config import BenchmarkConfig, DriveConfig, FeedbackParams, SolverConfig, TopologyParams
from .model import simulate


def bounded_delay_search(topology: TopologyParams, drive: DriveConfig, solver: SolverConfig, benchmark: BenchmarkConfig) -> dict[str, Any]:
    # Kerr is disabled during architecture selection; its physical ablation is run later.
    topology = replace(topology, kerr_enabled=False)
    grid = list(itertools.product((1.0, 2.0, 4.0, 8.0), (0.2, 0.5, 0.8), (0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi)))
    first_seed = benchmark.seeds[0]
    u, target = generate_narma(benchmark.n_total, benchmark.order, first_seed)
    stage_one = []
    for delay_symbols, strength, phase_rad in grid:
        feedback = FeedbackParams(True, strength, phase_rad, delay_symbols * drive.symbol_time_s)
        result = simulate(u, topology, drive, solver, feedback)
        score, alpha = validation_nmse(result.features, target, benchmark)
        stage_one.append({"delay_symbols": delay_symbols, "strength": strength, "phase_rad": phase_rad, "seed": first_seed, "validation_nmse": score, "best_alpha": alpha, "diverged": result.diverged})
    finalists = sorted(stage_one, key=lambda row: row["validation_nmse"])[:3]
    stage_two = []
    for candidate in finalists:
        seed_scores = []
        feedback = FeedbackParams(True, float(candidate["strength"]), float(candidate["phase_rad"]), float(candidate["delay_symbols"]) * drive.symbol_time_s)
        for seed in benchmark.seeds:
            u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
            result = simulate(u, topology, drive, solver, feedback)
            score, alpha = validation_nmse(result.features, target, benchmark)
            seed_scores.append({"seed": seed, "validation_nmse": score, "best_alpha": alpha})
        stage_two.append({**{key: candidate[key] for key in ("delay_symbols", "strength", "phase_rad")}, "seed_scores": seed_scores, "median_validation_nmse": float(np.median([row["validation_nmse"] for row in seed_scores]))})
    selected = min(stage_two, key=lambda row: row["median_validation_nmse"])
    selected_feedback = FeedbackParams(True, float(selected["strength"]), float(selected["phase_rad"]), float(selected["delay_symbols"]) * drive.symbol_time_s)
    return {
        "selection_metric": "median validation NMSE only",
        "test_set_evaluated": False,
        "grid_size": len(grid),
        "stage_one": stage_one,
        "stage_two": stage_two,
        "selected": selected,
        "selected_feedback": asdict(selected_feedback),
    }


def write_delay_search(result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
