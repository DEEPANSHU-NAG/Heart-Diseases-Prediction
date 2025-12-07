from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# 1. Load the model and scaler once when server starts
print("Loading model and scaler...")
model = joblib.load("heart_disease_best_model.pkl")
scaler = joblib.load("scaler.pkl")
print("Model loaded!")


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
        return jsonify({"error": str(e), "status": "error"})


if __name__ == "__main__":
    # Run on Port 5000
    app.run(port=5000, debug=True)
