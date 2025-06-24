import pandas as pd
import datetime
import psycopg
import logging 
import random
import time
import uuid
import pytz
import io

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

# SQL statement to create the 'dummy_metrics' table
create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
timestamp timestamp,
value1 integer,
value2 varchar,
value3 float
)
"""


def prep_db(host, port, user, password, db_name):
    """
    Checks if the 'test' database exists, creates it if not,
    and then creates a table named 'dummy_metrics' with the specified schema.
    """
    with psycopg.connect(f"host={host} port={port} user={user} password={password}", autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname={db_name!r};")
        # Check if the database exists
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(f"host={host} port={port} dbname={db_name} user={user} password={password}") as conn:
            conn.execute(create_table_statement)


def calculate_dummy_metrics_postgresql(curr):
    """
    Generates dummy metrics and inserts them into the 'dummy_metrics' table.

    :param curr: The database cursor to execute the SQL command.
    """
    value1 = rand.randint(0, 1000)
    value2 = str(uuid.uuid4())
    value3 = rand.random()

    # Insert the generated metrics into the 'dummy_metrics' table
    curr.execute(
        "insert into dummy_metrics(timestamp, value1, value2, value3) values (%s, %s, %s, %s)",
        (datetime.datetime.now(pytz.timezone('Europe/London')), value1, value2, value3)
    )


def main(**kwargs):
    """
    Main function to prepare the database and continuously insert dummy metrics
    into the 'dummy_metrics' table every 10 seconds.
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
        for i in range(0, 100):
            with conn.cursor() as curr:
                calculate_dummy_metrics_postgresql(curr)

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
    main(host=host, port=port, user=user, password=password, db_name=db_name)