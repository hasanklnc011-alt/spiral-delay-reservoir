"""Typed, JSON-serializable experiment configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class RingParams:
    """One energy-normalized, FDTD-calibrated SiN microring."""

    wavelength_m: float = 1.55e-6
    radius_m: float = 10e-6
    group_index: float = 2.1073185917217856
    effective_area_m2: float = 7.378849169903934e-13
    n2_m2_per_w: float = 2.5e-19
    q_int: float = 720.3636278716973
    q_ext: float = 2910.079496528742
    detuning_linewidths: float = 0.0

    @property
    def omega0(self) -> float:
        return 2.0 * np.pi * 299_792_458.0 / self.wavelength_m

    @property
    def circumference_m(self) -> float:
        return 2.0 * np.pi * self.radius_m

    @property
    def q_loaded(self) -> float:
        return 1.0 / (1.0 / self.q_int + 1.0 / self.q_ext)

    @property
    def tau_field_s(self) -> float:
        return 2.0 * self.q_loaded / self.omega0

    @property
    def tau_external_s(self) -> float:
        return 2.0 * self.q_ext / self.omega0

    @property
    def linewidth_rad_s(self) -> float:
        return 1.0 / self.tau_field_s

    @property
    def detuning_rad_s(self) -> float:
        return self.detuning_linewidths * self.linewidth_rad_s

    @property
    def fsr_hz(self) -> float:
        return 299_792_458.0 / (self.group_index * self.circumference_m)

    @property
    def kerr_rad_per_s_j(self) -> float:
        return self.omega0 * 299_792_458.0 * self.n2_m2_per_w / (
            self.group_index**2 * self.circumference_m * self.effective_area_m2
        )


def default_three_rings() -> tuple[RingParams, ...]:
    base = RingParams()
    return (
        RingParams(q_int=0.8 * base.q_int, q_ext=0.8 * base.q_ext, detuning_linewidths=-1.5),
        RingParams(q_int=1.15 * base.q_int, q_ext=1.0e9, detuning_linewidths=0.0),
        RingParams(q_int=1.5 * base.q_int, q_ext=1.0e9, detuning_linewidths=1.5),
    )


@dataclass(frozen=True)
class TopologyParams:
    rings: tuple[RingParams, ...] = field(default_factory=default_three_rings)
    coupling_linewidths: tuple[float, ...] = (0.45, 0.45)
    coupling_phases_rad: tuple[float, ...] = (0.0, 0.0)
    kerr_enabled: bool = True
    kerr_sensitivity_multiplier: float = 1.0

    def __post_init__(self) -> None:
        expected = len(self.rings) - 1
        if not self.rings:
            raise ValueError("at least one ring is required")
        if len(self.coupling_linewidths) != expected or len(self.coupling_phases_rad) != expected:
            raise ValueError("coupling arrays must have n_rings - 1 entries")
        if self.kerr_sensitivity_multiplier < 0:
            raise ValueError("kerr_sensitivity_multiplier cannot be negative")


@dataclass(frozen=True)
class FeedbackParams:
    enabled: bool = False
    strength: float = 0.0
    phase_rad: float = 0.0
    delay_s: float = 0.0
    # Delay line and cavity are separate memory subsystems. DriveConfig.reset_each_symbol
    # clears only the ring state, so isolating intrinsic memory needs this flag too.
    reset_each_symbol: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.strength < 1.0:
            raise ValueError("feedback strength must satisfy 0 <= eta < 1")
        if self.enabled and self.delay_s <= 0:
            raise ValueError("enabled feedback requires a positive delay")


@dataclass(frozen=True)
class DriveConfig:
    symbol_time_s: float = 1.0e-12
    n_virtual: int = 20
    power_bias_w: float = 50e-3
    power_modulation_w: float = 45e-3
    minimum_power_w: float = 0.2e-3
    mask_seed: int = 12
    reset_each_symbol: bool = False
    observation: str = "direct_power"

    def __post_init__(self) -> None:
        if self.symbol_time_s <= 0 or self.n_virtual <= 0:
            raise ValueError("symbol_time_s and n_virtual must be positive")
        if self.observation not in {"direct_power", "coherent_field"}:
            raise ValueError("unknown observation")


@dataclass(frozen=True)
class SolverConfig:
    steps_per_min_lifetime: float = 12.0
    min_substeps_per_node: int = 2
    integrator: str = "rk4"
    divergence_energy_j: float = 1e-6

    def __post_init__(self) -> None:
        if self.integrator not in {"rk4", "euler"}:
            raise ValueError("integrator must be rk4 or euler")
        if self.steps_per_min_lifetime <= 0 or self.min_substeps_per_node < 1:
            raise ValueError("invalid solver resolution")


@dataclass(frozen=True)
class BenchmarkConfig:
    order: int = 10
    n_washout: int = 200
    n_train: int = 1000
    n_validation: int = 400
    n_test: int = 599
    seeds: tuple[int, ...] = (11, 23, 37)
    ridge_alphas: tuple[float, ...] = tuple(float(v) for v in np.logspace(-10, 2, 25))
    esn_state_dim: int = 20

    @property
    def n_total(self) -> int:
        return 1 + self.n_washout + self.n_train + self.n_validation + self.n_test


def dataclass_dict(value: Any) -> dict[str, Any]:
    return asdict(value)


def topology_from_dict(data: dict[str, Any]) -> TopologyParams:
    payload = dict(data)
    payload["rings"] = tuple(RingParams(**item) for item in payload["rings"])
    payload["coupling_linewidths"] = tuple(payload.get("coupling_linewidths", ()))
    payload["coupling_phases_rad"] = tuple(payload.get("coupling_phases_rad", (0.0,) * len(payload["coupling_linewidths"])))
    return TopologyParams(**payload)


def benchmark_from_dict(data: dict[str, Any]) -> BenchmarkConfig:
    payload = dict(data)
    payload["seeds"] = tuple(int(v) for v in payload.get("seeds", (11, 23, 37)))
    if "ridge_alphas" in payload:
        payload["ridge_alphas"] = tuple(float(v) for v in payload["ridge_alphas"])
    return BenchmarkConfig(**payload)


# --- FDTD calibration window -------------------------------------------------
# Measured, not assumed. results/explicit_three_ring_spectrum_best.csv holds 121
# points from 193.623 to 196.023 THz at 20 GHz spacing; ringdown_tau_refined.json
# puts the resonance (Tidy3D ResonanceFinder) at 194.823 THz = 1538.79 nm.
CALIBRATED_BAND_HZ = 2.400e12
CALIBRATED_CENTER_HZ = 194_823_011_804_641.12


def drive_bandwidth_hz(drive: DriveConfig) -> float:
    """Spectral extent of the drive: the waveform changes once per virtual node."""
    return drive.n_virtual / drive.symbol_time_s


def physical_validity(topology: TopologyParams, drive: DriveConfig, band_hz: float = CALIBRATED_BAND_HZ) -> dict[str, Any]:
    """Is this drive inside the band the single-mode TCMT was calibrated over?

    The model carries one resonance amplitude per ring, so it is defensible only
    while the drive's spectral content stays inside the calibrated window (which
    is itself about one FSR wide). This reports the ratios; it does not decide.
    """
    ring = topology.rings[0]
    node_rate = drive_bandwidth_hz(drive)
    symbol_rate = 1.0 / drive.symbol_time_s
    return {
        "node_rate_hz": node_rate,
        "symbol_rate_hz": symbol_rate,
        "calibrated_band_hz": band_hz,
        "fsr_hz": ring.fsr_hz,
        "node_rate_over_band": node_rate / band_hz,
        "node_rate_over_fsr": node_rate / ring.fsr_hz,
        "model_center_hz": ring.omega0 / (2.0 * np.pi),
        "calibrated_center_hz": CALIBRATED_CENTER_HZ,
        "center_offset_fsr": (ring.omega0 / (2.0 * np.pi) - CALIBRATED_CENTER_HZ) / ring.fsr_hz,
        "within_calibrated_band": bool(node_rate <= band_hz),
    }
