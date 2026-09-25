using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace AlbertEV.EditorTools
{
    /// <summary>
    /// Tools > Albert EV menu:
    ///   Create URP Materials   - builds the 34 URP/Lit materials from the spec and remaps them onto both FBX files
    ///   Add Colliders          - convex body collider + a box per door / hood / trunk / bumper on the selected car
    ///   Add Openings Component - adds AlbertCarOpenings (doors, hood, trunk) to the selected car
    /// </summary>
    public static class AlbertEVSetup
    {
        enum Surface { Opaque, Transparent, Cutout }

        class Spec
        {
            public string name, tex;             // tex = texture set, e.g. "leather_black" -> ev_sedan_leather_black_d/_n + unity_packed/_ms
            public Color color = Color.white;    // linear, as in the spec table
            public float metallic, roughness, alpha = 1f, emission;
            public Surface surface = Surface.Opaque;
            public bool normal, packed;
        }

        static Spec S(string name, float r, float g, float b, float metallic, float roughness)
        {
            return new Spec { name = name, color = new Color(r, g, b), metallic = metallic, roughness = roughness };
        }

        static Spec T(string name, string tex, float metallic, float roughness, bool normal = true, bool packed = true)
        {
            return new Spec { name = name, tex = tex, metallic = metallic, roughness = roughness, normal = normal, packed = packed };
        }

        static Spec Glass(string name, float r, float g, float b, float roughness, float alpha)
        {
            Spec s = S(name, r, g, b, 0f, roughness); s.alpha = alpha; s.surface = Surface.Transparent; return s;
        }

        static Spec Lamp(string name, float emission)
        {
            return new Spec { name = name, tex = "lights", roughness = 0.3f, emission = emission, surface = Surface.Cutout };
        }

        // EV_Sedan_TechnicalSpec.md section 7
        static readonly Spec[] Materials =
        {
            S("Paint_Body", 0.86f, 0.87f, 0.85f, 0.18f, 0.3f),
            S("Trim_Black_Gloss", 0.008f, 0.008f, 0.009f, 0f, 0.12f),
            T("Plastic_Black_Satin", "plastic_black", 0f, 0.45f),
            T("Plastic_Black_Matte", "plastic_black", 0f, 0.7f),
            T("Fabric_Dark", "fabric_dark", 0f, 0.95f),
            S("Chrome", 0.92f, 0.92f, 0.93f, 1f, 0.06f),
            T("Aluminium_Brushed", "aluminium", 1f, 0.38f),
            S("Metal_Dark", 0.22f, 0.22f, 0.23f, 0.85f, 0.6f),
            S("Light_Housing", 0.85f, 0.85f, 0.87f, 1f, 0.22f),
            Glass("Glass_Window", 0.45f, 0.5f, 0.52f, 0.02f, 0.32f),
            Glass("Glass_Roof", 0.12f, 0.13f, 0.14f, 0.02f, 0.62f),
            Glass("Lens_Clear", 0.8f, 0.85f, 0.9f, 0.02f, 0.22f),
            Glass("Lens_Red", 0.6f, 0.015f, 0.015f, 0.05f, 0.55f),
            Lamp("Light_Head", 1f), Lamp("Light_Fog", 0f), Lamp("Light_Tail", 1f),
            Lamp("Light_Indicator", 0f), Lamp("Light_Reverse", 0f), Lamp("Light_Interior", 0f),
            new Spec { name = "Reflector_Red", color = new Color(0.5f, 0.01f, 0.01f), metallic = 0.4f, roughness = 0.2f, emission = 0.25f },
            T("Tyre_Tread", "tyre", 0f, 0.8f),
            T("Tyre_Sidewall", "tyre_side", 0f, 0.75f),
            T("Rim", "rim", 1f, 0.22f, normal: false, packed: false),
            T("Brake_Disc", "brake_disc", 0.9f, 0.42f, normal: false, packed: false),
            T("Brake_Caliper", "caliper", 0f, 0.35f, normal: false, packed: false),
            T("Leather_Black", "leather_black", 0f, 0.55f),
            T("Leather_White", "leather_white", 0f, 0.5f),
            T("Carpet", "carpet", 0f, 0.95f),
            T("Belt", "belt", 0f, 0.8f),
            new Spec { name = "Buttons", tex = "buttons", roughness = 0.4f, emission = 0.6f },
            new Spec { name = "Screen", tex = "screen", roughness = 0.08f, emission = 1.6f },
            S("Mirror", 0.95f, 0.95f, 0.95f, 1f, 0f),
            new Spec { name = "Plate", tex = "plate", roughness = 0.35f, normal = true },
            S("Accent_Red", 0.45f, 0.02f, 0.02f, 0f, 0.4f),
        };

        // ------------------------------------------------------------------ materials

        [MenuItem("Tools/Albert EV/Create URP Materials")]
        public static void CreateMaterials()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            if (lit == null)
            {
                EditorUtility.DisplayDialog("Albert EV", "URP is not installed: 'Universal Render Pipeline/Lit' was not found.", "OK");
                return;
            }
            List<string> models = FindModels();
            if (models.Count == 0)
            {
                EditorUtility.DisplayDialog("Albert EV", "No EV_Sedan*.fbx found in the project.", "OK");
                return;
            }
            string folder = Path.GetDirectoryName(models[0]).Replace('\\', '/') + "/Materials";
            if (!AssetDatabase.IsValidFolder(folder))
                AssetDatabase.CreateFolder(Path.GetDirectoryName(folder).Replace('\\', '/'), "Materials");

            var created = new Dictionary<string, Material>();
            foreach (Spec s in Materials)
            {
                string path = folder + "/" + s.name + ".mat";
                Material m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null) { m = new Material(lit); AssetDatabase.CreateAsset(m, path); }
                m.shader = lit;
                Configure(m, s);
                EditorUtility.SetDirty(m);
                created[s.name] = m;
            }
            AssetDatabase.SaveAssets();

            foreach (string model in models)
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath(model);
                foreach (var kv in created)
                    mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), kv.Key), kv.Value);
                mi.SaveAndReimport();
            }
            Debug.Log("Albert EV: " + created.Count + " URP materials in " + folder + ", remapped on " + models.Count + " model(s).");
        }

        static List<string> FindModels()
        {
            var list = new List<string>();
            foreach (string guid in AssetDatabase.FindAssets("EV_Sedan t:Model"))
            {
                string p = AssetDatabase.GUIDToAssetPath(guid);
                if (p.EndsWith(".fbx") && Path.GetFileName(p).StartsWith("EV_Sedan")) list.Add(p);
            }
            return list;
        }

        static Texture2D Tex(string file)
        {
            foreach (string guid in AssetDatabase.FindAssets(file + " t:Texture2D"))
            {
                string p = AssetDatabase.GUIDToAssetPath(guid);
                if (Path.GetFileNameWithoutExtension(p) == file) return AssetDatabase.LoadAssetAtPath<Texture2D>(p);
            }
            return null;
        }

        static void Configure(Material m, Spec s)
        {
            m.shaderKeywords = new string[0];
            Color baseColor = s.tex != null ? Color.white : s.color.gamma;   // spec colours are linear
            baseColor.a = s.alpha;
            m.SetColor("_BaseColor", baseColor);
            m.SetFloat("_Metallic", s.metallic);
            m.SetFloat("_Smoothness", 1f - s.roughness);
            m.SetFloat("_SmoothnessTextureChannel", 0f);

            Texture2D baseMap = s.tex != null ? Tex("ev_sedan_" + s.tex + "_d") : null;
            m.SetTexture("_BaseMap", baseMap);

            Texture2D normal = s.tex != null && s.normal ? Tex("ev_sedan_" + s.tex + "_n") : null;
            m.SetTexture("_BumpMap", normal);
            if (normal != null) m.EnableKeyword("_NORMALMAP");

            Texture2D packed = s.tex != null && s.packed ? Tex("ev_sedan_" + s.tex + "_ms") : null;
            m.SetTexture("_MetallicGlossMap", packed);
            if (packed != null)
            {
                m.EnableKeyword("_METALLICSPECGLOSSMAP");
                m.SetFloat("_Smoothness", 1f);                 // map alpha carries the smoothness
            }

            if (s.emission > 0f || s.surface == Surface.Cutout)
            {
                // lamps keep emission enabled at 0 so scripts can animate _EmissionColor (0 = off)
                m.EnableKeyword("_EMISSION");
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
                Color e = (s.tex != null ? Color.white : s.color) * s.emission;
                m.SetColor("_EmissionColor", e);
                m.SetTexture("_EmissionMap", s.tex != null ? baseMap : null);
            }
            else
            {
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
                m.SetColor("_EmissionColor", Color.black);
            }

            m.SetFloat("_Cull", (float)CullMode.Back);
            switch (s.surface)
            {
                case Surface.Opaque:
                    m.SetFloat("_Surface", 0f);
                    m.SetFloat("_AlphaClip", 0f);
                    m.SetOverrideTag("RenderType", "Opaque");
                    m.SetFloat("_SrcBlend", (float)BlendMode.One);
                    m.SetFloat("_DstBlend", (float)BlendMode.Zero);
                    m.SetFloat("_ZWrite", 1f);
                    m.renderQueue = (int)RenderQueue.Geometry;
                    break;
                case Surface.Cutout:
                    m.SetFloat("_Surface", 0f);
                    m.SetFloat("_AlphaClip", 1f);
                    m.SetFloat("_Cutoff", 0.5f);
                    m.EnableKeyword("_ALPHATEST_ON");
                    m.SetOverrideTag("RenderType", "TransparentCutout");
                    m.SetFloat("_SrcBlend", (float)BlendMode.One);
                    m.SetFloat("_DstBlend", (float)BlendMode.Zero);
                    m.SetFloat("_ZWrite", 1f);
                    m.renderQueue = (int)RenderQueue.AlphaTest;
                    break;
                case Surface.Transparent:
                    m.SetFloat("_Surface", 1f);
                    m.SetFloat("_Blend", 0f);                  // alpha blend
                    m.SetFloat("_AlphaClip", 0f);
                    m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                    m.SetOverrideTag("RenderType", "Transparent");
                    m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                    m.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                    m.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
                    m.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
                    m.SetFloat("_ZWrite", 0f);
                    m.SetShaderPassEnabled("ShadowCaster", false);
                    m.renderQueue = (int)RenderQueue.Transparent;
                    break;
            }
            m.enableInstancing = true;
        }

        // ------------------------------------------------------------------ colliders / components

        [MenuItem("Tools/Albert EV/Add Colliders To Selected Car")]
        public static void AddColliders()
        {
            GameObject car = Selection.activeGameObject;
            if (car == null) { EditorUtility.DisplayDialog("Albert EV", "Select the car (EV_Sedan) in the scene first.", "OK"); return; }
            Undo.RegisterFullObjectHierarchyUndo(car, "Albert EV colliders");

            // body: convex hull of the lowest body LOD (PhysX cooks it to <= 255 faces)
            MeshFilter body = FindMesh(car.transform, "Body_LOD2") ?? FindMesh(car.transform, "Body_LOD0");
            if (body != null && body.GetComponent<MeshCollider>() == null)
            {
                var mc = Undo.AddComponent<MeshCollider>(body.gameObject);
                mc.sharedMesh = body.sharedMesh;
                mc.convex = true;
            }
            // moving panels: a box each, on the LOD0 mesh so it follows its hinge
            foreach (string part in new[] { "Door_FL", "Door_FR", "Door_RL", "Door_RR", "Hood", "Trunk", "Bumper_F", "Bumper_R" })
            {
                MeshFilter mf = FindMesh(car.transform, part + "_LOD0");
                if (mf == null || mf.GetComponent<Collider>() != null) continue;
                var box = Undo.AddComponent<BoxCollider>(mf.gameObject);
                box.center = mf.sharedMesh.bounds.center;
                box.size = mf.sharedMesh.bounds.size;
            }
            Debug.Log("Albert EV: colliders added to " + car.name + ". Put the Rigidbody on the car root.");
        }

        [MenuItem("Tools/Albert EV/Add Openings Component To Selected Car")]
        public static void AddOpenings()
        {
            GameObject car = Selection.activeGameObject;
            if (car == null) { EditorUtility.DisplayDialog("Albert EV", "Select the car (EV_Sedan) in the scene first.", "OK"); return; }
            if (car.GetComponent<AlbertCarOpenings>() == null) Undo.AddComponent<AlbertCarOpenings>(car);
        }

        static MeshFilter FindMesh(Transform root, string objectName)
        {
            foreach (MeshFilter mf in root.GetComponentsInChildren<MeshFilter>(true))
                if (mf.gameObject.name == objectName) return mf;
            return null;
        }
    }
}
