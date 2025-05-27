import os
import pickle
import click
import mlflow

from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

HPO_EXPERIMENT_NAME = "random-forest-hyperopt"
EXPERIMENT_NAME = "random-forest-best-models"
RF_PARAMS = ['max_depth', 'n_estimators', 'min_samples_split', 'min_samples_leaf', 'random_state']

mlflow.set_tracking_uri("http://127.0.0.1:5000")


def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def train_and_log_model(data_path, params):
    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))
    X_test, y_test = load_pickle(os.path.join(data_path, "test.pkl"))

    # Set the experiment inside the function to ensure correct tracking
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    with mlflow.start_run():
        # Log the parameters
        new_params = {}
        for param in RF_PARAMS:
            new_params[param] = int(params[param])
        
        # Log parameters to MLflow
        mlflow.log_params(new_params)

        rf = RandomForestRegressor(**new_params)
        rf.fit(X_train, y_train)

        # Evaluate model on the validation and test sets
        val_rmse = root_mean_squared_error(y_val, rf.predict(X_val))
        mlflow.log_metric("val_rmse", val_rmse)
        test_rmse = root_mean_squared_error(y_test, rf.predict(X_test))
        mlflow.log_metric("test_rmse", test_rmse)
        
        # Log the model explicitly
        mlflow.sklearn.log_model(rf, "model")
        
        print(f"Logged model with test_rmse: {test_rmse}")
        
        return test_rmse


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
@click.option(
    "--top_n",
    default=5,
    type=int,
    help="Number of top models that need to be evaluated to decide which one to promote"
)
def run_register_model(data_path: str, top_n: int):

    client = MlflowClient()

    # Retrieve the top_n model runs and log the models
    print(f"Searching for top {top_n} models from {HPO_EXPERIMENT_NAME}...")
    experiment = client.get_experiment_by_name(HPO_EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n,
        order_by=["metrics.rmse ASC"]
    )
    
    print(f"Found {len(runs)} runs from hyperparameter optimization")
    
    # Train and log models for each of the top runs
    test_rmses = []
    for i, run in enumerate(runs):
        print(f"Training model {i+1}/{len(runs)}...")
        test_rmse = train_and_log_model(data_path=data_path, params=run.data.params)
        test_rmses.append(test_rmse)

    print(f"All {len(runs)} models trained and logged to {EXPERIMENT_NAME}")

    # Select the model with the lowest test RMSE
    print("Searching for the best model based on test_rmse...")
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    best_runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n,  # Get all recent runs
        order_by=["metrics.test_rmse ASC"]
    )
    
    if not best_runs:
        print("No runs found in the best models experiment!")
        return
    
    best_run = best_runs[0]
    print(f"Found {len(best_runs)} runs in {EXPERIMENT_NAME}")

    # Get the test RMSE of the best model
    test_rmse = best_run.data.metrics["test_rmse"]
    print(f"Test RMSE of the best model: {test_rmse}")

    # Register the best model
    run_id = best_run.info.run_id
    model_uri = f"runs:/{run_id}/model"
    
    print(f"Registering model with URI: {model_uri}")
    mlflow.register_model(
        model_uri=model_uri,
        name='nyc-taxi-predictor'
    )

    print(f"Model registered successfully!")
    print(f"Run ID: {run_id}")
    print(f"Test RMSE: {test_rmse}")
    
    return test_rmse


if __name__ == '__main__':
    run_register_model()