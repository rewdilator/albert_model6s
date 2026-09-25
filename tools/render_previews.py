"""Render the reference images in preview/ with Cycles (CPU, works headless).

Run: python3 tools/render_previews.py [shot ...]      (bpy pip module, or blender -b -P)
With no arguments every shot is rendered.  Nothing is saved back into the .blend.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "preview")
SW = Vector((-0.4192, 0.5423, 0.8272))                 # Steering_Pivot
SW_N = Vector((0.0104, -0.945, 0.327)).normalized()    # wheel-plane normal, towards the driver

# name: (camera location, target, lens mm, options)
SHOTS = {
    "front":         ((0.0, 7.6, 0.95), (0.0, 0.0, 0.62), 50, {}),
    "rear":          ((0.0, -7.6, 1.05), (0.0, 0.0, 0.66), 50, {}),
    "side":          ((-7.8, 0.0, 0.95), (0.0, 0.0, 0.62), 50, {}),
    "front_34":      ((-4.3, 5.4, 1.55), (0.0, 0.25, 0.55), 45, {}),
    "front_34_LOD1": ((-4.3, 5.4, 1.55), (0.0, 0.25, 0.55), 45, {"lod": 1}),
    "front_34_LOD2": ((-4.3, 5.4, 1.55), (0.0, 0.25, 0.55), 45, {"lod": 2}),
    "rear_34":       ((4.3, -5.6, 1.55), (0.0, -0.3, 0.6), 45, {}),
    "wheel":         ((-1.95, 1.567, 0.36), (-0.83, 1.567, 0.339), 50, {}),
    "tyre_closeup":  ((-1.25, 2.05, 0.18), (-0.86, 1.62, 0.2), 40, {}),
    "dash":          ((-0.40, -0.02, 1.13), (-0.12, 0.9, 0.84), 20, {"cabin": True}),
    "interior":      ((0.0, -0.95, 1.16), (-0.08, 0.8, 0.86), 20, {"cabin": True}),
    "steering_wheel": (tuple(SW + SW_N * 0.36), tuple(SW), 35, {"cabin": True, "fill": 5}),
    "seat":          ((0.05, -0.45, 1.28), (-0.45, 0.35, 0.55), 22, {"cabin": True}),
    "rear_seat":     ((0.0, 0.02, 1.12), (0.0, -0.8, 0.72), 22, {"cabin": True}),
    "front_seats":   ((0.0, 0.45, 1.1), (0.0, -0.2, 0.92), 18, {"cabin": True}),
    "door_card":     ((0.35, 0.15, 1.05), (-0.9, 0.45, 0.72), 24, {"cabin": True}),
    "door_sill":     ((-1.45, 0.25, 1.12), (-0.79, 0.52, 0.36), 32, {"door_fl": -65}),
    "openings":      ((-4.0, 4.6, 2.6), (0.0, 0.3, 0.6), 35, {"open_all": True}),
    "console":       ((0.28, 0.05, 1.02), (0.0, 0.40, 0.53), 32, {"cabin": True}),
    "rear_console":  ((0.12, -0.78, 0.86), (0.0, -0.135, 0.47), 30, {"cabin": True}),
    "charge_port":   ((-1.45, -2.4, 0.98), (-0.84, -1.85, 0.72), 55, {"port": -100}),
    "charge_port_closed": ((-1.6, -2.15, 0.9), (-0.86, -1.85, 0.73), 50, {}),
    "badge_front":   ((0.25, 3.2, 0.75), (0.0, 2.34, 0.52), 50, {}),
    "badge_rear":    ((0.3, -3.3, 1.05), (0.0, -2.26, 0.9), 50, {}),
}


def setup():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = 1400, 900
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("PreviewWorld")
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(35)
    sky.sun_rotation = math.radians(140)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs[1].default_value = 0.35
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    sc.world = w
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    g = bpy.context.object
    m = bpy.data.materials.new("PreviewGround")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.09, 0.09, 0.095, 1)
    b.inputs["Roughness"].default_value = 0.65
    g.data.materials.append(m)
    cam = bpy.data.objects.new("PreviewCam", bpy.data.cameras.new("PreviewCam"))
    sc.collection.objects.link(cam)
    cam.data.clip_start = 0.01
    sc.camera = cam
    light = bpy.data.objects.new("CabinFill", bpy.data.lights.new("CabinFill", "AREA"))
    sc.collection.objects.link(light)
    light.data.size = 0.6
    light.visible_camera = False
    return cam, light


def show_lod(lod):
    for o in bpy.data.objects:
        if o.type == "MESH" and "_LOD" in o.name:
            o.hide_render = not o.name.endswith(f"_LOD{lod}")


def main(names):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "EV_Sedan.blend"))
    cam, light = setup()
    obj = bpy.data.objects
    for name in names:
        loc, target, lens, opt = SHOTS[name]
        show_lod(opt.get("lod", 0))
        # hinge pivots (Blender axes): doors about Z, hood / trunk about X
        every = opt.get("open_all", False)
        obj["Door_FL_Pivot"].rotation_euler.z = math.radians(-65 if every else opt.get("door_fl", 0))
        obj["Door_RL_Pivot"].rotation_euler.z = math.radians(-65 if every else 0)
        obj["Door_FR_Pivot"].rotation_euler.z = math.radians(65 if every else 0)
        obj["Door_RR_Pivot"].rotation_euler.z = math.radians(65 if every else 0)
        obj["Hood_Pivot"].rotation_euler.x = math.radians(45 if every else 0)
        obj["Trunk_Pivot"].rotation_euler.x = math.radians(-60 if every else 0)
        if "ChargePort_Pivot" in obj:
            obj["ChargePort_Pivot"].rotation_euler.z = math.radians(-100 if every else opt.get("port", 0))
        cabin = opt.get("cabin", False)
        light.data.energy = opt.get("fill", 25) if cabin else 0.0
        light.location = (-0.1, 0.1, 1.15) if name != "steering_wheel" else SW + SW_N * 0.6 + Vector((0.2, 0, 0.25))
        light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()
        cam.location = Vector(loc)
        cam.data.lens = lens
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.render.filepath = os.path.join(OUT, name + ".png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[sys.argv.index("--") + 1:]] if "--" in sys.argv else sys.argv[1:]
    args = [a for a in args if a in SHOTS]
    main(args or list(SHOTS))
