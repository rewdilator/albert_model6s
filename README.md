# Albert EV sedan - game-ready electric sedan
4-door EV sedan (pearl white) wearing the **Albert** brand, with independently opening doors, frunk, trunk and a detailed CCS2 charge port: black-and-chrome **A+** badges on the nose and trunk with a large **ALBERT** wordmark, chrome **A+** on the steering wheel and wheel caps, embroidered **A+** headrests, **ALBERT** door-sill plates and a full Albert touchscreen UI. Full technical details, dimensions, Unity/RCC setup and material/texture tables: **`EV_Sedan_TechnicalSpec.md`**.

| File | Purpose |
|---|---|
| `EV_Sedan.fbx` | LOD0 + pivot/locator hierarchy, textures relative in `textures/` |
| `EV_Sedan_LODs.fbx` | LOD0/1/2 siblings (Unity `_LODn` convention) |
| `EV_Sedan.blend` | Blender 4.5 source (all LODs) |
| `textures/` | PBR PNGs (`_d` colour, `_n` OpenGL normal, `_r` roughness); `unity_packed/` MetallicSmoothness |
| `brand/` | Albert logo files for your game UI: `A+` emblem, `ALBERT` wordmark and stacked lockup as SVG + transparent PNG (white / black), and a transparent car render |
| `Unity/AlbertEV/` | Unity scripts: automatic optimized import settings, one-click URP materials + colliders, and `AlbertCarOpenings` to open each door, the hood (frunk), trunk and charge port independently. See spec section 12 |
| `tools/` | Scripts that build the branding, export the FBX files and render the previews (see below) |
| `preview/` | Reference renders |

Triangles: LOD0 477,525 / LOD1 169,387 / LOD2 56,419.
Photo-scanned textures are CC0 (ambientCG.com).

## Rebuilding
All scripts run with Blender 4.5 (`blender -b -P <script>`) or with the `bpy` Python module (`pip install bpy==4.5.*`, Python 3.11):

1. `python3 tools/make_brand_assets.py` - writes `brand/` and draws the touchscreen UI into `textures/ev_sedan_screen_d.png` (needs Pillow).
2. `python3 tools/apply_albert_branding.py` - adds the 3D badges to `EV_Sedan.blend` (runs once per file; it refuses to brand a file twice).
3. `python3 tools/apply_black_trim.py` - gloss-black door handles and fender side-repeaters.
4. `python3 tools/add_charge_port.py` - opening charge-port door, pocket and CCS2 inlet.
5. `python3 tools/add_interior_details.py` - wireless phone pads, rear console screen, vents and USB-C.
6. `python3 tools/export_fbx.py` - re-exports both FBX files.
7. `python3 tools/render_previews.py [shot ...]` - re-renders `preview/` with Cycles.

Steps 2, 4 and 5 run once on the unbranded `.blend` (`git show 090bcaa:EV_Sedan.blend > EV_Sedan.blend`) and refuse to run twice.

The logo and wordmark outlines live in `tools/albert_brand.py`; change them there and rerun the steps on the unbranded `.blend` to restyle every badge at once.
