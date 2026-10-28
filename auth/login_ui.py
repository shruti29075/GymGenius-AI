import streamlit as st
import base64
import os
from auth.auth import login_user, register_user, reset_password

def get_base64_image(image_path: str) -> str:
    """Reads a local image and converts to base64 string."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_login_page():
    """Renders the Hyper Gym split-card login and registration page."""
    
    # Read query parameters for seamless link-based tab switching
    query_mode = st.query_params.get("mode", "").upper()
    if query_mode in ["REGISTER", "LOGIN"]:
        st.session_state['auth_mode'] = query_mode
        if query_mode != "FORGOT":
            st.session_state['show_forgot'] = False
    elif query_mode == "FORGOT":
        st.session_state['show_forgot'] = True
        
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'LOGIN'
    if 'show_forgot' not in st.session_state:
        st.session_state['show_forgot'] = False
        
    base_dir = os.path.dirname(os.path.dirname(__file__))
    reg_img_path = os.path.join(base_dir, "assets", "panel_register_crisp.png")
    log_img_path = os.path.join(base_dir, "assets", "panel_login_crisp.png")
    
    reg_b64 = get_base64_image(reg_img_path)
    log_b64 = get_base64_image(log_img_path)
    
    current_mode = st.session_state['auth_mode']
    left_img_b64 = reg_b64 if current_mode == 'REGISTER' else log_b64
    
    # Custom CSS for the Hyper Gym Split Card
    st.markdown("""
    <style>
        /* Light textured gym floor background */
        html, body, .stApp {
            background-color: #ebebeb !important;
            background-image: radial-gradient(#cbd2da 1.5px, transparent 1.5px) !important;
            background-size: 16px 16px !important;
            color: #2b303a !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        /* Hide Streamlit header, footer, and chrome */
        header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
        }

        /* Center container in viewport */
        .main .block-container, div[data-testid="stMainBlockContainer"] {
            max-width: 680px !important;
            padding-top: max(35px, calc(50vh - 240px)) !important;
            padding-bottom: 35px !important;
            padding-left: 15px !important;
            padding-right: 15px !important;
            margin: 0 auto !important;
        }

        /* Outer Split Card */
        .main div[data-testid="stHorizontalBlock"]:first-of-type,
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.16), 0 6px 16px rgba(0, 0, 0, 0.06) !important;
            gap: 0px !important;
            align-items: stretch !important;
            min-height: 410px !important;
        }

        /* Left column (Dark charcoal with character illustration) */
        div[data-testid="column"]:first-child {
            background-color: #484e56 !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
            border-top-left-radius: 12px !important;
            border-bottom-left-radius: 12px !important;
        }

        div[data-testid="column"]:first-child img {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #484e56 !important;
        }

        /* Right column (White form panel) */
        div[data-testid="column"]:nth-child(2) {
            background-color: #ffffff !important;
            padding: 26px 34px 22px 34px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            border-top-right-radius: 12px !important;
            border-bottom-right-radius: 12px !important;
        }

        /* Centered logo */
        .right-logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 12px;
        }

        /* Tab Switcher Links */
        .hyper-tab-wrapper {
            display: flex;
            justify-content: center;
            margin-bottom: 22px;
            width: 100%;
        }
        .hyper-tab-track {
            display: flex;
            justify-content: space-around;
            align-items: center;
            width: 85%;
            border-bottom: 2px solid #e5e8ec;
            position: relative;
            padding-bottom: 8px;
        }
        .hyper-tab {
            text-decoration: none !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            color: #9299a3 !important;
            padding: 0 12px !important;
            position: relative !important;
            transition: all 0.2s ease !important;
        }
        .hyper-tab:hover {
            color: #3b424c !important;
        }
        .hyper-tab.active {
            color: #3b424c !important;
            font-weight: 700 !important;
        }
        .hyper-tab.active::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100%;
            height: 2.5px;
            background-color: #3b424c;
            border-radius: 2px;
        }
        .hyper-tab.active::before {
            content: '';
            position: absolute;
            bottom: -15px;
            left: calc(50% - 6px);
            width: 12px;
            height: 12px;
            background: rgba(59, 66, 76, 0.15);
            border: 2px solid #3b424c;
            border-radius: 50%;
        }

        /* Forms styling */
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Input fields and wrappers */
        div[data-testid="stTextInput"],
        .stTextInput {
            margin-bottom: 12px !important;
        }

        div[data-testid="stTextInput"] label,
        .stTextInput label {
            display: none !important;
        }

        /* BaseWeb Input box wrapper */
        div[data-testid="stTextInput"] div[data-baseweb="input"],
        div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        .stTextInput div[data-baseweb="input"],
        .stTextInput div[data-baseweb="base-input"] {
            background-color: #f2f4f7 !important;
            border: 1.5px solid #d4d8df !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
        div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
        .stTextInput div[data-baseweb="input"]:focus-within,
        .stTextInput div[data-baseweb="base-input"]:focus-within {
            border-color: #383f49 !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 2px rgba(56, 63, 73, 0.15) !important;
        }

        /* The actual <input> text element - FORCE DARK TEXT FOR HIGH VISIBILITY */
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextInput"] input[type="text"],
        div[data-testid="stTextInput"] input[type="password"],
        .stTextInput input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {
            background-color: transparent !important;
            border: none !important;
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            caret-color: #111827 !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            letter-spacing: 0.3px !important;
            padding: 9px 12px !important;
            height: 38px !important;
            opacity: 1 !important;
        }

        /* Placeholder text */
        div[data-testid="stTextInput"] input::placeholder,
        .stTextInput input::placeholder {
            color: #8c939d !important;
            -webkit-text-fill-color: #8c939d !important;
            font-size: 12.5px !important;
            font-weight: 400 !important;
            opacity: 1 !important;
        }

        /* Browser Autofill fix (Chrome / Edge / Safari) */
        div[data-testid="stTextInput"] input:-webkit-autofill,
        div[data-testid="stTextInput"] input:-webkit-autofill:hover,
        div[data-testid="stTextInput"] input:-webkit-autofill:focus,
        .stTextInput input:-webkit-autofill {
            -webkit-text-fill-color: #111827 !important;
            -webkit-box-shadow: 0 0 0px 1000px #f2f4f7 inset !important;
            caret-color: #111827 !important;
            font-weight: 600 !important;
            transition: background-color 5000s ease-in-out 0s !important;
        }

        /* Password eye icon and buttons inside input */
        div[data-testid="stTextInput"] button,
        div[data-testid="stTextInput"] svg {
            color: #484e56 !important;
            fill: #484e56 !important;
        }

        /* Forgot Password Expander styling */
        div[data-testid="stExpander"] {
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            margin-top: 14px !important;
        }
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary span {
            color: #3b424c !important;
            font-weight: 600 !important;
            font-size: 13px !important;
        }
        div[data-testid="stExpander"] button {
            background-color: #4a525d !important;
            color: #ffffff !important;
            border-radius: 4px !important;
        }

        /* Submit action button (SIGN UP / LOGIN) */
        div[data-testid="stFormSubmitButton"] {
            width: 100% !important;
            display: block !important;
            margin-top: 8px !important;
        }

        div[data-testid="stFormSubmitButton"] > button {
            background-color: #4a525d !important;
            background: #4a525d !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 11px !important;
            width: 100% !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
            transition: all 0.2s ease !important;
            display: block !important;
        }

        div[data-testid="stFormSubmitButton"] > button p {
            color: #ffffff !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #383f49 !important;
            background: #383f49 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
            transform: translateY(-1px) !important;
        }

        /* Forgot password link */
        .forgot-wrapper {
            text-align: center;
            margin-top: 14px;
        }
        .forgot-link {
            text-decoration: none !important;
            font-size: 12px !important;
            color: #8c939d !important;
            font-weight: 500 !important;
            transition: color 0.2s ease !important;
        }
        .forgot-link:hover {
            color: #3b424c !important;
            text-decoration: underline !important;
        }

        /* Alert notifications */
        div[data-testid="stAlert"] {
            padding: 8px 12px !important;
            font-size: 12.5px !important;
            margin-top: 10px !important;
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Split Card Layout
    col_left, col_right = st.columns([1, 1], gap="small")
    
    with col_left:
        # Left panel: Character illustration + Hyper Gym logo
        if left_img_b64:
            st.markdown(f'''
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background-color: #484e56;">
                    <img src="data:image/png;base64,{left_img_b64}" alt="Hyper Gym" />
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="padding: 40px; text-align: center; color: white;">
                    <h2>Hyper Gym</h2>
                </div>
            """, unsafe_allow_html=True)
            
    with col_right:
        # Right panel: Dumbbell logo
        st.markdown('''
            <div class="right-logo-container">
                <svg width="44" height="34" viewBox="0 0 52 40" fill="#3b424c" xmlns="http://www.w3.org/2000/svg">
                  <rect x="4" y="11" width="5.5" height="18" rx="2.75" />
                  <rect x="15" y="4" width="5.5" height="32" rx="2.75" />
                  <rect x="18" y="17.5" width="16" height="5" />
                  <rect x="31.5" y="4" width="5.5" height="32" rx="2.75" />
                  <rect x="42.5" y="11" width="5.5" height="18" rx="2.75" />
                </svg>
            </div>
        ''', unsafe_allow_html=True)
        
        # HTML Tab Switcher
        is_reg = (current_mode == "REGISTER")
        st.markdown(f'''
            <div class="hyper-tab-wrapper">
                <div class="hyper-tab-track">
                    <a href="/?mode=register" target="_self" class="hyper-tab {"active" if is_reg else ""}">REGISTER</a>
                    <a href="/?mode=login" target="_self" class="hyper-tab {"active" if not is_reg else ""}">LOGIN</a>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # Render Form based on active tab
        if current_mode == "REGISTER":
            with st.form("register_form", clear_on_submit=False):
                reg_user = st.text_input("Username", placeholder="Username", label_visibility="collapsed", key="reg_u")
                reg_email = st.text_input("E-mail", placeholder="E-mail", label_visibility="collapsed", key="reg_e")
                reg_pass = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed", key="reg_p")
                
                submitted = st.form_submit_button("SIGN UP", use_container_width=True)
                if submitted:
                    if not reg_user or not reg_pass:
                        st.error("Please fill in Username and Password.")
                    else:
                        success, msg = register_user(reg_user, reg_pass, email=reg_email)
                        if success:
                            st.success(f"{msg} You can now log in.")
                        else:
                            st.error(msg)
                            
        else: # LOGIN mode
            with st.form("login_form", clear_on_submit=False):
                log_user = st.text_input("Username", placeholder="Username", label_visibility="collapsed", key="log_u")
                log_pass = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed", key="log_p")
                
                submitted = st.form_submit_button("LOGIN", use_container_width=True)
                if submitted:
                    if not log_user or not log_pass:
                        st.error("Please enter your Username and Password.")
                    else:
                        success, user_data = login_user(log_user, log_pass)
                        if success:
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = user_data
                            st.rerun()
                        else:
                            st.error(user_data)
                            
            # Forgot password link
            st.markdown('''
                <div class="forgot-wrapper">
                    <a href="/?mode=forgot" target="_self" class="forgot-link">Forgot password ?</a>
                </div>
            ''', unsafe_allow_html=True)
                
            if st.session_state.get('show_forgot', False):
                with st.expander("Reset Your Password", expanded=True):
                    f_user = st.text_input("Username", placeholder="Enter your username", key="f_user")
                    f_newpass = st.text_input("New Password", placeholder="Enter new password", type="password", key="f_newpass")
                    if st.button("Update Password", key="f_submit", use_container_width=True):
                        if not f_user or not f_newpass:
                            st.error("Please provide both fields.")
                        else:
                            res, m = reset_password(f_user, f_newpass)
                            if res:
                                st.success(m)
                                st.session_state['show_forgot'] = False
                                st.rerun()
                            else:
                                st.error(m)
