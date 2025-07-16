import pandas as pd
import datetime
import psycopg
import logging 
import time

from evidently.metrics import ColumnQuantileMetric, ColumnMissingValuesMetric
from evidently.report import Report
from prefect import task, flow

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# SQL statement to create the 'homework_metrics' table
create_table_statement = """
drop table if exists homework_metrics;
create table homework_metrics(
    timestamp timestamp,
    fare_amount_quantile_05 float,
    fare_amount_missing_values integer,
    date date
)
"""

# Load March 2024 data
raw_data = pd.read_parquet('data/green_tripdata_2024-03.parquet')


@task(name="Prepare Database")
def prep_db(host, port, user, password, db_name):
    """
    Creates database and table for homework metrics.
    """
    with psycopg.connect(f"host={host} port={port} user={user} password={password}", autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname={db_name!r};")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(f"host={host} port={port} dbname={db_name} user={user} password={password}") as conn:
            conn.execute(create_table_statement)


@task(name="Calculate Daily Metrics")
def calculate_daily_metrics(curr, date, daily_data):
    """
    Calculate homework metrics for a specific day.
    """
    # Setup metrics
    metrics = [
        ColumnQuantileMetric("fare_amount", quantile=0.5),
        ColumnMissingValuesMetric("fare_amount")
    ]
    
    report = Report(metrics=metrics)
    report.run(reference_data=None, current_data=daily_data)
    
    result = report.as_dict()
    
    # Extract metrics
    fare_quantile_05 = result['metrics'][0]['result']['current']['value']
    missing_values = result['metrics'][1]['result']['current']['number_of_missing_values']
    
    # Insert into database
    curr.execute(
        "insert into homework_metrics(timestamp, fare_amount_quantile_05, fare_amount_missing_values, date) values (%s, %s, %s, %s)",
        (datetime.datetime.combine(date, datetime.time()), fare_quantile_05, missing_values, date)
    )


@flow(name="Homework Monitoring")
def homework_monitoring(**kwargs):
    """
    Main function to calculate and store homework metrics for March 2024.
    """
    prep_db(
        kwargs['host'],
        kwargs['port'],
        kwargs['user'],
        kwargs['password'],
        kwargs['db_name']
    )
    
    # Add date column
    raw_data['date'] = pd.to_datetime(raw_data['lpep_pickup_datetime']).dt.date
    
    # Filter only March 2024
    march_data = raw_data[
        (pd.to_datetime(raw_data['lpep_pickup_datetime']).dt.month == 3) &
        (pd.to_datetime(raw_data['lpep_pickup_datetime']).dt.year == 2024)
    ]
    
    with psycopg.connect(f"host={kwargs['host']} port={kwargs['port']} dbname={kwargs['db_name']} user={kwargs['user']} password={kwargs['password']}", autocommit=True) as conn:
        
        # Process each day in March
        for date in sorted(march_data['date'].unique()):
            daily_data = march_data[march_data['date'] == date]
            
            with conn.cursor() as curr:
                calculate_daily_metrics(curr, date, daily_data)
            
            logging.info(f"Processed data for {date}")
            time.sleep(1)  # Small delay


if __name__ == '__main__':
    host = 'localhost'
    port = 5432
    user = 'postgres'
    password = 'password'
    db_name = 'test'
    homework_monitoring(host=host, port=port, user=user, password=password, db_name=db_name)