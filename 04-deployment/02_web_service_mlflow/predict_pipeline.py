from flask import Flask, request, jsonify
import pickle 

from mlflow.tracking import MlflowClient
import mlflow

MLFLOW_TRACKING_URI = 'http://localhost:5000'
mlflow.set_tracking_uri('sqlite:///mlflow.db')

"""
If tracking server is instacieated on remote server like S3,
it's possible to remove the dependency on the tracking server by locating directly the S3 model location.
"""

RUN_ID = '9be4c96d18c343ef9e49396b388006a7'

# log model and artifacts in one run with Pipeline
logged_model = f'runs:/{RUN_ID}/models_mlflow'
model = mlflow.pyfunc.load_model(logged_model)

def prepare_features(ride):
    features = {
        'PU_DO': f'{ride["PULocationID"]}_{ride["DOLocationID"]}',
        'trip_distance': ride['trip_distance']
    }
    return features

def predict(features):
    # pipeline = DV + model
    preds = model.predict(features)
    return preds[0]

app = Flask('duration-prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    prediction = predict(features)

    result = {
        'duration': float(prediction),
        'model_version': RUN_ID
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
