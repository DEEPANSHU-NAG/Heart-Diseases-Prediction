import warnings
from sklearn.exceptions import InconsistentVersionWarning

# 1. Suppress scikit-learn version warnings
# These warnings occur when the model was pickled with a different version of sklearn
# than the one currently running. If the model loads, it's usually safe to ignore.
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# 2. Load the model and scaler once when server starts
print("Loading model and scaler...")

try:
    # UPDATED: Loading the correct file 'heart_model.pkl'
    # Ensure these files exist in the same directory as ml_server.py
    model = joblib.load("heart_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ Model and Scaler loaded successfully!")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print(
        "❌ Critical Error: 'heart_model.pkl' or 'scaler.pkl' was not found in the current directory."
    )
    print(f"Current Directory: {os.getcwd()}")
    # We exit here because the server cannot function without the model
    exit(1)
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)


@app.route("/predict_api", methods=["POST"])
def predict_api():
    try:
        # Get JSON data from Node.js or Client
        data = request.get_json()

        if not data or "features" not in data:
            return jsonify({"error": "No features provided", "status": "error"}), 400

        # Expecting a list of features: [50, 1, 0, 120, ...]
        features = data["features"]

        # Convert to numpy array and shape it for the model
        features_array = np.array([features])

        # Scale the data using the loaded scaler
        scaled_features = scaler.transform(features_array)

        # Predict
        prediction = model.predict(scaled_features)[0]

        # Calculate probability/confidence
        probability = model.predict_proba(scaled_features)[0].tolist()

        # Return result
        return jsonify(
            {
                "prediction": int(prediction),
                "confidence": probability,
                "status": "success",
            }
        )

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"error": str(e), "status": "error"})


if __name__ == "__main__":
    # Run on Port 5000
    print("🚀 Starting Flask Server on port 5000...")
    app.run(port=5000, debug=True)