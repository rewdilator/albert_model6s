"""Add an opening, detailed charge port to the rear-left quarter panel (Blender 4.5).

  * a hole cut into Body_LOD0/1/2 and the trunk lining behind it (exact boolean)
  * a 45 mm deep pocket with a CCS2 inlet: Type 2 AC socket (7 contacts) + 2-pin DC socket,
    metal contact pins and a green status-LED ring (material Light_Charge)
  * a body-coloured door (ChargePort_LOD0/1/2) on its own hinge empty, ChargePort_Pivot,
    hinged at its front edge: rotate the pivot about Z by -100 deg in Blender
    (+100 deg about Y in Unity) to open it
  * Loc_ChargePort moved onto the socket (cable / plug attach point)

Run once after apply_albert_branding.py:  python3 tools/add_charge_port.py
"""
import math
import os
import sys

import bpy  # noqa: I001  (bpy must be imported before bmesh)
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply_albert_branding as br  # noqa: E402

MM = 0.001
CENTRE = Vector((-1.2, -1.85, 0.73))        # ray start outside the car, rear-left quarter panel
DOOR_W, DOOR_H, DOOR_R = 125 * MM, 115 * MM, 16 * MM
GAP = 1.5 * MM                              # panel gap around the door
DEPTH = 45 * MM                             # pocket depth
OPEN_ANGLE = -100.0                         # Blender degrees about Z


def rounded_rect(w, h, r, steps=6):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                       (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(cx, cy, r, steps=32):
    return [(cx + r * math.cos(2 * math.pi * i / steps), cy + r * math.sin(2 * math.pi * i / steps)) for i in range(steps)]


def type2_outline(cx, cy, r, steps=40):
    """Type 2 socket face: a circle with the top flattened."""
    flat = r * 0.78
    cut = math.degrees(math.asin(flat / r))
    pts = []
    for i in range(steps + 1):                   # from the right end of the flat, clockwise round the bottom
        a = math.radians(cut - (360 - 2 * (90 - cut)) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts[::-1]


def world_bvh(ob):
    m = ob.matrix_world
    return BVHTree.FromPolygons([m @ v.co for v in ob.data.vertices], [tuple(p.vertices) for p in ob.data.polygons])


def to_object(me, ob):
    me.transform(ob.matrix_world.inverted())


def rigid(me, frame, origin, lift=0.0):
    """Place a flat (x, y, z) mesh on the plane through ``origin`` spanned by the frame."""
    for v in me.vertices:
        x, y, z = v.co
        v.co = origin + frame.r * x + frame.u * y + frame.n * (z + lift)


def set_material(me, name):
    me.materials.clear()
    me.materials.append(bpy.data.materials[name])


def ensure_charge_light():
    m = bpy.data.materials.get("Light_Charge")
    if m is None:
        m = bpy.data.materials.new("Light_Charge")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.05, 0.85, 0.25, 1)
        b.inputs["Roughness"].default_value = 0.3
        b.inputs["Emission Color"].default_value = (0.05, 0.85, 0.25, 1)
        b.inputs["Emission Strength"].default_value = 3.0
    return m


def cut_hole(body, frame, lod):
    outline = rounded_rect(DOOR_W + 2 * GAP, DOOR_H + 2 * GAP, DOOR_R + GAP)
    me = br.glyphs_mesh("ChargePort_Cutter", [[outline]], 1.0, 0.12, 0.0, lod)
    rigid(me, frame, frame.o, lift=-0.06)
    to_object(me, body)
    cutter = bpy.data.objects.new("ChargePort_Cutter", me)
    bpy.context.scene.collection.objects.link(cutter)
    cutter.matrix_world = body.matrix_world
    mod = body.modifiers.new("ChargePortHole", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.use_hole_tolerant = True
    mod.object = cutter
    with bpy.context.temp_override(object=body, active_object=body):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter)
    bpy.data.meshes.remove(me)


def pocket_and_socket(body, frame, bvh, lod):
    parts = []
    # pocket: a prism of the hole outline, open towards the outside, normals facing the viewer
    outline = rounded_rect(DOOR_W + 2 * GAP, DOOR_H + 2 * GAP, DOOR_R + GAP)
    cup = br.glyphs_mesh("ChargePort_Pocket", [[outline]], 1.0, DEPTH, 0.0, lod)
    bm = bmesh.new()
    bm.from_mesh(cup)
    top = max(v.co.z for v in bm.verts)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(abs(v.co.z - top) < 1e-6 for v in f.verts)],
                     context="FACES")
    for f in bm.faces:
        c = f.calc_center_median()
        if all(abs(v.co.z) < 1e-6 for v in f.verts):          # back plate: face the opening
            want = Vector((0, 0, 1))
            f.material_index = 1
        else:                                                 # walls: face the pocket's centre
            want = Vector((-c.x, -c.y, 0))
            f.material_index = 0
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
    bm.to_mesh(cup)
    bm.free()
    br.project_onto(cup, frame, bvh, sink=DEPTH - 0.4 * MM)   # rim 0.4 mm proud so no seam shows at the hole edge
    cup.materials.append(bpy.data.materials["Plastic_Black_Matte"])
    cup.materials.append(bpy.data.materials["Plastic_Black_Satin"])
    parts.append(cup)

    floor = frame.o - frame.n * (DEPTH + 0.1 * MM)        # just into the back plate
    ac_c, dc_c = (0.0, 14 * MM), (0.0, -30 * MM)
    ac_r = 24 * MM
    steps = {0: 40, 1: 24, 2: 14}[lod]
    ac_holes = [circle(ac_c[0] + dx * MM, ac_c[1] + dy * MM, r * MM, max(10, steps // 3))
                for dx, dy, r in ((-7, 13, 2.4), (7, 13, 2.4), (-13, 1, 4.0), (13, 1, 4.0),
                                  (0, -3, 4.6), (-7.5, -13, 4.0), (7.5, -13, 4.0))]
    ac = br.glyphs_mesh("ChargePort_AC", [[type2_outline(*ac_c, ac_r, steps)] + [h[::-1] for h in ac_holes]],
                        1.0, 11 * MM, 0.8 * MM, lod)
    dc_holes = [circle(dc_c[0] + dx * MM, dc_c[1], 8.5 * MM, steps // 2) for dx in (-15, 15)]
    dc_body = rounded_rect(62 * MM, 25 * MM, 12 * MM, max(3, steps // 8))
    dc_body = [(x + dc_c[0], y + dc_c[1]) for x, y in dc_body]
    dc = br.glyphs_mesh("ChargePort_DC", [[dc_body] + [h[::-1] for h in dc_holes]], 1.0, 11 * MM, 0.8 * MM, lod)
    for me in (ac, dc):
        rigid(me, frame, floor)
        set_material(me, "Plastic_Black_Satin")
        parts.append(me)
    if lod < 2:
        pins = [[circle(ac_c[0] + dx * MM, ac_c[1] + dy * MM, r * MM, 10)]
                for dx, dy, r in ((-7, 13, 1.1), (7, 13, 1.1), (-13, 1, 2.0), (13, 1, 2.0),
                                  (0, -3, 2.3), (-7.5, -13, 2.0), (7.5, -13, 2.0))]
        pins += [[circle(dc_c[0] + dx * MM, dc_c[1], 4.2 * MM, 16)] for dx in (-15, 15)]
        pin_me = br.glyphs_mesh("ChargePort_Pins", pins, 1.0, 7 * MM, 0.3 * MM, lod)
        rigid(pin_me, frame, floor)
        set_material(pin_me, "Chrome")
        parts.append(pin_me)
    ring = [circle(ac_c[0], ac_c[1], ac_r + 3.2 * MM, steps), circle(ac_c[0], ac_c[1], ac_r + 1.4 * MM, steps)[::-1]]
    led = br.glyphs_mesh("ChargePort_LED", [ring], 1.0, 4 * MM, 0.3 * MM, lod)
    rigid(led, frame, floor)
    set_material(led, "Light_Charge")
    parts.append(led)

    objs = []
    for me in parts:
        br.mark_sharp(me)
        br.planar_uv(me, frame)
        to_object(me, body)
        if body.data.has_custom_normals:
            me.update()
            me.normals_split_custom_set([tuple(n.vector) for n in me.corner_normals])
        o = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(o)
        o.matrix_world = body.matrix_world
        objs.append(o)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs + [body]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = body
    with bpy.context.temp_override(active_object=body, selected_editable_objects=objs + [body]):
        bpy.ops.object.join()


def door(frame, bvh, pivot, lod, template):
    outline = rounded_rect(DOOR_W, DOOR_H, DOOR_R)
    me = br.glyphs_mesh(f"ChargePort_LOD{lod}", [[outline]], 1.0, 2.5 * MM, 0.6 * MM, lod)
    br.project_onto(me, frame, bvh, sink=2.5 * MM)            # outer skin flush with the body
    me.materials.append(bpy.data.materials["Paint_Body"])
    me.materials.append(bpy.data.materials["Plastic_Black_Matte"])
    me.update()
    for p in me.polygons:
        p.material_index = 0 if p.normal.dot(frame.n) > 0.6 else 1
    br.mark_sharp(me)
    br.planar_uv(me, frame)
    me.transform(pivot.matrix_world.inverted())
    if template.data.has_custom_normals:
        me.update()
        me.normals_split_custom_set([tuple(n.vector) for n in me.corner_normals])
    ob = bpy.data.objects.new(f"ChargePort_LOD{lod}", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = pivot
    ob.matrix_parent_inverse.identity()
    return ob


def main():
    if bpy.data.filepath != br.BLEND:
        bpy.ops.wm.open_mainfile(filepath=br.BLEND)
    scene = bpy.context.scene
    if scene.get("albert_charge_port"):
        raise SystemExit("Charge port already added to this file.")
    ensure_charge_light()

    body0 = bpy.data.objects["Body_LOD0"]
    hit = world_bvh(body0).ray_cast(CENTRE, Vector((1, 0, 0)), 1.0)
    centre, nrm = hit[0], hit[1]
    if nrm.x > 0:
        nrm = -nrm
    # viewer outside on the left looks towards +X: right = rear (-Y), up = +Z
    frame = br.Frame(centre, Vector((0, -1, 0)), Vector((0, 0, 1)), nrm)

    pivot = bpy.data.objects.new("ChargePort_Pivot", None)
    scene.collection.objects.link(pivot)
    chassis = bpy.data.objects["Chassis"]
    hinge_world = frame.point(-DOOR_W / 2, 0.0)             # front edge of the door
    pivot.parent = chassis
    pivot.location = chassis.matrix_world.inverted() @ hinge_world
    bpy.context.view_layer.update()

    for lod in (0, 1, 2):
        body = bpy.data.objects[f"Body_LOD{lod}"]
        bvh = world_bvh(body)                                 # sample the surface before cutting
        cut_hole(body, frame, lod)
        cut_hole(bpy.data.objects[f"Interior_LOD{lod}"], frame, lod)   # trunk side lining behind the port
        pocket_and_socket(body, frame, bvh, lod)
        door(frame, bvh, pivot, lod, body)

    loc = bpy.data.objects["Loc_ChargePort"]
    socket_world = frame.o - frame.n * (DEPTH - 12 * MM) + frame.u * (14 * MM)
    loc.location = loc.parent.matrix_world.inverted() @ socket_world

    scene["albert_charge_port"] = 1
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_mainfile(filepath=br.BLEND, compress=False)
    print("charge port added; hinge at", tuple(round(c, 3) for c in hinge_world),
          "socket at", tuple(round(c, 3) for c in socket_world))


if __name__ == "__main__":
    main()
