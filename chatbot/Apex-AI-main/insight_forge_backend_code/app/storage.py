"""S3 / MinIO storage helpers (boto3).

Uploads stream to the landing bucket in ~1 MB parts so we never hold the whole
file in memory. This module only *stores* bytes — it never inspects or parses
the file contents.
"""
from typing import BinaryIO

import boto3
from boto3.s3.transfer import TransferConfig

from app.config import settings

_ONE_MB = 1024 * 1024

# Multipart upload in ~1 MB parts; boto3 falls back to a single PUT below the
# threshold. (S3 requires >=5 MB parts for true multipart; boto3 handles the
# small-file case transparently.)
_transfer_config = TransferConfig(multipart_threshold=_ONE_MB, multipart_chunksize=_ONE_MB)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
    )


def build_object_key(organization_id: str, dataset_id: str, filename: str) -> str:
    """Namespace every object under its organization so buckets stay isolated too."""
    safe_name = filename.replace("/", "_").strip() or "upload"
    return f"{organization_id}/{dataset_id}/{safe_name}"


def stream_to_landing(fileobj: BinaryIO, key: str, content_type: str | None) -> int:
    """Stream a file object to the landing bucket. Returns the stored size in bytes."""
    client = get_s3_client()
    extra = {"ContentType": content_type} if content_type else {}
    client.upload_fileobj(
        fileobj, settings.s3_bucket, key, ExtraArgs=extra or None, Config=_transfer_config
    )
    head = client.head_object(Bucket=settings.s3_bucket, Key=key)
    return int(head["ContentLength"])
