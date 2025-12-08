import dotenv from "dotenv";
dotenv.config();
import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import argon2 from "argon2";

const app = express();

// Middleware
app.use(express.json({ limit: "50mb" }));
app.use(cors());

// 1. Connect to MongoDB
mongoose
  .connect("mongodb://localhost:27017/heart_disease_db")
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.log(err));

// ==========================================
// SCHEMAS
// ==========================================

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});
const User = mongoose.model("User", UserSchema);

const AdminSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});
const Admin = mongoose.model("Admin", AdminSchema);

// --- PATIENT SCHEMA (Strictly Data Only) ---
const PatientSchema = new mongoose.Schema({
  username: String, // Doctor/User who saved it
  patient_name: String, // ✅ Added Patient Name
  age: Number,
  sex: Number,
  cp: Number,
  trestbps: Number,
  chol: Number,
  fbs: Number,
  restecg: Number,
  thalach: Number,
  exang: Number,
  oldpeak: Number,
  slope: Number,
  ca: Number,
  thal: Number,
  prediction_result: Number,
  disease_name: String,
  timestamp: { type: Date, default: Date.now },
  // ❌ pdf_report is NOT here, so it cannot be saved
});

const Patient = mongoose.model("Patient", PatientSchema);

// ==========================================
// AUTH ROUTES
// ==========================================

app.post("/api/signup", async (req, res) => {
  try {
    const { username, password } = req.body;
    const existingUser = await User.findOne({ username });
    if (existingUser)
      return res.json({ success: false, message: "User already exists" });

    const hashedPassword = await argon2.hash(password);
    const newUser = new User({ username, password: hashedPassword });
    await newUser.save();

    res.json({ success: true, message: "User created successfully" });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

app.post("/api/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user) return res.json({ success: false, message: "User not found" });

    const validPassword = await argon2.verify(user.password, password);
    if (validPassword) {
      res.json({
        success: true,
        message: "Login successful",
        username: user.username,
      });
    } else {
      res.json({ success: false, message: "Invalid password" });
    }
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Admin Auth
app.post("/api/admin/signup", async (req, res) => {
  try {
    const { username, password, secretKey } = req.body;
    if (secretKey !== "admin123")
      return res.json({ success: false, message: "Invalid Secret Key" });

    const existingAdmin = await Admin.findOne({ username });
    if (existingAdmin)
      return res.json({ success: false, message: "Admin exists" });

    const hashedPassword = await argon2.hash(password);
    const newAdmin = new Admin({ username, password: hashedPassword });
    await newAdmin.save();

    res.json({ success: true, message: "Admin created" });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

app.post("/api/admin/login", async (req, res) => {
  try {
    const { username, password } = req.body;
    const admin = await Admin.findOne({ username });
    if (!admin) return res.json({ success: false, message: "Admin not found" });

    const validPassword = await argon2.verify(admin.password, password);
    if (validPassword) {
      res.json({
        success: true,
        message: "Login successful",
        username: admin.username,
      });
    } else {
      res.json({ success: false, message: "Invalid password" });
    }
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ==========================================
// DATA ROUTES
// ==========================================

// 1. Save Report (Data ONLY, No PDF)
app.post("/api/save-report", async (req, res) => {
  try {
    const data = req.body;

    const newPatient = new Patient({
      username: data.username,
      patient_name: data.patient_name, // ✅ Save Patient Name
      age: data.age,
      sex: data.sex,
      cp: data.cp,
      trestbps: data.trestbps,
      chol: data.chol,
      fbs: data.fbs,
      restecg: data.restecg,
      thalach: data.thalach,
      exang: data.exang,
      oldpeak: data.oldpeak,
      slope: data.slope,
      ca: data.ca,
      thal: data.thal,
      prediction_result: data.prediction,
      disease_name: data.disease,
      // ❌ No PDF field here
    });

    await newPatient.save();

    res.json({
      success: true,
      message: "Patient clinical data saved successfully!",
    });
  } catch (error) {
    console.error("Save Error:", error);
    res.status(500).json({ success: false, message: "Failed to save data." });
  }
});

// 2. Admin: Get All Patients
app.get("/api/admin/patients", async (req, res) => {
  try {
    const patients = await Patient.find().sort({ timestamp: -1 });
    res.json({ success: true, data: patients });
  } catch (error) {
    res.status(500).json({ success: false, message: "Error fetching data" });
  }
});

app.listen(3000, () => {
  console.log("Node Server running on port 3000");
});
