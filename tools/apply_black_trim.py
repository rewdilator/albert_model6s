"""Black out exterior details the way they are on the production car (Blender 4.5).

  * flush door handles (all four doors)          Chrome -> Trim_Black_Gloss
  * fender side-repeater camera housings (L/R)   Chrome -> Trim_Black_Gloss

Works on every LOD and is safe to run more than once.
Run: python3 tools/apply_black_trim.py   (bpy pip module)  or  blender -b EV_Sedan.blend -P tools/apply_black_trim.py
"""
import os

import bpy  # noqa: I001  (bpy must be imported before bmesh)
import bmesh
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "EV_Sedan.blend")
BLACK = "Trim_Black_Gloss"


def chrome_islands(ob):
    """Yield (face indices, world-space centroid) for each connected Chrome island."""
    me = ob.data
    chrome = {i for i, m in enumerate(me.materials) if m and m.name == "Chrome"}
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    todo = {f.index for f in bm.faces if f.material_index in chrome}
    while todo:
        seed = todo.pop()
        island, stack = [seed], [seed]
        while stack:
            for e in bm.faces[stack.pop()].edges:
                for g in e.link_faces:
                    if g.index in todo:
                        todo.remove(g.index)
                        stack.append(g.index)
                        island.append(g.index)
        c = sum((bm.faces[i].calc_center_median() for i in island), Vector()) / len(island)
        yield island, ob.matrix_world @ c
    bm.free()


def recolour(ob, is_target):
    me = ob.data
    if BLACK not in [m.name for m in me.materials if m]:
        me.materials.append(bpy.data.materials[BLACK])
    black = [m.name if m else None for m in me.materials].index(BLACK)
    count = 0
    for faces, c in list(chrome_islands(ob)):
        if is_target(c):
            for i in faces:
                me.polygons[i].material_index = black
            count += 1
    # drop the slot again if nothing used it (keeps draw calls unchanged)
    if count == 0 and not any(p.material_index == black for p in me.polygons):
        me.materials.pop(index=black)
    return count


def main():
    if bpy.data.filepath != BLEND:
        bpy.ops.wm.open_mainfile(filepath=BLEND)
    for lod in (0, 1, 2):
        for d in ("FL", "FR", "RL", "RR"):
            # handles sit proud of the door skin, below the belt line and behind the mirror
            n = recolour(bpy.data.objects[f"Door_{d}_LOD{lod}"],
                         lambda c: abs(c.x) > 0.88 and c.z < 0.88 and c.y < 0.3)
            print(f"Door_{d}_LOD{lod}: {n} handle island(s)")
        # side-repeater housings on the front fenders are stored in the Interior mesh
        n = recolour(bpy.data.objects[f"Interior_LOD{lod}"], lambda c: abs(c.x) > 0.88 and c.y > 1.0)
        print(f"Interior_LOD{lod}: {n} repeater island(s)")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_mainfile(filepath=BLEND, compress=False)


if __name__ == "__main__":
    main()
