import os

EXERCISE_GUIDES = {
    "Squat": {
        "category": "Lower Body Compound",
        "muscles": "Quadriceps, Gluteus Maximus, Hamstrings, Spinal Erectors, Core",
        "target_angle": "Knee flexion: < 90° for full depth; standing lock: > 160°",
        "start_position": [
            "Feet Placement: Stand with feet shoulder-width apart, toes pointed 15-30° outward.",
            "Torso & Head: Chest proud, shoulders pinned back, neutral spine with eyes looking slightly forward.",
            "Joint Alignment: Knees and hips fully extended (standing upright at ~180° lockout).",
            "Core Engagement: Take a deep diaphragmatic breath and brace abs like you are expecting a punch."
        ],
        "execution": [
            "Descent Phase: Push your hips backward and bend knees simultaneously, tracking knees over toes.",
            "Depth Target: Lower your body under control until hip crease breaks parallel with knees (angle < 90°).",
            "Bottom Position: Keep heels firmly planted into the ground; avoid knees caving inward.",
            "Ascent & Lockout: Drive forcefully through the midfoot to return to full standing lockout."
        ],
        "cues": [
            "Keep feet shoulder-width apart with toes flared 15-30 degrees outward.",
            "Brace core and initiate movement by pushing hips back and bending knees.",
            "Descend smoothly until hip joint is at or below parallel to knee level.",
            "Drive powerfully through the midfoot while keeping chest upright and proud."
        ],
        "mistakes": [
            "Knees caving inward (knee valgus) on the ascent.",
            "Heels lifting off the ground or shifting weight onto toes.",
            "Excessive forward torso lean and spinal rounding."
        ]
    },
    "Push Up": {
        "category": "Upper Body Horizontal Press",
        "muscles": "Pectoralis Major, Anterior Deltoids, Triceps Brachii, Core",
        "target_angle": "Elbow flexion: < 90° at bottom; lockout: > 160° at top",
        "start_position": [
            "Hand Placement: Hands on floor slightly wider than shoulder-width, fingers spread forward.",
            "Body Line: Form a rigid, unbroken straight plank line from the crown of your head to your heels.",
            "Joint Alignment: Arms fully straight (elbow lockout > 160°), wrists stacked under shoulders.",
            "Glutes & Core: Squeeze glutes and tighten abdomen to prevent lower-back hyperextension."
        ],
        "execution": [
            "Descent Phase: Inhale and lower chest toward floor by bending elbows back at a 45° angle.",
            "Depth Target: Lower until chest hovers 1-2 inches above the ground (elbow angle < 90°).",
            "Body Stability: Keep neck neutral; do not let hips dip or pike up.",
            "Ascent & Lockout: Exhale and press powerfully through your palms to return to full high-plank lockout."
        ],
        "cues": [
            "Place hands slightly wider than shoulder-width apart on the floor.",
            "Maintain a rigid plank line from crown of head down through ankles.",
            "Lower chest until elbows bend to roughly 90 degrees or chest nears floor.",
            "Press firmly through palms to full lockout without sagging hips."
        ],
        "mistakes": [
            "Flaring elbows excessively out to 90 degrees (tuck elbows to ~45 degrees).",
            "Hips sagging down or piking upward towards ceiling.",
            "Failing to achieve full depth or skipping top lockout."
        ]
    },
    "Bicep Curl": {
        "category": "Upper Body Isolation",
        "muscles": "Biceps Brachii, Brachialis, Forearm Flexors",
        "target_angle": "Elbow flexion: < 50° at peak contraction; extension: > 150°",
        "start_position": [
            "Stance: Stand tall with feet hip-width apart and knees slightly unlocked.",
            "Arm Setup: Hold dumbbells with palms supinated (facing forward), arms hanging down (> 150° extension).",
            "Elbow Position: Pin elbows snugly against the sides of your ribcage.",
            "Shoulders: Keep shoulder blades retracted; avoid shrugging or rolling shoulders forward."
        ],
        "execution": [
            "Curl Phase: Exhale and curl weights upward while keeping elbows completely stationary.",
            "Peak Squeeze: Lift until forearms near upper arms (< 50° angle) and squeeze biceps for 1 second.",
            "No Body Swing: Do not lean back or use momentum to swing the weights up.",
            "Eccentric Lowering: Inhale and lower dumbbells slowly over 2-3 seconds to full starting extension."
        ],
        "cues": [
            "Pin elbows closely against torso sides without swinging forward.",
            "Curl resistance upward with controlled muscular contraction.",
            "Squeeze biceps firmly at top of rep for 1 full second.",
            "Lower weight along an eccentric path over 2-3 seconds."
        ],
        "mistakes": [
            "Using momentum and swinging the lower back to propel weight.",
            "Letting elbows drift forward away from the body.",
            "Rushing through the lowering (eccentric) phase."
        ]
    },
    "Lunge": {
        "category": "Unilateral Lower Body",
        "muscles": "Quadriceps, Glutes, Hamstrings, Calves, Hip Stabilizers",
        "target_angle": "Front knee flexion: < 90° at bottom; standing: > 150°",
        "start_position": [
            "Stance: Stand upright with feet together or hip-width apart, hands on hips or chest.",
            "Torso: Keep chest up, core braced, and shoulders back in neutral alignment.",
            "Focus: Pick a steady eye focal point ahead to maintain balance."
        ],
        "execution": [
            "Step Forward: Take a generous step forward with lead leg while keeping torso upright.",
            "Descent Phase: Lower back knee toward the floor until both front and rear knees bend to ~90°.",
            "Knee Alignment: Keep lead knee centered directly over middle toes (avoid collapsing inward).",
            "Drive Back: Push forcefully through front heel to step back smoothly into the start position."
        ],
        "cues": [
            "Step forward into a wide stance, keeping torso perpendicular to floor.",
            "Lower back knee towards floor until both front and rear knees reach ~90 degrees.",
            "Keep front knee tracking in direct alignment with middle toes.",
            "Drive through front heel to step smoothly back to start position."
        ],
        "mistakes": [
            "Front knee collapsing inward or projecting past front toes excessively.",
            "Torso pitching forward over the lead thigh.",
            "Stance too narrow causing balance instability."
        ]
    },
    "Jumping Jack": {
        "category": "Cardiovascular & Plyometric",
        "muscles": "Calves, Quadriceps, Deltoids, Lats, Cardiovascular System",
        "target_angle": "Shoulder abduction: > 130° at top; < 45° at sides",
        "start_position": [
            "Stance: Stand straight with feet together and arms hanging naturally by your thighs (< 45°).",
            "Posture: Head up, core braced, knees soft (not locked stiff)."
        ],
        "execution": [
            "Jump Out: Spring lightly off the floor, jumping feet out wider than shoulder-width.",
            "Arm Sweep: Simultaneously sweep arms outward in a high arc until hands clap or meet overhead (> 130°).",
            "Soft Landing: Land smoothly on the balls of your feet with knees slightly bent to absorb impact.",
            "Return Phase: Immediately jump feet back together while bringing arms back down to sides."
        ],
        "cues": [
            "Start upright with feet together and arms hanging naturally at sides.",
            "Simultaneously jump feet out wide while swinging arms in high arc overhead.",
            "Land softly on balls of feet with knees slightly bent to absorb impact.",
            "Maintain a rhythmic, energetic pace throughout the entire set."
        ],
        "mistakes": [
            "Landing stiff-legged with locked knees.",
            "Incomplete arm sweep (arms should touch or come close overhead).",
            "Irregular breathing cadence."
        ]
    },
    "Plank": {
        "category": "Isometric Core Stability",
        "muscles": "Rectus Abdominis, Transverse Abdominis, Obliques, Shoulders",
        "target_angle": "Spinal alignment (shoulder-hip-ankle): 160° - 180° straight line",
        "start_position": [
            "Forearm Base: Rest on forearms on gym mat with elbows stacked directly beneath shoulders.",
            "Footing: Place toes together or hip-width apart on the floor.",
            "Grip: Keep forearms parallel or clasp hands comfortably."
        ],
        "execution": [
            "Lift & Lock: Raise knees off floor to form a straight line from neck to heels (160°-180°).",
            "Core Tension: Pull belly button toward spine and squeeze glutes hard to lock pelvis in place.",
            "Neutral Neck: Gaze down at floor slightly forward of hands to prevent neck hyperextension.",
            "Static Hold: Hold the isometric contraction with steady nasal breathing for target duration."
        ],
        "cues": [
            "Rest on forearms with elbows stacked directly beneath shoulders.",
            "Engage glutes and pull belly button towards spine to lock pelvis.",
            "Gaze down at floor slightly ahead of hands to maintain neutral cervical spine.",
            "Breathe steadily and hold tension throughout the body."
        ],
        "mistakes": [
            "Hips sagging down toward floor causing lower lumbar strain.",
            "Piking hips up into inverted V shape.",
            "Holding breath during prolonged static hold."
        ]
    }
}

def get_exercise_svg(exercise_name: str) -> str:
    """Loads the pre-generated SVG illustration for the given exercise."""
    clean_name = exercise_name.lower().replace(" ", "_")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg_path = os.path.join(base_dir, "assets", "exercises", f"{clean_name}.svg")
    
    if os.path.exists(svg_path):
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""
