import React, { useState } from "react";
import { Heart, Activity, User, LogOut, Info, CheckCircle } from "lucide-react";

// ==========================================
// 1. INTERNAL CONSTANTS
// Defined here to prevent import errors
// ==========================================
const API_URL = "http://localhost:3000/api";

const DISEASE_MAP = {
  0: "✅ No Disease",
  1: "🫀 Angina",
  2: "🩺 Coronary Artery Disease",
  3: "🚑 Myocardial Infarction",
  4: "⚠️ Heart Failure",
};

const PRECAUTIONS = {
  0: [
    "Maintain a balanced, heart-healthy diet",
    "Exercise at least 30 minutes daily",
    "Avoid smoking & alcohol",
    "Get regular health checkups",
  ],
  1: [
    "Avoid heavy physical activity",
    "Control stress",
    "Reduce salt intake",
    "Follow doctor-prescribed medication",
  ],
  2: [
    "Quit smoking completely",
    "Follow low fat / low cholesterol diet",
    "Monitor BP & cholesterol regularly",
    "Consult cardiologist frequently",
  ],
  3: [
    "Strictly follow medicines",
    "Attend cardiac rehabilitation",
    "Avoid stressful activities",
    "Regular cardiology visits",
  ],
  4: [
    "Limit salt and fluid intake",
    "Monitor weight daily",
    "Avoid strenuous activity",
    "Frequent heart checkups",
  ],
};

// ==========================================
// 2. INTERNAL HELPER COMPONENTS
// Defined here to prevent import errors
// ==========================================

const InputGroup = ({ label, name, type = "text", value, onChange, step }) => (
  <div>
    <label className="block text-sm font-medium text-gray-500 mb-1">
      {label}
    </label>
    <input
      type={type}
      name={name}
      step={step}
      value={value}
      onChange={onChange}
      className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-[#5b6bbf] focus:ring-2 focus:ring-indigo-50 outline-none transition-all font-medium text-gray-700"
    />
  </div>
);

const SelectGroup = ({ label, name, value, onChange, options }) => (
  <div>
    <label className="block text-sm font-medium text-gray-500 mb-1">
      {label}
    </label>
    <div className="relative">
      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-[#5b6bbf] focus:ring-2 focus:ring-indigo-50 outline-none transition-all font-medium text-gray-700 appearance-none bg-white"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </div>
    </div>
  </div>
);

// ==========================================
// 3. MAIN DASHBOARD COMPONENT
// ==========================================

const Dashboard = ({ user, onLogout }) => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form State initialized with defaults
  const [formData, setFormData] = useState({
    age: 45,
    sex: 1, // 1 = Male
    cp: 0,
    trestbps: 120,
    chol: 200,
    fbs: 0,
    restecg: 0,
    thalach: 150,
    exang: 0,
    oldpeak: 1.0,
    slope: 1,
    ca: 0,
    thal: 2,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: parseFloat(value),
    }));
  };

  const handlePredict = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/check-heart`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.message === "Success") {
        let finalResult = 0;
        const risk = data.risk;

        // Convert server risk to numeric base
        let mlResult = risk === "High Risk" || risk === 1 ? 1 : 0;

        // --- CLIENT SIDE RULE-BASED OVERRIDE LOGIC ---
        finalResult = mlResult;

        if (mlResult === 0) {
          if ([2, 3].includes(formData.cp) && formData.oldpeak < 1) {
            finalResult = 1; // Angina
          } else if (formData.chol > 240 && formData.oldpeak >= 1) {
            finalResult = 2; // Coronary Artery Disease
          } else if (formData.cp === 3 && formData.oldpeak > 2) {
            finalResult = 3; // Myocardial Infarction
          } else if (
            formData.exang === 1 &&
            formData.oldpeak > 2 &&
            formData.thalach < 120
          ) {
            finalResult = 4; // Heart Failure
          }
        }

        setResult(finalResult);
      }
    } catch (err) {
      alert("Error connecting to prediction engine. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8f9fc] pb-12">
      {/* Navbar */}
      <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="bg-red-50 p-2 rounded-full">
            <Heart className="text-red-500" size={24} fill="currentColor" />
          </div>
          <span className="font-bold text-xl text-gray-800">MediCare AI</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-gray-600 bg-gray-50 px-3 py-1.5 rounded-full">
            <User size={18} />
            <span className="font-medium">{user}</span>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 text-gray-500 hover:text-red-500 transition-colors"
          >
            <LogOut size={20} />
            <span className="hidden md:inline">Logout</span>
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto mt-8 px-4">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Heart Disease Prediction System
          </h1>
          <p className="text-gray-500">
            Enter patient vitals below for an AI-powered diagnosis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* --- INPUT FORM --- */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center gap-2 mb-6 border-b pb-4">
                <User className="text-[#5b6bbf]" />
                <h2 className="text-lg font-bold text-gray-800">
                  Patient Details
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputGroup
                  label="Age"
                  name="age"
                  type="number"
                  value={formData.age}
                  onChange={handleChange}
                />
                <SelectGroup
                  label="Sex"
                  name="sex"
                  value={formData.sex}
                  onChange={handleChange}
                  options={[
                    { value: 1, label: "Male" },
                    { value: 0, label: "Female" },
                  ]}
                />
                <SelectGroup
                  label="Chest Pain Type"
                  name="cp"
                  value={formData.cp}
                  onChange={handleChange}
                  options={[
                    { value: 0, label: "Typical Angina" },
                    { value: 1, label: "Atypical Angina" },
                    { value: 2, label: "Non-anginal Pain" },
                    { value: 3, label: "Asymptomatic" },
                  ]}
                />
                <InputGroup
                  label="Resting BP (mm Hg)"
                  name="trestbps"
                  type="number"
                  value={formData.trestbps}
                  onChange={handleChange}
                />
                <InputGroup
                  label="Cholesterol (mg/dl)"
                  name="chol"
                  type="number"
                  value={formData.chol}
                  onChange={handleChange}
                />
                <SelectGroup
                  label="Fasting BS > 120 mg/dl"
                  name="fbs"
                  value={formData.fbs}
                  onChange={handleChange}
                  options={[
                    { value: 1, label: "True" },
                    { value: 0, label: "False" },
                  ]}
                />
                <SelectGroup
                  label="Resting ECG"
                  name="restecg"
                  value={formData.restecg}
                  onChange={handleChange}
                  options={[
                    { value: 0, label: "Normal" },
                    { value: 1, label: "ST-T Wave Abnormality" },
                    { value: 2, label: "Left Ventricular Hypertrophy" },
                  ]}
                />
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center gap-2 mb-6 border-b pb-4">
                <Activity className="text-[#5b6bbf]" />
                <h2 className="text-lg font-bold text-gray-800">
                  Cardiac Metrics
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputGroup
                  label="Max Heart Rate"
                  name="thalach"
                  type="number"
                  value={formData.thalach}
                  onChange={handleChange}
                />
                <SelectGroup
                  label="Exercise Induced Angina"
                  name="exang"
                  value={formData.exang}
                  onChange={handleChange}
                  options={[
                    { value: 1, label: "Yes" },
                    { value: 0, label: "No" },
                  ]}
                />
                <InputGroup
                  label="Oldpeak (ST Depression)"
                  name="oldpeak"
                  type="number"
                  step="0.1"
                  value={formData.oldpeak}
                  onChange={handleChange}
                />
                <SelectGroup
                  label="Slope"
                  name="slope"
                  value={formData.slope}
                  onChange={handleChange}
                  options={[
                    { value: 0, label: "Upsloping" },
                    { value: 1, label: "Flat" },
                    { value: 2, label: "Downsloping" },
                  ]}
                />
                <SelectGroup
                  label="Major Vessels (0-3)"
                  name="ca"
                  value={formData.ca}
                  onChange={handleChange}
                  options={[
                    { value: 0, label: "0" },
                    { value: 1, label: "1" },
                    { value: 2, label: "2" },
                    { value: 3, label: "3" },
                  ]}
                />
                <SelectGroup
                  label="Thalassemia"
                  name="thal"
                  value={formData.thal}
                  onChange={handleChange}
                  options={[
                    { value: 1, label: "Normal" },
                    { value: 2, label: "Fixed Defect" },
                    { value: 3, label: "Reversible Defect" },
                  ]}
                />
              </div>
            </div>

            <button
              onClick={handlePredict}
              disabled={loading}
              className="w-full bg-[#5b6bbf] hover:bg-[#4a5aa8] text-white text-lg font-bold py-4 rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Activity className="animate-spin" /> : <Activity />}
              {loading ? "Analyzing Vitals..." : "Predict Disease Type"}
            </button>
          </div>

          {/* --- RESULTS PANEL --- */}
          <div className="lg:col-span-1">
            <div
              className={`sticky top-24 transition-all duration-500 ${
                result !== null
                  ? "opacity-100 translate-y-0"
                  : "opacity-50 translate-y-4"
              }`}
            >
              {result === null ? (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center h-full flex flex-col justify-center items-center text-gray-400">
                  <Activity size={64} className="mb-4 opacity-20" />
                  <p>Results will appear here after analysis.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Diagnosis Card */}
                  <div
                    className={`rounded-2xl shadow-lg p-6 text-center border-t-8 ${
                      result === 0
                        ? "bg-green-50 border-green-500"
                        : "bg-red-50 border-red-500"
                    }`}
                  >
                    <h3 className="text-gray-500 font-medium uppercase tracking-wider text-sm mb-2">
                      Diagnosis Result
                    </h3>
                    <h2
                      className={`text-2xl font-bold mb-2 ${
                        result === 0 ? "text-green-700" : "text-red-700"
                      }`}
                    >
                      {DISEASE_MAP[result]}
                    </h2>
                  </div>

                  {/* Precautions Card */}
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <Info className="text-[#5b6bbf]" size={20} />
                      <h3 className="font-bold text-gray-800">
                        Recommended Precautions
                      </h3>
                    </div>
                    <ul className="space-y-3">
                      {PRECAUTIONS[result].map((tip, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-3 text-gray-600 text-sm"
                        >
                          <CheckCircle
                            size={16}
                            className="text-green-500 mt-0.5 shrink-0"
                          />
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;