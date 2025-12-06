# ================================
# 💓 HEART DISEASE TYPE PREDICTOR
# FINAL YEAR PROJECT – STREAMLIT APP
# ================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Heart Disease Diagnosis",
    page_icon="💓",
    layout="centered"
)

# -----------------------------
# Load Trained Model & Scaler
# -----------------------------
model = joblib.load("heart_model.pkl")
scaler = joblib.load("scaler.pkl")

# -----------------------------
# Disease Label Mapping
# -----------------------------
disease_map = {
    0: "✅ No Disease",
    1: "🫀 Angina",
    2: "🩺 Coronary Artery Disease",
    3: "🚑 Myocardial Infarction",
    4: "⚠️ Heart Failure"
}

# -----------------------------
# Precaution Mapping
# -----------------------------
precautions = {
    0: [
        "Maintain a balanced, heart-healthy diet",
        "Exercise at least 30 minutes daily",
        "Avoid smoking & alcohol",
        "Get regular health checkups"
    ],
    1: [
        "Avoid heavy physical activity",
        "Control stress",
        "Reduce salt intake",
        "Follow doctor-prescribed medication"
    ],
    2: [
        "Quit smoking completely",
        "Follow low fat / low cholesterol diet",
        "Monitor BP & cholesterol regularly",
        "Consult cardiologist frequently"
    ],
    3: [
        "Strictly follow medicines",
        "Attend cardiac rehabilitation",
        "Avoid stressful activities",
        "Regular cardiology visits"
    ],
    4: [
        "Limit salt and fluid intake",
        "Monitor weight daily",
        "Avoid strenuous activity",
        "Frequent heart checkups"
    ]
}

# -----------------------------
# CSS Styling
# -----------------------------
st.markdown("""
<style>
    .main {
        background: linear-gradient(120deg,#fdfbfb,#ebedee);
    }
    h1 {
        color:#B71C1C;
        text-align:center;
    }
    .card {
        background:white;
        border-radius:18px;
        padding:22px;
        box-shadow:0px 0px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Page Header
# -----------------------------
st.markdown("<h1>💓 Heart Disease Prediction System</h1>", unsafe_allow_html=True)
st.markdown("### AI-based Disease Type Diagnosis App")
st.divider()

# -----------------------------
# Patient Input Form
# -----------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ---- Column 1
with col1:
    age = st.number_input("Age", 1, 120, 45)
    sex = st.selectbox("Sex (0 = Female | 1 = Male)", [0, 1])
    cp = st.selectbox("Chest Pain Type (0–3)", [0, 1, 2, 3])
    trestbps = st.number_input("Resting Blood Pressure", 80, 220, 120)
    chol = st.number_input("Cholesterol", 100, 600, 200)
    fbs = st.selectbox("Fasting Blood Sugar > 120", [0, 1])
    restecg = st.selectbox("ECG Result (0–2)", [0, 1, 2])

# ---- Column 2
with col2:
    thalach = st.number_input("Maximum Heart Rate", 60, 220, 150)
    exang = st.selectbox("Exercise Induced Angina", [0, 1])
    oldpeak = st.number_input("ST Depression (Oldpeak)", 0.0, 6.5)
    slope = st.selectbox("Slope (0–2)", [0, 1, 2])
    ca = st.selectbox("Major Vessels (0–3)", [0, 1, 2, 3])
    thal = st.selectbox("Thalassemia (1 = Normal | 2 = Fixed | 3 = Reversible)", [1, 2, 3])

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# PREDICTION
# -----------------------------
if st.button("🔍 Predict Disease Type", use_container_width=True):

    # -----------------------------
    # Create Input DataFrame
    # -----------------------------
    input_df = pd.DataFrame({
        "age": [age],
        "sex": [sex],
        "cp": [cp],
        "trestbps": [trestbps],
        "chol": [chol],
        "fbs": [fbs],
        "restecg": [restecg],
        "thalach": [thalach],
        "exang": [exang],
        "oldpeak": [oldpeak],
        "slope": [slope],
        "ca": [ca],
        "thal": [thal]
    })

    # Scale data
    input_scaled = scaler.transform(input_df)

    # -----------------------------
    # ML PREDICTION
    # -----------------------------
    ml_result = model.predict(input_scaled)[0]
    result = ml_result

    # -----------------------------
    # ✅ RULE-BASED OVERRIDE LOGIC
    # (Fixes rare disease underprediction)
    # -----------------------------

    # Angina
    if ml_result == 0 and cp in [2,3] and oldpeak < 1:
        result = 1

    # Coronary Artery Disease
    elif ml_result == 0 and chol > 240 and oldpeak >= 1:
        result = 2

    # Myocardial Infarction
    elif ml_result == 0 and cp == 3 and oldpeak > 2:
        result = 3

    # Heart Failure
    elif ml_result == 0 and exang == 1 and oldpeak > 2 and thalach < 120:
        result = 4

    # -----------------------------
    # DISPLAY OUTPUT
    # -----------------------------
    st.divider()

    st.success(f"## 🧠 Diagnosis Result\n\n### {disease_map[result]}")

    st.markdown("## ✅ Recommended Precautions")

    for tip in precautions[result]:
        st.markdown(f"✔️ {tip}")
