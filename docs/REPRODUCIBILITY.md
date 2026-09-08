# Reproducibility

1. Clone the repository and inspect `provenance/file_manifest.csv`.
2. Review the source snapshot under `archive/canonical-project-records/`.
3. Use Python 3.11+ with the dependencies declared in its `pyproject.toml`.
4. Set `PYTHONPATH` to the archived `src` directory and run `python scripts/verify_p0_protocol.py` from the source snapshot.
5. Run the test suite only after reviewing phase documentation and external-service requirements.
6. Do not re-run P5 blind evaluation: the source record explicitly locks that result.
7. Open `blender/scenes/mcp.blend` in a compatible Blender version for inspection. Treat all geometry as presentation-level unless independently verified.
