# EV_Sedan - game-ready electric sedan
Generic, unbranded 4-door EV sedan (pearl white). Full technical details, dimensions, Unity/RCC setup and material/texture tables: **`EV_Sedan_TechnicalSpec.md`**.

| File | Purpose |
|---|---|
| `EV_Sedan.fbx` | LOD0 + pivot/locator hierarchy, textures relative in `textures/` |
| `EV_Sedan_LODs.fbx` | LOD0/1/2 siblings (Unity `_LODn` convention) |
| `EV_Sedan.glb` | LOD0, textures embedded, full PBR incl. clear coat |
| `EV_Sedan.blend` | Blender 4.5 source (all LODs) |
| `textures/` | PBR PNGs (`_d` colour, `_n` OpenGL normal, `_r` roughness); `unity_packed/` MetallicSmoothness |
| `preview/` | Reference renders |

Triangles: LOD0 443,925 / LOD1 155,353 / LOD2 53,251.
Photo-scanned textures are CC0 (ambientCG.com).
