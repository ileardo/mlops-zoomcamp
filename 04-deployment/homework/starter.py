import pandas as pd
import numpy as np
import argparse
import pickle
import os


def main(args):
    # load the model and the DictVectorizer
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)

    categorical = ['PULocationID', 'DOLocationID']


    # read the data from parquet file
    def read_data(filename):
        df = pd.read_parquet(filename)
        
        df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
        df['duration'] = df.duration.dt.total_seconds() / 60

        df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

        df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
        
        return df

    year, month = args.year, args.month
    # read the data
    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet')

    # transform the data
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)

    # make predictions
    y_pred = model.predict(X_val)

    mean_duration = np.mean(y_pred)
    print(f"Mean predicted duration for {year:04d}-{month:02d}: {mean_duration:.2f}")

    # create ride_id
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    # create the result DataFrame
    df_result = pd.DataFrame({
        'ride_id': df['ride_id'],
        'predicted_duration': y_pred
    })
    df_result.head()

    # save the result to a parquet file
    output_file = f'predictions_{year:04d}_{month:02d}.parquet'
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict trip durations')
    parser.add_argument('--year', type=int, required=True, help='Year of the trip data')
    parser.add_argument('--month', type=int, required=True, help='Month of the trip data')
    
    args = parser.parse_args()
    
    main(args)