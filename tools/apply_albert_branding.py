"""Apply the Albert brand to EV_Sedan.blend (Blender 4.5).

Adds real 3D chrome "A+" emblems (steering-wheel hub, front fascia, trunk, wheel
centre caps) and the "ALBERT" wordmark on the trunk.  Every badge is built from
the vector outlines in ``albert_brand.py``, projected onto the panel it sits on and
joined into that part's mesh for every LOD, so it moves with the part (steering
wheel turns, wheels spin, bumper detaches) without adding renderers.  Only existing
materials are used (``Chrome`` and ``Trim_Black_Gloss``).

Run:  blender -b EV_Sedan.blend -P tools/apply_albert_branding.py
  or: python3 tools/apply_albert_branding.py            (with the ``bpy`` pip module)
The script refuses to run twice on the same file.
"""
import math
import os
import sys

import bpy  # noqa: I001  (bpy must be imported before bmesh)
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import albert_brand as ab  # noqa: E402

BLEND = os.path.join(ROOT, "EV_Sedan.blend")
MM = 0.001

# Per-LOD detail: bevel segments and whether to bevel at all
LOD_DETAIL = {0: dict(bevel_res=2, bevel=True, steps=1.0),
              1: dict(bevel_res=0, bevel=True, steps=0.5),
              2: dict(bevel_res=0, bevel=False, steps=0.34)}


def lod_steps(steps, lod):
    return max(12, int(steps * LOD_DETAIL[lod]["steps"]))


# ---------------------------------------------------------------- geometry helpers

def superellipse(a, b, n=2.6, steps=72):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s)))
    return pts


def glyphs_mesh(name, glyphs, scale, depth, bevel, lod, offset=(0.0, 0.0), grow=0.0):
    """Extrude 2D rings into a mesh. Returns a mesh whose z runs from 0 (back) to depth (face).

    grow (metres) fattens every stroke outwards, e.g. for a chrome rim around a black badge.
    """
    det = LOD_DETAIL[lod]
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.resolution_u = 1
    b = bevel if det["bevel"] else 0.0
    cu.extrude = max(depth / 2 - b, 1e-5)
    cu.bevel_depth = b
    cu.bevel_resolution = det["bevel_res"]
    cu.offset = grow - b                           # keep the outline at its true size (+ grow)
    ox, oy = offset
    for g in glyphs:
        for ring in g:
            sp = cu.splines.new("POLY")
            sp.points.add(len(ring) - 1)
            for i, (x, y) in enumerate(ring):
                sp.points[i].co = ((x + ox) * scale, (y + oy) * scale, 0.0, 1.0)
            sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    zmin = min(v.co.z for v in me.vertices)
    for v in me.vertices:
        v.co.z -= zmin
    return me


class Frame:
    """Badge frame in the destination object's local space."""

    def __init__(self, origin, right, up_hint, normal):
        n = Vector(normal).normalized()
        r = (Vector(right) - n * Vector(right).dot(n)).normalized()
        u = n.cross(r).normalized()
        if u.dot(Vector(up_hint)) < 0:
            raise ValueError("frame is mirrored")
        self.o, self.r, self.u, self.n = Vector(origin), r, u, n

    def point(self, x, y):
        return self.o + self.r * x + self.u * y


def project_onto(me, frame, bvh, sink, reach=0.25):
    """Wrap a flat badge mesh onto the surface along -frame.n (keeps its thickness)."""
    for v in me.vertices:
        x, y, z = v.co
        p0 = frame.point(x, y)
        hit = bvh.ray_cast(p0 + frame.n * reach, -frame.n, 2 * reach)
        base = hit[0] if hit[0] is not None else p0
        v.co = base + frame.n * (z - sink)


def mark_sharp(me, angle_deg=35.0):
    me.shade_smooth()
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.radians(angle_deg)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim:
            e.smooth = False
    bm.to_mesh(me)
    bm.free()


def planar_uv(me, frame):
    uv = me.uv_layers.new(name="UVMap")
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co - frame.o
        uv.data[loop.index].uv = (co.dot(frame.r) * 10 + 0.5, co.dot(frame.u) * 10 + 0.5)


def attach(dest, parts, frame, bvh):
    """parts: list of (mesh, material_name, sink). Projects (unless sink is None), joins into ``dest``."""
    objs = []
    for me, mat_name, sink in parts:
        if sink is not None:
            project_onto(me, frame, bvh, sink)
        mark_sharp(me)
        planar_uv(me, frame)
        me.materials.append(bpy.data.materials[mat_name])
        if dest.data.has_custom_normals:
            me.update()
            me.normals_split_custom_set([tuple(n.vector) for n in me.corner_normals])
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.matrix_world = dest.matrix_world
        objs.append(ob)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs + [dest]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = dest
    with bpy.context.temp_override(active_object=dest, selected_editable_objects=objs + [dest]):
        bpy.ops.object.join()


def bvh_local(ob):
    return BVHTree.FromPolygons([v.co.copy() for v in ob.data.vertices],
                                [tuple(p.vertices) for p in ob.data.polygons])


def to_local(ob, v, is_dir=False):
    m = ob.matrix_world.inverted()
    return (m.to_3x3() @ Vector(v)).normalized() if is_dir else m @ Vector(v)


def surface_normal(bvh, origin, direction, reach=0.5):
    hit = bvh.ray_cast(Vector(origin) - Vector(direction) * reach, Vector(direction), 2 * reach)
    if hit[0] is None:
        raise RuntimeError(f"no surface at {origin}")
    return hit[0], hit[1]

# ---------------------------------------------------------------- badges

def emblem_parts(name, lod, cap, depth, bevel):
    glyphs, _ = ab.emblem()
    return glyphs_mesh(f"{name}_AplusGlyphs", glyphs, cap, depth, bevel, lod, offset=(0.0, -0.5))


def steering_wheel_emblem(ob, lod):
    """Gloss-black plaque with a chrome surround and chrome A+ on the airbag cover."""
    me = ob.data
    pts = [v.co for v in me.vertices]
    c = sum(pts, Vector()) / len(pts)
    # wheel-plane normal (towards the driver) from the rim: fit via covariance
    arr = np.array([p[:] for p in pts]) - np.array(c[:])
    _, _, vt = np.linalg.svd(arr, full_matrices=False)
    n = Vector(vt[2])
    if n.y > 0:                        # driver sits towards -Y (rear)
        n = -n
    r_axis = Vector((1, 0, 0))
    # rim centre: mean of the outermost ring of vertices in the wheel plane
    rad = [((p - c) - n * (p - c).dot(n)).length for p in pts]
    rmax = max(rad)
    rim = [p for p, r in zip(pts, rad) if r > 0.85 * rmax]
    centre = sum(rim, Vector()) / len(rim)
    bvh = bvh_local(ob)
    hub_pt, _ = surface_normal(bvh, centre + n * 0.3, -n)
    frame = Frame(hub_pt, r_axis, Vector((0, 0, 1)), n)

    a, b = 37 * MM, 24 * MM
    steps = lod_steps(72, lod)
    plaque = glyphs_mesh("SW_Plaque", [[superellipse(a, b, steps=steps)]], 1.0, 3.0 * MM, 1.0 * MM, lod)
    letters = emblem_parts("SW", lod, cap=27 * MM, depth=4.4 * MM, bevel=0.5 * MM)
    parts = [(plaque, "Trim_Black_Gloss", 1.2 * MM), (letters, "Chrome", 1.2 * MM)]
    if lod == 2:                      # far LOD: plaque + letters only
        attach(ob, parts, frame, bvh)
        return
    outer = superellipse(a + 1.6 * MM, b + 1.6 * MM, steps=steps)
    inner = superellipse(a - 0.4 * MM, b - 0.4 * MM, steps=steps)[::-1]
    parts.append((glyphs_mesh("SW_Surround", [[outer, inner]], 1.0, 3.8 * MM, 0.6 * MM, lod), "Chrome", 1.2 * MM))
    # thumb-wheel pods either side of the emblem (media / cruise controls)
    for x in (-0.085, 0.085):
        pod_c = frame.point(x, -0.02)
        pod = glyphs_mesh("SW_ScrollPod", [[superellipse(10.5 * MM, 15.5 * MM, n=3.0, steps=lod_steps(48, lod))]], 1.0,
                          2.2 * MM, 0.7 * MM, lod, offset=(x, -0.02))
        parts.append((pod, "Trim_Black_Gloss", 1.0 * MM))
        surf, nrm = surface_normal(bvh, pod_c + n * 0.3, -n)
        nrm = nrm if nrm.dot(n) > 0 else -nrm
        axis = (r_axis - nrm * r_axis.dot(nrm)).normalized()
        wheel = scroll_wheel(lod)
        up = nrm.cross(axis).normalized()
        centre = surf + nrm * (1.2 * MM + 3.8 * MM - 7.5 * MM)   # sits in a slot, 3.8 mm proud of the pod
        xf = Matrix((axis, up, nrm)).transposed().to_4x4()
        xf.translation = centre
        wheel.transform(xf)
        parts.append((wheel, "Chrome", None))
    attach(ob, parts, frame, bvh)


def scroll_wheel(lod, radius=7.5 * MM, width=10 * MM):
    """Knurled thumb wheel, axis along +X, centred on the origin."""
    ridges = {0: 36, 1: 18, 2: 10}[lod]
    bm = bmesh.new()
    rings = []
    for side in (-0.5, 0.5):
        ring = []
        for i in range(ridges * 2):
            a = 2 * math.pi * i / (ridges * 2)
            rr = radius if i % 2 == 0 or lod == 2 else radius - 0.45 * MM
            ring.append(bm.verts.new((side * width, rr * math.cos(a), rr * math.sin(a))))
        rings.append(ring)
    m = len(rings[0])
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
    bm.faces.new(rings[1])
    bm.faces.new(rings[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if lod == 0:  # chamfer the rims so the edge catches a highlight
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and
                 any(len(f.verts) > 4 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=edges, offset=0.5 * MM, segments=1, affect="EDGES")
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    me = bpy.data.meshes.new("SW_ScrollWheel")
    bm.to_mesh(me)
    bm.free()
    return me


def surface_badge(ob, lod, world_centre, view_dir, right_world, parts_fn):
    """Badge on a body panel. view_dir: direction the viewer looks at the panel (world)."""
    bvh = bvh_local(ob)
    c_local = to_local(ob, world_centre)
    d_local = to_local(ob, view_dir, is_dir=True)
    hit, nrm = surface_normal(bvh, c_local, d_local)
    frame = Frame(hit, to_local(ob, right_world, is_dir=True), to_local(ob, (0, 0, 1), is_dir=True), nrm)
    attach(ob, parts_fn(lod), frame, bvh)


def black_chrome(name, glyphs, cap, lod, y, depth, rim):
    """Gloss-black letters sitting on a slightly larger chrome base: reads clearly on white paint."""
    off = (0.0, y / cap - 0.5)
    return [(glyphs_mesh(name + "_Rim", glyphs, cap, depth * 0.7, 0.45 * MM, lod, offset=off, grow=rim),
             "Chrome", 0.8 * MM),
            (glyphs_mesh(name + "_Face", glyphs, cap, depth, 0.5 * MM, lod, offset=off),
             "Trim_Black_Gloss", 0.8 * MM)]


def ext_emblem(cap, y=0.0, depth=5.0 * MM, rim=1.4 * MM):
    def fn(lod):
        glyphs, _ = ab.emblem()
        return black_chrome("Front_Aplus", glyphs, cap, lod, y, depth, rim)
    return fn


def rear_badges(cap_emblem, cap_word, y_emblem, y_word, tracking):
    def fn(lod):
        glyphs, _ = ab.emblem()
        word, _ = ab.wordmark(tracking=tracking)
        return (black_chrome("Rear_Aplus", glyphs, cap_emblem, lod, y_emblem, 5.0 * MM, 1.3 * MM) +
                black_chrome("Rear_Wordmark", word, cap_word, lod, y_word, 4.0 * MM, 1.0 * MM))
    return fn


def wheel_cap_emblem(ob, lod):
    side = -1 if ob.name.startswith("Wheel_FL") or ob.name.startswith("Wheel_RL") else 1
    n = Vector((side, 0, 0))            # local == world orientation for wheels
    right = Vector((0, side, 0))
    bvh = bvh_local(ob)
    hit, _ = surface_normal(bvh, Vector((0, 0, 0)) + n * 0.3, -n)
    frame = Frame(hit, right, Vector((0, 0, 1)), n)
    glyphs, _ = ab.emblem()
    letters = glyphs_mesh("Cap_Aplus", glyphs, 25 * MM, 2.2 * MM, 0.4 * MM, lod, offset=(0.0, -0.5))
    attach(ob, [(letters, "Chrome", 0.6 * MM)], frame, bvh)


def sill_plates(ob, lod):
    """Brushed-aluminium kick plates with a black ALBERT inlay on both front door sills."""
    bvh = bvh_local(ob)
    for side in (-1, 1):
        # readable from outside the car: text runs towards the rear on the left, forwards on the right
        frame_world = (Vector((side * 0.79, 0.50, 0.348)), Vector((0, side, 0)), Vector((-side, 0, 0)))
        o, r, u = (to_local(ob, frame_world[0]), to_local(ob, frame_world[1], True), to_local(ob, frame_world[2], True))
        hit, _ = surface_normal(bvh, o + Vector((0, 0, 0.2)), Vector((0, 0, -1)))
        frame = Frame(hit, r, u, Vector((0, 0, 1)))
        plate = glyphs_mesh("Sill_Plate", [[superellipse(0.19, 0.017, n=8.0, steps=lod_steps(96, lod))]], 1.0,
                            1.6 * MM, 0.5 * MM, lod)
        word, _ = ab.wordmark()
        inlay = glyphs_mesh("Sill_Wordmark", word, 15 * MM, 0.5 * MM, 0.1 * MM, lod, offset=(0.0, -0.5))
        attach(ob, [(plate, "Aluminium_Brushed", 0.4 * MM), (inlay, "Plastic_Black_Matte", -0.8 * MM)], frame, bvh)


def seat_logos(ob, lod):
    """Dark embroidered A+ on the front-seat headrest areas (driver and passenger)."""
    bvh = bvh_local(ob)
    for x in (-0.42, 0.42):
        hit, nrm = surface_normal(bvh, to_local(ob, (x, 0.3, 1.07)), to_local(ob, (0, -1, 0), is_dir=True))
        nrm = nrm if nrm.y > 0 else -nrm            # face the front of the car
        frame = Frame(hit, to_local(ob, (-1, 0, 0), is_dir=True), to_local(ob, (0, 0, 1), is_dir=True), nrm)
        glyphs, _ = ab.emblem()
        stitch = glyphs_mesh("Seat_Aplus", glyphs, 40 * MM, 1.0 * MM, 0.3 * MM, lod, offset=(0.0, -0.5))
        attach(ob, [(stitch, "Leather_Black", 0.5 * MM)], frame, bvh)


def fix_screen_uvs(ob):
    """The source mapped the touchscreen texture upside down (v grows downwards); flip it."""
    me = ob.data
    idx = {i for i, m in enumerate(me.materials) if m and m.name == "Screen"}
    uv = me.uv_layers["UVMap"].data
    for p in me.polygons:
        if p.material_index in idx:
            for li in p.loop_indices:
                uv[li].uv.y = 1.0 - uv[li].uv.y


def main():
    if bpy.data.filepath != BLEND:
        bpy.ops.wm.open_mainfile(filepath=BLEND)
    scene = bpy.context.scene
    if scene.get("albert_branding"):
        raise SystemExit("Albert branding is already applied to this file.")

    for lod in (0, 1, 2):
        steering_wheel_emblem(bpy.data.objects[f"SteeringWheel_LOD{lod}"], lod)
        # front fascia, centred just under the bonnet shut-line
        surface_badge(bpy.data.objects[f"Bumper_F_LOD{lod}"], lod, (0.0, 2.345, 0.50), (0, -1, 0), (-1, 0, 0),
                      ext_emblem(cap=68 * MM))
        # trunk: emblem between the tail lamps, wide-spaced wordmark underneath
        surface_badge(bpy.data.objects[f"Trunk_LOD{lod}"], lod, (0.0, -2.26, 0.905), (0, 1, 0), (1, 0, 0),
                      rear_badges(cap_emblem=50 * MM, cap_word=34 * MM, y_emblem=0.052, y_word=-0.032,
                                  tracking=0.75))
        fix_screen_uvs(bpy.data.objects[f"Interior_LOD{lod}"])
        if lod < 2:                   # sill plates only matter up close
            sill_plates(bpy.data.objects[f"Interior_LOD{lod}"], lod)
            seat_logos(bpy.data.objects[f"Interior_LOD{lod}"], lod)
        for w in ("FL", "FR", "RL", "RR"):
            wheel_cap_emblem(bpy.data.objects[f"Wheel_{w}_LOD{lod}"], lod)

    scene["albert_branding"] = 1
    bpy.context.preferences.filepaths.save_version = 0   # no .blend1 backup next to the asset
    bpy.ops.wm.save_mainfile(filepath=BLEND, compress=False)
    print("Albert branding applied and saved to", BLEND)


if __name__ == "__main__":
    main()
