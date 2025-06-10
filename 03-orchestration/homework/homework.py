from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression
import sklearn

from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import pathlib
import pickle
import scipy

import mlflow

from prefect import flow, task
from prefect_aws import S3Bucket
from prefect.artifacts import create_markdown_artifact
import prefect

mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_experiment('nyc-taxi-experiment')

models_folder = Path('models')
models_folder.mkdir(exist_ok=True)

@task(name="read_dataframe", retries=3, retry_delay_seconds=2, log_prints=True)
def read_dataframe(filename):
    df = pd.read_parquet(filename)

    print(f"\nRead {len(df)} rows from {filename}")

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    print(f"After filtering, {len(df)} rows remain")

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    
    return df


@task(name="create_X")
def create_X(df, dv=None):
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv


@task(name="train_model", log_prints=True) 
def train_model(X_train, y_train, dv):
    with mlflow.start_run() as run:
        # fit
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        # predict
        y_train_hat = lr.predict(X_train)
        # calculate RMSE
        rmse = root_mean_squared_error(y_train, y_train_hat)
        # log the model and metrics
        mlflow.sklearn.log_model(lr, artifact_path="models_sklearn")
        mlflow.log_metric("rmse", rmse)
        mlflow.log_param("model_type", "linear_regression")
        mlflow.log_param("rmse", rmse)
        mlflow.log_param("intercept", lr.intercept_)
        mlflow.log_param("date", date.today().isoformat())
        print(f'Intercept: {lr.intercept_}, RMSE: {rmse}')

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        return lr.intercept_, run.info.run_id

@task(name="get_model_size_bytes", log_prints=True)
def get_model_size_bytes(run_id):
    client = mlflow.tracking.MlflowClient()    
    artifacts = client.list_artifacts(run_id, path="models_sklearn")
    total_size = 0
    for artifact in artifacts:
        if artifact.is_dir:
            sub_artifacts = client.list_artifacts(run_id, path=artifact.path)
            for sub_artifact in sub_artifacts:
                if hasattr(sub_artifact, 'file_size') and sub_artifact.file_size:
                    total_size += sub_artifact.file_size
        else:
            if hasattr(artifact, 'file_size') and artifact.file_size:
                total_size += artifact.file_size
    print(f"Total model size for run {run_id}: {total_size} bytes")
    return total_size

@flow(name="train-taxi-duration-homework", log_prints=True) 
def run():
    print(f'=' * 100)
    print('Starting the training flow...')
    print(f'Prefect version: {prefect.__version__}\n')

    # train data
    df_train = read_dataframe('./data/yellow_tripdata_2023-03.parquet')
    X_train, dv = create_X(df_train)
    target = 'duration'
    y_train = df_train[target].values
    intercept, run_id = train_model(X_train, y_train, dv)
    print(f"MLflow run_id: {run_id}")

    # get model size
    model_size_bytes = get_model_size_bytes(run_id)
    print(f"Model size: {model_size_bytes} bytes")
    # create artifact with intercept and model size
    markdown_report = f"""# Model Training Report

## Summary

Duration Prediction Model - Linear Regression

## Model Performance

| Metric    | Value |
|:----------|-------:|
| Date | {date.today()} |
| Intercept | {intercept:.4f} |

## Model Details

| Property    | Value |
|:----------|-------:|
| Model Type | Linear Regression |
| Model Size | {model_size_bytes:,} bytes |
| Run ID | {run_id} |
"""

    create_markdown_artifact(
        key="model-report", 
        markdown=markdown_report
    )

    print(f'=' * 100)
    return run_id


if __name__ == "__main__":
    run_id = run()
    with open("run_id.txt", "w") as f:
        f.write(run_id)
