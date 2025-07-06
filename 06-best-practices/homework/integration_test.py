from datetime import datetime
import pandas as pd
import os

S3_ENDPOINT_URL = 'http://localhost:4566'
os.environ['S3_ENDPOINT_URL'] = S3_ENDPOINT_URL
os.environ['INPUT_FILE_PATTERN'] = 's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'
os.environ['OUTPUT_FILE_PATTERN'] = 's3://nyc-duration/out/{year:04d}-{month:02d}.parquet'


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def create_test_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(data, columns=columns)
    
    options = {
        'client_kwargs': {
            'endpoint_url': S3_ENDPOINT_URL
        }
    }
    
    input_file = 's3://nyc-duration/in/2023-01.parquet'
    
    df_input.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )
    
    print(f"Test data created and saved to {input_file}")
    return input_file


def run_batch_script(year, month):
    """Esegue batch.py usando os.system"""
    cmd = f"python batch.py {year} {month}"
    print(f"Running: {cmd}")
    result = os.system(cmd)
    if result == 0:
        print("Batch script completed successfully")
    else:
        print(f"Batch script failed with exit code: {result}")
    return result


def read_and_verify_results():
    """Legge i risultati e calcola la somma delle durate predette"""
    options = {
        'client_kwargs': {
            'endpoint_url': S3_ENDPOINT_URL
        }
    }
    
    output_file = 's3://nyc-duration/out/2023-01.parquet'
    
    try:
        df_result = pd.read_parquet(output_file, storage_options=options)
        
        print(f"Results loaded successfully. Shape: {df_result.shape}")
        print("Columns:", df_result.columns.tolist())
        print("Sample data:")
        print(df_result.head())
        
        sum_predicted_durations = df_result['predicted_duration'].sum()
        print(f"\nSum of predicted durations: {sum_predicted_durations:.2f}")
        
        return sum_predicted_durations, df_result
        
    except Exception as e:
        print(f"Error reading results: {e}")
        return None, None


def main():
    print("=== MLOps Integration Test ===")
    
    print("\n1. Creating test data...")
    create_test_data()
    
    print("\n2. Running batch processing...")
    result = run_batch_script(2023, 1)
    
    if result != 0:
        print("Batch script failed. Stopping test.")
        return
    
    print("\n3. Verifying results...")
    sum_durations, df_results = read_and_verify_results()
    
    if sum_durations is not None:
        print(f"\n=== FINAL RESULT ===")
        print(f"Sum of predicted durations: {sum_durations:.2f}")
        
        options = [13.08, 36.28, 69.28, 81.08]
        closest = min(options, key=lambda x: abs(x - sum_durations))
        print(f"Closest option from homework: {closest}")
    else:
        print("Test failed - could not read results")


if __name__ == "__main__":
    main()