import os
from google.cloud import storage
import datetime

def generate_signed_url(bucket_name: str, file_name: str, content_type: str):
    """Generates a v4 signed URL for uploading a file."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="PUT",
        content_type=content_type,
    )
    return url

def upload_file_to_gcs(file_path: str, destination_blob_name: str):
    """Uploads a file to the bucket."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

    return f"gs://{bucket_name}/{destination_blob_name}" 