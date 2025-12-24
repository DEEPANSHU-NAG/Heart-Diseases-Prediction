# ===============================================
# 🏥 MEDI-CARE: HOSPITAL GRADE HEART PREDICTOR
# FINAL YEAR PROJECT – PROFESSIONAL UI
# ===============================================

import warnings
from sklearn.exceptions import InconsistentVersionWarning

# --- 1. SUPPRESS WARNINGS (Fix for Logs) ---
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

import streamlit as st
import streamlit.components.v1 as components  # ✅ Added for Google Maps
import pandas as pd
import joblib
import requests
import time
import io
import base64
import urllib.parse  # ✅ Added for Map URL encoding
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# -----------------------------
# 2. PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="MediCare Diagnostic Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 3. API & STATE SETUP
# -----------------------------
NODE_API_URL = "http://localhost:3000/api"

# --- PERSISTENCE LOGIC ---
if "auth_user" in st.query_params:
    st.session_state.user_logged_in = True
    st.session_state.user_username = st.query_params["auth_user"]

if "auth_admin" in st.query_params:
    st.session_state.admin_logged_in = True
    st.session_state.admin_username = st.query_params["auth_admin"]

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "user_username" not in st.session_state:
    st.session_state.user_username = ""
if "user_auth_mode" not in st.session_state:
    st.session_state.user_auth_mode = "login"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""
if "admin_auth_mode" not in st.session_state:
    st.session_state.admin_auth_mode = "login"

# Initialize prediction state if it doesn't exist
if "prediction_data" not in st.session_state:
    st.session_state.prediction_data = None

# -----------------------------
# 4. CUSTOM CSS (HOSPITAL THEME)
# -----------------------------
st.markdown(
    """
<style>
    /* --- GLOBAL THEME & BACKGROUND --- */
    *{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    .stApp {
        background-color: #f4f7f6; /* Fallback color if image fails */
        background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                    url("https://hmcarchitects.com/wp-content/uploads/1359024000_N23_hmchigh-2.jpg");
        background-attachment: fixed !important;
        background-size: cover !important;
        background-position: center !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* --- TYPOGRAPHY --- */
    h1 {
        background: linear-gradient(90deg, #055f85, #31b990) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding-bottom: 15px !important;
    }
    
    h2, h3, h4, h5 {
        color: #055f85 !important; /* Deep Medical Blue */
        font-weight: 700 !important;
    }

    /* --- FORM CARD STYLING (Glassmorphism) --- */
    /* Targets the form container specifically */
    [data-testid="stForm"] {
        background: linear-gradient(180deg, rgba(5, 95, 133, 0.25) 0%, rgba(49, 185, 144, 0.25) 100%); !important; 
        backdrop-filter: blur(12px) !important;
        border-radius: 50px !important;
        padding: 40px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1) !important;
        border-top: 5px solid #31b990 !important;
    }

    /* --- INPUT FIELDS --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8faff !important;
        border: 1px solid #cbd5e0 !important;
        border-radius: 10px !important;
        color: #2d3748 !important;
        padding: 10px 12px !important;
        transition: all 0.3s ease !important;
        font-size: 15px !important;
        //height: 45px !important; 
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
        border-color: #00A8E8 !important;
        box-shadow: 0 0 0 3px rgba(0, 168, 232, 0.15) !important;
    }
    
    /* Input Labels */
    .stMarkdown label p, [data-testid="stForm"] label p {
        font-weight: 600 !important;
        color: #055f85 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* --- BUTTONS --- */
    div[data-testid="stFormSubmitButton"] > button, 
    div[data-testid="stButton"] > button {
        background: linear-gradient(180deg, #055f85 0%, #31b990 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 10px rgba(5, 95, 133, 0.2) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        //margin-top: 1rem !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover, 
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(90deg, #31b990 0%, #055f85 100%)!important;
        box-shadow: 0 6px 20px rgba(0, 78, 100, 0.35)!important;
        transform: translateY(-2px)!important;
    }

    /* --- EYE ICON FIX --- */
    /* Prevent the eye icon in password fields from getting the giant button style */
    button[aria-label="Show password"],
    button[aria-label="Hide password"] {
        background: transparent !important;
        width: auto !important;
        box-shadow: none !important;
        border: none !important;
        color: inherit !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* --- SIDEBAR (GRADIENT THEME) --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #055f85 0%, #31b990 100%); /* Deep Teal to Greenish Teal */
        border-right: 1px solid #044a6e;
        box-shadow: 4px 0 15px rgba(0,0,0,0.2);
    }
    
    /* FORCE ALL SIDEBAR TEXT TO WHITE */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Sidebar H1 specific tweaks */
    section[data-testid="stSidebar"] h1 {
        background: none;
        font-size: 20px;
        text-align: center;
        margin-top: 10px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Sidebar Radio Buttons */
    section[data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        font-weight: 500;
        cursor: pointer;
    }

    /* --- METRICS --- */
    [data-testid="stMetric"] {
        background-color: white !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 1px solid #e1e8ed !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    div[data-testid="stMetricValue"] {
        color: #055f85 !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    
    /* --- LOGIN TEXT LINK ALIGNMENT --- */
    .login-text {
        text-align: right !important;
        font-size: 14px !important;
        color: #666 !important;
        font-weight: 500 !important;
        padding-top: 10px !important; 
    }
    
    /* --- REPORT CARDS --- */
    .medical-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #31b990;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }

</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# 5. HELPER FUNCTIONS
# -----------------------------
def auth_user(endpoint, username, password):
    try:
        res = requests.post(
            f"{NODE_API_URL}/{endpoint}",
            json={"username": username, "password": password},
        )
        if res.status_code == 200:
            return res.json()
        return {"success": False, "message": "Server Error"}
    except:
        return {"success": False, "message": "Connection Error"}


def auth_admin(endpoint, username, password, secret=None):
    try:
        payload = {"username": username, "password": password}
        if secret:
            payload["secretKey"] = secret
        res = requests.post(f"{NODE_API_URL}/admin/{endpoint}", json=payload)
        if res.status_code == 200:
            return res.json()
        return {"success": False, "message": "Server Error"}
    except:
        return {"success": False, "message": "Connection Error"}


def create_pdf(patient_name, df, disease, precautions_list):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Header Background
    c.setFillColorRGB(0.02, 0.37, 0.52)  # #055f85
    c.rect(0, h - 90, w, 90, fill=1, stroke=0)

    # Header Text
    c.setFillColorRGB(1, 1, 1)  # White
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(w / 2, h - 45, "CITY HEART CARE DIAGNOSTIC CENTER")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w / 2, h - 65, "Advanced AI-Powered Cardiac Analysis Unit")

    # Reset
    c.setFillColorRGB(0, 0, 0)

    # Patient Info Block
    c.setLineWidth(0.5)
    c.rect(40, h - 160, w - 80, 50, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, h - 135, f"PATIENT: {patient_name}")
    c.drawRightString(
        w - 50, h - 135, f"DATE: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}"
    )

    # Clinical Data
    y = h - 200
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.19, 0.72, 0.56)  # #31b990
    c.drawString(40, y, "CLINICAL PARAMETERS")
    c.setFillColorRGB(0, 0, 0)
    c.line(40, y - 5, w - 40, y - 5)
    y -= 30

    c.setFont("Helvetica", 10)
    row = df.iloc[0]

    # Map values
    sex_str = "Male" if row["sex"] == 1 else "Female"
    fbs_str = "> 120 mg/dl" if row["fbs"] == 1 else "< 120 mg/dl"
    exang_str = "Yes" if row["exang"] == 1 else "No"

    params = [
        ("Age", f"{row['age']} Years"),
        ("Gender", sex_str),
        ("Chest Pain Type", str(row["cp"])),
        ("Resting BP", f"{row['trestbps']} mm Hg"),
        ("Cholesterol", f"{row['chol']} mg/dl"),
        ("Fasting Blood Sugar", fbs_str),
        ("ECG Result", str(row["restecg"])),
        ("Max Heart Rate", str(row["thalach"])),
        ("Exercise Angina", exang_str),
        ("ST Depression", str(row["oldpeak"])),
        ("Slope", str(row["slope"])),
        ("Major Vessels", str(row["ca"])),
        ("Thalassemia", str(row["thal"])),
    ]

    # Grid Layout
    start_y = y
    for i, (k, v) in enumerate(params):
        # Left column
        if i % 2 == 0:
            c.drawString(50, y, f"{k}:")
            c.drawString(150, y, f"{v}")
        # Right column
        else:
            c.drawString(300, y, f"{k}:")
            c.drawString(400, y, f"{v}")
            y -= 20  # Move down after completing a row

    # If odd number of params, move y down for the last half-row
    if len(params) % 2 != 0:
        y -= 20

    # Diagnosis Box
    y -= 30
    c.setFillColorRGB(0.96, 0.98, 1)  # Very light blue
    c.rect(40, y - 50, w - 80, 60, fill=1, stroke=1)

    c.setFillColorRGB(0.8, 0, 0)  # Red
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w / 2, y - 15, "FINAL DIAGNOSIS")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w / 2, y - 35, disease.upper())

    # Precautions
    y -= 90
    c.setFillColorRGB(0.02, 0.37, 0.52)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "MEDICAL RECOMMENDATIONS")
    c.setFillColorRGB(0, 0, 0)
    c.line(40, y - 5, w - 40, y - 5)
    y -= 25

    c.setFont("Helvetica", 11)

    # ✅ IMPROVED: Text Wrapping for Recommendations
    def draw_wrapped_text(c, text, x, y, max_width):
        """Helper to draw text with word wrapping."""
        from reportlab.lib.utils import simpleSplit

        lines = simpleSplit(text, c._fontname, c._fontsize, max_width)
        for line in lines:
            c.drawString(x, y, line)
            y -= 15  # Line spacing
        return y

    # Drawing the list
    for p in precautions_list:
        # Draw bullet point
        c.drawString(50, y, "•")
        # Draw wrapped text starting slightly to the right of the bullet
        # 500 is roughly the width available (A4 width ~595 - margin)
        y = draw_wrapped_text(c, p, 65, y, 480)
        y -= 5  # Extra spacing between items

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(
        w / 2,
        30,
        "This report is generated by AI. Please consult a cardiologist for clinical correlation.",
    )

    c.save()
    buffer.seek(0)
    return buffer, f"Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Header Background
    c.setFillColorRGB(0.02, 0.37, 0.52)  # #055f85
    c.rect(0, h - 90, w, 90, fill=1, stroke=0)

    # Header Text
    c.setFillColorRGB(1, 1, 1)  # White
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(w / 2, h - 45, "CITY HEART CARE DIAGNOSTIC CENTER")
    c.setFont("Helvetica", 12)
    c.drawCentredString(w / 2, h - 65, "Advanced AI-Powered Cardiac Analysis Unit")

    # Reset
    c.setFillColorRGB(0, 0, 0)

    # Patient Info Block
    c.setLineWidth(0.5)
    c.rect(40, h - 160, w - 80, 50, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, h - 135, f"PATIENT: {patient_name}")
    c.drawRightString(
        w - 50, h - 135, f"DATE: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}"
    )

    # Clinical Data
    y = h - 200
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.19, 0.72, 0.56)  # #31b990
    c.drawString(40, y, "CLINICAL PARAMETERS")
    c.setFillColorRGB(0, 0, 0)
    c.line(40, y - 5, w - 40, y - 5)
    y -= 30

    c.setFont("Helvetica", 10)
    row = df.iloc[0]

    # Map values
    sex_str = "Male" if row["sex"] == 1 else "Female"
    fbs_str = "> 120 mg/dl" if row["fbs"] == 1 else "< 120 mg/dl"
    exang_str = "Yes" if row["exang"] == 1 else "No"

    params = [
        ("Age", f"{row['age']} Years"),
        ("Gender", sex_str),
        ("Chest Pain Type", str(row["cp"])),
        ("Resting BP", f"{row['trestbps']} mm Hg"),
        ("Cholesterol", f"{row['chol']} mg/dl"),
        ("Fasting Blood Sugar", fbs_str),
        ("ECG Result", str(row["restecg"])),
        ("Max Heart Rate", str(row["thalach"])),
        ("Exercise Angina", exang_str),
        ("ST Depression", str(row["oldpeak"])),
        ("Slope", str(row["slope"])),
        ("Major Vessels", str(row["ca"])),
        ("Thalassemia", str(row["thal"])),
    ]

    # Grid Layout
    start_y = y
    for i, (k, v) in enumerate(params):
        # Left column
        if i % 2 == 0:
            c.drawString(50, y, f"{k}:")
            c.drawString(150, y, f"{v}")
        # Right column
        else:
            c.drawString(300, y, f"{k}:")
            c.drawString(400, y, f"{v}")
            y -= 20  # Move down after completing a row

    # If odd number of params, move y down for the last half-row
    if len(params) % 2 != 0:
        y -= 20

    # Diagnosis Box
    y -= 30
    c.setFillColorRGB(0.96, 0.98, 1)  # Very light blue
    c.rect(40, y - 50, w - 80, 60, fill=1, stroke=1)

    c.setFillColorRGB(0.8, 0, 0)  # Red
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w / 2, y - 15, "FINAL DIAGNOSIS")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w / 2, y - 35, disease.upper())

    # Precautions
    y -= 90
    c.setFillColorRGB(0.02, 0.37, 0.52)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "MEDICAL RECOMMENDATIONS")
    c.setFillColorRGB(0, 0, 0)
    c.line(40, y - 5, w - 40, y - 5)
    y -= 25

    c.setFont("Helvetica", 11)
    for p in precautions_list:
        c.drawString(50, y, f"• {p}")
        y -= 18

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(
        w / 2,
        30,
        "This report is generated by AI. Please consult a cardiologist for clinical correlation.",
    )

    c.save()
    buffer.seek(0)
    return buffer, f"Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf"


# -----------------------------
# 6. SIDEBAR NAVIGATION
# -----------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=80)
    st.markdown("### MediCare Portal")
    st.markdown("---")
    # ✅ EMOJIS ADDED HERE
    app_mode = st.radio(
        "Navigate", ["🏠 Patient Dashboard", "🏥 Hospital Admin"], index=0
    )
    st.markdown("---")

    # Footer
    st.caption("© 2025 City Heart Care")
    st.caption("Secure Medical System")

# -----------------------------
# 7. PATIENT PORTAL UI
# -----------------------------
if app_mode == "🏠 Patient Dashboard":

    if not st.session_state.user_logged_in:
        # === LOGIN SCREEN ===
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                "<h1 style='text-align: center; color: #055f85;'>Patient Portal</h1>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; color: #555;'>Secure Access to Your Cardiac Health Records</p>",
                unsafe_allow_html=True,
            )

            # ✅ Login Form wrapped in styled FORM
            if st.session_state.user_auth_mode == "login":
                # ✅ ADDED KEY HERE
                with st.form("login_form", border=True):
                    st.markdown(
                        "<h3 style='text-align: center; color: #055f85; margin-top: 0;'>Sign In</h3>",
                        unsafe_allow_html=True,
                    )
                    u = st.text_input("Username", key="u_login")
                    p = st.text_input("Password", type="password", key="p_login")

                    st.markdown("<br>", unsafe_allow_html=True)
                    # ✅ Replaced st.button with st.form_submit_button
                    submitted = st.form_submit_button(
                        "Secure Login", type="primary", use_container_width=True
                    )

                    if submitted:
                        res = auth_user("login", u, p)
                        if res["success"]:
                            st.session_state.user_logged_in = True
                            st.session_state.user_username = res["username"]
                            st.query_params["auth_user"] = res["username"]
                            st.rerun()
                        else:
                            st.error(res["message"])

                st.markdown("---")

                # ✅ "New here?" text and "Create Account" button aligned (Outside form)
                c_txt, c_btn = st.columns([1.5, 1.2])
                with c_txt:
                    st.markdown(
                        "<div class='login-text'>New here?</div>",
                        unsafe_allow_html=True,
                    )
                with c_btn:
                    if st.button("Create Account", use_container_width=True):
                        st.session_state.user_auth_mode = "signup"
                        st.rerun()

            else:  # Signup Mode
                with st.form("signup_form", border=True):
                    st.markdown(
                        "<h3 style='text-align: center; color: #055f85; margin-top: 0;'>Register</h3>",
                        unsafe_allow_html=True,
                    )
                    u = st.text_input("Choose Username", key="u_signup")
                    p = st.text_input(
                        "Create Password", type="password", key="p_signup"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button(
                        "Register Account", type="primary", use_container_width=True
                    )

                    if submitted:
                        res = auth_user("signup", u, p)
                        if res["success"]:
                            st.success("Account created! Login now.")
                            st.session_state.user_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res["message"])

                st.markdown("---")
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.user_auth_mode = "login"
                    st.rerun()

    else:
        # === MAIN DASHBOARD ===
        # Header
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.title("🩺 Cardiac Diagnosis System")
            st.markdown(f"**Welcome, {st.session_state.user_username}**")
        with col_h2:
            if st.button("🔒 Secure Logout", width="stretch"):
                st.session_state.user_logged_in = False
                st.session_state.user_username = ""
                # Clear session state on logout
                if "prediction_data" in st.session_state:
                    del st.session_state["prediction_data"]
                st.query_params.clear()
                st.rerun()

        st.markdown("<hr style='margin: 0 0 20px 0;'>", unsafe_allow_html=True)

        # Load Models
        try:
            model = joblib.load("heart_model.pkl")
            scaler = joblib.load("scaler.pkl")
        except:
            st.error("System Error: Models not found.")
            st.stop()

        # ✅ MAIN FORM - Using st.form
        with st.form("patient_data_form", border=True):
            st.markdown(
                "<h3 style='color: #055f85; margin-bottom: 20px;'>📝 Patient Information Form</h3>",
                unsafe_allow_html=True,
            )
            patient_name = st.text_input("Full Name", placeholder="e.g. John Doe")

            st.markdown("<br>", unsafe_allow_html=True)

            # 2-Column Grid Layout
            c1, c2 = st.columns(2)

            with c1:
                age = st.number_input("Age", 1, 100, 45)
                sex = st.selectbox("Sex (0 = Female | 1 = Male)", [0, 1])
                cp = st.selectbox("Chest Pain Type (0–3)", [0, 1, 2, 3])
                trestbps = st.number_input("Resting Blood Pressure", 80, 200, 120)
                chol = st.number_input("Cholesterol", 100, 600, 200)
                fbs = st.selectbox("Fasting Blood Sugar > 120", [0, 1])
                restecg = st.selectbox("ECG Result (0–2)", [0, 1, 2])

            with c2:
                thalach = st.number_input("Maximum Heart Rate", 60, 250, 150)
                exang = st.selectbox("Exercise Induced Angina", [0, 1])
                oldpeak = st.number_input("ST Depression (Oldpeak)", 0.0, 10.0, 0.0)
                slope = st.selectbox("Slope (0–2)", [0, 1, 2])
                ca = st.selectbox("Major Vessels (0–3)", [0, 1, 2, 3])
                thal = st.selectbox(
                    "Thalassemia (1 = Normal | 2 = Fixed | 3 = Reversible)", [1, 2, 3]
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Action Button - Must be form_submit_button inside st.form
            col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
            with col_act2:
                analyze_btn = st.form_submit_button(
                    "🔍 ANALYZE CLINICAL DATA", type="primary", use_container_width=True
                )

        # Logic
        if analyze_btn:
            if not patient_name:
                st.warning("⚠️ Please enter the Patient Name first.")
            else:
                with st.spinner("Processing Medical Records..."):
                    time.sleep(1)  # UX effect

                    # Data Prep
                    df = pd.DataFrame(
                        [
                            [
                                age,
                                sex,
                                cp,
                                trestbps,
                                chol,
                                fbs,
                                restecg,
                                thalach,
                                exang,
                                oldpeak,
                                slope,
                                ca,
                                thal,
                            ]
                        ],
                        columns=[
                            "age",
                            "sex",
                            "cp",
                            "trestbps",
                            "chol",
                            "fbs",
                            "restecg",
                            "thalach",
                            "exang",
                            "oldpeak",
                            "slope",
                            "ca",
                            "thal",
                        ],
                    )

                    scaled = scaler.transform(df)
                    pred = model.predict(scaled)[0]

                    # Rule Engine Override
                    final_pred = pred
                    if pred == 0:
                        if cp in [2, 3] and oldpeak < 1:
                            final_pred = 1
                        elif chol > 240 and oldpeak >= 1:
                            final_pred = 2
                        elif cp == 3 and oldpeak > 2:
                            final_pred = 3
                        elif exang == 1 and oldpeak > 2 and thalach < 120:
                            final_pred = 4

                    # Mappings
                    disease_map = {
                        0: "✅ No Significant Disease",
                        1: "🫀 Angina Pectoris",
                        2: "🩺 Coronary Artery Disease",
                        3: "🚑 Myocardial Infarction",
                        4: "⚠️ Heart Failure",
                    }

                    # ✅ SEPARATE RECOMMENDATIONS (DETAILED) & PRECAUTIONS (LIFESTYLE)
                    recommended_protocol = {
                        0: [
                            "Maintain a consistent cardiovascular exercise routine (e.g., brisk walking, jogging) for at least 30 minutes daily.",
                            "Adhere to a balanced, heart-healthy diet rich in fruits, vegetables, whole grains, and lean proteins.",
                            "Schedule annual comprehensive cardiac health checkups to monitor cholesterol, blood pressure, and other risk factors.",
                        ],
                        1: [
                            "Implement stress management techniques (e.g., meditation, deep breathing) to reduce triggers for angina attacks.",
                            "Strictly avoid heavy lifting, strenuous physical exertion, or emotional stress that may precipitate chest pain.",
                            "Keep prescribed Nitroglycerin medication accessible at all times and take immediately upon onset of symptoms.",
                        ],
                        2: [
                            "Adopt a strict low-cholesterol, low-saturated fat diet (Mediterranean diet recommended) to prevent plaque buildup.",
                            "Immediate and complete cessation of smoking and avoidance of passive smoke exposure is critical.",
                            "Ensure strict adherence to prescribed Statins and anti-platelet medications to stabilize coronary arteries.",
                        ],
                        3: [
                            "Follow emergency protocols immediately: Call emergency services if chest pain, shortness of breath, or sweating occurs.",
                            "Adhere strictly to post-MI medication regimen (Beta-blockers, ACE inhibitors, Anti-platelets) as directed.",
                            "Enroll and participate in a medically supervised Cardiac Rehabilitation program to safely regain functional capacity.",
                        ],
                        4: [
                            "Monitor fluid intake strictly (typically restricted to 1.5 - 2.0 liters per day) to prevent fluid overload and edema.",
                            "Follow a strict low-sodium diet (less than 2g of salt per day) to manage blood pressure and fluid retention.",
                            "Perform daily weight checks at the same time; report sudden weight gain (>2-3 lbs in a day) to your cardiologist immediately.",
                        ],
                    }

                    safety_precautions = {
                        0: [
                            "Avoid smoking and excessive alcohol consumption.",
                            "Monitor blood pressure regularly at home.",
                        ],
                        1: [
                            "Stop physical activity immediately if chest pain occurs.",
                            "Keep emergency contacts and medical ID accessible.",
                        ],
                        2: [
                            "Avoid processed foods high in trans fats.",
                            "Monitor lipid profile every 6 months.",
                        ],
                        3: [
                            "Carry personal medical history at all times.",
                            "Avoid sudden strenuous exertion or temperature extremes.",
                        ],
                        4: [
                            "Elevate head while sleeping to ease breathing.",
                            "Avoid NSAIDs (painkillers) that worsen fluid retention.",
                        ],
                    }

                    # ✅ NEW: Typical Symptoms
                    typical_symptoms = {
                        0: [
                            "No significant cardiac symptoms reported",
                            "General well-being normal",
                        ],
                        1: [
                            "Chest discomfort (pressure/squeezing)",
                            "Pain radiating to arm/jaw",
                            "Shortness of breath on exertion",
                        ],
                        2: [
                            "Chest pain (Angina)",
                            "Fatigue & weakness",
                            "Irregular heartbeats (Palpitations)",
                        ],
                        3: [
                            "Severe, crushing chest pain",
                            "Cold sweat, nausea, vomiting",
                            "Lightheadedness or sudden dizziness",
                        ],
                        4: [
                            "Shortness of breath (active or at rest)",
                            "Swelling in legs/ankles/feet",
                            "Persistent coughing or wheezing",
                        ],
                    }

                    res_text = disease_map[final_pred]

                    # Combine for DB/PDF
                    full_precautions_list = (
                        recommended_protocol[final_pred]
                        + safety_precautions[final_pred]
                    )

                    # Save result to session state (PERSISTENCE)
                    st.session_state.prediction_data = {
                        "patient_name": patient_name,
                        "final_pred": final_pred,
                        "res_text": res_text,
                        "typical_symptoms": typical_symptoms[final_pred],
                        "recommended_protocol": recommended_protocol[final_pred],
                        "safety_precautions": safety_precautions[final_pred],
                        "df": df,
                        "full_precautions_list": full_precautions_list,
                    }

                    # Save (No PDF)
                    try:
                        payload = {
                            "username": st.session_state.user_username,
                            "patient_name": patient_name,
                            "age": age,
                            "sex": sex,
                            "cp": cp,
                            "trestbps": trestbps,
                            "chol": chol,
                            "fbs": fbs,
                            "restecg": restecg,
                            "thalach": thalach,
                            "exang": exang,
                            "oldpeak": oldpeak,
                            "slope": slope,
                            "ca": ca,
                            "thal": thal,
                            "prediction": int(final_pred),
                            "disease": res_text,
                        }
                        requests.post(f"{NODE_API_URL}/save-report", json=payload)
                    except:
                        pass

        # ✅ Display Results if data exists in session state
        if st.session_state.prediction_data:
            data = st.session_state.prediction_data

            # --- RESULTS DISPLAY ---
            st.markdown("---")

            # Header
            if data["final_pred"] == 0:
                st.success(f"### {data['res_text']}")
            else:
                st.error(f"### {data['res_text']}")

            # ✅ UPDATED LAYOUT: SYMPTOMS, PROTOCOL & PRECAUTIONS SIDE-BY-SIDE
            c_res1, c_res2, c_res3 = st.columns(3)

            with c_res1:
                st.markdown(
                    "<div class='medical-card'><h5>🔍 Typical Symptoms</h5>",
                    unsafe_allow_html=True,
                )
                for p in data["typical_symptoms"]:
                    st.markdown(f"🔸 {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c_res2:
                st.markdown(
                    "<div class='medical-card'><h5>📋 Recommended Protocol</h5>",
                    unsafe_allow_html=True,
                )
                for p in data["recommended_protocol"]:
                    st.markdown(f"✔️ {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c_res3:
                st.markdown(
                    "<div class='medical-card'><h5>🛡️ Safety Precautions</h5>",
                    unsafe_allow_html=True,
                )
                for p in data["safety_precautions"]:
                    st.markdown(f"⚠️ {p}")
                st.markdown("</div>", unsafe_allow_html=True)

            # ✅ REPORTS SECTION BELOW
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container():
                st.markdown(
                    "<div class='medical-card'><h5>📂 Official Reports</h5>",
                    unsafe_allow_html=True,
                )
                c_rep1, c_rep2 = st.columns([3, 1])
                with c_rep1:
                    st.write(
                        "Official AI-generated diagnosis report is ready for download."
                    )
                with c_rep2:
                    pdf_buff, pdf_name = create_pdf(
                        data["patient_name"],
                        data["df"],
                        data["res_text"],
                        data["full_precautions_list"],
                    )
                    st.download_button(
                        "📄 Download Report (PDF)",
                        data=pdf_buff,
                        file_name=pdf_name,
                        mime="application/pdf",
                        width="stretch",
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            # ✅ NEW: GOOGLE MAP SECTION
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📍 Locate Nearest Heart Specialists")

            # Search functionality for Map
            search_col1, search_col2 = st.columns([4, 1.5])  # Adjusted alignment
            with search_col1:
                # Removed default value, added label_visibility="collapsed" and placeholder
                location_query = st.text_input(
                    "Enter Location (City, Zip, or 'Near Me')",
                    "",
                    key="map_search",
                    label_visibility="collapsed",
                    placeholder="Enter City, Zip, or 'Near Me'",
                )
            with search_col2:
                search_clicked = st.button("Search Location", use_container_width=True)

            # Intelligent query construction
            if location_query.lower() == "near me" or not location_query.strip():
                query_term = "Heart Specialist Hospital Near Me"
            else:
                query_term = f"Heart Specialist Hospital in {location_query}"

            # Encode query for URL
            query_string = urllib.parse.quote(query_term)

            # Embedding Google Maps with a search query
            map_html = f"""
            <iframe 
                width="100%" 
                height="450" 
                frameborder="0" 
                scrolling="no" 
                marginheight="0" 
                marginwidth="0" 
                src="https://maps.google.com/maps?q={query_string}&t=&z=13&ie=UTF8&iwloc=&output=embed">
            </iframe>
            <br>
            <small>
                <a href="https://maps.google.com/maps?q={query_string}" target="_blank" style="color:#0000FF;text-align:left">
                    View Larger Map
                </a>
            </small>
            """
            components.html(map_html, height=500)

# -----------------------------
# 8. HOSPITAL ADMIN DASHBOARD
# -----------------------------
elif app_mode == "🏥 Hospital Admin":

    if not st.session_state.admin_logged_in:
        # Admin Login
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown(
                "<br><h1 style='text-align: center; color: #004E64;'>Admin Portal</h1>",
                unsafe_allow_html=True,
            )
            # ✅ ADDED KEY HERE
            with st.form("admin_login_form", border=True):
                if st.session_state.admin_auth_mode == "login":
                    st.markdown(
                        "<h2 style='text-align: center; color: #004E64; margin-bottom: 20px;'>Admin Sign In</h2>",
                        unsafe_allow_html=True,
                    )
                    u = st.text_input("Admin ID")
                    p = st.text_input("Password", type="password")
                    # ✅ Replaced st.button with st.form_submit_button
                    submitted = st.form_submit_button(
                        "Access Dashboard", type="primary", use_container_width=True
                    )

                    if submitted:
                        res = auth_admin("login", u, p)
                        if res["success"]:
                            st.session_state.admin_logged_in = True
                            st.session_state.admin_username = res["username"]
                            st.query_params["auth_admin"] = res["username"]
                            st.rerun()
                        else:
                            st.error(res["message"])

                else:
                    st.markdown(
                        "<h3 style='text-align: center; color: #004E64; margin-bottom: 20px;'>New Admin Registration</h3>",
                        unsafe_allow_html=True,
                    )
                    st.warning("🔒 Authorization Required")
                    u = st.text_input("New Admin ID")
                    p = st.text_input("New Password", type="password")
                    k = st.text_input(
                        "Hospital Secret Key",
                        type="password",
                        help="Contact IT Dept if lost",
                    )
                    # ✅ Replaced st.button with st.form_submit_button
                    submitted = st.form_submit_button(
                        "Register Admin", type="primary", use_container_width=True
                    )

                    if submitted:
                        res = auth_admin("signup", u, p, k)
                        if res["success"]:
                            st.success("Admin Registered.")
                            st.session_state.admin_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res["message"])

            # Switching buttons (outside form)
            st.markdown("---")
            c_txt, c_btn = st.columns([1.8, 1.2])
            with c_txt:
                if st.session_state.admin_auth_mode == "login":
                    st.markdown(
                        "<div class='login-text'>New Administrator?</div>",
                        unsafe_allow_html=True,
                    )
            with c_btn:
                if st.session_state.admin_auth_mode == "login":
                    if st.button("Register"):
                        st.session_state.admin_auth_mode = "signup"
                        st.rerun()
                else:
                    if st.button("Back"):
                        st.session_state.admin_auth_mode = "login"
                        st.rerun()

    else:
        # Admin Dashboard
        st.title("🛡️ Hospital Administration")
        st.markdown(f"**Logged in as:** {st.session_state.admin_username}")
        if st.button("Log Out"):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = ""
            st.query_params.clear()
            st.rerun()

        st.divider()

        try:
            res = requests.get(f"{NODE_API_URL}/admin/patients")
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    df = pd.DataFrame(data)

                    # --- ADD EMOJIS TO TABLE DISPLAY ---
                    def add_emoji_to_disease(name):
                        name = str(name).strip()
                        if any(char in name for char in ["✅", "🫀", "🩺", "🚑", "⚠️"]):
                            return name

                        if "No Significant" in name or "No Disease" in name:
                            return f"✅ {name}"
                        if "Angina" in name:
                            return f"🫀 {name}"
                        if "Coronary" in name:
                            return f"🩺 {name}"
                        if "Myocardial" in name:
                            return f"🚑 {name}"
                        if "Heart Failure" in name:
                            return f"⚠️ {name}"
                        return name

                    if "disease_name" in df.columns:
                        df["disease_name"] = df["disease_name"].apply(
                            add_emoji_to_disease
                        )

                    # ✅ ADD TIME EMOJI AND FORMAT TIMESTAMP
                    if "timestamp" in df.columns:
                        # Convert ISO 8601 to Datetime object then format nicely to DD-MM-YYYY HH:MM:SS
                        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime(
                            "%d-%m-%Y %H:%M:%S"
                        )
                        df["timestamp"] = df["timestamp"].apply(lambda x: f"🕒 {x}")

                    # ✅ MAP SEX COLUMN (0 -> Female, 1 -> Male)
                    if "sex" in df.columns:
                        df["sex"] = df["sex"].apply(
                            lambda x: "Male" if int(x) == 1 else "Female"
                        )

                    # ✅ ADD PRECAUTIONS COLUMN (Summary for Table)
                    precautions_map = {
                        0: "• Regular Cardio\n• Balanced Diet\n• Annual Checkups",
                        1: "• Stress Management\n• Avoid Heavy Lifting\n• Nitroglycerin SOS",
                        2: "• Low Cholesterol Diet\n• Stop Smoking\n• Statins Adherence",
                        3: "• Emergency Protocols\n• Beta-blockers\n• Cardiac Rehab",
                        4: "• Fluid Restriction\n• Low Sodium\n• Daily Weight Check",
                    }

                    if "prediction_result" in df.columns:
                        df["precautions"] = df["prediction_result"].apply(
                            lambda x: precautions_map.get(int(x), "Consult Doctor")
                        )
                    # -----------------------------------

                    # Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Patients", len(df))
                    m2.metric(
                        "Positive Cases",
                        len(df[df["prediction_result"] > 0]),
                        delta_color="inverse",
                    )
                    m3.metric("Healthy Cases", len(df[df["prediction_result"] == 0]))
                    m4.metric("Last Update", datetime.now().strftime("%H:%M"))

                    st.markdown("### 🗂️ Patient Records Database")

                    # Filter
                    search = st.text_input("🔍 Search Database (Name / Disease)")
                    if search:
                        df = df[
                            df["patient_name"].str.contains(
                                search, case=False, na=False
                            )
                            | df["disease_name"].str.contains(
                                search, case=False, na=False
                            )
                        ]

                    # Table
                    disp_cols = [
                        "patient_name",
                        "age",
                        "sex",
                        "disease_name",
                        "precautions",  # ✅ Added column
                        "timestamp",
                    ]
                    final_cols = [c for c in disp_cols if c in df.columns]
                    st.dataframe(df[final_cols], width="stretch", hide_index=True)

                    # Download
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Export Database (CSV)",
                        csv,
                        "hospital_records.csv",
                        "text/csv",
                    )
                else:
                    st.info("No records found in the hospital database.")
            else:
                st.error("Database connection failed.")
        except:
            st.error("Server unavailable.")
