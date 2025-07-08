from deepdiff import DeepDiff

import requests


ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 40
}

url = 'http://127.0.0.1:9696/predict'  # or 'http://localhost:9696/predict'

actual_response = requests.post(url, json=ride)
actual_response = actual_response.json()
actual_response['duration'] = round(actual_response['duration'], 1)
print(actual_response)

except_response = {'duration': 22.8}

diff = DeepDiff(actual_response, except_response)

assert not diff, f"Response mismatch: {diff}"
