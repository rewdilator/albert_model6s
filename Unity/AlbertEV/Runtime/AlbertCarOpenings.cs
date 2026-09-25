using System;
using UnityEngine;

namespace AlbertEV
{
    public enum CarOpening { DoorFrontLeft, DoorFrontRight, DoorRearLeft, DoorRearRight, Hood, Trunk }

    /// <summary>
    /// Opens and closes each door, the hood (frunk) and the trunk of the Albert EV independently.
    /// Add it to the car root (the imported "EV_Sedan" object or any parent of it). The hinge
    /// pivots are found by name, and the hinge axes are derived from the model itself, so it works
    /// whatever the import axis settings or the car's orientation.
    ///
    ///   GetComponent&lt;AlbertCarOpenings&gt;().Toggle(CarOpening.DoorFrontLeft);
    /// </summary>
    [DisallowMultipleComponent]
    public class AlbertCarOpenings : MonoBehaviour
    {
        [Serializable]
        public class Hinge
        {
            public CarOpening opening;
            public string pivotName;
            [Tooltip("Assigned automatically from Pivot Name if left empty.")]
            public Transform pivot;
            [Tooltip("Opening angle in degrees about the hinge axis (sign = swing direction).")]
            public float openAngle;
            [Tooltip("Seconds for a full open or close.")]
            public float duration = 0.9f;
            public bool startOpen;

            [NonSerialized] public Quaternion closedLocal;
            [NonSerialized] public Vector3 localAxis;
            [NonSerialized] public float openness;   // 0 closed .. 1 open
            [NonSerialized] public bool target;
        }

        public Hinge[] hinges =
        {
            new Hinge { opening = CarOpening.DoorFrontLeft,  pivotName = "Door_FL_Pivot", openAngle = 65f },
            new Hinge { opening = CarOpening.DoorFrontRight, pivotName = "Door_FR_Pivot", openAngle = -65f },
            new Hinge { opening = CarOpening.DoorRearLeft,   pivotName = "Door_RL_Pivot", openAngle = 65f },
            new Hinge { opening = CarOpening.DoorRearRight,  pivotName = "Door_RR_Pivot", openAngle = -65f },
            new Hinge { opening = CarOpening.Hood,           pivotName = "Hood_Pivot",    openAngle = -45f, duration = 1.2f },
            new Hinge { opening = CarOpening.Trunk,          pivotName = "Trunk_Pivot",   openAngle = 60f,  duration = 1.2f },
        };

        public event Action<CarOpening, bool> OpeningChanged;

        bool initialised;

        void Awake() { Initialise(); }

        void Initialise()
        {
            if (initialised) return;
            Transform fl = Find("Door_FL_Pivot"), fr = Find("Door_FR_Pivot"), rl = Find("Door_RL_Pivot");
            if (fl == null || fr == null || rl == null)
            {
                Debug.LogError("AlbertCarOpenings: hinge pivots not found under " + name + ".", this);
                enabled = false;
                return;
            }
            // Car axes from the model: the door hinges all sit at the same height, so
            // right = front-left -> front-right hinge, forward = rear-left -> front-left hinge.
            Vector3 right = (fr.position - fl.position).normalized;
            Vector3 forward = Vector3.ProjectOnPlane(fl.position - rl.position, right).normalized;
            Vector3 up = Vector3.Cross(forward, right);

            foreach (Hinge h in hinges)
            {
                if (h.pivot == null) h.pivot = Find(h.pivotName);
                if (h.pivot == null) continue;
                bool isDoor = h.opening <= CarOpening.DoorRearRight;
                Vector3 worldAxis = isDoor ? up : right;
                h.closedLocal = h.pivot.localRotation;
                h.localAxis = Quaternion.Inverse(h.pivot.rotation) * worldAxis;
                h.target = h.startOpen;
                h.openness = h.startOpen ? 1f : 0f;
                Apply(h);
            }
            initialised = true;
        }

        Transform Find(string pivotName)
        {
            foreach (Transform t in GetComponentsInChildren<Transform>(true))
                if (t.name == pivotName) return t;
            return null;
        }

        void Update()
        {
            foreach (Hinge h in hinges)
            {
                if (h.pivot == null) continue;
                float goal = h.target ? 1f : 0f;
                if (Mathf.Approximately(h.openness, goal)) continue;
                h.openness = Mathf.MoveTowards(h.openness, goal, Time.deltaTime / Mathf.Max(0.01f, h.duration));
                Apply(h);
            }
        }

        static void Apply(Hinge h)
        {
            float eased = Mathf.SmoothStep(0f, 1f, h.openness);
            h.pivot.localRotation = h.closedLocal * Quaternion.AngleAxis(h.openAngle * eased, h.localAxis);
        }

        Hinge Get(CarOpening o)
        {
            Initialise();
            foreach (Hinge h in hinges) if (h.opening == o) return h;
            return null;
        }

        public bool IsOpen(CarOpening o) { Hinge h = Get(o); return h != null && h.target; }

        /// <summary>0 = fully closed, 1 = fully open (animated value).</summary>
        public float Openness(CarOpening o) { Hinge h = Get(o); return h != null ? h.openness : 0f; }

        public void SetOpen(CarOpening o, bool open, bool instant = false)
        {
            Hinge h = Get(o);
            if (h == null || h.pivot == null) return;
            bool changed = h.target != open;
            h.target = open;
            if (instant) { h.openness = open ? 1f : 0f; Apply(h); }
            if (changed && OpeningChanged != null) OpeningChanged(o, open);
        }

        public void Open(CarOpening o) { SetOpen(o, true); }
        public void Close(CarOpening o) { SetOpen(o, false); }
        public void Toggle(CarOpening o) { SetOpen(o, !IsOpen(o)); }

        public void CloseAll(bool instant = false)
        {
            foreach (CarOpening o in Enum.GetValues(typeof(CarOpening))) SetOpen(o, false, instant);
        }

        // Inspector test buttons (component ⋮ menu)
        [ContextMenu("Toggle Front Left Door")] void CtxFL() { Toggle(CarOpening.DoorFrontLeft); }
        [ContextMenu("Toggle Front Right Door")] void CtxFR() { Toggle(CarOpening.DoorFrontRight); }
        [ContextMenu("Toggle Rear Left Door")] void CtxRL() { Toggle(CarOpening.DoorRearLeft); }
        [ContextMenu("Toggle Rear Right Door")] void CtxRR() { Toggle(CarOpening.DoorRearRight); }
        [ContextMenu("Toggle Hood (Frunk)")] void CtxHood() { Toggle(CarOpening.Hood); }
        [ContextMenu("Toggle Trunk")] void CtxTrunk() { Toggle(CarOpening.Trunk); }
        [ContextMenu("Close All")] void CtxClose() { CloseAll(); }
    }
}
