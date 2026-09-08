"""Development-only P2 screening for constrained coherent readout channels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, generate_narma, split_slices, supervised_alignment
from ..config import BenchmarkConfig
from ..p1_coherent_delay.ideal import coherent_square_law_features, fast_validation_nmse
from ..protocol import dataset_sha256, source_tree_sha256


def channel_labels(n_lags: int, include_local_oscillator: bool = True) -> list[str]:
    labels = [f"self:{lag}" for lag in range(n_lags)]
    if include_local_oscillator:
        labels.extend(f"lo:{lag}" for lag in range(n_lags))
    labels.extend(f"pair:{left},{right}" for left in range(n_lags) for right in range(left + 1, n_lags))
    return labels


def normalized_binary_masks(n_channels: int, n_lags: int, seed: int) -> np.ndarray:
    """Unit-norm real masks implementable with 0/pi phase signs and equal taps."""
    if n_channels < 1 or n_lags < 1:
        raise ValueError("mask dimensions must be positive")
    rng = np.random.default_rng(seed)
    masks = rng.choice((-1.0, 1.0), size=(n_channels, n_lags))
    return masks / np.sqrt(float(n_lags))


def random_mzi_intensities(delayed_fields: np.ndarray, masks: np.ndarray, local_oscillator: float = 1.0) -> np.ndarray:
    fields = np.asarray(delayed_fields, dtype=float)
    weights = np.asarray(masks, dtype=float)
    if fields.ndim != 2 or weights.ndim != 2 or fields.shape[1] != weights.shape[1]:
        raise ValueError("field and mask dimensions do not match")
    if not np.all(np.isfinite(fields)) or not np.all(np.isfinite(weights)):
        raise ValueError("field and mask values must be finite")
    return np.abs(local_oscillator + fields @ weights.T) ** 2


def _benchmark(protocol: dict[str, Any], ridge_alphas: tuple[float, ...]) -> BenchmarkConfig:
    suite = protocol["development"]
    split = suite["split"]
    if int(split["test"]) != 0:
        raise ValueError("P2 requires the development suite with n_test=0")
    blind = {int(seed) for seed in protocol["publication_blind"]["seeds"]}
    seeds = tuple(int(seed) for seed in suite["seeds"])
    if blind.intersection(seeds):
        raise PermissionError("P2 development suite overlaps blind seeds")
    return BenchmarkConfig(
        order=int(protocol["task"]["order"]),
        n_washout=int(split["washout"]),
        n_train=int(split["train"]),
        n_validation=int(split["validation"]),
        n_test=0,
        seeds=seeds,
        ridge_alphas=ridge_alphas,
    )


def _development_data(protocol: dict[str, Any], benchmark: BenchmarkConfig, n_lags: int) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    data = {}
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        if dataset_sha256(u, target) != protocol["development"]["dataset_sha256"][str(seed)]:
            raise ValueError(f"development dataset commitment mismatch for seed {seed}")
        delayed = delayed_input_features(u, n_lags)
        primitive = coherent_square_law_features(delayed)
        data[seed] = (delayed, primitive, target)
    return data


def rank_primitive_channels_train_only(
    data: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]],
    benchmark: BenchmarkConfig,
    ridge_alpha: float,
) -> np.ndarray:
    """Aggregate standardized full-model coefficients using training slices only."""
    coefficients = []
    train_slice = split_slices(benchmark)["train"]
    for _, primitive, target in data.values():
        x, y = supervised_alignment(primitive, target)
        x_train, y_train = x[train_slice], y[train_slice]
        mean = np.mean(x_train, axis=0)
        std = np.std(x_train, axis=0)
        std[~np.isfinite(std) | (std == 0)] = 1.0
        x_train = (x_train - mean) / std
        y_train = y_train - np.mean(y_train)
        gram = x_train.T @ x_train
        weights = np.linalg.solve(gram + float(ridge_alpha) * np.eye(gram.shape[0]), x_train.T @ y_train)
        coefficients.append(np.abs(weights))
    importance = np.median(np.vstack(coefficients), axis=0)
    return np.argsort(-importance, kind="stable")


def _summarize(scores: list[dict[str, Any]], threshold: float, robust_threshold: float, robust_count: int) -> dict[str, Any]:
    values = np.asarray([row["validation_nmse"] for row in scores], dtype=float)
    median = float(np.median(values))
    count = int(np.sum(values <= robust_threshold))
    return {
        "median_validation_nmse": median,
        "min_validation_nmse": float(np.min(values)),
        "max_validation_nmse": float(np.max(values)),
        "seeds_at_or_below_robust_threshold": count,
        "passed": bool(median <= threshold and count >= robust_count),
    }


def run_screen(protocol: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    n_lags = int(config["n_lags"])
    budgets = tuple(sorted({int(value) for value in config["channel_budgets"]}))
    ridge_alphas = tuple(float(value) for value in config["ridge_alphas"])
    benchmark = _benchmark(protocol, ridge_alphas)
    data = _development_data(protocol, benchmark, n_lags)
    total_primitive = coherent_square_law_features(next(iter(data.values()))[0]).shape[1]
    if budgets[-1] > total_primitive:
        raise ValueError("channel budget exceeds primitive coherent basis")

    ranking = rank_primitive_channels_train_only(data, benchmark, float(config["ranking_alpha"]))
    threshold = float(config["median_gate"])
    robust_threshold = float(config["robust_seed_threshold"])
    robust_count = int(config["robust_seed_count"])
    candidates: list[dict[str, Any]] = []

    for budget in budgets:
        selected = ranking[:budget]
        scores = []
        for seed, (_, primitive, target) in data.items():
            result = fast_validation_nmse(primitive[:, selected], target, benchmark)
            scores.append({"seed": seed, "validation_nmse": result.validation_nmse, "best_alpha": result.best_alpha})
        candidates.append({
            "family": "sparse_primitive_pd",
            "channels": budget,
            "parallel_ports": budget,
            "time_multiplex_steps": 1,
            "mask_seed": None,
            "summary": _summarize(scores, threshold, robust_threshold, robust_count),
            "scores": scores,
            "selected_channel_indices": [int(index) for index in selected],
        })
        candidates.append({
            "family": "single_port_sparse_time_multiplex",
            "channels": budget,
            "parallel_ports": 1,
            "time_multiplex_steps": budget,
            "mask_seed": None,
            "summary": _summarize(scores, threshold, robust_threshold, robust_count),
            "scores": scores,
            "selected_channel_indices": [int(index) for index in selected],
        })

    for mask_seed in (int(value) for value in config["random_mask_seeds"]):
        for budget in budgets:
            masks = normalized_binary_masks(budget, n_lags, mask_seed)
            scores = []
            for seed, (delayed, _, target) in data.items():
                features = random_mzi_intensities(delayed, masks, float(config["local_oscillator"]))
                result = fast_validation_nmse(features, target, benchmark)
                scores.append({"seed": seed, "validation_nmse": result.validation_nmse, "best_alpha": result.best_alpha})
            summary = _summarize(scores, threshold, robust_threshold, robust_count)
            common = {
                "channels": budget,
                "mask_seed": mask_seed,
                "summary": summary,
                "scores": scores,
            }
            candidates.append({
                "family": "parallel_random_mzi_pd",
                "parallel_ports": budget,
                "time_multiplex_steps": 1,
                **common,
            })
            candidates.append({
                "family": "single_port_time_multiplex",
                "parallel_ports": 1,
                "time_multiplex_steps": budget,
                **common,
            })

    passing = [candidate for candidate in candidates if candidate["summary"]["passed"]]
    family_order = {"single_port_sparse_time_multiplex": 0, "sparse_primitive_pd": 1, "single_port_time_multiplex": 2, "parallel_random_mzi_pd": 3}
    selected = min(
        passing,
        key=lambda item: (item["channels"], item["parallel_ports"], item["time_multiplex_steps"], family_order[item["family"]], item["summary"]["median_validation_nmse"]),
    ) if passing else None
    labels = channel_labels(n_lags)
    selected_details = None
    if selected is not None:
        selected_details = {key: value for key, value in selected.items() if key != "scores"}
        if selected["family"] in {"sparse_primitive_pd", "single_port_sparse_time_multiplex"}:
            selected_details["selected_channel_labels"] = [labels[index] for index in selected["selected_channel_indices"]]

    return {
        "claim_level": "ideal lossless architecture screen; not yet P3 realistic",
        "development_only": True,
        "test_evaluations": 0,
        "p0_protocol_sha256": protocol["protocol_sha256"],
        "source_sha256": source_tree_sha256(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "n_lags": n_lags,
        "max_delay_symbols": n_lags - 1,
        "total_primitive_channels": total_primitive,
        "channel_ranking": [int(index) for index in ranking],
        "channel_ranking_labels": [labels[index] for index in ranking],
        "candidates": candidates,
        "selected_candidate": selected_details,
        "p2_gate_passed": selected is not None,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
