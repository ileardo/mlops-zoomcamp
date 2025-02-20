from flask import Flask, request, jsonify
import pickle 

from mlflow.tracking import MlflowClient
import mlflow

mlflow.set_tracking_uri('sqlite:///mlflow.db')

RUN_ID = '1b91ef40481d4e2bacb49373ea84d4d8'
MLFLOW_TRACKING_URI = 'http://localhost:5000'

logged_model = f'runs:/{RUN_ID}/models_mlflow'

# load model from model registry
model = mlflow.pyfunc.load_model(logged_model)

# load artifacts through MLflow client
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
path = client.download_artifacts(run_id=RUN_ID, path='preprocessor/preprocessor.b')
print(f'... Downloading dict vectorizer to {path}')
with open(path, 'rb') as f_in:
    dv = pickle.load(f_in)

def prepare_features(ride):
    features = {
        'PU_DO': f'{ride["PULocationID"]}_{ride["DOLocationID"]}',
        'trip_distance': ride['trip_distance']
    }
    return features

def predict(features):
    X = dv.transform(features)
    preds = model.predict(X)
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
