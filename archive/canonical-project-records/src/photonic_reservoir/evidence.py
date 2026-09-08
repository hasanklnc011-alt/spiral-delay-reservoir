"""LEGACY: inventory for the old Tidy3D evidence artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


EVIDENCE_FILES = (
    "results/ringdown_tau_refined.json",
    "results/time_domain_memory_metrics_refined_w800_h400_r10_memory_t1ps.json",
    "results/fdtd_vs_tcmt_summary_w800_h400_r10_memory_t1ps.json",
    "results/explicit_three_ring_best_summary.json",
    "results/reservoir_narma3_explicit3ring_summary.json",
    "results/explicit_three_ring_spectrum_best.csv",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(source_root: Path) -> dict[str, Any]:
    rows = []
    for relative in EVIDENCE_FILES:
        path = source_root / relative
        rows.append({
            "relative_path": relative,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
            "sha256": sha256_file(path) if path.exists() else None,
        })
    return {
        "source_root": str(source_root),
        "source_policy": "read-only",
        "claim_correction": "The three-ring NARMA-3 metric is produced by an FDTD-spectrum-fitted TCMT surrogate, not a direct temporal three-ring FDTD benchmark.",
        "files": rows,
    }


def write_inventory(source_root: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(inventory(source_root), indent=2), encoding="utf-8")
