# ===============================================
# 🏥 MEDI-CARE: HOSPITAL GRADE HEART PREDICTOR
# FINAL YEAR PROJECT – PROFESSIONAL UI
# ===============================================

import streamlit as st
import pandas as pd
import joblib
import requests
import time
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# -----------------------------
# 1. PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="MediCare Diagnostic Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 2. API & STATE SETUP
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

# -----------------------------
# 3. CUSTOM CSS (HOSPITAL THEME)
# -----------------------------
st.markdown(
    """
<style>
    /* --- BACKGROUND IMAGE & MAIN THEME --- */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                          url("https://img.freepik.com/free-photo/blur-hospital_1203-7957.jpg");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* --- HEADERS --- */
    h1 {
        color: #004E64; /* Deep Medical Blue */
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h2, h3 {
        color: #007EA7; /* Lighter Medical Blue */
        font-weight: 600;
    }
    
    /* --- CARDS --- */
    .medical-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #00A8E8; /* Accent Color Strip */
        margin-bottom: 20px;
    }
    
    /* --- INPUT FIELDS --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border: 1px solid #d1d9e6;
        border-radius: 8px;
        background-color: #f8fbff;
        color: #333;
    }
    
    /* --- BUTTONS --- */
    div[data-testid="stForm"] .stButton>button, 
    button[kind="primary"] {
        background: linear-gradient(135deg, #007EA7 0%, #004E64 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 78, 100, 0.2);
        transition: transform 0.2s;
        text-transform: uppercase;
        font-size: 14px;
        letter-spacing: 0.5px;
    }
    div[data-testid="stForm"] .stButton>button:hover,
    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 78, 100, 0.3);
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    section[data-testid="stSidebar"] h1 {
        color: #004E64;
        font-size: 20px;
    }
    
    /* --- METRICS (CENTERED) --- */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px 0;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin: auto;
    }
    
    [data-testid="stMetricLabel"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        color: #555;
        font-weight: 500;
    }

    div[data-testid="stMetricValue"] {
        color: #00A8E8;
        font-size: 28px;
        font-weight: 700;
    }
    
    /* --- ALERTS/MESSAGES --- */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
    }
    
    /* --- LOGIN TEXT ALIGNMENT --- */
    .login-text {
        text-align: right;
        padding-top: 15px; /* Adjusted for better vertical centering */
        font-size: 14px;
        color: #666;
        font-weight: 500;
        white-space: nowrap;
    }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# 4. HELPER FUNCTIONS
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
    c.setFillColorRGB(0, 0.30, 0.39)  # #004E64
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
    c.setFillColorRGB(0, 0.49, 0.65)  # #007EA7
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
    c.setFillColorRGB(0, 0.49, 0.65)
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
# 5. SIDEBAR NAVIGATION
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
# 6. PATIENT PORTAL UI
# -----------------------------
if app_mode == "🏠 Patient Dashboard":

    if not st.session_state.user_logged_in:
        # === LOGIN SCREEN ===
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                "<h1 style='text-align: center; color: #004E64;'>Patient Portal</h1>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; color: #666;'>Secure Access to Your Cardiac Health Records</p>",
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                if st.session_state.user_auth_mode == "login":
                    st.subheader("Sign In")
                    u = st.text_input("Username", key="u_login")
                    p = st.text_input("Password", type="password", key="p_login")
                    if st.button(
                        "Secure Login", type="primary", use_container_width=True
                    ):
                        res = auth_user("login", u, p)
                        if res["success"]:
                            st.session_state.user_logged_in = True
                            st.session_state.user_username = res["username"]
                            st.query_params["auth_user"] = res["username"]
                            st.rerun()
                        else:
                            st.error(res["message"])

                    st.markdown("---")

                    # --- FIXED LAYOUT FOR CREATE ACCOUNT ---
                    c_txt, c_btn = st.columns([1.5, 1.2])
                    with c_txt:
                        st.markdown(
                            "<div class='login-text'>Do not have account?</div>",
                            unsafe_allow_html=True,
                        )
                    with c_btn:
                        if st.button("Create Account"):
                            st.session_state.user_auth_mode = "signup"
                            st.rerun()
                    # ---------------------------------------

                else:  # Signup Mode
                    st.subheader("New Patient Registration")
                    u = st.text_input("Choose Username", key="u_signup")
                    p = st.text_input(
                        "Create Password", type="password", key="p_signup"
                    )
                    if st.button(
                        "Register Account", type="primary", use_container_width=True
                    ):
                        res = auth_user("signup", u, p)
                        if res["success"]:
                            st.success("Account created! Login now.")
                            st.session_state.user_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res["message"])
                    if st.button("Back to Login"):
                        st.session_state.user_auth_mode = "login"
                        st.rerun()

    else:
        # === MAIN DASHBOARD ===
        # Header
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.title("🩺 Cardiac Diagnosis System")
            st.markdown("**Patient:** " + st.session_state.user_username)
        with col_h2:
            if st.button("🔒 Secure Logout", use_container_width=True):
                st.session_state.user_logged_in = False
                st.session_state.user_username = ""
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

        # Input Form Layout
        with st.container():
            st.markdown(
                "<div class='medical-card'><h4>📝 Patient Information</h4>",
                unsafe_allow_html=True,
            )
            patient_name = st.text_input("Full Name", placeholder="e.g. John Doe")
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)

            # --- Column 1: Demographics ---
            with c1:
                st.markdown(
                    "<div class='medical-card'><b>👤 Demographics & Lab</b>",
                    unsafe_allow_html=True,
                )
                age = st.number_input("Age", 1, 100, 45)
                sex = st.selectbox(
                    "Sex",
                    [0, 1],
                    format_func=lambda x: "Male" if x == 1 else "Female",
                )
                chol = st.number_input("Cholesterol (mg/dl)", 100, 600, 200)
                fbs = st.selectbox(
                    "Fasting BS > 120",
                    [0, 1],
                    format_func=lambda x: "Yes" if x == 1 else "No",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Column 2: Vitals ---
            with c2:
                st.markdown(
                    "<div class='medical-card'><b>❤️ Vitals & ECG</b>",
                    unsafe_allow_html=True,
                )
                trestbps = st.number_input("Resting BP (mm Hg)", 80, 200, 120)
                thalach = st.number_input("Max Heart Rate", 60, 250, 150)
                restecg = st.selectbox("Resting ECG", [0, 1, 2])
                slope = st.selectbox("ST Slope", [0, 1, 2])
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Column 3: Advanced ---
            with c3:
                st.markdown(
                    "<div class='medical-card'><b>🩺 Cardiac Symptoms</b>",
                    unsafe_allow_html=True,
                )
                cp = st.selectbox(
                    "Chest Pain Type",
                    [0, 1, 2, 3],
                    format_func=lambda x: [
                        "Typical",
                        "Atypical",
                        "Non-Anginal",
                        "Asymptomatic",
                    ][x],
                )
                exang = st.selectbox(
                    "Exercise Angina",
                    [0, 1],
                    format_func=lambda x: "Yes" if x == 1 else "No",
                )
                oldpeak = st.number_input("ST Depression", 0.0, 10.0, 0.0)
                ca = st.selectbox("Major Vessels", [0, 1, 2, 3])
                thal = st.selectbox(
                    "Thalassemia",
                    [1, 2, 3],
                    format_func=lambda x: ["Normal", "Fixed", "Reversible"][x - 1],
                )
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Action Button
        col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
        with col_act2:
            analyze_btn = st.button(
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
                    precautions = {
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

                    res_text = disease_map[final_pred]

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

                    # --- RESULTS DISPLAY ---
                    st.markdown("---")

                    # Header
                    if final_pred == 0:
                        st.success(f"### {res_text}")
                    else:
                        st.error(f"### {res_text}")

                    c_res1, c_res2 = st.columns(2)

                    with c_res1:
                        st.markdown(
                            "<div class='medical-card'><h5>📋 Recommended Protocol</h5>",
                            unsafe_allow_html=True,
                        )
                        for p in precautions[final_pred]:
                            st.markdown(f"✔️ {p}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    with c_res2:
                        st.markdown(
                            "<div class='medical-card'><h5>📂 Reports</h5>",
                            unsafe_allow_html=True,
                        )
                        st.write("Official diagnosis report ready for download.")

                        pdf_buff, pdf_name = create_pdf(
                            patient_name, df, res_text, precautions[final_pred]
                        )
                        st.download_button(
                            "📄 Download Medical Report (PDF)",
                            data=pdf_buff,
                            file_name=pdf_name,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 7. HOSPITAL ADMIN DASHBOARD
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
            with st.container(border=True):
                if st.session_state.admin_auth_mode == "login":
                    u = st.text_input("Admin ID")
                    p = st.text_input("Password", type="password")
                    if st.button(
                        "Access Dashboard", type="primary", use_container_width=True
                    ):
                        res = auth_admin("login", u, p)
                        if res["success"]:
                            st.session_state.admin_logged_in = True
                            st.session_state.admin_username = res["username"]
                            st.query_params["auth_admin"] = res["username"]
                            st.rerun()
                        else:
                            st.error(res["message"])

                    st.markdown("---")
                    c_txt, c_btn = st.columns([1.8, 1.2])
                    with c_txt:
                        st.markdown(
                            "<div class='login-text'>New Administrator?</div>",
                            unsafe_allow_html=True,
                        )
                    with c_btn:
                        if st.button("Register"):
                            st.session_state.admin_auth_mode = "signup"
                            st.rerun()

                else:
                    st.warning("🔒 Authorization Required")
                    u = st.text_input("New Admin ID")
                    p = st.text_input("New Password", type="password")
                    k = st.text_input(
                        "Hospital Secret Key",
                        type="password",
                        help="Contact IT Dept if lost",
                    )

                    if st.button(
                        "Register Admin", type="primary", use_container_width=True
                    ):
                        res = auth_admin("signup", u, p, k)
                        if res["success"]:
                            st.success("Admin Registered.")
                            st.session_state.admin_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res["message"])
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
                        "timestamp",
                    ]
                    final_cols = [c for c in disp_cols if c in df.columns]
                    st.dataframe(
                        df[final_cols], use_container_width=True, hide_index=True
                    )

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
