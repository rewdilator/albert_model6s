"""Export the Unity FBX files from EV_Sedan.blend (same settings as the original build).

  EV_Sedan.fbx       LOD0 meshes + the full pivot / locator hierarchy
  EV_Sedan_LODs.fbx  LOD0/1/2 siblings (Unity LODGroup naming)

Run: python3 tools/export_fbx.py   (bpy pip module)  or  blender -b EV_Sedan.blend -P tools/export_fbx.py
"""
import os

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS = dict(
    use_selection=True,
    object_types={"EMPTY", "MESH"},
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_NONE",
    axis_forward="-Z",
    axis_up="Y",
    use_mesh_modifiers=True,
    mesh_smooth_type="EDGE",
    use_tspace=True,
    add_leaf_bones=False,
    bake_anim=False,
    path_mode="RELATIVE",
    embed_textures=False,
)


def export(path, lods):
    for o in bpy.context.view_layer.objects:
        keep = o.type == "EMPTY" or (o.type == "MESH" and any(o.name.endswith(f"_LOD{i}") for i in lods))
        o.select_set(keep)
    bpy.ops.export_scene.fbx(filepath=path, **SETTINGS)
    print("exported", path)


def main():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, "EV_Sedan.blend"))
    export(os.path.join(ROOT, "EV_Sedan.fbx"), lods=(0,))
    export(os.path.join(ROOT, "EV_Sedan_LODs.fbx"), lods=(0, 1, 2))


if __name__ == "__main__":
    main()
