# ===============================================
# 💓 HEART DISEASE TYPE PREDICTOR
# FINAL YEAR PROJECT – STREAMLIT APP
# WITH NODE.JS AUTHENTICATION & PDF REPORT
# ===============================================

import streamlit as st
import pandas as pd
import joblib
import requests
import time
import io  # ✅ Required for in-memory PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black, red
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Heart Disease Diagnosis", page_icon="💓", layout="wide")

# -----------------------------
# API CONFIGURATION
# -----------------------------
NODE_API_URL = "http://localhost:3000/api"

# -----------------------------
# SESSION STATE
# -----------------------------
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
# AUTH FUNCTIONS
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


# -----------------------------
# PDF FUNCTION (IN-MEMORY - NO FILE SAVED)
# -----------------------------
def create_pdf(patient_name, df, disease, precautions_list):
    buffer = io.BytesIO()  # Create a buffer in RAM
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # --- HEADER ---
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w / 2, h - 50, "CITY HEART CARE DIAGNOSTIC CENTER")

    c.setFont("Helvetica", 10)
    c.drawCentredString(w / 2, h - 65, "AI Powered Cardiac Diagnosis Report")

    # Horizontal Line
    c.setLineWidth(1)
    c.line(40, h - 75, w - 40, h - 75)

    # --- PATIENT INFO ---
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, h - 100, f"Patient Name : {patient_name}")
    c.setFont("Helvetica", 10)
    c.drawString(40, h - 115, f"Date: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

    # --- CLINICAL PARAMETERS ---
    y = h - 150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "PATIENT CLINICAL PARAMETERS")
    y -= 8
    c.line(40, y, w - 40, y)
    y -= 25

    c.setFont("Helvetica", 10)
    row = df.iloc[0]

    # Map values to readable strings
    sex_str = "Male" if row["sex"] == 1 else "Female"
    fbs_str = "< 120 mg/dl" if row["fbs"] == 0 else "> 120 mg/dl"
    exang_str = "Yes" if row["exang"] == 1 else "No"

    # Data to display (Left Column, Right Column)
    data_pairs = [
        (f"Age: {row['age']}", f"Sex: {sex_str}"),
        (f"Chest Pain: {row['cp']}", f"BP: {row['trestbps']} mm Hg"),
        (f"Cholesterol: {row['chol']} mg/dl", f"Fasting BS: {fbs_str}"),
        (f"ECG: {row['restecg']}", f"Max HR: {row['thalach']}"),
        (f"Ex. Angina: {exang_str}", f"Oldpeak: {row['oldpeak']}"),
        (f"Slope: {row['slope']}", f"Major Vessels: {row['ca']}"),
        (f"Thal: {row['thal']}", ""),
    ]

    for left, right in data_pairs:
        c.drawString(40, y, left)
        if right:
            c.drawString(300, y, right)
        y -= 18

    # --- FINAL DIAGNOSIS ---
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "FINAL DIAGNOSIS")
    y -= 8
    c.line(40, y, w - 40, y)
    y -= 25

    # Red Square Bullet + Diagnosis
    c.setFillColor(red)
    c.rect(40, y - 2, 8, 8, fill=1, stroke=0)  # Red square
    c.rect(50, y - 2, 8, 8, fill=1, stroke=0)  # Red square

    c.setFont("Helvetica-Bold", 14)
    c.drawString(65, y, disease)
    c.setFillColor(black)

    # --- MEDICAL PRECAUTIONS ---
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "MEDICAL PRECAUTIONS")
    y -= 8
    c.line(40, y, w - 40, y)
    y -= 20

    c.setFont("Helvetica", 10)
    for p in precautions_list:
        c.drawString(50, y, f"• {p}")
        y -= 15

    c.save()

    # Reset buffer position to the beginning
    buffer.seek(0)

    # Create filename string (but don't save file)
    clean_name = patient_name.replace(" ", "_")
    filename = f"Report_{clean_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return buffer, filename


# ==========================================================
# 🎨 MAIN UI
# ==========================================================

# Sidebar Navigation
st.sidebar.title("🏥 MediCare Portal")
app_mode = st.sidebar.radio("Choose Portal", ["👤 Patient Portal", "🛡️ Admin Dashboard"])

# ==========================================================
# 👤 PATIENT PORTAL
# ==========================================================
if app_mode == "👤 Patient Portal":

    if not st.session_state.user_logged_in:
        st.markdown(
            "<h1 style='text-align: center; color: #B71C1C;'>Patient Login</h1>",
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.session_state.user_auth_mode == "login":
                with st.form("user_login"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Log In", use_container_width=True):
                        res = auth_user("login", u, p)
                        if res["success"]:
                            st.session_state.user_logged_in = True
                            st.session_state.user_username = res["username"]
                            st.rerun()
                        else:
                            st.error(res.get("message"))

                # Switch to Signup
                cols = st.columns([1.8, 1.2])
                cols[0].markdown(
                    "<div style='text-align: right; padding-top: 10px;'>Do not have account ?</div>",
                    unsafe_allow_html=True,
                )
                if cols[1].button("Create Account"):
                    st.session_state.user_auth_mode = "signup"
                    st.rerun()

            else:
                st.subheader("Patient Registration")
                with st.form("user_signup"):
                    u = st.text_input("Choose Username")
                    p = st.text_input("Choose Password", type="password")
                    if st.form_submit_button("Sign Up", use_container_width=True):
                        res = auth_user("signup", u, p)
                        if res["success"]:
                            st.success("Account created! Go to Login.")
                            st.session_state.user_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res.get("message"))

                if st.button("Back to Login"):
                    st.session_state.user_auth_mode = "login"
                    st.rerun()

    else:
        # --- PATIENT DASHBOARD ---
        st.sidebar.markdown("---")
        st.sidebar.write(f"Logged in as: **{st.session_state.user_username}**")
        if st.sidebar.button("Logout"):
            st.session_state.user_logged_in = False
            st.rerun()

        # Load Model
        try:
            model = joblib.load("heart_model.pkl")
            scaler = joblib.load("scaler.pkl")
        except:
            st.error("Model files not found.")
            st.stop()

        disease_map = {
            0: "✅ No Disease",
            1: "🫀 Angina",
            2: "🩺 Coronary Artery Disease",
            3: "🚑 Myocardial Infarction",
            4: "⚠️ Heart Failure",
        }
        precautions = {
            0: ["Balanced diet", "Exercise daily", "Avoid smoking", "Regular checkups"],
            1: [
                "Avoid heavy activity",
                "Stress control",
                "Low salt diet",
                "Follow medication",
            ],
            2: ["Quit smoking", "Low fat diet", "Monitor BP", "Cardiology visits"],
            3: [
                "Post-attack medicines",
                "Cardiac rehab",
                "Avoid stress",
                "Medical supervision",
            ],
            4: [
                "Limit salt & fluids",
                "Daily weight monitoring",
                "Low exertion",
                "Heart checkups",
            ],
        }

        st.markdown(
            "<h2 style='text-align: center; color: #B71C1C;'>Heart Disease Prediction</h2>",
            unsafe_allow_html=True,
        )
        st.divider()

        patient_name = st.text_input("Patient Name")

        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 100, 45)
            sex = st.selectbox(
                "Sex", [0, 1], format_func=lambda x: "Male" if x == 1 else "Female"
            )
            cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3])
            trestbps = st.number_input("Resting BP", 80, 200, 120)
            chol = st.number_input("Cholesterol", 100, 600, 200)
            fbs = st.selectbox("Fasting BS > 120", [0, 1])
            restecg = st.selectbox("ECG Results", [0, 1, 2])
        with c2:
            thalach = st.number_input("Max Heart Rate", 60, 220, 150)
            exang = st.selectbox("Exercise Angina", [0, 1])
            oldpeak = st.number_input("Oldpeak", 0.0, 10.0, 0.0)
            slope = st.selectbox("Slope", [0, 1, 2])
            ca = st.selectbox("Major Vessels", [0, 1, 2, 3])
            thal = st.selectbox("Thalassemia", [1, 2, 3])

        if st.button("Analyze & Predict", use_container_width=True):
            if not patient_name:
                st.warning("Please enter patient name.")
            else:
                # Prepare & Predict
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

                final_pred = pred
                if pred == 0:
                    if cp in [2, 3] and oldpeak < 1:
                        final_pred = 1
                    elif chol > 240 and oldpeak >= 1:
                        final_pred = 2
                    # ... (rest of logic) ...

                res_text = disease_map[final_pred]

                st.divider()
                st.subheader(f"Diagnosis: {res_text}")

                # --- SAVE DATA TO DB (ONLY DATA) ---
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
                    st.toast("Patient data saved to database!", icon="💾")
                except:
                    st.warning("Could not save to database (Server offline?)")

                # --- PDF DOWNLOAD (FROM MEMORY) ---
                pdf_buffer, pdf_filename = create_pdf(
                    patient_name, df, res_text, precautions[final_pred]
                )

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown("#### 🛡️ Recommended Precautions:")
                    for tip in precautions[final_pred]:
                        st.markdown(f"✅ {tip}")

                with col_p2:
                    st.markdown("#### 📂 Medical Report:")
                    st.download_button(
                        "Download Report PDF",
                        pdf_buffer,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )

# ==========================================================
# 🛡️ ADMIN DASHBOARD
# ==========================================================
elif app_mode == "🛡️ Admin Dashboard":

    if not st.session_state.admin_logged_in:
        st.markdown(
            "<h1 style='text-align: center; color: #1565C0;'>Admin Portal</h1>",
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.session_state.admin_auth_mode == "login":
                with st.form("admin_login"):
                    u = st.text_input("Admin Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("Admin Login", use_container_width=True):
                        res = auth_admin("login", u, p)
                        if res["success"]:
                            st.session_state.admin_logged_in = True
                            st.session_state.admin_username = res["username"]
                            st.rerun()
                        else:
                            st.error(res.get("message"))

                if st.button("Register New Admin"):
                    st.session_state.admin_auth_mode = "signup"
                    st.rerun()

            else:
                st.warning("Admin Registration Requires a Secret Key")
                with st.form("admin_signup"):
                    u = st.text_input("New Admin Username")
                    p = st.text_input("New Password", type="password")
                    k = st.text_input(
                        "Secret Key", type="password"
                    )  # Key is 'admin123'
                    if st.form_submit_button(
                        "Register Admin", use_container_width=True
                    ):
                        res = auth_admin("signup", u, p, k)
                        if res["success"]:
                            st.success("Admin created! Login now.")
                            st.session_state.admin_auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(res.get("message"))

                if st.button("Back to Login"):
                    st.session_state.admin_auth_mode = "login"
                    st.rerun()

    else:
        # --- ADMIN DASHBOARD ---
        st.sidebar.markdown("---")
        st.sidebar.write(f"Admin: **{st.session_state.admin_username}**")
        if st.sidebar.button("Admin Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        st.title("🛡️ Hospital Patient Records")

        # Fetch Data
        try:
            res = requests.get(f"{NODE_API_URL}/admin/patients")
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    df = pd.DataFrame(data)

                    # Dashboard Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Patients", len(df))
                    m2.metric("High Risk Cases", len(df[df["prediction_result"] > 0]))
                    m3.metric("Healthy Cases", len(df[df["prediction_result"] == 0]))

                    st.divider()

                    # Filters
                    search = st.text_input("Search by Name or Disease")
                    if search:
                        # Add search by patient_name
                        df = df[
                            df["patient_name"].str.contains(
                                search, case=False, na=False
                            )
                            | df["disease_name"].str.contains(
                                search, case=False, na=False
                            )
                        ]

                    # Main Table
                    st.subheader("Patient Database")

                    # Select specific columns to display
                    display_cols = [
                        "patient_name",  # Added Name
                        "age",
                        "sex",
                        "disease_name",
                        "prediction_result",
                        "timestamp",
                    ]
                    # Handle missing columns gracefully
                    available_cols = [c for c in display_cols if c in df.columns]

                    st.dataframe(df[available_cols], use_container_width=True)

                    # Download Database
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Full Database CSV", csv, "patients_db.csv", "text/csv"
                    )

                else:
                    st.info("No patient records found in database.")
            else:
                st.error("Failed to fetch data from server.")
        except Exception as e:
            st.error(f"Connection Error: {e}")
