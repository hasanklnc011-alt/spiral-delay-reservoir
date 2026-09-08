"""Shared benchmark protocol for the active NMSE < 0.05 research track.

Legacy three-ring models remain importable from their explicit modules only; they
are intentionally not re-exported from the package root.
"""

from .config import BenchmarkConfig

__all__ = ["BenchmarkConfig"]
__version__ = "0.1.0"
