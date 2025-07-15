import pickle


class ModelService:

    def __init__(self, dv, model):
        self.dv = dv
        self.model = model

    @staticmethod
    def prepare_features(ride):
        features = {
            "PU_DO": f'{ride["PULocationID"]}_{ride["DOLocationID"]}',
            "trip_distance": ride["trip_distance"],
        }
        return features

    def predict(self, features):
        X = self.dv.transform(features)
        preds = self.model.predict(X)
        return preds[0]


def initialize_model_service(model_id):
    with open(f"{model_id}.bin", "rb") as f_in:
        (dv, model) = pickle.load(f_in)
    return ModelService(dv, model)
