"""Leakage-safe NARMA benchmarks, readouts, baselines, and statistics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import BenchmarkConfig


class NarmaDivergenceError(ValueError):
    """Raised when the recursive NARMA target stops being finite."""


@dataclass(frozen=True)
class Metrics:
    best_alpha: float
    validation_nmse: float
    test_nmse: float
    test_rmse: float
    test_correlation: float
    prediction: np.ndarray
    target: np.ndarray


def generate_narma(n_steps: int, order: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate the canonical generalized NARMA-N sequence.

    The supervised task is features at t -> target y[t+1]. For NARMA-10 this
    reproduces the standard u[t-9] * u[t] convention.
    """
    if order < 1 or n_steps <= order + 1:
        raise ValueError("invalid NARMA dimensions")
    rng = np.random.default_rng(seed)
    u = rng.uniform(0.0, 0.5, size=n_steps)
    y = np.zeros(n_steps)
    for t in range(order, n_steps - 1):
        memory = np.sum(y[t - order + 1 : t + 1])
        with np.errstate(over="ignore", invalid="ignore"):
            next_value = 0.3 * y[t] + 0.05 * y[t] * memory + 1.5 * u[t - order + 1] * u[t] + 0.1
        if not np.isfinite(next_value):
            raise NarmaDivergenceError(
                f"NARMA-{order} diverged for seed {seed} at target index {t + 1}; "
                "the dataset is invalid and must not be clipped or scored"
            )
        y[t + 1] = next_value
    return u, y


def split_slices(config: BenchmarkConfig) -> dict[str, slice]:
    train_start = config.n_washout
    train_end = train_start + config.n_train
    validation_end = train_end + config.n_validation
    test_end = validation_end + config.n_test
    return {
        "train": slice(train_start, train_end),
        "validation": slice(train_end, validation_end),
        "test": slice(validation_end, test_end),
    }


def supervised_alignment(features: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(features) != len(target):
        raise ValueError("feature and target lengths differ")
    return np.asarray(features[:-1], dtype=float), np.asarray(target[1:], dtype=float)


def delayed_input_features(u: np.ndarray, n_lags: int) -> np.ndarray:
    features = np.zeros((len(u), n_lags))
    for lag in range(n_lags):
        if lag == 0:
            features[:, lag] = u
        else:
            features[lag:, lag] = u[:-lag]
    return features


def _fit_standardizer(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    std[~np.isfinite(std) | (std == 0)] = 1.0
    return mean, std


def _ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    xb = np.column_stack((np.ones(len(x)), x))
    penalty = alpha * np.eye(xb.shape[1])
    penalty[0, 0] = 0.0
    return np.linalg.solve(xb.T @ xb + penalty, xb.T @ y)


def _predict(x: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.column_stack((np.ones(len(x)), x)) @ weights


def nmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    variance = float(np.var(y_true))
    return float(np.mean((y_true - y_pred) ** 2) / variance) if variance else float("nan")


def evaluate_features(features: np.ndarray, target: np.ndarray, config: BenchmarkConfig) -> Metrics:
    if not np.all(np.isfinite(features)) or not np.all(np.isfinite(target)):
        nan = np.full(config.n_test, np.nan)
        return Metrics(float("nan"), float("inf"), float("inf"), float("inf"), float("nan"), nan, nan)
    x, y = supervised_alignment(features, target)
    splits = split_slices(config)
    x_train, y_train = x[splits["train"]], y[splits["train"]]
    x_validation, y_validation = x[splits["validation"]], y[splits["validation"]]
    mean, std = _fit_standardizer(x_train)
    x_train_s = (x_train - mean) / std
    x_validation_s = (x_validation - mean) / std
    best_alpha, best_score = None, float("inf")
    for alpha in config.ridge_alphas:
        weights = _ridge_fit(x_train_s, y_train, float(alpha))
        score = nmse(y_validation, _predict(x_validation_s, weights))
        if score < best_score:
            best_alpha, best_score = float(alpha), score

    train_validation = slice(splits["train"].start, splits["validation"].stop)
    x_fit, y_fit = x[train_validation], y[train_validation]
    x_test, y_test = x[splits["test"]], y[splits["test"]]
    mean, std = _fit_standardizer(x_fit)
    weights = _ridge_fit((x_fit - mean) / std, y_fit, float(best_alpha))
    prediction = _predict((x_test - mean) / std, weights)
    correlation = float(np.corrcoef(y_test, prediction)[0, 1]) if np.std(prediction) and np.std(y_test) else float("nan")
    return Metrics(
        best_alpha=float(best_alpha),
        validation_nmse=float(best_score),
        test_nmse=nmse(y_test, prediction),
        test_rmse=float(np.sqrt(np.mean((y_test - prediction) ** 2))),
        test_correlation=correlation,
        prediction=prediction,
        target=y_test,
    )


def validation_nmse(features: np.ndarray, target: np.ndarray, config: BenchmarkConfig) -> tuple[float, float]:
    """Return validation-only score and alpha without touching the test slice."""
    if not np.all(np.isfinite(features)) or not np.all(np.isfinite(target)):
        return float("inf"), float("nan")
    x, y = supervised_alignment(features, target)
    splits = split_slices(config)
    x_train, y_train = x[splits["train"]], y[splits["train"]]
    x_validation, y_validation = x[splits["validation"]], y[splits["validation"]]
    mean, std = _fit_standardizer(x_train)
    x_train_s = (x_train - mean) / std
    x_validation_s = (x_validation - mean) / std
    best_score, best_alpha = float("inf"), float("nan")
    for alpha in config.ridge_alphas:
        weights = _ridge_fit(x_train_s, y_train, float(alpha))
        score = nmse(y_validation, _predict(x_validation_s, weights))
        if score < best_score:
            best_score, best_alpha = score, float(alpha)
    return float(best_score), float(best_alpha)


def mean_baseline(target: np.ndarray, config: BenchmarkConfig) -> Metrics:
    _, y = supervised_alignment(np.zeros((len(target), 1)), target)
    splits = split_slices(config)
    fit_slice = slice(splits["train"].start, splits["validation"].stop)
    y_test = y[splits["test"]]
    prediction = np.full_like(y_test, np.mean(y[fit_slice]))
    return Metrics(float("nan"), float("nan"), nmse(y_test, prediction), float(np.sqrt(np.mean((y_test - prediction) ** 2))), float("nan"), prediction, y_test)


def esn_features(u: np.ndarray, state_dim: int, seed: int, spectral_radius: float = 0.9, leak: float = 0.5, input_scale: float = 0.5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    recurrent = rng.normal(size=(state_dim, state_dim))
    radius = float(np.max(np.abs(np.linalg.eigvals(recurrent))))
    recurrent *= spectral_radius / radius
    input_weights = rng.uniform(-input_scale, input_scale, size=state_dim)
    bias = rng.uniform(-0.1, 0.1, size=state_dim)
    state = np.zeros(state_dim)
    states = np.zeros((len(u), state_dim))
    for idx, value in enumerate(u):
        candidate = np.tanh(recurrent @ state + input_weights * float(value) + bias)
        state = (1.0 - leak) * state + leak * candidate
        states[idx] = state
    return states


def paired_bootstrap_ci(differences: np.ndarray, seed: int = 20260828, samples: int = 10_000) -> tuple[float, float]:
    values = np.asarray(differences, dtype=float)
    if len(values) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(samples, len(values)), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def linear_memory_capacity(features: np.ndarray, u: np.ndarray, config: BenchmarkConfig, max_delay: int = 20) -> dict[str, object]:
    """Jaeger-style linear memory function using the same locked readout splits."""
    capacities = []
    for delay in range(1, max_delay + 1):
        shifted_target = np.zeros(len(u))
        # evaluate_features maps features[t] to target[t+1].
        shifted_target[delay + 1 :] = u[1 : -delay]
        metric = evaluate_features(features, shifted_target, config)
        capacities.append(metric.test_correlation**2 if np.isfinite(metric.test_correlation) else 0.0)
    return {"delays": list(range(1, max_delay + 1)), "capacity_per_delay": capacities, "total_capacity": float(np.sum(capacities))}


def generate_mackey_glass(n_steps: int, seed: int = 11, tau: int = 17) -> np.ndarray:
    """Deterministic discrete integration of the canonical Mackey-Glass DDE."""
    if n_steps <= tau + 1:
        raise ValueError("n_steps must exceed tau")
    rng = np.random.default_rng(seed)
    x = np.full(n_steps + tau + 1, 1.2)
    x[: tau + 1] += rng.normal(0.0, 1e-4, size=tau + 1)
    dt = 0.1
    for idx in range(tau, len(x) - 1):
        delayed = x[idx - tau]
        derivative = 0.2 * delayed / (1.0 + delayed**10) - 0.1 * x[idx]
        x[idx + 1] = x[idx] + dt * derivative
    return x[tau + 1 :]
