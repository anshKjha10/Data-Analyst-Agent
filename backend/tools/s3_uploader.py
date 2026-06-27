import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def is_s3_configured():
    """
    Checks if all required S3 credentials and settings are defined in the environment.
    """
    required_keys = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "AWS_S3_BUCKET"
    ]
    return all(os.getenv(k) and os.getenv(k).strip() for k in required_keys)

def upload_image_buffer_to_s3(buffer, filename, content_type="image/png"):

    if not is_s3_configured():
        raise ValueError("AWS S3 environment variables are not fully configured.")

    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    bucket_name = os.getenv("AWS_S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=buffer.getvalue(),
            ContentType=content_type
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=43200 # 12 hours
        )
        return presigned_url

    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        raise e
