from datetime import datetime
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch import prepare_data


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_prepare_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),      # duration = 9 minutes ✓
        (1, 1, dt(1, 2), dt(1, 10)),            # duration = 8 minutes ✓  
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),   # duration = 59/60 ≈ 0.98 minutes ✗ (< 1)
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),       # duration = 60.017 minutes ✗ (> 60)
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)
    
    categorical = ['PULocationID', 'DOLocationID']
    
    result_df = prepare_data(df, categorical)
    
    expected_data = [
        (-1, -1, dt(1, 1), dt(1, 10), 9.0),     # None → -1, duration = 9 min
        (1, 1, dt(1, 2), dt(1, 10), 8.0),       # duration = 8 min
    ]
    
    expected_columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'duration']
    expected_df = pd.DataFrame(expected_data, columns=expected_columns)
    
    expected_df[categorical] = expected_df[categorical].astype('str')
    
    assert len(result_df) == 2, f"Expected 2 rows, got {len(result_df)}"
    
    # cat columns 
    assert result_df['PULocationID'].tolist() == ['-1', '1']
    assert result_df['DOLocationID'].tolist() == ['-1', '1']
    
    # duration
    assert result_df['duration'].tolist() == [9.0, 8.0]
    
    print("Test passed!")
    print(f"Result DataFrame has {len(result_df)} rows")


if __name__ == "__main__":
    test_prepare_data()