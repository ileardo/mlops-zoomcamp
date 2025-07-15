"""
This file contains the Flask application for predicting taxi ride durations.
It initializes the model service and defines an endpoint for predictions.
"""

from model import initialize_model_service

from flask import (
    Flask,
    jsonify,
    request
)


model_service = initialize_model_service('taxi_ridge_reg')

app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()
    features = model_service.prepare_features(ride)
    prediction = model_service.predict(features)

    result = {'duration': prediction}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
