# Albert EV sedan - game-ready electric sedan
4-door EV sedan (pearl white) wearing the **Albert** brand: chrome **A+** emblems on the steering wheel, front fascia, trunk and wheel centre caps, an **ALBERT** wordmark on the trunk and door sills, and Albert branding on the centre touchscreen. Full technical details, dimensions, Unity/RCC setup and material/texture tables: **`EV_Sedan_TechnicalSpec.md`**.

| File | Purpose |
|---|---|
| `EV_Sedan.fbx` | LOD0 + pivot/locator hierarchy, textures relative in `textures/` |
| `EV_Sedan_LODs.fbx` | LOD0/1/2 siblings (Unity `_LODn` convention) |
| `EV_Sedan.blend` | Blender 4.5 source (all LODs) |
| `textures/` | PBR PNGs (`_d` colour, `_n` OpenGL normal, `_r` roughness); `unity_packed/` MetallicSmoothness |
| `brand/` | Albert logo files for your game UI: `A+` emblem, `ALBERT` wordmark and stacked lockup as SVG + transparent PNG (white / black) |
| `tools/` | Scripts that build the branding, export the FBX files and render the previews (see below) |
| `preview/` | Reference renders |

Triangles: LOD0 463,077 / LOD1 162,585 / LOD2 53,959.
Photo-scanned textures are CC0 (ambientCG.com).

## Rebuilding
All scripts run with Blender 4.5 (`blender -b -P <script>`) or with the `bpy` Python module (`pip install bpy==4.5.*`, Python 3.11):

1. `python3 tools/make_brand_assets.py` - writes `brand/` and the Albert card on `textures/ev_sedan_screen_d.png` (needs Pillow).
2. `python3 tools/apply_albert_branding.py` - adds the 3D badges to `EV_Sedan.blend` (runs once per file; it refuses to brand a file twice).
3. `python3 tools/export_fbx.py` - re-exports both FBX files.
4. `python3 tools/render_previews.py [shot ...]` - re-renders `preview/` with Cycles.

The logo and wordmark outlines live in `tools/albert_brand.py`; change them there and rerun the steps on the unbranded `.blend` to restyle every badge at once.
