# artifacts/blender/

Visualization assets for the P6 architecture. **None of this is a fabrication
layout, a GDS source, or experimental geometry.**

## `scenes/mcp.blend` (Git LFS)

The author's presentation-scene file, carried over unmodified from the source
workspace. **This file is near-empty** (0 objects / 0 cameras / 0 lights): the
hand-built architecture geometry lived in a live Blender session that was never
saved to a file with a path, so it is not contained here. Its SHA-256 matches the
source workspace copy at archival time.

> To preserve the hand-built scene properly: open it in Blender, rebuild or
> re-import the geometry, and `Save As` over this file.

## `../../docs/figures/p6_overview_session_render.png`

A render **captured from the author's live Blender session**. It depicts the P6
architecture — spiral delay (L ≈ 142.4 mm, 93.2 turns, 5 µm pitch, Si
343 × 180 nm), 20 tap markers, a 3-slot electro-optic block, 10 PD/TIA receiver
branches, an LO + static phase-trim rail, and the label "P6: NOT PHYSICALLY
ACCEPTED". The numbers on it are consistent with
`p6-physical-validation/layout/` and the P4/P5 records. Its association with the
on-disk `mcp.blend` is **unverified** because the session had no saved filepath.

## `build_spiral_reference.py` + `scenes/spiral-reference-from-centerline.blend`

A **data-derived** reference model built directly from
`p6-physical-validation/layout/spiral-centerline-v1.csv` and
`.../runs/g2-spiral-layout-result-v1.json`. It reconstructs the accepted spiral
centerline as a bevelled curve, places the 20 tap markers at their exact
`(x, y)` coordinates, and renders a top-orthographic and a perspective view:

- `../../docs/figures/blender_spiral_top.png`
- `../../docs/figures/blender_spiral_perspective.png`

The waveguide bevel width is visually exaggerated (~3×) for legibility; the
centerline path, turn count, bounding box and tap positions are exact. Rebuild:

```bash
"<blender>/blender.exe" --background --factory-startup \
    --python artifacts/blender/build_spiral_reference.py
```

## Consistency check against the layout evidence

| Quantity | Layout record (`g2-spiral-layout-result-v1.json`) | Reference model |
|---|---|---|
| Centerline length | 142 400.61 µm | from CSV polyline (same source) |
| Pitch | 5.0 µm | 5.0 µm |
| Minimum curvature radius | 10.0 µm | preserved (curve follows CSV) |
| Turns | 93.23 | 93.23 |
| Die bounding box | 982.34 × 982.34 µm | 0.982 × 0.982 mm |
| Taps | 20, on the centerline | 20, at exact `(x, y)` |

All render PNGs live in [`../../docs/figures/`](../../docs/figures/) (they are
referenced from the README and `docs/`); this folder holds only the `.blend`
files and the build script.
