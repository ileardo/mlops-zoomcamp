import pandas as pd
import datetime
import psycopg
import logging 
import random
import joblib
import time
import uuid
import pytz
import io

from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric
from evidently.report import Report
from evidently import ColumnMapping

from prefect import task, flow

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

# SQL statement to create the 'evidently_metrics' table
create_table_statement = """
drop table if exists evidently_metrics;
create table evidently_metrics(
    timestamp timestamp,
    prediction_drift float,
    num_drifted_columns integer,
    share_missing_values float
)
"""

reference_data = pd.read_parquet('data/reference.parquet')
with open('models/lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in)

raw_data = pd.read_parquet('data/green_tripdata_2022-02.parquet')

begin = datetime.datetime(2022, 2, 1, 0, 0)
num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
cat_features = ['PULocationID', 'DOLocationID']
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])


@task(name="Prepare Database")
def prep_db(host, port, user, password, db_name):
    """
    Checks if the 'test' database exists, creates it if not,
    and then creates a table named 'evidently_metrics' with the specified schema.
    """
    with psycopg.connect(f"host={host} port={port} user={user} password={password}", autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname={db_name!r};")
        # Check if the database exists
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(f"host={host} port={port} dbname={db_name} user={user} password={password}") as conn:
            conn.execute(create_table_statement)


@task(name="Calculate Metrics")
def calculate_metrics_postgresql(curr, i):
    """
    Generates metrics and inserts them into the 'evidently_metrics' table.

    :param curr: The database cursor to execute the SQL command.
    :param i: Number of day in the month.
    """
    current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) & 
                    (raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]

    current_data.fillna(0, inplace=True)
    current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

    report.run(reference_data = reference_data, current_data = current_data,
        column_mapping=column_mapping)

    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']

    # Insert the generated metrics into the 'evidently_metrics' table
    curr.execute(
        "insert into evidently_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
        (begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values)
    )


@flow(name="Batch Monitoring Backfill")
def batch_monitoring_backfill(**kwargs):
    """
    Main function to prepare the database and continuously insert metrics until the end of the month.
    It ensures that the database is ready and that the metrics are sent at regular intervals.
    """
    prep_db(
        kwargs['host'],
        kwargs['port'],
        kwargs['user'],
        kwargs['password'],
        kwargs['db_name']
    )

    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)

    with psycopg.connect(f"host={kwargs['host']} port={kwargs['port']} dbname={kwargs['db_name']} user={kwargs['user']} password={kwargs['password']}", autocommit=True) as conn:
        for i in range(0, 27):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, i)

            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)
            logging.info("data sent")


if __name__ == '__main__':
    host = 'localhost'
    port = 5432
    user = 'postgres'
    password = 'password'
    db_name = 'test'
    batch_monitoring_backfill(host=host, port=port, user=user, password=password, db_name=db_name)