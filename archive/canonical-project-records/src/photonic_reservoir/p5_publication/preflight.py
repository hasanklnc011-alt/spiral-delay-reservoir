"""Development-only publication-control preflight before candidate locking."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, generate_narma, paired_bootstrap_ci
from ..p1_coherent_delay.ideal import coherent_square_law_features, fast_validation_nmse
from ..p2_architecture.screen import _benchmark
from ..p3_realistic.screen import physical_sparse_features
from ..protocol import dataset_sha256, source_tree_sha256


def no_photonic_core_features(u: np.ndarray) -> np.ndarray:
    """Memoryless electrical/input-chain features with no optical delay core."""
    values = np.asarray(u, dtype=float)
    return np.column_stack((values, values**2, (1.0 + values) ** 2))


def _summarize(by_variant: dict[str, dict[int, float]], config: dict[str, Any]) -> dict[str, Any]:
    candidate = by_variant["photonic_candidate"]
    medians = {name: float(np.median(list(scores.values()))) for name, scores in by_variant.items()}
    controls: dict[str, Any] = {}
    all_pass = True
    superiority_controls = config.get("superiority_controls", config.get("required_controls", []))
    for name in superiority_controls:
        differences = np.asarray([candidate[seed] - by_variant[name][seed] for seed in sorted(candidate)], dtype=float)
        ci = paired_bootstrap_ci(differences, seed=int(config["bootstrap_seed"]), samples=int(config["bootstrap_samples"]))
        relative_gain = (medians[name] - medians["photonic_candidate"]) / medians[name]
        passed = bool(relative_gain >= float(config["relative_gain_threshold"]) and ci[1] < 0.0)
        controls[name] = {
            "median_validation_nmse": medians[name],
            "relative_gain": float(relative_gain),
            "paired_difference_ci95": [float(ci[0]), float(ci[1])],
            "passed": passed,
        }
        all_pass = all_pass and passed
    candidate_values = np.asarray(list(candidate.values()), dtype=float)
    accuracy_passed = bool(
        medians["photonic_candidate"] <= float(config["median_gate"])
        and int(np.sum(candidate_values <= float(config["robust_seed_threshold"]))) >= int(config["robust_seed_count"])
    )
    return {
        "median_validation_nmse": medians,
        "candidate_accuracy_passed": accuracy_passed,
        "controls": controls,
        "reported_references": {
            name: {
                "median_validation_nmse": medians[name],
                "candidate_relative_penalty": float((medians["photonic_candidate"] - medians[name]) / medians[name]),
            }
            for name in config.get("reported_references", [])
        },
        "all_publication_preconditions_passed": bool(accuracy_passed and all_pass),
    }


def run_preflight(protocol: dict[str, Any], p2_result: dict[str, Any], p3_config: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    benchmark = _benchmark(protocol, tuple(float(value) for value in config["ridge_alphas"]))
    if benchmark.n_test != 0:
        raise PermissionError("P5 preflight must use development data with no test slice")
    n_lags = int(config["n_lags"])
    channel_count = int(config["channel_count"])
    selected_indices = np.asarray(p2_result["channel_ranking"][:channel_count], dtype=int)
    labels = list(p2_result["channel_ranking_labels"][:channel_count])
    physical = dict(p3_config["physical_profiles"][config["physical_profile"]])
    physical.update(config["physical_overrides"])
    by_variant: dict[str, dict[int, float]] = {
        "photonic_candidate": {}, "delayed_input": {}, "same_delay_digital": {}, "no_photonic_core": {}
    }
    rows: list[dict[str, Any]] = []
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        if dataset_sha256(u, target) != protocol["development"]["dataset_sha256"][str(seed)]:
            raise ValueError(f"development dataset commitment mismatch for seed {seed}")
        delayed = delayed_input_features(u, n_lags)
        ideal = coherent_square_law_features(delayed)[:, selected_indices]
        variants = {
            "photonic_candidate": physical_sparse_features(delayed, labels, physical, int(config["parallel_ports"]), int(config["hardware_seed"]) * 1_000_003 + seed),
            "delayed_input": delayed,
            "same_delay_digital": ideal,
            "no_photonic_core": no_photonic_core_features(u),
        }
        for name, features in variants.items():
            result = fast_validation_nmse(features, target, benchmark)
            by_variant[name][seed] = result.validation_nmse
            rows.append({"seed": int(seed), "variant": name, "validation_nmse": result.validation_nmse, "best_alpha": result.best_alpha, "feature_count": result.feature_count})
    summary = _summarize(by_variant, config)
    return {
        "claim_level": "P5 development-only publication preflight; blind suite untouched",
        "development_only": True,
        "test_evaluations": 0,
        "p0_protocol_sha256": protocol["protocol_sha256"],
        "source_sha256": source_tree_sha256(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "rows": rows,
        "summary": summary,
        "candidate_lock_allowed": summary["all_publication_preconditions_passed"],
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
