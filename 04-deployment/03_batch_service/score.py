import os
import sys
import uuid
import pickle

import pandas as pd

from mlflow.tracking import MlflowClient
import mlflow

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline


def generate_uuids(n):
    print('generating uuids ...')

    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


def read_dataframe(filename: str):
    print('reading dataframe ...')
    
    df = pd.read_parquet(filename)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    
    df['ride_id'] = generate_uuids(len(df))

    return df


def prepare_dictionaries(df: pd.DataFrame):
    print('preparing dictionaries ...')
    
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts


def load_model(run_id):
    print('loading models ...')
    
    logged_model = f'runs:/{run_id}/models_mlflow'
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def apply_model(input_file, run_id, output_file):
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    model = load_model(run_id)

    print('predicting ...')

    le = LabelEncoder()
    df_input = pd.DataFrame(dicts)
    df_input['PU_DO'] = le.fit_transform(df_input['PU_DO'])
    y_pred = model.predict(df_input)

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id
    
    df_result.to_parquet(output_file, index=False)
    print(f'results saved to {output_file}')


def run()
    taxi_type = sys.argv[1]   # 'green'
    year = int(sys.argv[2])   # 2024
    month = int(sys.argv[3])  # 1

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/{taxi_type}/{year:04d}-{month:02d}.parquet'

    RUN_ID = '40da67942f0740d7b27c002eb79f755e'

    MLFLOW_TRACKING_URI = 'http://localhost:5000'
    mlflow.set_tracking_uri('sqlite:///mlflow.db')
    mlflow.set_experiment('nyc-taxi-experiment')


    apply_model(input_file=input_file, run_id=RUN_ID, output_file=output_file)


# python score.py green 2024 1
if __name__ == '__main__':
    run()
