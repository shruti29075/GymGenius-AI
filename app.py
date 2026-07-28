import streamlit as st
import cv2
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import pandas as pd
import time
import streamlit.components.v1 as components
from fpdf import FPDF

from auth.auth import login_user, register_user, update_user_profile
from modules.pose_detector import PoseDetector
from modules.form_analyzer import FormAnalyzer
from modules.rep_counter import RepCounter
from modules.analytics import fetch_user_workouts, plot_calories_over_time, plot_exercise_distribution, save_workout
from database.db import init_db

# Initialize DB on first run
init_db()

# Page Config
st.set_page_config(page_title="GymGenius AI", page_icon="🏋️", layout="wide")

# Custom CSS for Premium Dark Theme
st.markdown("""
<style>
    :root {
        --primary: #FFD700; /* Luxury Gold */
        --primary-hover: #E6C200;
        --bg-dark: #0A0A0A; /* Matte Black */
        --bg-card: #141414; /* Slightly lighter black for cards */
        --text-light: #F5F5F5;
        --border-gold: 1px solid rgba(255, 215, 0, 0.3);
    }
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-light);
    }
    .css-1d391kg, .css-1lcbmhc, .stSidebar, [data-testid="stSidebar"] {
        background-color: var(--bg-card) !important;
        border-right: var(--border-gold);
    }
    .stButton>button {
        background-color: transparent;
        color: var(--primary);
        font-weight: bold;
        border-radius: 8px;
        border: 2px solid var(--primary);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: var(--primary);
        color: #000;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    }
    h1, h2, h3 {
        color: var(--primary);
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stat-card {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: var(--border-gold);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
    }
    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1a1a1a;
        color: #fff;
        border: 1px solid #333;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: var(--primary);
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

def login_page():
    st.title("Welcome to GymGenius AI 💪")
    st.markdown("### Your Personal AI Fitness Trainer")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Login")
        login_user_name = st.text_input("Username", key="log_user")
        login_password = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            success, msg = login_user(login_user_name, login_password)
            if success:
                st.session_state['logged_in'] = True
                st.session_state['user'] = msg
                st.rerun()
            else:
                st.error(msg)
                
    with col2:
        st.subheader("Sign Up")
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Sign Up"):
            success, msg = register_user(reg_user, reg_pass)
            if success:
                st.success(msg + " Please login.")
            else:
                st.error(msg)

# --- Video Processor for WebRTC ---
class GymVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = PoseDetector()
        self.analyzer = FormAnalyzer()
        self.counter = RepCounter()
        self.exercise = "Squat"
        
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        if self.detector.error:
            cv2.putText(img, "MediaPipe Error:", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, self.detector.error[:50], (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return av.VideoFrame.from_ndarray(img, format="bgr24")
            
        timestamp_ms = int(time.time() * 1000)
        img, pose_result = self.detector.find_pose(img, timestamp_ms, draw=True)
        lm_list = self.detector.get_position(img, pose_result, draw=False)
        
        angle = None
        feedback = ""
        count = self.counter.count
        stage = self.counter.stage
        
        if lm_list:
            if self.exercise == "Squat":
                angle, feedback = self.analyzer.analyze_squat(lm_list)
                count, stage = self.counter.count_squat_reps(angle)
            elif self.exercise == "Push Up":
                angle, feedback = self.analyzer.analyze_push_up(lm_list)
                count, stage = self.counter.count_push_up_reps(angle)
            elif self.exercise == "Bicep Curl":
                angle, feedback = self.analyzer.analyze_bicep_curl(lm_list)
                count, stage = self.counter.count_bicep_curl_reps(angle)
            elif self.exercise == "Lunge":
                angle, feedback = self.analyzer.analyze_lunge(lm_list)
                count, stage = self.counter.count_lunge_reps(angle)
            elif self.exercise == "Jumping Jack":
                angle, feedback = self.analyzer.analyze_jumping_jack(lm_list)
                count, stage = self.counter.count_jumping_jack_reps(angle)
            elif self.exercise == "Plank":
                angle, feedback = self.analyzer.analyze_plank(lm_list)
                count, stage = self.counter.count_plank_reps(angle)
                
            # Draw UI on frame
            cv2.rectangle(img, (0, 0), (350, 150), (21, 27, 43), cv2.FILLED)
            cv2.putText(img, f"Reps: {count} / {self.counter.target_reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
            cv2.putText(img, f"Sets: {self.counter.sets}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
            cv2.putText(img, f"Form: {feedback}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if feedback == "Excellent Form" else (0, 0, 255), 2)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")


def main_app():
    user = st.session_state['user']
    st.sidebar.title("GymGenius AI 🏃")
    st.sidebar.write(f"Welcome, **{user['username']}**")
    
    menu = ["Dashboard", "Live Workout", "Progress", "Profile", "Settings"]
    choice = st.sidebar.radio("Navigation", menu)
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()

    if choice == "Dashboard":
        st.title("Dashboard")
        df = fetch_user_workouts(user['id'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><h3>Total Workouts</h3><div class="stat-value">{len(df)}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h3>Total Calories (kcal)</h3><div class="stat-value">{df["calories"].sum() if not df.empty else 0:.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><h3>Total Duration (min)</h3><div class="stat-value">{(df["duration_seconds"].sum()/60) if not df.empty else 0:.0f}</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        if not df.empty:
            st.subheader("Recent Activity")
            st.dataframe(df.tail(5)[['date', 'exercise', 'reps', 'sets', 'calories']].sort_values(by='date', ascending=False), use_container_width=True)
        else:
            st.info("No workouts found. Head to Live Workout to start!")

    elif choice == "Live Workout":
        st.title("Live Workout Trainer")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            exercise = st.selectbox("Select Exercise", ["Squat", "Push Up", "Bicep Curl", "Lunge", "Jumping Jack", "Plank"])
            target_reps = st.number_input("Target Reps per Set", min_value=1, value=10)
            
            st.markdown("### 🎵 Workout Music")
            components.html(
                '''
                <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX70RN3TfR700?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                ''',
                height=160
            )
            
            st.markdown("---")
            st.write("1. Allow camera access.")
            st.write("2. Step back so your full body is visible.")
            st.write("3. Follow the on-screen form feedback.")
            
        with col2:
            ctx = webrtc_streamer(
                key="gym-trainer",
                mode=WebRtcMode.SENDRECV,
                video_processor_factory=GymVideoProcessor,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True
            )
            
            if ctx.video_processor:
                if ctx.video_processor.exercise != exercise:
                    ctx.video_processor.counter.reset()
                    ctx.video_processor.exercise = exercise
                ctx.video_processor.counter.target_reps = target_reps
                
                # Simple logic to save workout
                if st.button("Save Workout Session"):
                    reps_done = target_reps
                    sets_done = 1
                    save_workout(user['id'], exercise, reps_done, sets_done, 300, 95.0, 150.0)
                    st.success("Workout saved successfully! Check Progress tab.")

    elif choice == "Progress":
        st.title("Progress Analytics")
        df = fetch_user_workouts(user['id'])
        
        if df.empty:
            st.warning("No data available to show analytics.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                fig_cal = plot_calories_over_time(df)
                if fig_cal:
                    st.plotly_chart(fig_cal, use_container_width=True)
            with col2:
                fig_ex = plot_exercise_distribution(df)
                if fig_ex:
                    st.plotly_chart(fig_ex, use_container_width=True)
            
            st.markdown("### Export Reports")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name='gymgenius_progress_report.csv',
                    mime='text/csv',
                )
                
            with col_export2:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="GymGenius AI Progress Report", ln=1, align="C")
                pdf.ln(10)
                for i, row in df.iterrows():
                    pdf.cell(200, 10, txt=f"{row['date']}: {row['exercise']} - {row['reps']} reps, {row['sets']} sets", ln=1, align="L")
                
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name='gymgenius_progress_report.pdf',
                    mime='application/pdf',
                )

    elif choice == "Profile":
        st.title("User Profile")
        age = st.number_input("Age", value=user['age'] if user['age'] else 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
        weight = st.number_input("Weight (kg)", value=user['weight'] if user['weight'] else 70.0)
        height = st.number_input("Height (cm)", value=user['height'] if user['height'] else 170.0)
        goal = st.text_input("Fitness Goal", value=user['fitness_goal'] if user['fitness_goal'] else "")
        
        if st.button("Update Profile"):
            success, msg = update_user_profile(user['id'], age, gender, weight, height, goal)
            if success:
                st.success(msg)
                _, updated_user = login_user(user['username'], user['password_hash']) 
                st.session_state['user']['age'] = age
                st.session_state['user']['gender'] = gender
                st.session_state['user']['weight'] = weight
                st.session_state['user']['height'] = height
                st.session_state['user']['fitness_goal'] = goal
            else:
                st.error(msg)

    elif choice == "Settings":
        st.title("Settings")
        st.write("App settings configuration.")
        st.checkbox("Dark Mode", value=True, disabled=True, help="Premium Dark Theme is permanently enabled.")
        st.checkbox("Voice Feedback", value=True, help="Enable text-to-speech feedback (Future enhancement)")
        st.selectbox("Camera Selection", ["Default Camera"], help="Camera selection is handled by the browser directly when using the Live Workout feature.")

if st.session_state['logged_in']:
    main_app()
else:
    login_page()
