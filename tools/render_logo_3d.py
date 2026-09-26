"""Studio render of the 3D A+ badge -> brand/albert_logo_3d.png (transparent background).

Run: python3 tools/render_logo_3d.py   (bpy pip module; needs EV_Sedan.blend for the materials)
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_albert_branding as br  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "brand", "albert_logo_3d.png")


def main():
    bpy.ops.wm.open_mainfile(filepath=br.BLEND)
    scene = bpy.data.scenes.new("LogoStudio")
    bpy.context.window.scene = scene
    cap = 1.0
    for me, mat, sink in br.faceted_logo("Hero", cap, lod=0, zscale=0.55, sink=0.0):
        br.mark_sharp(me)
        me.materials.clear()
        me.materials.append(bpy.data.materials[mat])
        ob = bpy.data.objects.new(me.name, me)
        scene.collection.objects.link(ob)
        ob.rotation_euler.x = math.radians(90)           # stand the badge up, facing -Y
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1200
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("Studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.022, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    scene.world = world
    # softboxes: key top-left, rim right, strip below for the lower facets
    for name, loc, size, energy in (("Key", (-1.8, -2.4, 1.6), 1.5, 700), ("Rim", (2.2, -1.2, 0.6), 0.8, 450),
                                    ("Strip", (0.3, -2.2, -1.5), 3.0, 260), ("Top", (0.2, -1.0, 2.4), 2.0, 380)):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        light.data.size = size
        light.data.energy = energy
        light.location = loc
        light.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(light)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 85
    cam.location = (0.5, -5.0, 0.55)
    cam.rotation_euler = (Vector((0.0, 0.0, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
