"""
S3 client for presigned URL generation.
"""

import boto3
import uuid
from app.core.config import get_settings

settings = get_settings()
s3_client = boto3.client("s3", region_name=settings.AWS_REGION)

def create_presigned_url(filename: str, content_type: str, expires_in: int = 3600):
    file_id = str(uuid.uuid4())
    s3_key = f"videos/{file_id}_{filename}"

    url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": s3_key, "ContentType": content_type},
        ExpiresIn=expires_in,
    )

    return {"uploadUrl": url, "fileId": file_id, "s3Key": s3_key}
