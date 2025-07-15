from model import ModelService


def test_prepare_features():
    ride = {
        'PULocationID': 130,
        'DOLocationID': 205,
        'trip_distance': 3.66,
    }
    expected_features = {
        'PU_DO': '130_205',
        'trip_distance': 3.66,
    }

    features = ModelService.prepare_features(ride)
    assert features == expected_features


class MockDV:
    def transform(self, features):
        return [[features['PU_DO'], features['trip_distance']]]


class MockModel:
    def predict(self, X):
        # pylint: disable=unused-argument
        return [42.0]  # mock prediction value


def test_predict():
    dv = MockDV()
    model = MockModel()
    service = ModelService(dv, model)

    features = {
        'PU_DO': '130_205',
        'trip_distance': 3.66,
    }

    prediction = service.predict(features)
    expected_prediction = 42.0

    assert (
        prediction == expected_prediction
    ), f"Expected {expected_prediction}, got {prediction}"
