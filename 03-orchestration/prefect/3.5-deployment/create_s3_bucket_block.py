from prefect_aws import S3Bucket, AwsCredentials

from time import sleep
import os

def create_aws_creds_block():
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not aws_access_key or not aws_secret_key:
        raise ValueError(
            'AWS credentials not configured. \nSet environment variables: '
            '\nexport AWS_ACCESS_KEY_ID="your-access-key-here"'
            '\nexport AWS_SECRET_ACCESS_KEY="your-secret-key-here"'
            '\nexport AWS_DEFAULT_REGION="your-region"'
        )
    
    my_aws_creds_obj = AwsCredentials(
        aws_access_key_id=aws_access_key, 
        aws_secret_access_key=aws_secret_key
    )
    my_aws_creds_obj.save(name="my-aws-creds", overwrite=True)
    print('Credentials created and saved as "my-aws-creds"')


def create_s3_bucket_block():
    try:
        aws_creds = AwsCredentials.load("my-aws-creds")
    except Exception as e:
        print(f'Credential import error: {e}')
        return
    
    my_s3_bucket_obj = S3Bucket(
        bucket_name="prefect-artifacts-remote-lg",  # existing bucket
        credentials=aws_creds
    )
    my_s3_bucket_obj.save(name="s3-bucket-prefect-artifacts", overwrite=True)
    print('S3 bucket block created and saved as "s3-bucket-prefect-artifacts"')

def test_s3_connection():

    try:
        s3_bucket = S3Bucket.load("s3-bucket-prefect-artifacts")
        
        test_content = b"test-prefect-connection"
        test_key = "prefect-test/connection-test.txt"
        
        s3_bucket.write_path(test_key, content=test_content)
        print("✅ Test upload completed")
        
        downloaded = s3_bucket.read_path(test_key)
        if downloaded == test_content:
            print("✅ Test download completed")
        return True
        
    except Exception as e:
        print(f"S3 connection error: {e}")
        return False

if __name__ == "__main__":

    print()
    create_aws_creds_block()
    sleep(2)
    create_s3_bucket_block()
    sleep(2)
    print("\nTesting S3 connection...")
    if test_s3_connection():
        print('✅ Configuration completed and S3 connection tested successfully')
    else:
        print('S3 connection test failed. Please check your configuration.')