"""Extra interior details (Blender 4.5), joined into Interior_LOD0/1:

  * twin wireless phone-charging pads on the console tray, each with a small chrome A+
  * rear-passenger console: 8" rear touchscreen in a gloss-black bezel (shows the vehicle
    card of ev_sedan_screen_d.png), two air vents with louvres and two USB-C ports

Run once after apply_albert_branding.py:  python3 tools/add_interior_details.py
"""
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import albert_brand as ab  # noqa: E402
import apply_albert_branding as br  # noqa: E402
from add_charge_port import rounded_rect  # noqa: E402

MM = 0.001
# region of ev_sedan_screen_d.png shown on the rear screen, in the UI's 1306 x 1024 layout (px)
REAR_UI = (8, 250, 462, 538)


def local_frame(ob, origin_world, right, up, normal, ray_dir, reach=0.15):
    """Frame on the surface of ``ob`` hit by a ray from origin_world along ray_dir (object space)."""
    bvh = br.bvh_local(ob)
    hit, _ = br.surface_normal(bvh, br.to_local(ob, origin_world), br.to_local(ob, ray_dir, is_dir=True), reach=reach)
    frame = br.Frame(hit, br.to_local(ob, right, True), br.to_local(ob, up, True), br.to_local(ob, normal, True))
    return frame, bvh


def phone_pads(ob, lod):
    parts = []
    frame, bvh = local_frame(ob, Vector((0.0, 0.42, 0.60)), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1))
    glyphs, _ = ab.emblem()
    for x in (-0.049, 0.049):
        pad = br.glyphs_mesh("PhonePad", [[rounded_rect(86 * MM, 165 * MM, 12 * MM, 5)]], 1.0,
                             2.0 * MM, 0.6 * MM, lod, offset=(x, 0.0))
        parts.append((pad, "Plastic_Black_Matte", 0.5 * MM))
        logo = br.glyphs_mesh("PhonePad_Aplus", glyphs, 11 * MM, 2.3 * MM, 0.2 * MM, lod,
                              offset=(x / (11 * MM), 0.062 / (11 * MM) - 0.5))
        parts.append((logo, "Chrome", 0.5 * MM))
    br.attach(ob, parts, frame, bvh)


def rear_console(ob, lod):
    frame, bvh = local_frame(ob, Vector((0.0, -0.30, 0.465)), (1, 0, 0), (0, 0, 1), (0, -1, 0), (0, 1, 0), reach=0.25)
    parts = []
    # screen: gloss bezel + emissive display face using a crop of the main UI texture
    sy = 0.0
    bezel = br.glyphs_mesh("RearScreen_Bezel", [[rounded_rect(160 * MM, 100 * MM, 8 * MM, 5)]], 1.0,
                           6 * MM, 1.2 * MM, lod, offset=(0.0, sy))
    parts.append((bezel, "Trim_Black_Gloss", 1.0 * MM))
    w, h = 148 * MM, 88 * MM
    face = br.glyphs_mesh("RearScreen_Display", [[rounded_rect(w, h, 4 * MM, 3)]], 1.0, 0.6 * MM, 0.0, lod,
                          offset=(0.0, sy))
    x0, y0, x1, y1 = REAR_UI
    u0, u1 = x0 / 1306.0, x1 / 1306.0
    v0, v1 = 1 - y1 / 1024.0, 1 - y0 / 1024.0
    uv = face.uv_layers.get("UVMap") or face.uv_layers.new(name="UVMap")
    for loop in face.loops:
        co = face.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (u0 + (co.x / w + 0.5) * (u1 - u0), v0 + ((co.y - sy) / h + 0.5) * (v1 - v0))
    face["keep_uv"] = True
    parts.append((face, "Screen", -4.7 * MM))                 # cover glass 0.3 mm proud of the bezel
    # air vents above the screen: dark opening, three louvres
    for x in (-0.042, 0.042):
        vent = br.glyphs_mesh("RearVent", [[rounded_rect(66 * MM, 20 * MM, 5 * MM, 4)]], 1.0, 2.5 * MM, 0.5 * MM,
                              lod, offset=(x, 0.063))
        parts.append((vent, "Trim_Black_Gloss", 1.0 * MM))
        louvres = [rounded_rect(58 * MM, 1.6 * MM, 0.7 * MM, 1) for _ in range(3)]
        louvres = [[(px + x, py + 0.057 + i * 0.006) for px, py in ring] for i, ring in enumerate(louvres)]
        lv = br.glyphs_mesh("RearVent_Louvre", [[ring] for ring in louvres], 1.0, 3.5 * MM, 0.0, lod)
        parts.append((lv, "Metal_Dark", 1.0 * MM))
    # USB-C ports below the screen
    for x in (-0.018, 0.018):
        rim = [rounded_rect(12.5 * MM, 6 * MM, 3 * MM, 3), rounded_rect(9 * MM, 3.4 * MM, 1.7 * MM, 3)[::-1]]
        rim = [[(px + x, py - 0.063) for px, py in r] for r in rim]
        parts.append((br.glyphs_mesh("USBC_Rim", [rim], 1.0, 2.0 * MM, 0.3 * MM, lod), "Chrome", 1.0 * MM))
        slot = [(px + x, py - 0.063) for px, py in rounded_rect(9 * MM, 3.4 * MM, 1.7 * MM, 3)]
        parts.append((br.glyphs_mesh("USBC_Slot", [[slot]], 1.0, 0.8 * MM, 0.0, lod), "Trim_Black_Gloss", 1.0 * MM))
    br.attach(ob, parts, frame, bvh)


def main():
    if bpy.data.filepath != br.BLEND:
        bpy.ops.wm.open_mainfile(filepath=br.BLEND)
    scene = bpy.context.scene
    if scene.get("albert_interior_details"):
        raise SystemExit("Interior details already added to this file.")
    for lod in (0, 1):
        ob = bpy.data.objects[f"Interior_LOD{lod}"]
        phone_pads(ob, lod)
        rear_console(ob, lod)
    scene["albert_interior_details"] = 1
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_mainfile(filepath=br.BLEND, compress=False)
    print("interior details added")


if __name__ == "__main__":
    main()
