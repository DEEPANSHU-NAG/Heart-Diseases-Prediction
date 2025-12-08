from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# 1. Load the model and scaler once when server starts
print("Loading model and scaler...")

try:
    # UPDATED: Loading the correct file 'heart_model.pkl'
    model = joblib.load("heart_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("Model and Scaler loaded successfully!")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print(
        "❌ Critical Error: 'heart_model.pkl' or 'scaler.pkl' was not found in the current directory."
    )
    print(f"Current Directory: {os.getcwd()}")
    # We exit here because the server cannot function without the model
    exit(1)


@app.route("/predict_api", methods=["POST"])
def predict_api():
    try:
        # Get JSON data from Node.js
        data = request.get_json()

        # Expecting a list of features: [50, 1, 0, 120, ...]
        features = data["features"]

        # Convert to numpy array and shape it for the model
        features_array = np.array([features])

        # Scale the data
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
    print("Starting Flask Server on port 5000...")
    app.run(port=5000, debug=True)
