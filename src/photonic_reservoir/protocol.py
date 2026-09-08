"""P0 benchmark commitments and the blind-test authorization gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .benchmark import NarmaDivergenceError, generate_narma


DEFAULT_PROTOCOL_PATH = Path(__file__).resolve().parents[2] / "configs" / "p0_narma10_protocol.json"


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def protocol_sha256(protocol: dict[str, Any]) -> str:
    unsigned = dict(protocol)
    unsigned.pop("protocol_sha256", None)
    return canonical_sha256(unsigned)


def dataset_sha256(u: np.ndarray, target: np.ndarray) -> str:
    """Commit to exact float64 inputs and targets, including array shapes."""
    digest = hashlib.sha256()
    for name, values in (("u", u), ("target", target)):
        array = np.ascontiguousarray(values, dtype="<f8")
        digest.update(name.encode("ascii"))
        digest.update(json.dumps(list(array.shape)).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def source_tree_sha256(package_path: Path | None = None) -> str:
    package = package_path or Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for path in sorted(package.rglob("*.py")):
        digest.update(path.relative_to(package).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _verify_suite(name: str, suite: dict[str, Any], order: int) -> list[dict[str, Any]]:
    split = suite["split"]
    n_total = 1 + sum(int(split[key]) for key in ("washout", "train", "validation", "test"))
    commitments = suite["dataset_sha256"]
    rows: list[dict[str, Any]] = []
    for seed in suite["seeds"]:
        u, target = generate_narma(n_total, order, int(seed))
        actual = dataset_sha256(u, target)
        expected = commitments[str(seed)]
        if actual != expected:
            raise ValueError(f"{name} seed {seed} dataset commitment mismatch")
        rows.append({"suite": name, "seed": int(seed), "n_total": n_total, "sha256": actual})
    return rows


def verify_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    expected_digest = protocol_sha256(protocol)
    if protocol.get("protocol_sha256") != expected_digest:
        raise ValueError("protocol SHA-256 mismatch")
    if protocol.get("status") != "frozen":
        raise ValueError("benchmark protocol is not frozen")

    development = protocol["development"]
    blind = protocol["publication_blind"]
    development_seeds = {int(seed) for seed in development["seeds"]}
    blind_seeds = {int(seed) for seed in blind["seeds"]}
    if development_seeds & blind_seeds:
        raise ValueError("development and blind seed suites overlap")
    if len(blind_seeds) != 10:
        raise ValueError("blind publication suite must contain exactly 10 unique seeds")
    invalid_seeds = {int(item["seed"]) for item in protocol.get("rejected_datasets", [])}
    if invalid_seeds & (development_seeds | blind_seeds):
        raise ValueError("a rejected seed appears in an active suite")

    order = int(protocol["task"]["order"])
    rows = _verify_suite("development", development, order)
    rows.extend(_verify_suite("publication_blind", blind, order))
    for item in protocol.get("rejected_datasets", []):
        split = item["split"]
        n_total = 1 + sum(int(split[key]) for key in ("washout", "train", "validation", "test"))
        try:
            generate_narma(n_total, order, int(item["seed"]))
        except NarmaDivergenceError:
            continue
        raise ValueError(f"rejected seed {item['seed']} no longer reproduces its divergence")
    return {"protocol_id": protocol["protocol_id"], "protocol_sha256": expected_digest, "datasets_verified": len(rows)}


def load_and_verify_protocol(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = json.loads(path.read_text(encoding="utf-8"))
    return protocol, verify_protocol(protocol)


def require_blind_authorization(protocol: dict[str, Any], lock_path: Path) -> dict[str, Any]:
    """Reject blind scoring until an immutable candidate lock is present."""
    if not lock_path.is_file():
        raise PermissionError("blind test is sealed: candidate lock is missing")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("status") != "candidate_locked":
        raise PermissionError("blind test is sealed: candidate is not locked")
    if lock.get("protocol_sha256") != protocol["protocol_sha256"]:
        raise PermissionError("blind test is sealed: lock references another protocol")
    for key in ("candidate_config_sha256", "source_sha256"):
        value = lock.get(key, "")
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise PermissionError(f"blind test is sealed: invalid {key}")
    if not lock.get("locked_utc"):
        raise PermissionError("blind test is sealed: lock timestamp is missing")
    return lock


def guard_reserved_blind_seeds(
    seeds: tuple[int, ...],
    candidate_lock_path: Path | None = None,
    candidate_config_sha256: str | None = None,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    """Seal every main experiment that touches a reserved blind seed."""
    protocol, _ = load_and_verify_protocol(protocol_path)
    reserved = {int(seed) for seed in protocol["publication_blind"]["seeds"]}
    if reserved.intersection(int(seed) for seed in seeds):
        if candidate_lock_path is None:
            raise PermissionError("blind test is sealed: --candidate-lock is required")
        lock = require_blind_authorization(protocol, candidate_lock_path)
        if candidate_config_sha256 is None:
            raise PermissionError("blind test is sealed: running config hash is missing")
        if lock["candidate_config_sha256"] != candidate_config_sha256:
            raise PermissionError("blind test is sealed: running config does not match candidate lock")
        if lock["source_sha256"] != source_tree_sha256():
            raise PermissionError("blind test is sealed: running source does not match candidate lock")
