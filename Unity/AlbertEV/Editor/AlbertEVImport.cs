using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace AlbertEV.EditorTools
{
    /// <summary>
    /// Game-ready import settings for the Albert EV, applied automatically to
    /// EV_Sedan*.fbx and the ev_sedan_* textures wherever they are in the project.
    /// </summary>
    public class AlbertEVImport : AssetPostprocessor
    {
        // LOD switch points (fraction of screen height). Below the last one the part is culled.
        public static readonly float[] LodTransitions = { 0.45f, 0.15f, 0.015f };

        static bool IsCarModel(string path) { return Path.GetFileName(path).StartsWith("EV_Sedan") && path.EndsWith(".fbx"); }
        static bool IsCarTexture(string path) { return Path.GetFileName(path).StartsWith("ev_sedan_"); }

        void OnPreprocessModel()
        {
            if (!IsCarModel(assetPath)) return;
            var mi = (ModelImporter)assetImporter;
            mi.globalScale = 1f;
            mi.useFileScale = true;
            mi.bakeAxisConversion = true;           // nose = +Z, up = +Y, identity pivots
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.CalculateMikk;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.isReadable = false;                  // halves mesh memory; enable only for mesh damage
            mi.optimizeMeshPolygons = true;
            mi.optimizeMeshVertices = true;
            mi.weldVertices = true;
            mi.indexFormat = ModelImporterIndexFormat.Auto;
            mi.importBlendShapes = false;
            mi.importVisibility = false;
            mi.importCameras = false;
            mi.importLights = false;
            mi.addCollider = false;
            mi.generateSecondaryUV = false;
            mi.importAnimation = false;
            mi.animationType = ModelImporterAnimationType.None;
            mi.materialLocation = ModelImporterMaterialLocation.InPrefab;
        }

        void OnPostprocessModel(GameObject root)
        {
            if (!IsCarModel(assetPath)) return;
            foreach (LODGroup group in root.GetComponentsInChildren<LODGroup>(true))
            {
                LOD[] lods = group.GetLODs();
                for (int i = 0; i < lods.Length && i < LodTransitions.Length; i++)
                    lods[i].screenRelativeTransitionHeight = LodTransitions[i];
                group.SetLODs(lods);
                group.fadeMode = LODFadeMode.None;
            }
            foreach (Renderer r in root.GetComponentsInChildren<Renderer>(true))
            {
                string n = r.gameObject.name;
                // transparent glass does not need to cast shadows; far LODs cast cheaper shadows only from the body
                if (n.StartsWith("Glass")) r.shadowCastingMode = ShadowCastingMode.Off;
                if (n.EndsWith("_LOD2") && (n.StartsWith("Interior") || n.StartsWith("SteeringWheel") || n.StartsWith("Brake")))
                    r.shadowCastingMode = ShadowCastingMode.Off;
                r.lightProbeUsage = LightProbeUsage.BlendProbes;
                r.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
                r.allowOcclusionWhenDynamic = true;
            }
        }

        void OnPreprocessTexture()
        {
            if (!IsCarTexture(assetPath)) return;
            var ti = (TextureImporter)assetImporter;
            string file = Path.GetFileNameWithoutExtension(assetPath);
            ti.mipmapEnabled = true;
            ti.streamingMipmaps = true;
            ti.maxTextureSize = 1024;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
            ti.anisoLevel = 4;
            ti.wrapMode = TextureWrapMode.Repeat;
            if (file.EndsWith("_n"))
            {
                ti.textureType = TextureImporterType.NormalMap;   // OpenGL (+Y) normals, same as Unity
                ti.sRGBTexture = false;
            }
            else if (file.EndsWith("_ms") || file.EndsWith("_r"))
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = false;                           // packed data, not colour
                ti.alphaSource = TextureImporterAlphaSource.FromInput;
            }
            else
            {
                ti.textureType = TextureImporterType.Default;
                ti.sRGBTexture = true;
                ti.alphaIsTransparency = file == "ev_sedan_lights_d";
            }
        }
    }
}
