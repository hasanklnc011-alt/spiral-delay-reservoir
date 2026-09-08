"""P1 ideal quadratic and coherent square-law hypothesis tests.

Only the frozen P0 development train/validation suite is accepted here.  No test
slice or blind seed is evaluated by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, generate_narma, nmse, split_slices, supervised_alignment
from ..config import BenchmarkConfig
from ..protocol import dataset_sha256, source_tree_sha256


@dataclass(frozen=True)
class ValidationResult:
    validation_nmse: float
    best_alpha: float
    feature_count: int


def full_quadratic_features(delayed: np.ndarray) -> np.ndarray:
    """Linear lags plus every x_i*x_j term for i <= j."""
    values = np.asarray(delayed, dtype=float)
    if values.ndim != 2 or not np.all(np.isfinite(values)):
        raise ValueError("delayed inputs must be a finite 2D array")
    left, right = np.triu_indices(values.shape[1])
    quadratic = values[:, left] * values[:, right]
    return np.column_stack((values, quadratic))


def coherent_square_law_features(fields: np.ndarray, *, include_local_oscillator: bool = True, local_oscillator: float = 1.0) -> np.ndarray:
    """Ideal photodiode bank spanning delayed-field quadratic products.

    Each returned column is a physically interpretable intensity measurement:
    |E_i|^2, |LO+E_i|^2, or |E_i+E_j|^2.  For real field encoding E_i=u[t-i],
    this basis spans the same linear and quadratic feature space as
    ``full_quadratic_features``.  It is an upper bound, not yet a compact PIC.
    """
    values = np.asarray(fields)
    if values.ndim != 2 or not np.all(np.isfinite(values)):
        raise ValueError("fields must be a finite 2D array")
    self_intensity = np.abs(values) ** 2
    channels = [self_intensity]
    if include_local_oscillator:
        if not np.isfinite(local_oscillator) or local_oscillator == 0:
            raise ValueError("local oscillator must be finite and nonzero")
        channels.append(np.abs(local_oscillator + values) ** 2)
    left, right = np.triu_indices(values.shape[1], k=1)
    channels.append(np.abs(values[:, left] + values[:, right]) ** 2)
    return np.column_stack(channels).astype(float, copy=False)


def delayed_fields(
    u: np.ndarray,
    n_lags: int,
    encoding: str,
    *,
    power_bias: float = 1.0,
    power_scale: float = 1.0,
) -> np.ndarray:
    delayed = delayed_input_features(np.asarray(u, dtype=float), n_lags)
    if encoding == "field_u":
        return delayed
    if encoding == "sqrt_power":
        power = power_bias + power_scale * delayed
        if np.any(power < 0):
            raise ValueError("sqrt-power encoding produced negative power")
        return np.sqrt(power)
    raise ValueError(f"unknown field encoding: {encoding}")


def fast_validation_nmse(features: np.ndarray, target: np.ndarray, config: BenchmarkConfig) -> ValidationResult:
    """Validation-only ridge sweep with one symmetric eigendecomposition."""
    if config.n_test != 0:
        raise ValueError("P1 development evaluation requires n_test=0")
    if not np.all(np.isfinite(features)) or not np.all(np.isfinite(target)):
        raise ValueError("features and target must be finite")
    x, y = supervised_alignment(features, target)
    slices = split_slices(config)
    x_train, y_train = x[slices["train"]], y[slices["train"]]
    x_validation, y_validation = x[slices["validation"]], y[slices["validation"]]

    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    std[~np.isfinite(std) | (std == 0)] = 1.0
    x_train = (x_train - mean) / std
    x_validation = (x_validation - mean) / std
    intercept = float(np.mean(y_train))
    centered_target = y_train - intercept

    gram = x_train.T @ x_train
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    eigenvalues = np.maximum(eigenvalues, 0.0)
    projected_rhs = eigenvectors.T @ (x_train.T @ centered_target)
    best_score, best_alpha = float("inf"), float("nan")
    for alpha in config.ridge_alphas:
        weights = eigenvectors @ (projected_rhs / (eigenvalues + float(alpha)))
        prediction = intercept + x_validation @ weights
        score = nmse(y_validation, prediction)
        if score < best_score:
            best_score, best_alpha = float(score), float(alpha)
    return ValidationResult(best_score, best_alpha, int(features.shape[1]))


def _benchmark_from_protocol(protocol: dict[str, Any], ridge_alphas: tuple[float, ...]) -> BenchmarkConfig:
    suite = protocol["development"]
    split = suite["split"]
    if int(split["test"]) != 0:
        raise ValueError("P0 development suite unexpectedly contains a test slice")
    return BenchmarkConfig(
        order=int(protocol["task"]["order"]),
        n_washout=int(split["washout"]),
        n_train=int(split["train"]),
        n_validation=int(split["validation"]),
        n_test=0,
        seeds=tuple(int(seed) for seed in suite["seeds"]),
        ridge_alphas=ridge_alphas,
    )


def run_development(protocol: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    n_lags = int(config["n_lags"])
    ridge_alphas = tuple(float(value) for value in config["ridge_alphas"])
    benchmark = _benchmark_from_protocol(protocol, ridge_alphas)
    blind = {int(seed) for seed in protocol["publication_blind"]["seeds"]}
    if blind.intersection(benchmark.seeds):
        raise PermissionError("P1 development config touches a reserved blind seed")

    rows: list[dict[str, Any]] = []
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        expected = protocol["development"]["dataset_sha256"][str(seed)]
        if dataset_sha256(u, target) != expected:
            raise ValueError(f"development dataset commitment mismatch for seed {seed}")
        delayed = delayed_input_features(u, n_lags)
        variants = {
            "linear_lag20": delayed,
            "full_quadratic_oracle": full_quadratic_features(delayed),
            "coherent_field_u": coherent_square_law_features(delayed_fields(u, n_lags, "field_u")),
            "coherent_field_u_no_lo": coherent_square_law_features(delayed_fields(u, n_lags, "field_u"), include_local_oscillator=False),
            "coherent_sqrt_power": coherent_square_law_features(
                delayed_fields(
                    u,
                    n_lags,
                    "sqrt_power",
                    power_bias=float(config["sqrt_power"]["bias"]),
                    power_scale=float(config["sqrt_power"]["scale"]),
                )
            ),
        }
        for name, features in variants.items():
            result = fast_validation_nmse(features, target, benchmark)
            rows.append({
                "seed": seed,
                "variant": name,
                "validation_nmse": result.validation_nmse,
                "best_alpha": result.best_alpha,
                "feature_count": result.feature_count,
            })

    names = sorted({row["variant"] for row in rows})
    medians = {
        name: float(np.median([row["validation_nmse"] for row in rows if row["variant"] == name]))
        for name in names
    }
    gate = float(protocol["development"]["gate"]["threshold"])
    return {
        "claim_level": "ideal-feature upper bound; not a physical PIC result",
        "p0_protocol_sha256": protocol["protocol_sha256"],
        "source_sha256": source_tree_sha256(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "development_only": True,
        "test_evaluations": 0,
        "n_lags": n_lags,
        "rows": rows,
        "median_validation_nmse": medians,
        "gate_threshold": gate,
        "p1_gate_passed": bool(medians["coherent_field_u"] <= gate),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
