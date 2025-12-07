import dotenv from "dotenv";
dotenv.config();
import express from "express";
import mongoose from "mongoose";
import axios from "axios"; // Used to talk to Python
import cors from "cors";
import argon2 from "argon2"; // <--- Added Argon2

const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// 1. Connect to MongoDB
mongoose
  .connect("mongodb://localhost:27017/heart_disease_db")
  .then(() => console.log("MongoDB Connected"))
  .catch((err) => console.log(err));

// --- SCHEMAS ---

// 2a. User Schema (New)
const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true }, // Stores the hash
});
const User = mongoose.model("User", UserSchema);

// 2b. Patient Schema (Existing)
const PatientSchema = new mongoose.Schema({
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
  prediction_result: Number, // 0 or 1
  confidence_score: Array,
  timestamp: { type: Date, default: Date.now },
});

const Patient = mongoose.model("Patient", PatientSchema);

// --- AUTH ROUTES ---

// Signup Route
app.post("/api/signup", async (req, res) => {
  try {
    const { username, password } = req.body;

    // Check if user exists
    const existingUser = await User.findOne({ username });
    if (existingUser)
      return res.json({ success: false, message: "User already exists" });

    // Hash password with Argon2
    const hashedPassword = await argon2.hash(password);

    const newUser = new User({ username, password: hashedPassword });
    await newUser.save();

    res.json({ success: true, message: "User created successfully" });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// Login Route
app.post("/api/login", async (req, res) => {
  try {
    const { username, password } = req.body;

    // Find user
    const user = await User.findOne({ username });
    if (!user) return res.json({ success: false, message: "User not found" });

    // Verify password with Argon2
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

// --- PREDICTION ROUTE ---

// 3. The Route
app.post("/api/check-heart", async (req, res) => {
  try {
    const inputData = req.body;

    // Prepare the array for Python (Order matters! Must match training)
    const featureArray = [
      inputData.age,
      inputData.sex,
      inputData.cp,
      inputData.trestbps,
      inputData.chol,
      inputData.fbs,
      inputData.restecg,
      inputData.thalach,
      inputData.exang,
      inputData.oldpeak,
      inputData.slope,
      inputData.ca,
      inputData.thal,
    ];

    // A. Call the Python API
    // We use localhost:5000 where Flask is running
    const pythonResponse = await axios.post(
      "http://localhost:5000/predict_api",
      {
        features: featureArray,
      }
    );

    const prediction = pythonResponse.data.prediction;
    const confidence = pythonResponse.data.confidence;

    // B. Save to MongoDB
    const newPatient = new Patient({
      ...inputData,
      prediction_result: prediction,
      confidence_score: confidence,
    });

    await newPatient.save();

    // C. Respond to Frontend
    res.json({
      message: "Success",
      data: newPatient,
      risk: prediction === 1 ? "High Risk" : "Low Risk",
    });
  } catch (error) {
    console.error(error);
    res.status(500).send("Error processing request");
  }
});

// Run Node Server on Port 3000
app.listen(3000, () => {
  console.log("Node Server running on port 3000");
});
