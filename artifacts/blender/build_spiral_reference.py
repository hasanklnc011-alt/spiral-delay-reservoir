"""Build a data-derived Blender reference model of the P6 spiral delay line.

This script reconstructs the geometry *from the committed layout evidence*
(`p6-physical-validation/layout/spiral-centerline-v1.csv` and
`p6-physical-validation/runs/g2-spiral-layout-result-v1.json`). It is a
verification/visualisation aid, not the presentation scene the author built by
hand (`artifacts/blender/scenes/mcp.blend`).

Run headless from the repository root:

    "<blender>/blender.exe" --background --factory-startup \
        --python artifacts/blender/build_spiral_reference.py

Outputs:
    artifacts/blender/scenes/spiral-reference-from-centerline.blend
    docs/figures/blender_spiral_top.png
    docs/figures/blender_spiral_perspective.png
"""
import csv
import json
import math
from pathlib import Path

import bpy
import mathutils

ROOT = Path(bpy.path.abspath("//")) if bpy.data.filepath else Path.cwd()
# When run with --background from the repo root, cwd is the repo root.
REPO = Path.cwd()
CSV = REPO / "p6-physical-validation" / "layout" / "spiral-centerline-v1.csv"
G2 = REPO / "p6-physical-validation" / "runs" / "g2-spiral-layout-result-v1.json"
SCENES = REPO / "artifacts" / "blender" / "scenes"
FIGS = REPO / "docs" / "figures"

# --- clean scene -------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.unit_settings.system = "METRIC"
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.03, 0.04, 1.0)

# --- load centerline (micrometres -> millimetres for a comfortable scene) ----
pts = []
with CSV.open() as fh:
    for i, row in enumerate(csv.DictReader(fh)):
        if i % 12:  # decimate: 71k -> ~6k points, still smooth
            continue
        pts.append((float(row["x_um"]) * 1e-3, float(row["y_um"]) * 1e-3, 0.0))

g2 = json.loads(G2.read_text())
taps = g2["taps"]
pitch_mm = g2["pitch_um"] * 1e-3
bbox_mm = g2["die_bbox_um"][0] * 1e-3

# --- spiral waveguide as a bevelled curve ----------------------------------
cu = bpy.data.curves.new("spiral_centerline", "CURVE")
cu.dimensions = "3D"
spline = cu.splines.new("POLY")
spline.points.add(len(pts) - 1)
for p, (x, y, z) in zip(spline.points, pts):
    p.co = (x, y, z, 1.0)
cu.bevel_depth = g2["waveguide_width_um"] * 1e-3 * 3  # visually widened, noted in caption
cu.bevel_resolution = 2
wg = bpy.data.objects.new("spiral_delay_line", cu)
scene.collection.objects.link(wg)

mat = bpy.data.materials.new("waveguide")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.79, 0.57, 0.18, 1.0)
bsdf.inputs["Emission Color"].default_value = (0.79, 0.57, 0.18, 1.0)
bsdf.inputs["Emission Strength"].default_value = 0.4
wg.data.materials.append(mat)

# --- tap markers ----------------------------------------------------------
tap_mat = bpy.data.materials.new("tap")
tap_mat.use_nodes = True
tb = tap_mat.node_tree.nodes["Principled BSDF"]
tb.inputs["Base Color"].default_value = (0.15, 0.75, 0.85, 1.0)
tb.inputs["Emission Color"].default_value = (0.15, 0.8, 0.9, 1.0)
tb.inputs["Emission Strength"].default_value = 2.0
for t in taps:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=bbox_mm * 0.016,
                                         location=(t["x_um"] * 1e-3, t["y_um"] * 1e-3, bbox_mm * 0.012))
    s = bpy.context.active_object
    s.name = f"tap_{t['tap']:02d}"
    s.data.materials.append(tap_mat)

# --- lighting ----------------------------------------------------------
bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
bpy.context.active_object.data.energy = 3.0
bpy.ops.object.light_add(type="AREA", location=(bbox_mm, -bbox_mm, bbox_mm))
bpy.context.active_object.data.energy = 2000

# --- camera + render helper -------------------------------------------
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.resolution_x = 1600
scene.render.resolution_y = 1600
scene.render.film_transparent = False

SCENES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)


def look_at(obj, target):
    d = mathutils.Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def render(name, location, ortho=False, scale=1.0):
    cam.location = location
    look_at(cam, (0, 0, 0))
    cam_data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam_data.ortho_scale = bbox_mm * 1.15
    scene.render.filepath = str(FIGS / name)
    bpy.ops.render.render(write_still=True)


render("blender_spiral_top.png", (0, 0, bbox_mm * 1.6), ortho=True)
render("blender_spiral_perspective.png", (bbox_mm * 0.95, -bbox_mm * 0.95, bbox_mm * 0.75))

bpy.ops.wm.save_as_mainfile(filepath=str(SCENES / "spiral-reference-from-centerline.blend"))
print("OK spiral reference built:", len(pts), "points,", len(taps), "taps, bbox", round(bbox_mm, 4), "mm")
