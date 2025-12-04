# file_intake/services/storage_service.py
import os
from pathlib import Path
from botocore.client import Config

USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("INTAKE_S3_BUCKET", "my-intake-bucket")

if USE_S3:
    import boto3
    s3 = boto3.client("s3", config=Config(signature_version="s3v4"))

DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))

def generate_presigned_url(qid: str, filename: str, expires: int = 900):
    key = f"quarantine/{qid}/{filename}"
    if USE_S3:
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": S3_BUCKET, "Key": key},
            ExpiresIn=expires
        )
        return {"upload_url": url, "storage_path": f"s3://{S3_BUCKET}/{key}"}
    else:
        dest_dir = DATA_ROOT / "quarantine" / qid
        dest_dir.mkdir(parents=True, exist_ok=True)
        return {"upload_url": None, "storage_path": str(dest_dir / filename)}