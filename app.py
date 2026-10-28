import sys
import subprocess
import streamlit as st
import streamlit.runtime

# Auto-launch with `streamlit run` if executed directly via `python app.py`
if not streamlit.runtime.exists():
    cmd = [sys.executable, "-m", "streamlit", "run", __file__] + sys.argv[1:]
    subprocess.run(cmd)
    sys.exit(0)

import cv2
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import pandas as pd
import time
import streamlit.components.v1 as components
from fpdf import FPDF

from auth.auth import login_user, register_user, update_user_profile
from auth.login_ui import render_login_page
from modules.pose_detector import PoseDetector
from modules.form_analyzer import FormAnalyzer
from modules.rep_counter import RepCounter
from modules.analytics import fetch_user_workouts, plot_calories_over_time, plot_exercise_distribution, save_workout
from modules.gamification import calculate_streak, calculate_athlete_level, get_user_badges, get_community_leaderboard
from modules.nutrition import calculate_nutrition_plan
from modules.video_analysis import analyze_workout_video
from modules.exercise_guide import EXERCISE_GUIDES
from database.db import init_db

# Initialize DB on first run
init_db()

# Page Config
st.set_page_config(page_title="Hyper Gym - GymGenius AI", page_icon="🏋️", layout="wide")

# Custom CSS for Hyper Gym Theme (applied when logged in, matching login & register UI)
def apply_dashboard_theme():
    st.markdown("""
<style>
    /* Deep Obsidian Dark Cyber-Athletic Theme */
    html, body, .stApp {
        background-color: #0b0f17 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 255, 135, 0.05) 0px, transparent 45%),
            radial-gradient(at 100% 100%, rgba(0, 210, 255, 0.04) 0px, transparent 45%) !important;
        color: #e6edf3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    /* Main container padding and max-width */
    .main .block-container, div[data-testid="stMainBlockContainer"] {
        max-width: 1140px !important;
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Top Streamlit header */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    #MainMenu, footer {
        visibility: hidden;
    }

    /* Sidebar - Ultra-sleek Onyx & Glass athletic panel */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #0d121c !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }

    /* Sidebar typography */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e6edf3 !important;
    }

    /* Sidebar Navigation (Sleek Symbol Tiles with generous spacing) */
    [data-testid="stSidebar"] div[data-testid="stRadio"],
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div,
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"],
    [data-testid="stSidebar"] div[data-baseweb="radio-group"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 20px !important; /* Distance between symbols */
        padding: 6px 0 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] > label {
        display: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label,
    [data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 15px 18px !important;
        color: #c9d1d9 !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    /* Hide the default radio circle indicator completely */
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child:not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] p {
        font-size: 24px !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        text-align: center !important;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4)) !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: rgba(0, 255, 135, 0.08) !important;
        border-color: rgba(0, 255, 135, 0.35) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35), 0 0 10px rgba(0, 255, 135, 0.15) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, rgba(0, 255, 135, 0.14), rgba(0, 210, 255, 0.08)) !important;
        border: 1.5px solid #00ff87 !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4), 0 0 16px rgba(0, 255, 135, 0.25) !important;
        transform: scale(1.02) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
        transform: scale(1.1) !important;
    }

    /* Floating Tooltips on Hover for symbols */
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label::after {
        position: absolute !important;
        left: calc(100% + 14px) !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        background: #161b24 !important;
        color: #ffffff !important;
        padding: 7px 14px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        white-space: nowrap !important;
        pointer-events: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s ease !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6) !important;
        border: 1px solid rgba(0, 255, 135, 0.3) !important;
        z-index: 999999 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover::after {
        opacity: 1 !important;
        visibility: visible !important;
        transform: translateY(-50%) translateX(4px) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(1)::after { content: "Dashboard"; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(2)::after { content: "Live Workout"; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(3)::after { content: "Progress"; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(4)::after { content: "Nutrition"; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(5)::after { content: "Profile"; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(6)::after { content: "Settings"; }

    /* Allow tooltips to overflow the sidebar smoothly */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], div[data-testid="stSidebarUserContent"] {
        overflow: visible !important;
    }

    /* Small Logout Button positioned at the bottom left */
    [data-testid="stSidebar"] div:has(> button[data-testid*="sidebar_logout_btn"]),
    [data-testid="stSidebar"] .stButton:has(> button) {
        width: fit-content !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 90, 90, 0.08) !important;
        border: 1px solid rgba(255, 90, 90, 0.22) !important;
        color: #ff8585 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        width: auto !important;
        min-width: unset !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 90, 90, 0.2) !important;
        border-color: #ff5a5a !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(255, 90, 90, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stSidebar"] .stButton > button p {
        color: inherit !important;
        font-weight: inherit !important;
        letter-spacing: inherit !important;
        font-size: 11.5px !important;
    }

    /* Headings in Main Content */
    h1 {
        color: #ffffff !important;
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0.4rem !important;
    }
    h2, h3 {
        color: #f0f6fc !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }
    .page-subtitle {
        color: #8b949e !important;
        font-size: 14px !important;
        margin-top: -4px !important;
        margin-bottom: 24px !important;
    }

    /* Cyber-Athletic Glassmorphic Stat Cards */
    .stat-card {
        background: linear-gradient(145deg, #131924, #0e131d) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 22px 24px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), 0 2px 6px rgba(0, 0, 0, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }
    .stat-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.45), 0 0 16px rgba(0, 255, 135, 0.12) !important;
        border-color: rgba(0, 255, 135, 0.25) !important;
    }
    .stat-card-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00ff87, #60efff) !important;
    }
    .stat-label {
        font-size: 11.5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        color: #8b949e !important;
        margin-bottom: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    .stat-value {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.1 !important;
    }
    .stat-sub {
        font-size: 12px !important;
        color: #7d8590 !important;
        margin-top: 6px !important;
        font-weight: 500 !important;
    }

    /* Form Fields and Inputs (Dark Athletic inputs) */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] {
        background-color: #131924 !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
    div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"]:focus-within,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: #00ff87 !important;
        box-shadow: 0 0 0 2px rgba(0, 255, 135, 0.2) !important;
    }

    /* All input text elements */
    input, select, textarea {
        background-color: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        caret-color: #00ff87 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #7d8590 !important;
        -webkit-text-fill-color: #7d8590 !important;
    }

    /* Number input step controls (+ and -) */
    div[data-testid="stNumberInput"] button,
    div[data-testid="stNumberInput"] div[role="button"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"] button,
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background-color: #1a2232 !important;
        color: #00ff87 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    div[data-testid="stNumberInput"] button:hover,
    button[data-testid="stNumberInputStepDown"]:hover,
    button[data-testid="stNumberInputStepUp"]:hover {
        background-color: #242f42 !important;
        color: #60efff !important;
    }
    div[data-testid="stNumberInput"] svg,
    button[data-testid="stNumberInputStepDown"] svg,
    button[data-testid="stNumberInputStepUp"] svg {
        fill: #00ff87 !important;
    }

    /* Labels and descriptions */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] p {
        color: #e6edf3 !important;
        -webkit-text-fill-color: #e6edf3 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        letter-spacing: 0.3px !important;
    }

    /* Selectbox dropdown popup menus */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {
        background-color: #131924 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    }
    li[data-baseweb="menu-item"] {
        background-color: #131924 !important;
        color: #e6edf3 !important;
        -webkit-text-fill-color: #e6edf3 !important;
        transition: background-color 0.15s ease !important;
    }
    li[data-baseweb="menu-item"]:hover,
    li[data-baseweb="menu-item"][aria-selected="true"] {
        background-color: rgba(0, 255, 135, 0.15) !important;
        color: #00ff87 !important;
        -webkit-text-fill-color: #00ff87 !important;
    }

    /* Action Buttons in Main App (Vibrant Neon Accent) */
    section[data-testid="stMain"] div[data-testid="stButton"] button,
    section[data-testid="stMain"] div[data-testid="stDownloadButton"] button,
    div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button,
    div[data-testid="stMainBlockContainer"] div[data-testid="stDownloadButton"] button,
    .main div[data-testid="stButton"] button,
    .main div[data-testid="stDownloadButton"] button,
    div[data-testid="stButton"] button:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]),
    button[data-testid="stBaseButton-secondary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]),
    button[data-testid="stBaseButton-primary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) {
        background: linear-gradient(135deg, #00ff87 0%, #00d2ff 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        color: #0b0f17 !important;
        font-size: 13.5px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 16px rgba(0, 255, 135, 0.25) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] button:hover,
    section[data-testid="stMain"] div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button:hover,
    div[data-testid="stMainBlockContainer"] div[data-testid="stDownloadButton"] button:hover,
    .main div[data-testid="stButton"] button:hover,
    .main div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stButton"] button:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]):hover,
    button[data-testid="stBaseButton-secondary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]):hover,
    button[data-testid="stBaseButton-primary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]):hover {
        background: linear-gradient(135deg, #10f08e 0%, #15e1ff 100%) !important;
        box-shadow: 0 6px 22px rgba(0, 255, 135, 0.45) !important;
        transform: translateY(-2px) !important;
        color: #0b0f17 !important;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] button p,
    section[data-testid="stMain"] div[data-testid="stDownloadButton"] button p,
    div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button p,
    div[data-testid="stMainBlockContainer"] div[data-testid="stDownloadButton"] button p,
    .main div[data-testid="stButton"] button p,
    .main div[data-testid="stDownloadButton"] button p,
    div[data-testid="stButton"] button:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) p,
    button[data-testid="stBaseButton-secondary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) p,
    button[data-testid="stBaseButton-primary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) p,
    div[data-testid="stButton"] button:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) span,
    button[data-testid="stBaseButton-secondary"]:not([data-testid*="sidebar_logout_btn"]):not([data-testid*="sidebar"]) span {
        color: #0b0f17 !important;
        -webkit-text-fill-color: #0b0f17 !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
    }

    /* Dataframe & Tables in Dark Theme */
    div[data-testid="stDataFrame"] {
        background: #131924 !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
        overflow: hidden !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: #131924 !important;
        color: #e6edf3 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
        font-size: 13px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: #131924 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stExpander"] summary {
        color: #e6edf3 !important;
    }

    /* Dividers */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 24px 0 !important;
    }

    /* Gamification & Athlete Level Banner */
    .level-banner {
        background: linear-gradient(135deg, rgba(0, 255, 135, 0.08) 0%, rgba(0, 210, 255, 0.05) 100%), #131924;
        border: 1px solid rgba(0, 255, 135, 0.25);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
    }
    .level-badge {
        width: 52px;
        height: 52px;
        border-radius: 12px;
        background: linear-gradient(135deg, #00ff87, #00d2ff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 0 18px rgba(0, 255, 135, 0.4);
    }
    .xp-bar-track {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        overflow: hidden;
        margin-top: 8px;
    }
    .xp-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff87, #00d2ff);
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    .streak-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 138, 0, 0.12);
        border: 1px solid rgba(255, 138, 0, 0.4);
        color: #ff9d2b;
        font-weight: 700;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 20px;
        box-shadow: 0 0 14px rgba(255, 138, 0, 0.2);
    }

    /* Badges Cards */
    .badge-card {
        background: #131924;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 14px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .badge-card.unlocked {
        border-color: rgba(0, 255, 135, 0.35);
        background: linear-gradient(145deg, #16202c, #111722);
        box-shadow: 0 4px 18px rgba(0, 255, 135, 0.12);
    }
    .badge-card.locked {
        opacity: 0.42;
        filter: grayscale(0.8);
    }
    .badge-card:hover {
        transform: translateY(-2px);
    }

    /* Nutrition & Macro Cards */
    .macro-card {
        background: linear-gradient(145deg, #131924, #0e131d);
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

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
                
            # Draw UI on frame (Athletic slate charcoal box)
            cv2.rectangle(img, (0, 0), (350, 150), (45, 52, 60), cv2.FILLED)
            cv2.putText(img, f"Reps: {count} / {self.counter.target_reps}", (15, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            cv2.putText(img, f"Sets: {self.counter.sets}", (15, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            form_color = (0, 230, 115) if feedback == "Excellent Form" else (80, 80, 255)
            cv2.putText(img, f"Form: {feedback}", (15, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.7, form_color, 2)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")


def main_app():
    user = st.session_state['user']
    
    # Sidebar Brand Header matching Hyper Gym login identity
    st.sidebar.markdown('''
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
            <svg width="38" height="28" viewBox="0 0 52 40" fill="#ffffff" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="11" width="5.5" height="18" rx="2.75" />
                <rect x="15" y="4" width="5.5" height="32" rx="2.75" />
                <rect x="18" y="17.5" width="16" height="5" />
                <rect x="31.5" y="4" width="5.5" height="32" rx="2.75" />
                <rect x="42.5" y="11" width="5.5" height="18" rx="2.75" />
            </svg>
            <div>
                <div style="font-size: 16px; font-weight: 800; letter-spacing: 1.5px; color: #ffffff; text-transform: uppercase; line-height: 1.1;">HYPER GYM</div>
                <div style="font-size: 10.5px; color: #a4b0bd; letter-spacing: 0.6px; text-transform: uppercase;">AI Motion Suite</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Athlete status badge (Compact & Attractive Pill)
    initial = user['username'][0].upper() if user.get('username') else "A"
    st.sidebar.markdown(f'''
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.09); border-radius: 20px; padding: 4px 12px 4px 5px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); backdrop-filter: blur(8px);">
            <div style="width: 22px; height: 22px; border-radius: 50%; background: linear-gradient(135deg, #00ff87, #60efff); color: #0b0f17; font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; text-transform: uppercase;">
                {initial}
            </div>
            <div style="font-size: 12.5px; font-weight: 600; color: #f0f6fc; letter-spacing: 0.3px;">
                {user['username']}
            </div>
            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #00ff87; box-shadow: 0 0 8px #00ff87;"></span>
        </div>
    ''', unsafe_allow_html=True)
    
    nav_items = {
        "Dashboard": "📊",
        "Live Workout": "🏋️",
        "Progress": "📈",
        "Nutrition": "🥗",
        "Profile": "👤",
        "Settings": "⚙️"
    }
    choice = st.sidebar.radio(
        "Navigation",
        list(nav_items.keys()),
        format_func=lambda x: nav_items[x],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("<div style='height: 28px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Logout", key="sidebar_logout_btn"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()

    def speak_cue(text):
        """Speech synthesis helper via HTML5 Web Speech API."""
        if st.session_state.get('voice_coach_enabled', True):
            clean_text = text.replace('"', '').replace("'", "")
            components.html(f"""
                <script>
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        var msg = new SpeechSynthesisUtterance("{clean_text}");
                        msg.rate = 1.05;
                        msg.pitch = 1.0;
                        window.speechSynthesis.speak(msg);
                    }}
                </script>
            """, height=0, width=0)

    if choice == "Dashboard":
        st.markdown("<h1>Performance Dashboard</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Track your training metrics, daily volume, and movement consistency.</p>', unsafe_allow_html=True)
        
        df = fetch_user_workouts(user['id'])
        level_info = calculate_athlete_level(df)
        streak = calculate_streak(df)
        badges = get_user_badges(df)
        leaderboard = get_community_leaderboard()

        # Athlete Level & XP Banner
        st.markdown(f'''
            <div class="level-banner">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div class="level-badge">{level_info['badge_icon']}</div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #00ff87; font-weight: 800; letter-spacing: 1.5px;">ATHLETE RANK • LEVEL {level_info['level']}</div>
                        <div style="font-size: 21px; font-weight: 800; color: #ffffff;">{level_info['title']}</div>
                        <div style="font-size: 12px; color: #8b949e; margin-top: 2px;">{level_info['xp']} Total XP • Next tier at {level_info['next_xp']} XP</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="streak-pill">🔥 {streak}-Day Active Streak</div>
                    <div style="font-size: 11.5px; color: #8b949e; margin-top: 6px; font-weight: 600;">{level_info['progress_pct']}% to Level {level_info['level']+1}</div>
                </div>
            </div>
            <div class="xp-bar-track" style="margin-top: -16px; margin-bottom: 24px;">
                <div class="xp-bar-fill" style="width: {level_info['progress_pct']}%;"></div>
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-card-accent"></div>
                    <div class="stat-label">Total Workouts <span>🏋️</span></div>
                    <div class="stat-value">{len(df)}</div>
                    <div class="stat-sub">Completed sessions</div>
                </div>
            ''', unsafe_allow_html=True)
        with col2:
            cal_val = f'{df["calories"].sum():.0f}' if not df.empty else "0"
            st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-card-accent"></div>
                    <div class="stat-label">Total Calories <span>🔥</span></div>
                    <div class="stat-value">{cal_val} <span style="font-size: 1.1rem; font-weight: 500; color: #7b838e;">kcal</span></div>
                    <div class="stat-sub">Energy expended</div>
                </div>
            ''', unsafe_allow_html=True)
        with col3:
            dur_val = f'{(df["duration_seconds"].sum()/60):.0f}' if not df.empty else "0"
            st.markdown(f'''
                <div class="stat-card">
                    <div class="stat-card-accent"></div>
                    <div class="stat-label">Total Duration <span>⏱️</span></div>
                    <div class="stat-value">{dur_val} <span style="font-size: 1.1rem; font-weight: 500; color: #7b838e;">min</span></div>
                    <div class="stat-sub">Active training time</div>
                </div>
            ''', unsafe_allow_html=True)

        # Achievements & Badges Showcase
        st.markdown("<h3 style='margin-top: 32px;'>🏆 Athlete Achievements & Badges</h3>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Unlock trophies by building consistency, mastering movements, and pushing volume.</p>', unsafe_allow_html=True)

        b_cols = st.columns(4)
        for idx, badge in enumerate(badges):
            col_target = b_cols[idx % 4]
            with col_target:
                status_cls = "unlocked" if badge["unlocked"] else "locked"
                status_icon = "✨ Unlocked" if badge["unlocked"] else "🔒 Locked"
                status_color = "#00ff87" if badge["unlocked"] else "#7d8590"
                st.markdown(f'''
                    <div class="badge-card {status_cls}" style="margin-bottom: 14px;">
                        <div style="font-size: 32px; margin-bottom: 6px;">{badge["icon"]}</div>
                        <div style="font-weight: 700; font-size: 13.5px; color: #ffffff; margin-bottom: 3px;">{badge["name"]}</div>
                        <div style="font-size: 11px; color: #8b949e; line-height: 1.35; margin-bottom: 8px;">{badge["description"]}</div>
                        <span style="font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: {status_color};">{status_icon}</span>
                    </div>
                ''', unsafe_allow_html=True)

        # Community Leaderboard
        with st.expander("🌍 Community Leaderboard (Top Athletes)", expanded=False):
            if leaderboard:
                leader_df = pd.DataFrame(leaderboard)
                leader_df['rank_icon'] = leader_df['rank'].apply(lambda r: "🥇" if r==1 else ("🥈" if r==2 else ("🥉" if r==3 else f"#{r}")))
                st.dataframe(
                    leader_df[['rank_icon', 'username', 'reps', 'workouts', 'calories']].rename(columns={
                        'rank_icon': 'Rank',
                        'username': 'Athlete',
                        'reps': 'Total Reps',
                        'workouts': 'Workouts',
                        'calories': 'Calories (kcal)'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Leaderboard will populate as athletes complete sessions.")
            
        st.markdown("---")
        if not df.empty:
            st.subheader("Recent Activity")
            st.dataframe(df.tail(5)[['date', 'exercise', 'reps', 'sets', 'calories']].sort_values(by='date', ascending=False), use_container_width=True)
        else:
            st.info("No workouts found yet. Head over to **Live Workout** to begin your first session!")

    elif choice == "Live Workout":
        st.markdown("<h1>Live Workout Trainer & Video Analyzer</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Real-time computer vision pose analysis, voice coaching, and offline gym video evaluation.</p>', unsafe_allow_html=True)
        
mode = st.radio("Workout Input Mode", ["📹 Live Camera Trainer", "📁 Analyze Recorded Video (.mp4)"], horizontal=True, label_visibility="collapsed")
        
        if mode == "📹 Live Camera Trainer":
            col1, col2 = st.columns([1, 2])
            with col1:
                exercise = st.selectbox("Select Exercise", ["Squat", "Push Up", "Bicep Curl", "Lunge", "Jumping Jack", "Plank"])
                target_reps = st.number_input("Target Reps per Set", min_value=1, value=10)                
                # Voice Coach toggle
                v_enabled = st.checkbox("🔊 Voice Coach Feedback", value=st.session_state.get('voice_coach_enabled', True))
                st.session_state['voice_coach_enabled'] = v_enabled
                
                # Rest Timer Widget
                st.markdown("### ⏱️ Rest-Time Timer")
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    if st.button("30s Rest"):
                        st.session_state['rest_active'] = 30
                with col_r2:
                    if st.button("60s Rest"):
                        st.session_state['rest_active'] = 60
                with col_r3:
                    if st.button("90s Rest"):
                        st.session_state['rest_active'] = 90
                        
                if st.session_state.get('rest_active', 0) > 0:
                    dur = st.session_state['rest_active']
                    st.info(f"⏳ Rest Interval Active: **{dur} seconds**. Deep breaths!")
                    speak_cue(f"Rest interval started for {dur} seconds")
                    st.session_state['rest_active'] = 0

                st.markdown("### 🎵 Workout Music")
                components.html(
                    '''
                    <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DX70RN3TfR700?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                    ''',
                    height=160
                )
                
                # Exercise Technique & Form Guide Expander
                guide = EXERCISE_GUIDES.get(exercise, {})
                if guide:
                    with st.expander(f"📖 {exercise} Technique Guide", expanded=False):
                        st.markdown(f"**Target Muscles**: {guide.get('muscles', 'N/A')}")
                        st.markdown(f"**Target Angles**: `{guide.get('target_angle', '')}`")
                        st.markdown("**Form Cues:**")
                        for cue in guide.get('cues', []):
                            st.markdown(f"• {cue}")
                        st.markdown("**Common Mistakes:**")
                        for m in guide.get('mistakes', []):
                            st.markdown(f"⚠️ {m}")
                            
            with col2:
                RTC_CONFIGURATION = {
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                }
                ctx = webrtc_streamer(
                    key="gym-trainer",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration=RTC_CONFIGURATION,
                    video_processor_factory=GymVideoProcessor,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True
                )
                
                if ctx.video_processor:
                    if ctx.video_processor.exercise != exercise:
                        ctx.video_processor.counter.reset()
                        ctx.video_processor.exercise = exercise
                    ctx.video_processor.counter.target_reps = target_reps
                    
                    if st.button("Save Workout Session"):
                        counted_reps = ctx.video_processor.counter.count
                        counted_sets = ctx.video_processor.counter.sets
                        reps_done = counted_reps + (counted_sets * target_reps)
                        if reps_done == 0:
                            reps_done = target_reps
                        sets_done = max(1, counted_sets if counted_reps == 0 and counted_sets > 0 else (counted_sets + 1))
                        cal_rate = {"Squat": 0.45, "Push Up": 0.50, "Bicep Curl": 0.30, "Lunge": 0.40, "Jumping Jack": 0.20, "Plank": 0.15}.get(exercise, 0.35)
                        calories_est = round(max(10.0, reps_done * cal_rate * 3.5), 1)
                        duration_est = max(60, reps_done * 4)
                        save_workout(user['id'], exercise, reps_done, sets_done, duration_est, 95.0, calories_est)
                        speak_cue(f"Workout saved! Great job on {reps_done} reps!")
                        st.success(f"Workout saved! Logged {reps_done} reps across {sets_done} set(s) (~{calories_est} kcal). Check Progress tab.")

        else: # Offline Video Upload & Analysis Mode
            st.markdown("### 📁 Upload Gym Workout Video")
            st.markdown("Upload a video recorded from your smartphone at the gym. Our AI will analyze your joint angles, count reps, evaluate form, and generate an annotated video.")
            
            vid_col1, vid_col2 = st.columns([1, 1.2])
            with vid_col1:
                uploaded_file = st.file_uploader("Choose a video file (.mp4, .mov, .avi)", type=["mp4", "mov", "avi"])
                vid_exercise = st.selectbox("Exercise in Video", ["Squat", "Push Up", "Bicep Curl", "Lunge", "Jumping Jack", "Plank"], key="vid_ex")
                vid_target = st.number_input("Target Reps", min_value=1, value=10, key="vid_target")
                
                if uploaded_file and st.button("⚡ Run AI Video Analysis"):
                    import tempfile
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    tfile.write(uploaded_file.read())
                    tfile.close()
                    
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()
                    status_text.text("Processing frames with MediaPipe Pose Landmarker...")
                    
                    def update_progress(p):
                        progress_bar.progress(p)
                        status_text.text(f"Analyzing biomechanics... {int(p*100)}%")
                        
                    results = analyze_workout_video(tfile.name, vid_exercise, vid_target, progress_callback=update_progress)
                    status_text.empty()
                    progress_bar.empty()
                    
                    if "error" in results:
                        st.error(results["error"])
                    else:
                        st.session_state['last_video_results'] = results
                        st.session_state['last_video_exercise'] = vid_exercise
                        speak_cue(f"Video analysis complete. Counted {results['total_reps']} reps with {results['accuracy_score']} percent accuracy.")
                        st.success("Analysis complete! Review your results on the right.")
                        
            with vid_col2:
                if 'last_video_results' in st.session_state:
                    res = st.session_state['last_video_results']
                    ex = st.session_state.get('last_video_exercise', 'Workout')
                    st.markdown("#### 🎬 Analyzed Playback Video")
                    if os.path.exists(res['output_path']):
                        st.video(res['output_path'])
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Reps", res['total_reps'])
                    m2.metric("Sets", res['sets'])
                    m3.metric("Accuracy", f"{res['accuracy_score']}%")
                    m4.metric("Est. Calories", f"{res['calories']} kcal")
                    
                    if st.button("💾 Save Video Session to Profile History"):
                        save_workout(user['id'], ex, res['total_reps'], res['sets'], res['duration_sec'], res['accuracy_score'], res['calories'])
                        st.success("Workout session successfully logged to your profile!")

    elif choice == "Progress":
        st.markdown("<h1>Progress & Analytics</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Detailed breakdown of workout volume, caloric burn, and exercise distribution.</p>', unsafe_allow_html=True)
        
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
                
                pdf_out = pdf.output(dest='S')
                pdf_bytes = pdf_out.encode('latin1') if isinstance(pdf_out, str) else bytes(pdf_out)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name='gymgenius_progress_report.pdf',
                    mime='application/pdf',
                )

    elif choice == "Nutrition":
        st.markdown("<h1>Smart Nutrition & Caloric Architecture</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Scientific BMR, TDEE, macronutrient targets, and hydration calculated for your physique and goals.</p>', unsafe_allow_html=True)
        
        col_n1, col_n2 = st.columns([1, 1.3])
        with col_n1:
            st.markdown("### ⚙️ Body Stats & Activity")
            n_weight = st.number_input("Current Weight (kg)", value=float(user['weight']) if user['weight'] else 70.0, step=0.5)
            n_height = st.number_input("Height (cm)", value=float(user['height']) if user['height'] else 170.0, step=1.0)
            n_age = st.number_input("Age", value=int(user['age']) if user['age'] else 25, step=1)
            n_gender = st.selectbox("Biological Sex", ["Male", "Female"], index=0 if user.get('gender') != "Female" else 1)
            
            goals_list = ["Hypertrophy / Muscle Gain", "Fat Loss / Cutting", "Strength & Performance", "Maintenance"]
            n_goal = st.selectbox("Primary Objective", goals_list, index=0)
            n_activity = st.selectbox("Weekly Training Frequency", ["Sedentary", "Light (1-3 days/wk)", "Moderate (3-5 days/wk)", "Active (6-7 days/wk)"], index=2)
            act_clean = n_activity.split()[0]
            
        with col_n2:
            plan = calculate_nutrition_plan(n_weight, n_height, n_age, n_gender, n_goal, act_clean)
            
            st.markdown(f'''
                <div class="macro-card" style="margin-bottom: 16px; border-color: rgba(0, 255, 135, 0.3);">
                    <div style="font-size: 11.5px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #00ff87;">RECOMMENDED DAILY INTAKE</div>
                    <div style="font-size: 2.8rem; font-weight: 800; color: #ffffff; line-height: 1.1; margin: 4px 0;">{plan['target_calories']} <span style="font-size: 1.2rem; color: #8b949e; font-weight: 500;">kcal/day</span></div>
                    <div style="font-size: 12.5px; color: #a4b0bd;">Strategy: <b style="color: #00ff87;">{plan['strategy']}</b> • TDEE Baseline: {plan['tdee']} kcal • BMR: {plan['bmr']} kcal</div>
                </div>
            ''', unsafe_allow_html=True)
            
            m_c1, m_c2, m_c3, m_c4 = st.columns(4)
            with m_c1:
                st.markdown(f'''
                    <div class="macro-card" style="border-top: 3px solid #00d2ff;">
                        <div style="font-size: 11px; text-transform: uppercase; color: #00d2ff; font-weight: 700;">Protein</div>
                        <div style="font-size: 24px; font-weight: 800; color: #ffffff;">{plan['protein_g']}g</div>
                        <div style="font-size: 10.5px; color: #8b949e;">Muscle Repair</div>
                    </div>
                ''', unsafe_allow_html=True)
            with m_c2:
                st.markdown(f'''
                    <div class="macro-card" style="border-top: 3px solid #00ff87;">
                        <div style="font-size: 11px; text-transform: uppercase; color: #00ff87; font-weight: 700;">Carbs</div>
                        <div style="font-size: 24px; font-weight: 800; color: #ffffff;">{plan['carb_g']}g</div>
                        <div style="font-size: 10.5px; color: #8b949e;">Training Fuel</div>
                    </div>
                ''', unsafe_allow_html=True)
            with m_c3:
                st.markdown(f'''
                    <div class="macro-card" style="border-top: 3px solid #f59e0b;">
                        <div style="font-size: 11px; text-transform: uppercase; color: #f59e0b; font-weight: 700;">Healthy Fats</div>
                        <div style="font-size: 24px; font-weight: 800; color: #ffffff;">{plan['fat_g']}g</div>
                        <div style="font-size: 10.5px; color: #8b949e;">Hormone Health</div>
                    </div>
                ''', unsafe_allow_html=True)
            with m_c4:
                st.markdown(f'''
                    <div class="macro-card" style="border-top: 3px solid #38bdf8;">
                        <div style="font-size: 11px; text-transform: uppercase; color: #38bdf8; font-weight: 700;">Hydration</div>
                        <div style="font-size: 24px; font-weight: 800; color: #ffffff;">{plan['water_liters']}L</div>
                        <div style="font-size: 10.5px; color: #8b949e;">Daily Water</div>
                    </div>
                ''', unsafe_allow_html=True)
                
            st.markdown(f'''
                <div style="margin-top: 16px; background: #131924; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Physique Index (BMI)</span>
                        <div style="font-size: 18px; font-weight: 800; color: #ffffff;">{plan['bmi']} <span style="font-size: 13px; font-weight: 700; color: {plan['bmi_color']};">({plan['bmi_status']})</span></div>
                    </div>
                    <div style="font-size: 12px; color: #8b949e;">Optimal Range: 18.5 – 24.9</div>
                </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("### 💡 Sports Nutrition Pro Tips")
        n_tip1, n_tip2 = st.columns(2)
        with n_tip1:
            st.info("🕒 **Pre-Workout Fuel (60-90 min before)**: Consume complex carbohydrates with moderate protein (e.g., oatmeal with whey, or banana with peanut butter) for sustained muscle glycogen.")
        with n_tip2:
            st.success("⚡ **Post-Workout Recovery (within 45 min)**: Prioritize 25-35g of fast-digesting protein alongside simple carbs to trigger muscle protein synthesis (MPS) and replenish glycogen stores.")

    elif choice == "Profile":
        st.markdown("<h1>Athlete Profile</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Manage your personal physiological stats and fitness objectives.</p>', unsafe_allow_html=True)
        
        age = st.number_input("Age", value=user['age'] if user['age'] else 25)
        gender_options = ["Male", "Female", "Other"]
        current_gender = user.get('gender')
        gender_idx = gender_options.index(current_gender) if current_gender in gender_options else 0
        gender = st.selectbox("Gender", gender_options, index=gender_idx)
        weight = st.number_input("Weight (kg)", value=user['weight'] if user['weight'] else 70.0)
        height = st.number_input("Height (cm)", value=user['height'] if user['height'] else 170.0)
        goal = st.text_input("Fitness Goal", value=user['fitness_goal'] if user['fitness_goal'] else "")
        
        if st.button("Update Profile"):
            success, msg = update_user_profile(user['id'], age, gender, weight, height, goal)
            if success:
                st.success(msg)
                st.session_state['user']['age'] = age
                st.session_state['user']['gender'] = gender
                st.session_state['user']['weight'] = weight
                st.session_state['user']['height'] = height
                st.session_state['user']['fitness_goal'] = goal
            else:
                st.error(msg)

    elif choice == "Settings":
        st.markdown("<h1>Application Settings</h1>", unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Configure interface, audio feedback, and camera preferences.</p>', unsafe_allow_html=True)
        
        st.checkbox("Hyper Gym Athletic Theme", value=True, disabled=True, help="Unified theme matching the Hyper Gym split-card login and sign up experience.")
        
        vc = st.checkbox("AI Voice Coach & Audio Cues", value=st.session_state.get('voice_coach_enabled', True), help="Speaks real-time rep counts and postural correction cues using the browser's SpeechSynthesis API.")
        st.session_state['voice_coach_enabled'] = vc
        
        st.selectbox("Default Rest Timer Duration", [30, 45, 60, 90, 120], index=2, format_func=lambda s: f"{s} seconds", help="Default timer length when resting between heavy training sets.")
        st.selectbox("Camera Selection", ["Default Camera"], help="Camera selection is handled by the browser directly when using the Live Workout feature.")

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['logged_in']:
    apply_dashboard_theme()
    main_app()
else:
    render_login_page()

