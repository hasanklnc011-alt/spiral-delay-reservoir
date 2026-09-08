"""LEGACY: three-ring TCMT model retained only for reproducibility."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import DriveConfig, FeedbackParams, SolverConfig, TopologyParams


@dataclass(frozen=True)
class SimulationResult:
    features: np.ndarray
    through_field: np.ndarray
    cavity_energy_j: np.ndarray
    mask: np.ndarray
    dt_s: float
    substeps_per_node: int
    diverged: bool
    metadata: dict[str, float | int | str | bool]


def make_mask(n_virtual: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).uniform(-1.0, 1.0, size=n_virtual)


def encoded_power(u: float, mask: float, drive: DriveConfig) -> float:
    centered = 4.0 * float(u) - 1.0
    return max(drive.minimum_power_w, drive.power_bias_w + drive.power_modulation_w * centered * float(mask))


def _arrays(topology: TopologyParams) -> tuple[np.ndarray, ...]:
    tau = np.array([ring.tau_field_s for ring in topology.rings])
    tau_ext = np.array([ring.tau_external_s for ring in topology.rings])
    detuning = np.array([ring.detuning_rad_s for ring in topology.rings])
    kerr = np.array([ring.kerr_rad_per_s_j for ring in topology.rings])
    reference_linewidth = topology.rings[0].linewidth_rad_s
    coupling = np.asarray(topology.coupling_linewidths) * reference_linewidth
    phases = np.asarray(topology.coupling_phases_rad)
    return tau, tau_ext, detuning, kerr, coupling, phases


def rhs(a: np.ndarray, drive_field: complex, topology: TopologyParams) -> np.ndarray:
    tau, tau_ext, detuning, kerr, coupling, phases = _arrays(topology)
    da = (-1.0 / tau - 1j * detuning) * a
    da[0] += np.sqrt(2.0 / tau_ext[0]) * drive_field
    for idx, rate in enumerate(coupling):
        forward = rate * np.exp(1j * phases[idx])
        da[idx] += -1j * forward * a[idx + 1]
        da[idx + 1] += -1j * np.conj(forward) * a[idx]
    if topology.kerr_enabled:
        da += -1j * topology.kerr_sensitivity_multiplier * kerr * np.abs(a) ** 2 * a
    return da


def _step(a: np.ndarray, drive_field: complex, dt: float, topology: TopologyParams, integrator: str) -> np.ndarray:
    if integrator == "euler":
        return a + dt * rhs(a, drive_field, topology)
    k1 = rhs(a, drive_field, topology)
    k2 = rhs(a + 0.5 * dt * k1, drive_field, topology)
    k3 = rhs(a + 0.5 * dt * k2, drive_field, topology)
    k4 = rhs(a + dt * k3, drive_field, topology)
    return a + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def _prepared_rhs(a: np.ndarray, drive_field: complex, linear: np.ndarray, drive_coefficient: float, links: tuple[complex, ...], kerr: np.ndarray | None) -> np.ndarray:
    da = linear * a
    da[0] += drive_coefficient * drive_field
    for idx, link in enumerate(links):
        da[idx] += -1j * link * a[idx + 1]
        da[idx + 1] += -1j * np.conj(link) * a[idx]
    if kerr is not None:
        da += -1j * kerr * np.abs(a) ** 2 * a
    return da


def _prepared_step(a: np.ndarray, drive_field: complex, dt: float, integrator: str, linear: np.ndarray, drive_coefficient: float, links: tuple[complex, ...], kerr: np.ndarray | None) -> np.ndarray:
    if integrator == "euler":
        return a + dt * _prepared_rhs(a, drive_field, linear, drive_coefficient, links, kerr)
    k1 = _prepared_rhs(a, drive_field, linear, drive_coefficient, links, kerr)
    k2 = _prepared_rhs(a + 0.5 * dt * k1, drive_field, linear, drive_coefficient, links, kerr)
    k3 = _prepared_rhs(a + 0.5 * dt * k2, drive_field, linear, drive_coefficient, links, kerr)
    k4 = _prepared_rhs(a + dt * k3, drive_field, linear, drive_coefficient, links, kerr)
    return a + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def through_field(a: np.ndarray, drive_field: complex, topology: TopologyParams) -> complex:
    return drive_field - np.sqrt(2.0 / topology.rings[0].tau_external_s) * a[0]


class _DelayHistory:
    def __init__(self, dt_s: float) -> None:
        self.dt_s = dt_s
        self.values: list[complex] = []
        self.discarded = 0

    def append(self, value: complex) -> None:
        self.values.append(value)

    def clear(self) -> None:
        """Drop the stored field history but keep absolute-time indexing valid."""
        self.discarded += len(self.values)
        self.values = []

    def interpolate(self, time_s: float) -> complex:
        if not self.values or time_s < 0.0:
            return 0.0j
        position = time_s / self.dt_s - self.discarded
        if position < 0.0:
            return 0.0j
        lower = int(np.floor(position))
        if lower >= len(self.values) - 1:
            return self.values[-1]
        weight = position - lower
        return (1.0 - weight) * self.values[lower] + weight * self.values[lower + 1]


def simulate(input_signal: np.ndarray, topology: TopologyParams, drive: DriveConfig, solver: SolverConfig = SolverConfig(), feedback: FeedbackParams = FeedbackParams()) -> SimulationResult:
    """Simulate time-multiplexed rings; delay feedback uses field interpolation."""
    input_signal = np.asarray(input_signal, dtype=float)
    if input_signal.ndim != 1 or not np.all(np.isfinite(input_signal)):
        raise ValueError("input_signal must be a finite one-dimensional array")
    mask = make_mask(drive.n_virtual, drive.mask_seed)
    node_time = drive.symbol_time_s / drive.n_virtual
    min_lifetime = min(ring.tau_field_s for ring in topology.rings)
    substeps = max(solver.min_substeps_per_node, int(np.ceil(node_time / (min_lifetime / solver.steps_per_min_lifetime))))
    dt = node_time / substeps
    n_rings = len(topology.rings)
    n_features = drive.n_virtual if drive.observation == "direct_power" else 2 * drive.n_virtual
    features = np.zeros((len(input_signal), n_features))
    through = np.zeros((len(input_signal), drive.n_virtual), dtype=complex)
    energy = np.zeros((len(input_signal), drive.n_virtual, n_rings))
    state = np.zeros(n_rings, dtype=complex)
    tau, tau_ext, detuning, physical_kerr, coupling, phases = _arrays(topology)
    linear = -1.0 / tau - 1j * detuning
    drive_coefficient = float(np.sqrt(2.0 / tau_ext[0]))
    links = tuple(complex(rate * np.exp(1j * phase)) for rate, phase in zip(coupling, phases))
    kerr = topology.kerr_sensitivity_multiplier * physical_kerr if topology.kerr_enabled else None
    history = _DelayHistory(dt)
    time_s = 0.0
    diverged = False

    for symbol_idx, u_value in enumerate(input_signal):
        if drive.reset_each_symbol:
            state.fill(0.0)
        if feedback.reset_each_symbol:
            history.clear()
        for node_idx, mask_value in enumerate(mask):
            external_field = complex(np.sqrt(encoded_power(float(u_value), float(mask_value), drive)))
            for _ in range(substeps):
                delayed = history.interpolate(time_s - feedback.delay_s) if feedback.enabled else 0.0j
                drive_field = external_field + feedback.strength * np.exp(1j * feedback.phase_rad) * delayed
                state = _prepared_step(state, drive_field, dt, solver.integrator, linear, drive_coefficient, links, kerr)
                current_output = through_field(state, drive_field, topology)
                history.append(current_output)
                time_s += dt
                if not np.all(np.isfinite(state)) or float(np.max(np.abs(state) ** 2)) > solver.divergence_energy_j:
                    diverged = True
                    break
            if diverged:
                features[symbol_idx:] = np.nan
                through[symbol_idx:] = np.nan + 1j * np.nan
                energy[symbol_idx:] = np.nan
                break
            through[symbol_idx, node_idx] = current_output
            energy[symbol_idx, node_idx] = np.abs(state) ** 2
            if drive.observation == "direct_power":
                features[symbol_idx, node_idx] = float(np.abs(current_output) ** 2)
            else:
                features[symbol_idx, 2 * node_idx : 2 * node_idx + 2] = (current_output.real, current_output.imag)
        if diverged:
            break

    return SimulationResult(features, through, energy, mask, dt, substeps, diverged, {
        "n_rings": n_rings, "n_symbols": len(input_signal), "n_virtual": drive.n_virtual,
        "observation": drive.observation, "kerr_enabled": topology.kerr_enabled,
        "kerr_sensitivity_multiplier": topology.kerr_sensitivity_multiplier, "feedback_enabled": feedback.enabled,
    })


def linear_s21(topology: TopologyParams, frequency_offsets_hz: np.ndarray) -> np.ndarray:
    """Analytic complex through-port response of the linearized topology."""
    tau, tau_ext, detuning, _, coupling, phases = _arrays(topology)
    b = np.zeros(len(topology.rings), dtype=complex)
    b[0] = np.sqrt(2.0 / tau_ext[0])
    outputs = np.zeros(len(frequency_offsets_hz), dtype=complex)
    for out_idx, offset_hz in enumerate(np.asarray(frequency_offsets_hz, dtype=float)):
        matrix = np.diag(1.0 / tau + 1j * (detuning - 2.0 * np.pi * offset_hz)).astype(complex)
        for idx, rate in enumerate(coupling):
            forward = rate * np.exp(1j * phases[idx])
            matrix[idx, idx + 1] = 1j * forward
            matrix[idx + 1, idx] = 1j * np.conj(forward)
        fields = np.linalg.solve(matrix, b)
        outputs[out_idx] = 1.0 - np.sqrt(2.0 / tau_ext[0]) * fields[0]
    return outputs
