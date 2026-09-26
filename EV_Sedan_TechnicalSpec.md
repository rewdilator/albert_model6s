# EV_Sedan - Technical Specification
Generated 2026-09-22 by `build_game_asset.py` (Blender 4.5 headless); Albert branding added 2026-09-25 by `tools/apply_albert_branding.py` (section 10). Target project: **Blue Horizon** (Unity 6 / URP / Realistic Car Controller V3).

## 1. Asset summary
| | |
|---|---|
| Type | **Albert** 4-door electric sedan: chrome `A+` emblems (steering wheel, front fascia, trunk, wheel caps), `ALBERT` wordmark (trunk, door sills), Albert touchscreen card. No third-party badges, logos or tyre lettering |
| Units | Metres, real-world scale (source was scaled by 0.892 to true mid-size-sedan dimensions) |
| Origin | Root `EV_Sedan` at ground level, centred between the wheels (x=0, y=0 on the ground plane) |
| Axes | Blender: +Y nose, +Z up, +X right (passenger side, LHD). FBX exported `-Z forward / Y up`, so in **Unity: nose = +Z, up = +Y, right = +X** |
| Triangles | LOD0 475,341 / LOD1 169,211 / LOD2 56,559 (source 684,315) |
| Draw calls (LOD0) | 134 sub-meshes across 23 renderers, 36 materials (additions: `Chrome_Dark` for the 3D logo, `Light_Charge` for the charge-port LED) |
| Textures | 44 PNG files (1K max); Unity packed maps in `textures/unity_packed/` |
| Texture licence | Photo-scanned sets (leather, carpet, felt, plastic, rubber, brushed metal) are **CC0** from ambientCG.com - no attribution required |

## 2. Dimensions (metres)
| Measure | Value |
|---|---|
| Overall length | 4.691 |
| Overall width (body) | 1.947 |
| Overall width (incl. mirrors) | 2.184 |
| Overall height | 1.408 |
| Wheelbase | 2.858 |
| Track front / rear | 1.659 / 1.659 |
| Front / rear overhang | 0.787 / 1.046 |
| Ground clearance (body) | 0.139 |
| Tyre radius front / rear | 0.333 / 0.339 |
| Tyre width | 0.269 |

## 3. Renderer parts (LOD0 / LOD1 / LOD2 triangles) - origins in Unity space (x, y, z)
| Object (suffix `_LODn`) | LOD0 | LOD1 | LOD2 | Mats | Parent | Origin (Unity) |
|---|---|---|---|---|---|---|
| `Door_FL` | 27,193 | 9,516 | 3,263 | 10 | `Door_FL_Pivot` | (-0.897, 0.615, 1.048) |
| `Door_FR` | 24,592 | 8,606 | 2,950 | 10 | `Door_FR_Pivot` | (0.897, 0.615, 1.048) |
| `Door_RL` | 19,480 | 6,818 | 2,337 | 9 | `Door_RL_Pivot` | (-0.922, 0.615, -0.116) |
| `Door_RR` | 19,452 | 6,808 | 2,334 | 9 | `Door_RR_Pivot` | (0.922, 0.615, -0.116) |
| `Hood` | 4,022 | 1,406 | 482 | 1 | `Hood_Pivot` | (0.0, 0.882, 1.183) |
| `Trunk` | 27,978 | 10,521 | 3,983 | 11 | `Trunk_Pivot` | (0.0, 1.203, -1.509) |
| `Bumper_F` | 25,918 | 9,227 | 3,269 | 9 | `Bumper_F_Pivot` | (0.779, 0.785, 1.723) |
| `Bumper_R` | 19,687 | 6,890 | 2,361 | 4 | `Bumper_R_Pivot` | (0.779, 0.921, -1.72) |
| `ChargePort` | 444 | 220 | 108 | 2 | `ChargePort_Pivot` | (-0.882, 0.733, -1.79) |
| `Glass` | 6,460 | 2,260 | 774 | 2 | `Chassis` | (0.0, -0.0, 0.0) |
| `Interior` | 136,365 | 49,146 | 14,908 | 14 | `Chassis` | (0.0, -0.0, 0.0) |
| `Body` | 78,419 | 27,756 | 9,475 | 14 | `Chassis` | (0.0, -0.0, 0.0) |
| `SteeringWheel` | 8,779 | 2,950 | 890 | 5 | `Steering_Pivot` | (-0.419, 0.827, 0.542) |
| `Wiper_R` | 3,138 | 1,097 | 375 | 1 | `Wiper_R_Pivot` | (-0.074, 0.829, 1.431) |
| `Wiper_L` | 3,045 | 1,065 | 364 | 1 | `Wiper_L_Pivot` | (-0.629, 0.859, 1.266) |
| `Brake_FL` | 2,504 | 876 | 299 | 1 | `EV_Sedan` | (0.0, 0.0, 0.0) |
| `Brake_FR` | 2,504 | 876 | 299 | 1 | `EV_Sedan` | (0.0, 0.0, 0.0) |
| `Brake_RL` | 2,793 | 976 | 335 | 1 | `EV_Sedan` | (0.0, 0.0, 0.0) |
| `Brake_RR` | 2,793 | 976 | 335 | 1 | `EV_Sedan` | (0.0, 0.0, 0.0) |
| `Wheel_FL` | 14,947 | 5,307 | 1,855 | 7 | `EV_Sedan` | (-0.829, 0.339, 1.567) |
| `Wheel_FR` | 14,941 | 5,304 | 1,854 | 7 | `EV_Sedan` | (0.829, 0.339, 1.567) |
| `Wheel_RL` | 14,942 | 5,304 | 1,854 | 7 | `EV_Sedan` | (-0.829, 0.339, -1.291) |
| `Wheel_RR` | 14,945 | 5,306 | 1,855 | 7 | `EV_Sedan` | (0.829, 0.339, -1.291) |

## 4. Pivots and locators (empties)
Pivot empties are pure translations (no rotation/scale). Child meshes have their origin **on** the pivot, so rotating the mesh in local space swings the part on its hinge.

| Empty | Unity (x, y, z) | Blender (x, y, z) |
|---|---|---|
| `Bumper_F_Pivot` | (0.779, 0.785, 1.723) | (0.779, 1.723, 0.785) |
| `Bumper_R_Pivot` | (0.779, 0.921, -1.72) | (0.779, -1.72, 0.921) |
| `ChargePort_Pivot` | (-0.882, 0.733, -1.79) | (-0.882, -1.79, 0.733) |
| `Chassis` | (0.0, 0.67, 0.0) | (0.0, 0.0, 0.67) |
| `Door_FL_Pivot` | (-0.897, 0.615, 1.048) | (-0.897, 1.048, 0.615) |
| `Door_FR_Pivot` | (0.897, 0.615, 1.048) | (0.897, 1.048, 0.615) |
| `Door_RL_Pivot` | (-0.922, 0.615, -0.116) | (-0.922, -0.116, 0.615) |
| `Door_RR_Pivot` | (0.922, 0.615, -0.116) | (0.922, -0.116, 0.615) |
| `EV_Sedan` | (0.0, 0.67, 0.0) | (0.0, 0.0, 0.67) |
| `Hood_Pivot` | (0.0, 0.882, 1.183) | (0.0, 1.183, 0.882) |
| `Loc_Brakelight_L1` | (-0.236, 1.113, -1.907) | (-0.236, -1.907, 1.113) |
| `Loc_Brakelight_L2` | (-0.684, 0.861, -2.091) | (-0.684, -2.091, 0.861) |
| `Loc_Brakelight_L3` | (-0.126, 1.113, -1.922) | (-0.126, -1.922, 1.113) |
| `Loc_Brakelight_L4` | (-0.042, 1.113, -1.938) | (-0.042, -1.938, 1.113) |
| `Loc_Brakelight_R1` | (0.239, 1.113, -1.907) | (0.239, -1.907, 1.113) |
| `Loc_Brakelight_R2` | (0.692, 0.861, -2.091) | (0.692, -2.091, 0.861) |
| `Loc_Brakelight_R3` | (0.128, 1.113, -1.922) | (0.128, -1.922, 1.113) |
| `Loc_Brakelight_R4` | (0.042, 1.113, -1.938) | (0.042, -1.938, 1.113) |
| `Loc_ChargePort` | (-0.832, 0.739, -1.841) | (-0.832, -1.841, 0.739) |
| `Loc_Engine` | (0.0, 0.88, 1.519) | (0.0, 1.519, 0.88) |
| `Loc_Exhaust` | (0.0, 0.418, -1.106) | (0.0, -1.106, 0.418) |
| `Loc_Foglight_L` | (-0.732, 0.401, 2.155) | (-0.732, 2.155, 0.401) |
| `Loc_Foglight_R` | (0.731, 0.401, 2.155) | (0.731, 2.155, 0.401) |
| `Loc_Headlight_R` | (0.579, 0.646, 2.017) | (0.579, 2.017, 0.646) |
| `Loc_Hood_Damage` | (0.0, 0.872, 1.641) | (0.0, 1.641, 0.872) |
| `Loc_Hood_Latch` | (0.0, 0.852, 1.744) | (0.0, 1.744, 0.852) |
| `Loc_Indicator_FL` | (-0.751, 0.681, 1.927) | (-0.751, 1.927, 0.681) |
| `Loc_Indicator_FR` | (0.751, 0.681, 1.929) | (0.751, 1.929, 0.681) |
| `Loc_Indicator_RL` | (-0.545, 0.865, -2.152) | (-0.545, -2.152, 0.865) |
| `Loc_Indicator_RR` | (0.547, 0.865, -2.152) | (0.547, -2.152, 0.865) |
| `Loc_Rear_Aux` | (-0.09, 0.769, -3.263) | (-0.09, -3.263, 0.769) |
| `Loc_Reverse_L` | (-0.546, 0.867, -2.153) | (-0.546, -2.153, 0.867) |
| `Loc_Reverse_R` | (0.549, 0.867, -2.153) | (0.549, -2.153, 0.867) |
| `Loc_Roof` | (0.0, 1.163, -1.633) | (0.0, -1.633, 1.163) |
| `Loc_Seat_Arm` | (-0.861, 0.979, 0.173) | (-0.861, 0.173, 0.979) |
| `Loc_Seat_Front` | (0.428, 0.542, 0.227) | (0.428, 0.227, 0.542) |
| `Loc_Seat_Rear` | (0.385, 0.604, -0.66) | (0.385, -0.66, 0.604) |
| `Loc_Spoiler` | (0.0, 1.047, -2.164) | (0.0, -2.164, 1.047) |
| `Loc_Spoiler_Damage` | (0.01, 1.066, -2.086) | (0.01, -2.086, 1.066) |
| `Loc_Taillight_R` | (0.765, 0.848, -1.999) | (0.765, -1.999, 0.848) |
| `Steering_Pivot` | (-0.419, 0.827, 0.542) | (-0.419, 0.542, 0.827) |
| `Trunk_Pivot` | (0.0, 1.203, -1.509) | (0.0, -1.509, 1.203) |
| `Wiper_L_Pivot` | (-0.629, 0.859, 1.266) | (-0.629, 1.266, 0.859) |
| `Wiper_R_Pivot` | (-0.074, 0.829, 1.431) | (-0.074, 1.431, 0.829) |

All four doors, the hood (frunk, with its own tub), the trunk and the charge-port door are separate meshes on their own pivots, so each opens independently; `Unity/AlbertEV/Runtime/AlbertCarOpenings.cs` animates them (section 12).

Hinge axes (Unity local space):
- `Door_FL/FR/RL/RR` - rotate about **Y** (vertical). Open 65°: **left doors +65°, right doors −65°** (earlier revisions of this file had the signs swapped). Hinges are at the front edge of each door.
- `Hood` - rotate about **X** (`Hood_Pivot` is at the cowl edge); open -45°.
- `ChargePort` - rotate about **Y** (hinge at the door's front edge); open **+100°**.
- `Trunk` - rotate about **X** (`Trunk_Pivot` at the rear-glass edge); open +60°.
- `SteeringWheel` - rotate about the wheel-plane normal (tilted ~25° from Z); ±450° lock-to-lock. RCC's "Steering Wheel" slot accepts it directly.
- `Wheel_*` - spin about **X**, steer about **Y** (front). Origin at hub centre; RCC drives them from the WheelColliders.
- `Wiper_L/R` - rotate about **Z** (local) at the pivot; sweep ~60°.
- `Bumper_F/R` - separate meshes under pivots for detachable/damage bumpers.

## 5. Suggested vehicle physics (RCC V3 `RCC_CarControllerV3` on `EV_Sedan`)
| Parameter | Suggested | Note |
|---|---|---|
| Mass | 1,750 kg | mid-size EV with floor battery |
| Centre of mass (`COM` child) | (0.00, 0.30, 0.15) | 0.30 m above ground, slightly forward of the wheelbase centre |
| Wheelbase / track | 2.858 / 1.659 | from mesh |
| WheelCollider radius | 0.333 m | same for all four |
| Suspension distance | 0.16 m | spring 45,000 N/m, damper 4,500 |
| Wheel positions | `Wheel_*` origins in table 3 | create colliders with RCC's "Create Wheel Colliders" using the four `Wheel_*_LOD0` transforms as wheel models |
| Drive | AWD (or RWD) | EV: max torque ~450 Nm flat, single speed - 1 gear ratio ~9.0 (or RCC electric preset) |
| Max speed | 225 km/h | |
| Brake torque | 3,000 Nm | |
| Steer angle | 38° | |
| Drag | 0.23 Cd, frontal area 2.2 m² | Rigidbody drag ≈ 0.02 |
| Body collider | `MeshCollider` (convex) on `Body_LOD2` mesh + a `BoxCollider` per door, hood, trunk and bumper | keep glass/interior out of collision; *Tools > Albert EV > Add Colliders* sets this up |

RCC lights: add `RCC_Light` objects at `Loc_Headlight_R` (mirror x for left), `Loc_Taillight_R` (mirror), `Loc_Brakelight_*`, `Loc_Indicator_*`, `Loc_Reverse_*`, `Loc_Foglight_*`.
Drive the lamp *meshes* by animating the emission of `Light_Head`, `Light_Tail`, `Light_Indicator`, `Light_Reverse`, `Light_Fog`, `Light_Interior` (all use `ev_sedan_lights_d` as emission colour; emission 0 = off).

## 6. Unity import settings (FBX)
Everything in this section is applied automatically by `Unity/AlbertEV/Editor/AlbertEVImport.cs` (section 12).

- Model: Scale Factor 1, Convert Units on, Bake Axis Conversion **on**, Read/Write off (turn it on only if you use RCC mesh damage), Mesh Compression off, Optimize Mesh on, Generate Lightmap UVs off, no animation / cameras / lights / blend shapes.
- Normals: Import; Tangents: Calculate Mikktspace; Smoothness Source: From Smoothing Groups.
- Materials: extract; shader **Universal Render Pipeline/Lit**, Metallic workflow (see section 7).
- `EV_Sedan_LODs.fbx` imports with an automatic `LODGroup` per part (`Name_LOD0/1/2` siblings). Transitions: LOD0 ≥ 45 %, LOD1 ≥ 15 %, LOD2 ≥ 1.5 %, culled below. Glass and the far-LOD interior / steering wheel / brakes do not cast shadows.
- Normal maps: Texture Type = Normal map, sRGB off. Files are OpenGL (+Y) - same as Unity - **do not** flip green.
- `unity_packed/*_ms.png`: sRGB **off**; URP/Lit *Metallic Map* (R = metallic, A = smoothness).
- `_r` roughness maps are for Blender / Unreal / glTF; in URP use the packed `_ms` instead.

## 7. Materials
| Material | Render mode | Base colour (linear) | Metallic | Roughness | Clear coat | Alpha | Emission | Textures | Used for |
|---|---|---|---|---|---|---|---|---|---|
| `Paint_Body` | Opaque | (0.86, 0.87, 0.85) | 0.18 | 0.3 | 1.0 | 1.0 | 0.0 | - | Pearl-white car paint; recolour via Base Color |
| `Trim_Black_Gloss` | Opaque | (0.008, 0.008, 0.009) | 0.0 | 0.12 | 0.6 | 1.0 | 0.0 | - | Piano-black pillars, lower trims, wheel caps, door handles, front / rear badge faces, fender side-repeater housings, steering-wheel emblem plaque + thumbwheel pods |
| `Plastic_Black_Satin` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.45 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_plastic_black_d.png`, Normal: `ev_sedan_plastic_black_n.png`, Roughness: `ev_sedan_plastic_black_r.png` | Satin exterior plastics, lamp housings |
| `Plastic_Black_Matte` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.7 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_plastic_black_d.png`, Normal: `ev_sedan_plastic_black_n.png`, Roughness: `ev_sedan_plastic_black_r.png` | Grained interior plastics, dash, door cards, underbody, `ALBERT` sill-plate inlay |
| `Fabric_Dark` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.95 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_fabric_dark_d.png`, Normal: `ev_sedan_fabric_dark_n.png`, Roughness: `ev_sedan_fabric_dark_r.png` | Headliner / trunk felt |
| `Chrome` | Opaque | (0.92, 0.92, 0.93) | 1.0 | 0.06 | 0.0 | 1.0 | 0.0 | - | Window belt-line trim, badge rims and ledges, wheel-cap `A+`, steering-wheel thumbwheels |
| `Chrome_Dark` | Opaque | (0.16, 0.16, 0.17) | 1.0 | 0.1 | 0.0 | 1.0 | 0.0 | - | Faceted strokes of the 3D `A+` logo (nose, steering wheel) |
| `Aluminium_Brushed` | Opaque | (0.8, 0.8, 0.8) | 1.0 | 0.38 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_aluminium_d.png`, Normal: `ev_sedan_aluminium_n.png`, Roughness: `ev_sedan_aluminium_r.png` | Brushed dash / door trim strips, door-sill plates |
| `Metal_Dark` | Opaque | (0.22, 0.22, 0.23) | 0.85 | 0.6 | 0.0 | 1.0 | 0.0 | - | Suspension, dust shields |
| `Light_Housing` | Opaque | (0.85, 0.85, 0.87) | 1.0 | 0.22 | 0.0 | 1.0 | 0.0 | - | Reflector bowls inside lamps |
| `Glass_Window` | Transparent (alpha blend) | (0.45, 0.5, 0.52) | 0.0 | 0.02 | 0.0 | 0.32 | 0.0 | - | Windscreen + side glass |
| `Glass_Roof` | Transparent (alpha blend) | (0.12, 0.13, 0.14) | 0.0 | 0.02 | 0.0 | 0.62 | 0.0 | - | Tinted glass roof / rear glass |
| `Lens_Clear` | Transparent (alpha blend) | (0.8, 0.85, 0.9) | 0.0 | 0.02 | 0.0 | 0.22 | 0.0 | - | Headlamp cover |
| `Lens_Red` | Transparent (alpha blend) | (0.6, 0.015, 0.015) | 0.0 | 0.05 | 0.0 | 0.55 | 0.0 | - | Tail-lamp cover, high-mount brake lens |
| `Light_Head` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 1.0 | BaseColor: `ev_sedan_lights_d.png` | Headlamp DRL/low beam emitters |
| `Light_Fog` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 0.0 | BaseColor: `ev_sedan_lights_d.png` | Front fog lamps |
| `Light_Tail` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 1.0 | BaseColor: `ev_sedan_lights_d.png` | Tail / brake emitters |
| `Light_Indicator` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 0.0 | BaseColor: `ev_sedan_lights_d.png` | Turn indicators (4) |
| `Light_Reverse` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 0.0 | BaseColor: `ev_sedan_lights_d.png` | Reverse lamps |
| `Light_Interior` | Alpha clip/hashed | (0.8, 0.8, 0.8) | 0.0 | 0.3 | 0.0 | texture | 0.0 | BaseColor: `ev_sedan_lights_d.png` | Dome light |
| `Reflector_Red` | Opaque | (0.5, 0.01, 0.01) | 0.4 | 0.2 | 0.0 | 1.0 | 0.25 | - | Rear bumper reflectors |
| `Tyre_Tread` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.8 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_tyre_d.png`, Normal: `ev_sedan_tyre_n.png`, Roughness: `ev_sedan_tyre_r.png` | Tyre tread + outer sidewall |
| `Tyre_Sidewall` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.75 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_tyre_side_d.png`, Normal: `ev_sedan_tyre_side_n.png`, Roughness: `ev_sedan_tyre_side_r.png` | Tyre inner sidewall |
| `Rim` | Opaque | (0.8, 0.8, 0.8) | 1.0 | 0.22 | 0.8 | 1.0 | 0.0 | BaseColor: `ev_sedan_rim_d.png` | Alloy wheel (clear-coated silver) |
| `Brake_Disc` | Opaque | (0.8, 0.8, 0.8) | 0.9 | 0.42 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_brake_disc_d.png` | Brake disc |
| `Brake_Caliper` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.35 | 0.5 | 1.0 | 0.0 | BaseColor: `ev_sedan_caliper_d.png` | Red brake caliper |
| `Leather_Black` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.55 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_leather_black_d.png`, Normal: `ev_sedan_leather_black_n.png`, Roughness: `ev_sedan_leather_black_r.png` | Black leather (dash top, wheel, armrests), headrest `A+` embroidery |
| `Leather_White` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.5 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_leather_white_d.png`, Normal: `ev_sedan_leather_white_n.png`, Roughness: `ev_sedan_leather_white_r.png` | White leather (seats, door inserts) |
| `Carpet` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.95 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_carpet_d.png`, Normal: `ev_sedan_carpet_n.png`, Roughness: `ev_sedan_carpet_r.png` | Floor carpet + mats |
| `Belt` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.8 | 0.0 | 1.0 | 0.0 | BaseColor: `ev_sedan_belt_d.png`, Normal: `ev_sedan_belt_n.png`, Roughness: `ev_sedan_belt_r.png` | Seat belts |
| `Buttons` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.4 | 0.0 | 1.0 | 0.6 | BaseColor: `ev_sedan_buttons_d.png` | Stalk / switch icons |
| `Screen` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.08 | 0.0 | 1.0 | 1.6 | BaseColor: `ev_sedan_screen_d.png` | Centre touchscreen (Albert vehicle card) |
| `Mirror` | Opaque | (0.95, 0.95, 0.95) | 1.0 | 0.0 | 0.0 | 1.0 | 0.0 | - | Mirror glass |
| `Plate` | Opaque | (0.8, 0.8, 0.8) | 0.0 | 0.35 | 0.4 | 1.0 | 0.0 | BaseColor: `ev_sedan_plate_d.png`, Normal: `ev_sedan_plate_n.png` | License plate (embossed) |
| `Light_Charge` | Opaque | (0.05, 0.85, 0.25) | 0.0 | 0.3 | 0.0 | 1.0 | 3.0 | - | Charge-port status LED ring (animate emission for charging states) |
| `Accent_Red` | Opaque | (0.45, 0.02, 0.02) | 0.0 | 0.4 | 0.0 | 1.0 | 0.0 | - | Red accent (seat-belt buckles) |

URP/Lit mapping: Base Map ← `*_d`, Normal Map ← `*_n`, Metallic Map ← `unity_packed/*_ms` (Smoothness Source: Metallic Alpha). Untextured materials: constant colour, metallic and smoothness = 1 − roughness.
Clear-coat paint: URP **Complex Lit** with Clear Coat (mask 1, smoothness 0.98) or HDRP Lit.
`Glass_*`, `Lens_*`: Surface Type Transparent, Blending Alpha, Render Face Front, colour alpha = value in the table.
`Light_*`: Surface Type Transparent (or Alpha Clip 0.5), Emission map = Base Map, HDR intensity per group.

## 8. Textures
| File | Size | Colour space | Usage |
|---|---|---|---|
| `textures/ev_sedan_aluminium_d.png` | 1024² | sRGB | Brushed aluminium trim - base colour |
| `textures/ev_sedan_aluminium_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Brushed aluminium trim - tangent normal |
| `textures/ev_sedan_aluminium_r.png` | 1024² | Linear | Brushed aluminium trim - roughness |
| `textures/ev_sedan_belt_d.png` | 512² | sRGB | Seat-belt webbing (procedural twill) - base colour |
| `textures/ev_sedan_belt_n.png` | 512² | Linear (Normal map, OpenGL +Y) | Seat-belt webbing (procedural twill) - tangent normal |
| `textures/ev_sedan_belt_r.png` | 512² | Linear | Seat-belt webbing (procedural twill) - roughness |
| `textures/ev_sedan_brake_disc_d.png` | 256² | sRGB | Brake disc - base colour |
| `textures/ev_sedan_buttons_d.png` | 1024² | sRGB | Stalk / button icons (emissive) |
| `textures/ev_sedan_caliper_d.png` | 256² | sRGB | Brake caliper - base colour |
| `textures/ev_sedan_carpet_d.png` | 1024² | sRGB | Charcoal loop-pile carpet - base colour |
| `textures/ev_sedan_carpet_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Charcoal loop-pile carpet - tangent normal |
| `textures/ev_sedan_carpet_r.png` | 1024² | Linear | Charcoal loop-pile carpet - roughness |
| `textures/ev_sedan_fabric_dark_d.png` | 1024² | sRGB | Dark felt (headliner, trunk lining) - base colour |
| `textures/ev_sedan_fabric_dark_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Dark felt (headliner, trunk lining) - tangent normal |
| `textures/ev_sedan_fabric_dark_r.png` | 1024² | Linear | Dark felt (headliner, trunk lining) - roughness |
| `textures/ev_sedan_leather_black_d.png` | 1024² | sRGB | Black leather (dash, steering wheel) - base colour |
| `textures/ev_sedan_leather_black_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Black leather (dash, steering wheel) - tangent normal |
| `textures/ev_sedan_leather_black_r.png` | 1024² | Linear | Black leather (dash, steering wheel) - roughness |
| `textures/ev_sedan_leather_white_d.png` | 1024² | sRGB | White leather (seats, door inserts) - base colour |
| `textures/ev_sedan_leather_white_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | White leather (seats, door inserts) - tangent normal |
| `textures/ev_sedan_leather_white_r.png` | 1024² | Linear | White leather (seats, door inserts) - roughness |
| `textures/ev_sedan_lights_d.png` | 1024² | sRGB | Lamp atlas - colour + alpha, also emission |
| `textures/ev_sedan_plastic_black_d.png` | 1024² | sRGB | Grained black plastic (dash, door cards, trims) - base colour |
| `textures/ev_sedan_plastic_black_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Grained black plastic (dash, door cards, trims) - tangent normal |
| `textures/ev_sedan_plastic_black_r.png` | 1024² | Linear | Grained black plastic (dash, door cards, trims) - roughness |
| `textures/ev_sedan_plate_d.png` | 1024² | sRGB | License plate - base colour |
| `textures/ev_sedan_plate_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | License plate - embossed characters |
| `textures/ev_sedan_rim_d.png` | 1024² | sRGB | Alloy rim - silver with baked occlusion |
| `textures/ev_sedan_screen_d.png` | 1024² | sRGB | Centre screen Albert UI (emissive), drawn on a 1306×1024 canvas squeezed to square |
| `textures/ev_sedan_tyre_d.png` | 1024² | sRGB | Tyre tread + outer sidewall (radial layout) - base colour |
| `textures/ev_sedan_tyre_n.png` | 1024² | Linear (Normal map, OpenGL +Y) | Tyre tread + outer sidewall (radial layout) - tangent normal |
| `textures/ev_sedan_tyre_r.png` | 1024² | Linear | Tyre tread + outer sidewall (radial layout) - roughness |
| `textures/ev_sedan_tyre_side_d.png` | 512² | sRGB | Tyre inner sidewall strip - base colour |
| `textures/ev_sedan_tyre_side_n.png` | 512² | Linear (Normal map, OpenGL +Y) | Tyre inner sidewall strip - tangent normal |
| `textures/ev_sedan_tyre_side_r.png` | 512² | Linear | Tyre inner sidewall strip - roughness |
| `textures/unity_packed/ev_sedan_aluminium_ms.png` | 1024² | Linear (sRGB off) | Brushed aluminium trim - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_belt_ms.png` | 512² | Linear (sRGB off) | Seat-belt webbing (procedural twill) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_carpet_ms.png` | 1024² | Linear (sRGB off) | Charcoal loop-pile carpet - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_fabric_dark_ms.png` | 1024² | Linear (sRGB off) | Dark felt (headliner, trunk lining) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_leather_black_ms.png` | 1024² | Linear (sRGB off) | Black leather (dash, steering wheel) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_leather_white_ms.png` | 1024² | Linear (sRGB off) | White leather (seats, door inserts) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_plastic_black_ms.png` | 1024² | Linear (sRGB off) | Grained black plastic (dash, door cards, trims) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_tyre_ms.png` | 1024² | Linear (sRGB off) | Tyre tread + outer sidewall (radial layout) - URP MetallicSmoothness (R=metallic, A=smoothness) |
| `textures/unity_packed/ev_sedan_tyre_side_ms.png` | 512² | Linear (sRGB off) | Tyre inner sidewall strip - URP MetallicSmoothness (R=metallic, A=smoothness) |

UV notes: white/black leather, carpet, belt and aluminium tile with the original UVs (≈0.128 m per UV unit on leather, 0.35 m on carpet, 0.054 m = belt width). Black plastics and felt were re-projected (box projection, 0.30 m and 0.50 m per UV unit). Tyre tread uses a radial layout (tread in the centre square, sidewall ring around it); the inner sidewall strip tiles 7.5× around the circumference.

## 9. Known limitations
- Body silhouette is still the source car's shape; only branding, textures, materials, scale and topology were changed.
- Interior is a single renderer (`Interior`); split it if you need a separate first-person cull.
- Doors contain their own glass/inner panel; no separate per-door window renderer.
- No blend shapes. RCC mesh damage works on the `Body_LOD0` MeshFilter; add door/bumper MeshFilters to the damage list if wanted (needs Read/Write enabled on the FBX).
- FBX does not carry clear-coat or roughness maps into Unity's importer - use the tables above.

## 10. Albert branding
All badges are real geometry built from the vector outlines in `tools/albert_brand.py`, wrapped onto the panel they sit on and **joined into that part's mesh on every LOD**, so they move with the part (the steering-wheel emblem turns with the wheel, cap emblems spin with the wheels, the nose badge detaches with `Bumper_F`). No new renderers, materials or textures were added.

| Badge | Part (`_LOD0/1/2`) | Size | Build | Material |
|---|---|---|---|---|
| Steering-wheel logo | `SteeringWheel` | 3D `A+` 42 mm tall | Faceted 3D logo (see below) straight on the airbag cover | `Chrome_Dark`, `Chrome`, `Trim_Black_Gloss` |
| Steering-wheel thumbwheels | `SteeringWheel` | Ø 15 mm × 10 mm in 21 × 31 mm pods, 85 mm either side of centre | Knurled chrome rollers (36 ridges) in gloss-black pods; LOD0/1 only | `Chrome`, `Trim_Black_Gloss` |
| Nose logo | `Bumper_F` | 3D `A+` 72 mm tall, 89 mm wide | Faceted 3D logo on the front fascia centre line, where the source car carried its maker's badge | `Chrome_Dark`, `Chrome`, `Trim_Black_Gloss` |
| Trunk wordmark | `Trunk` | `ALBERT` 36 mm cap height, 27 cm wide | Wordmark only (no logo): gloss-black letters on a chrome rim, centred between the tail lamps | `Trim_Black_Gloss`, `Chrome` |
| Wheel-cap emblems | `Wheel_FL/FR/RL/RR` | `A+` 25 mm tall | Chrome, upright when the wheel is at rest | `Chrome` |
| Door-sill plates | `Interior` | 380 × 34 mm, `ALBERT` 15 mm cap height | Brushed-aluminium plate with black inlay on both front sills, readable from outside; LOD0/1 only | `Aluminium_Brushed`, `Plastic_Black_Matte` |
| Headrest embroidery | `Interior` | `A+` 40 mm tall | Dark raised stitching on both front headrests; LOD0/1 only | `Leather_Black` |
| Phone pads | `Interior` | 2 × 86 × 125 mm | Rubberised wireless-charging pads on the console tray, small brushed-aluminium `A+` each; LOD0/1 | `Plastic_Black_Matte`, `Aluminium_Brushed` |
| Rear console | `Interior` | 148 × 88 mm display | Rear-passenger touchscreen in a gloss bezel (shows the vehicle card of the main UI), two louvred air vents, two USB-C ports; LOD0/1 | `Screen`, `Trim_Black_Gloss`, `Metal_Dark`, `Chrome` |
| Touchscreen | `Interior` (`Screen`) | - | Full Albert UI in `ev_sedan_screen_d.png`: gear / speed, battery / range, car render, frunk / trunk / lock buttons, media, turn-by-turn navigation map, climate and app dock | `Screen` |

- Door handles (all four doors) and the fender side-repeater housings are gloss black (`Trim_Black_Gloss`) like the production car, instead of chrome (`tools/apply_black_trim.py`).
- The touchscreen UVs were flipped vertically: the source mapped the UI upside down. It now shows the right way up in Blender and Unity.
- **3D logo** (from the reference artwork): a bold A with a flat apex and a "+" overlapping its right leg. Every stroke is a convex bar with a hip roof whose planar facets meet at a central ridge; where strokes overlap their roofs cross in crisp creases, giving the diamond-cut look. Layers: gloss-black border (outline + 3.5 % of cap height), thin chrome ledge, dark-chrome faceted strokes; the "+" stands proud of the A on its own wider black frame. Flat uses (wheel caps, headrests, phone pads, touchscreen, `brand/` files) use the silhouette with a clearance gap cut round the "+".
- Logo files for menus, loading screens and decals are in `brand/` (SVG + transparent PNG, white and black), plus `albert_logo_3d.png` (transparent studio render of the 3D badge) and `albert_car_render.png`, a transparent render of the car for garage / selection screens.
- Branding is applied by `tools/apply_albert_branding.py` on the unbranded `.blend`; the FBX files are exported by `tools/export_fbx.py` with the same settings as the original build (FBX 7.4, `-Z` forward / `Y` up, edge smoothing, tangents, relative texture paths).

## 11. Charge port
Rear-left quarter panel, between the wheel arch and the tail lamp (`tools/add_charge_port.py`).
- **Door** `ChargePort_LOD0/1/2` under `ChargePort_Pivot`: 125 × 115 mm, body-coloured outside, black inside, 1.5 mm panel gap; hinged at its front edge, opens +100° about Y in Unity (`CarOpening.ChargePort`).
- **Pocket** cut through the body skin and trunk lining, 45 mm deep, joined into `Body`.
- **Inlet** CCS2: Type 2 AC socket (flat-topped, 7 contacts incl. PP/CP) above a 2-pin DC socket, with metal contact pins recessed 4 mm and a green status-LED ring (`Light_Charge`: set its emission to 0 when not charging, or pulse it while charging).
- `Loc_ChargePort` sits on the socket face: attach the charging-cable plug there.

## 12. Unity quick start (Unity 6 / URP)
1. Copy `EV_Sedan_LODs.fbx` (or `EV_Sedan.fbx`), the `textures/` folder and `Unity/AlbertEV/` into one folder under `Assets/`, e.g. `Assets/AlbertEV/`. The import settings from section 6 are applied automatically by `AlbertEVImport.cs`.
2. **Tools > Albert EV > Create URP Materials** builds the 36 URP/Lit materials from section 7 (textures, packed metallic/smoothness, transparency, alpha-clipped lamps with emission ready to animate) in a `Materials/` folder and remaps them onto both FBX files.
3. Drag the model into the scene, select it and run **Tools > Albert EV > Add Colliders To Selected Car** and **Add Openings Component To Selected Car**. Add your Rigidbody / RCC controller to the root as in section 5.
4. Open things from code or from the component's ⋮ menu in the Inspector:
   ```csharp
   var car = GetComponent<AlbertEV.AlbertCarOpenings>();
   car.Toggle(AlbertEV.CarOpening.DoorFrontLeft);   // DoorFrontRight, DoorRearLeft, DoorRearRight, Hood, Trunk, ChargePort
   car.SetOpen(AlbertEV.CarOpening.Trunk, true, instant: true);
   ```
   The component rotates the `*_Pivot` objects, so all LODs, door glass, handles and badges move together. Hinge axes are derived from the model, so it works with any import orientation.

Performance notes: LOD0 is a hero-quality 475k triangles; with the LOD transitions above a car at normal gameplay distance renders LOD1 (169k) or LOD2 (56k). All materials use the same URP/Lit shader and have GPU instancing on, so the SRP Batcher keeps the ~135 sub-meshes cheap. Textures are 1K with streaming mip maps.

