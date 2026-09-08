# Implementation

The canonical source snapshot in `archive/canonical-project-records/` retains the Python package, configuration files, test suite, protocol documents, and JSON result records. Its top-level `pyproject.toml` specifies Python `>=3.11`, NumPy `>=2.0`, and Matplotlib `>=3.8`.

Important entry points include:

- `scripts/verify_p0_protocol.py` — checks P0 benchmark/protocol integrity.
- `scripts/run_p1_ideal.py` through `scripts/run_p4_optimization.py` — phase-specific development workflows.
- `scripts/create_p5_candidate_lock.py` — records the candidate lock.
- `scripts/run_p5_blind.py` — locked blind evaluation; **do not re-run** for this archive.
- `p6-physical-validation/` — component and acceptance evidence, including scripts that can require external simulation services.

No script in this archive is asserted to have generated the Blender scene, and no archival-time script execution changed Blender.
