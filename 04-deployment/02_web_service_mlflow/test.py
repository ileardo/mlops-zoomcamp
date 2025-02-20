# Test functions

"""
import predict

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 40
}
print(f'ride: {ride}')

features = predict.prepare_features(ride)
print(f'features: {features}')

prediction = predict.predict(features)
print(f'prediction: {prediction}')
"""

# Test API
import requests

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 40
}

url = 'http://127.0.0.1:9696/predict'  # or 'http://localhost:9696/predict'
response = requests.post(url, json=ride)
print(response.json())
