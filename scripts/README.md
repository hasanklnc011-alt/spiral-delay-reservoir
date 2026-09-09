# Scripts

Live research scripts. Run from the repository root with
`PYTHONPATH` pointing at `src/`:

```bash
export PYTHONPATH="$PWD/src"     # Windows: $env:PYTHONPATH="$PWD\src"
```

| Script | Purpose | Safe to run? |
|---|---|---|
| `verify_p0_protocol.py` | Re-check P0 benchmark/protocol integrity (20 dataset commitments; expects `blind_test_authorized: false`) | **Yes** |
| `run_p1_ideal.py` | P1 ideal coherent-delay + square-law model, development data only | **Yes** |
| `run_p2_screen.py` | P2 architecture / feature-budget screen, development data only | **Yes** |
| `run_p3_screen.py` | P3 realistic-physics system model, development data only | **Yes** |
| `run_p4_optimization.py` | P4 robust optimization over hardware × data seeds, development data only | **Yes** |
| `run_p5_preflight.py` | P5 development-only publication preflight | **Yes** |
| `create_p5_candidate_lock.py` | Write the P5 candidate lock (config + source hashes) | Only if you intend to (re)lock |
| `run_p5_blind.py` | **Locked one-shot blind evaluation** | **NO** — see below |
| `make_figures.py` | Regenerate `docs/figures/fig*.png` from committed result records | **Yes** |
| `make_animation_gif.py` | Render `docs/figures/system-animation.gif` (the README animation) | **Yes** |

## Do not run `run_p5_blind.py`

`p5-publication/runs/blind-v2.json` is the authorized, immutable output of the
single permitted blind evaluation. The protocol treats a second blind run as
invalid, and the candidate-lock guard is designed to refuse casual re-runs. A new
hypothesis needs a **new protocol version and a new disjoint blind suite**, not a
re-run of this one. See [`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md).

Default argparse paths in the `run_p*.py` scripts are repository-root-relative
(e.g. `p2-architecture/runs/screen-v4-pareto.json`); run them from the repo root.
