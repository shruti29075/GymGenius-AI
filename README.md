<h1 align="center">GymGenius AI</h1>

<p align="center">
  <b>GymGenius AI – AI Fitness Coach</b><br>
  <i>Your intelligent AI Fitness Coach for real-time form correction, workout tracking, video analysis, and sports nutrition.</i>
</p>

<hr>

## ✨ Features
- **Real-Time Pose Tracking**: Leverages Google MediaPipe (Pose Landmarker) to track 33 3D skeletal landmarks.
- **Form Correction & Audio Coaching**: Instant visual & spoken feedback (*"Go deeper"*, *"Keep chest up"*) using browser Web Speech API.
- **Offline Video Upload Mode**: Upload recorded gym videos (.mp4/.mov) for automated frame-by-frame rep counting & biomechanical analysis.
- **Gamification & Athlete XP**: Unlock 8 achievements & trophies, maintain daily streaks (🔥), and climb the community leaderboard.
- **Smart Nutrition & Macro Calculator**: Scientific BMR, TDEE, goal-based calorie targets, macro splits (protein/carbs/fats), and hydration.
- **Technique Guides**: Biomechanical cues, angle thresholds, and common mistakes for all supported exercises.
- **Data Analytics & Reports**: Plotly charts for calories & exercises, downloadable CSV and PDF progress reports.

## 🛠️ Tech Stack
- **Frontend & App Framework**: Streamlit, Custom Cyber-Athletic CSS, Plotly Interactive Charts
- **Backend & Storage**: Python, SQLite, bcrypt
- **AI & Computer Vision**: Google MediaPipe (Pose Landmarker), OpenCV, Streamlit-WebRTC
- **Exporting**: FPDF, Pandas (CSV)

## 📸 Screenshots
*(Include additional screenshots of your application here)*

## 🏋️ Supported Exercises (Proper Form Guide)

<p align="center">
<img src="screenshots/basic_exercises.png" width="900">
</p>

GymGenius AI currently tracks and provides real-time feedback on 6 core exercises:

### 1. Squat (Legs & Glutes)
- **Tips**: Feet shoulder-width apart, chest up, and back straight. Push hips back and down. Keep knees behind toes, and engage core and glutes.

### 2. Push-Up (Chest, Shoulders, Triceps)
- **Tips**: Hands slightly wider than shoulders. Keep your body in a straight line. Lower until chest is near the floor, push back up, and engage core.

### 3. Bicep Curl (Arms)
- **Tips**: Keep elbows tucked close to your torso. Curl the weight upwards smoothly without swinging your back, squeeze at the top, and lower slowly.

### 4. Plank (Core)
- **Tips**: Elbows under shoulders, body in a straight line. Tighten your core, don't let hips drop, and breathe normally.

### 5. Lunge (Legs & Glutes)
- **Tips**: Step forward, front knee at 90°. Back knee near the floor. Keep torso upright, and push back to start.

### 6. Jumping Jack (Full Body)
- **Tips**: Jump and spread arms and legs. Return to the start position. Keep a steady rhythm and land softly.

> **💡 General Fitness Guidelines:**
> - 🎯 **Warm Up**: 5-10 Minutes
> - 💧 **Stay Hydrated**: Drink Water
> - ❤️ **Be Consistent**: 3-5 Times a Week
> - 📈 **Progress Gradually**: Increase Reps & Intensity

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shruti29075/GymGenius-AI.git
   cd GymGenius-AI
   ```

2. **Set up a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   # or simply:
   python app.py
   ```

## 📖 Usage
1. Launch the application and open your browser to `http://localhost:8501`.
2. Create an account or sign in to your Hyper Gym dashboard.
3. Allow camera access in your browser to enable live skeleton pose tracking, or switch to Video Upload mode.
4. Select your exercise, start your workout, and let GymGenius AI analyze your form in real-time!

## 🔮 Future Enhancements
- **Wearable Integration**: Sync with smartwatches (Apple Watch, Garmin, etc.) for heart rate and calorie tracking.
- **Dynamic Workout Plans**: AI-generated multi-week routines tailored to your specific goals and progress.
