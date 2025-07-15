# Test API
import requests


ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 40,
}

URL = "http://127.0.0.1:9696/predict"  # or 'http://localhost:9696/predict'
response = requests.post(URL, json=ride, timeout=10)
print(response.json())
