import React, { useState } from "react";
import { Stethoscope, AlertCircle } from "lucide-react";

// Defined locally to prevent import errors
const API_URL = "http://localhost:3000/api";

const AuthPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = isLogin ? "/login" : "/signup";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.success) {
        if (isLogin) {
          onLogin(formData.username);
        } else {
          alert("Account created! Please log in.");
          setIsLogin(true);
        }
      } else {
        setError(data.message || "Authentication failed");
      }
    } catch (err) {
      setError("Cannot connect to server. Is Node.js running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl overflow-hidden w-full max-w-4xl flex flex-col md:flex-row min-h-[600px]">
        {/* Left Panel - Visuals */}
        <div className="w-full md:w-1/2 bg-[#C4CDFB] p-12 flex flex-col justify-center items-center text-center text-white relative overflow-hidden">
          <div className="z-10">
            <h1 className="text-5xl font-bold mb-2">MediCare</h1>
            <h3 className="text-xl text-[#5b6bbf] font-medium mb-8">
              Heart Health AI
            </h3>
            <Stethoscope
              size={80}
              className="mx-auto mb-6 text-white opacity-90"
            />
            <p className="text-[#5b6bbf] text-lg font-medium max-w-xs mx-auto">
              We are fully focused on helping you predict and prevent heart
              disease early.
            </p>
          </div>
          {/* Decorative Circles */}
          <div className="absolute top-0 left-0 w-64 h-64 bg-white opacity-10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-48 h-48 bg-[#5b6bbf] opacity-20 rounded-full translate-x-1/3 translate-y-1/3"></div>
        </div>

        {/* Right Panel - Form */}
        <div className="w-full md:w-1/2 p-12 flex flex-col justify-center bg-white">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="text-gray-500 mb-8">
            {isLogin
              ? "Please enter your details to sign in."
              : "Start your journey to better health."}
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                required
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-[#5b6bbf] focus:ring-2 focus:ring-[#C4CDFB] outline-none transition-all"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                required
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-[#5b6bbf] focus:ring-2 focus:ring-[#C4CDFB] outline-none transition-all"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-center">
                <AlertCircle size={16} className="mr-2" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#5b6bbf] hover:bg-[#4a5aa8] text-white font-bold py-3 rounded-xl transition-colors duration-200 shadow-lg shadow-indigo-200"
            >
              {loading ? "Processing..." : isLogin ? "Sign In" : "Sign Up"}
            </button>
          </form>

          <div className="mt-8 text-center text-gray-600">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-[#5b6bbf] font-bold hover:underline"
            >
              {isLogin ? "Sign Up" : "Log In"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;