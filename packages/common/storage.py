from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from .settings import settings


@dataclass(frozen=True)
class PutResult:
    bucket: str
    key: str
    sha256: str
    size_bytes: int


def build_s3_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


_s3 = build_s3_client()


def ensure_bucket(bucket: str) -> None:
    # idempotent bucket create
    try:
        _s3.head_bucket(Bucket=bucket)
    except Exception:
        _s3.create_bucket(Bucket=bucket)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def put_bytes(
    *,
    bucket: str,
    key: str,
    data: bytes,
    content_type: str,
) -> PutResult:
    ensure_bucket(bucket)
    _s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
    return PutResult(bucket=bucket, key=key, sha256=sha256_hex(data), size_bytes=len(data))


def presign_get_url(*, bucket: str, key: str, expires_seconds: int = 300) -> str:
    """Return a time-limited GET URL."""
    return _s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_seconds,
    )
