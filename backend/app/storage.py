from dataclasses import dataclass
from enum import Enum
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Callable, NoReturn
from urllib.parse import quote

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import Settings, get_settings


class StorageBucket(str, Enum):
    RECIPE_MEDIA = "recipe-media"
    CHEF_CERTIFICATES = "chef-certificates"


@dataclass(frozen=True)
class UploadMetadata:
    bucket: StorageBucket
    object_key: str
    content_type: str
    size_bytes: int | None


@dataclass(frozen=True)
class UploadPolicy:
    certificate_max_bytes: int = 10 * 1024 * 1024
    recipe_media_max_bytes: int = 25 * 1024 * 1024
    certificate_content_types: frozenset[str] = frozenset(
        {"application/pdf", "image/jpeg", "image/png"}
    )
    recipe_media_content_types: frozenset[str] = frozenset(
        {"image/jpeg", "image/png", "image/webp", "video/mp4"}
    )

    def __post_init__(self) -> None:
        if self.certificate_max_bytes <= 0 or self.recipe_media_max_bytes <= 0:
            raise ValueError("Upload size limits must be positive")

    def max_bytes(self, bucket: StorageBucket) -> int:
        if bucket is StorageBucket.CHEF_CERTIFICATES:
            return self.certificate_max_bytes
        return self.recipe_media_max_bytes

    def content_types(self, bucket: StorageBucket) -> frozenset[str]:
        if bucket is StorageBucket.CHEF_CERTIFICATES:
            return self.certificate_content_types
        return self.recipe_media_content_types


UploadValidationHook = Callable[[UploadMetadata], None]


class StorageError(RuntimeError):
    """Base error for storage operation failures."""


class StorageObjectNotFound(StorageError):
    """The requested object does not exist."""


class StorageUnavailable(StorageError):
    """The object storage service could not be reached."""


class StorageOperationError(StorageError):
    """The object storage service rejected or failed an operation."""


class StorageValidationError(StorageError):
    """An upload was rejected by the configured validation hook."""


class PrivateObjectAccessDenied(StorageError):
    """Private certificate access was not authorized by the caller."""


class S3Storage:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        client=None,
        presign_client=None,
        validation_hook: UploadValidationHook | None = None,
        upload_policy: UploadPolicy | None = None,
    ) -> None:
        settings = settings or get_settings()
        self._settings = settings
        self._client = client or self._create_client(settings.s3_endpoint, settings)
        self._presign_client = presign_client or self._create_client(settings.s3_public_endpoint, settings)
        self._validation_hook = validation_hook
        self._upload_policy = upload_policy or UploadPolicy()

    @staticmethod
    def _create_client(endpoint: str, settings: Settings):
        return boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name="us-east-1",
            config=Config(s3={"addressing_style": "path"}),
        )

    @staticmethod
    def _bucket(bucket: StorageBucket | str) -> StorageBucket:
        try:
            return StorageBucket(bucket)
        except ValueError as error:
            raise ValueError("Unsupported storage bucket") from error

    @staticmethod
    def _validate_key(object_key: str) -> None:
        if not object_key or "\x00" in object_key:
            raise ValueError("Object key must be non-empty and contain no NUL characters")

    def _validate_upload(
        self,
        bucket: StorageBucket,
        object_key: str,
        content_type: str,
        size_bytes: int | None,
    ) -> str:
        normalized_content_type = self._normalize_content_type(content_type)
        if normalized_content_type not in self._upload_policy.content_types(bucket):
            raise StorageValidationError(
                f"Content type {normalized_content_type!r} is not allowed for {bucket.value}"
            )
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes < 0:
            raise ValueError("Upload size must be a non-negative integer")
        if size_bytes > self._upload_policy.max_bytes(bucket):
            raise StorageValidationError(
                f"Upload exceeds the {self._upload_policy.max_bytes(bucket)} byte limit for {bucket.value}"
            )
        if self._validation_hook is not None:
            self._validation_hook(
                UploadMetadata(bucket, object_key, normalized_content_type, size_bytes)
            )
        return normalized_content_type

    @staticmethod
    def _normalize_content_type(content_type: str) -> str:
        if not content_type or not content_type.strip():
            raise ValueError("Content type is required")
        return content_type.split(";", 1)[0].strip().lower()

    @staticmethod
    def _validate_format(content_type: str, prefix: bytes) -> None:
        valid = {
            "application/pdf": prefix.startswith(b"%PDF-"),
            "image/jpeg": prefix.startswith(b"\xff\xd8\xff"),
            "image/png": prefix.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/webp": len(prefix) >= 12 and prefix[:4] == b"RIFF" and prefix[8:12] == b"WEBP",
            "video/mp4": len(prefix) >= 12 and prefix[4:8] == b"ftyp",
        }
        if not valid.get(content_type, False):
            raise StorageValidationError(
                f"Upload contents do not match the declared {content_type} format"
            )

    @staticmethod
    def _raise_storage_error(operation: str, error: ClientError | BotoCoreError) -> NoReturn:
        if isinstance(error, ClientError):
            code = str(error.response.get("Error", {}).get("Code", "Unknown"))
            if operation == "download" and code in {"404", "NoSuchKey", "NotFound"}:
                raise StorageObjectNotFound("Stored object was not found") from error
            raise StorageOperationError(f"S3 {operation} failed ({code})") from error
        raise StorageUnavailable(f"S3 storage unavailable during {operation}") from error

    def upload(
        self,
        bucket: StorageBucket | str,
        object_key: str,
        body: bytes | BinaryIO,
        content_type: str,
        *,
        expected_size: int | None = None,
    ) -> None:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        normalized_content_type = self._normalize_content_type(content_type)
        if normalized_content_type not in self._upload_policy.content_types(bucket):
            raise StorageValidationError(
                f"Content type {normalized_content_type!r} is not allowed for {bucket.value}"
            )
        max_bytes = self._upload_policy.max_bytes(bucket)
        if expected_size is not None:
            if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
                raise ValueError("Expected upload size must be a non-negative integer")
            if expected_size > max_bytes:
                raise StorageValidationError(
                    f"Upload exceeds the {max_bytes} byte limit for {bucket.value}"
                )

        staged_body = None
        if isinstance(body, bytes):
            size_bytes = len(body)
            if expected_size is not None and expected_size != size_bytes:
                raise ValueError("Expected upload size does not match the body")
            upload_body = body
            prefix = body[:12]
        elif hasattr(body, "read"):
            staged_body = SpooledTemporaryFile(max_size=1024 * 1024, mode="w+b")
            size_bytes = 0
            prefix = bytearray()
            try:
                while True:
                    chunk = body.read(min(64 * 1024, max_bytes - size_bytes + 1))
                    if not chunk:
                        break
                    if not isinstance(chunk, (bytes, bytearray, memoryview)):
                        raise TypeError("Upload file object must return bytes")
                    size_bytes += len(chunk)
                    if size_bytes > max_bytes:
                        raise StorageValidationError(
                            f"Upload exceeds the {max_bytes} byte limit for {bucket.value}"
                        )
                    if len(prefix) < 12:
                        prefix.extend(chunk[: 12 - len(prefix)])
                    staged_body.write(chunk)
                if expected_size is not None and expected_size != size_bytes:
                    raise ValueError("Expected upload size does not match the body")
                staged_body.seek(0)
                upload_body = staged_body
            except Exception:
                staged_body.close()
                raise
        else:
            raise TypeError("Upload body must be bytes or a binary file object")
        try:
            normalized_content_type = self._validate_upload(
                bucket, object_key, normalized_content_type, size_bytes
            )
            self._validate_format(normalized_content_type, bytes(prefix))
            self._client.put_object(
                Bucket=bucket.value,
                Key=object_key,
                Body=upload_body,
                ContentType=normalized_content_type,
            )
        except (ClientError, BotoCoreError) as error:
            self._raise_storage_error("upload", error)
        finally:
            if staged_body is not None:
                staged_body.close()

    def download(self, bucket: StorageBucket | str, object_key: str) -> bytes:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        try:
            response = self._client.get_object(Bucket=bucket.value, Key=object_key)
            body = response["Body"]
            try:
                return body.read()
            finally:
                body.close()
        except (ClientError, BotoCoreError) as error:
            self._raise_storage_error("download", error)

    def delete(self, bucket: StorageBucket | str, object_key: str) -> None:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        try:
            self._client.delete_object(Bucket=bucket.value, Key=object_key)
        except (ClientError, BotoCoreError) as error:
            self._raise_storage_error("delete", error)

    def generate_presigned_upload_url(
        self,
        bucket: StorageBucket | str,
        object_key: str,
        content_type: str,
        *,
        expires_in: int = 900,
        expected_size: int | None = None,
    ) -> str:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        normalized_content_type = self._normalize_content_type(content_type)
        if normalized_content_type not in self._upload_policy.content_types(bucket):
            raise StorageValidationError(
                f"Content type {normalized_content_type!r} is not allowed for {bucket.value}"
            )
        if expected_size is not None:
            if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
                raise ValueError("Expected upload size must be a non-negative integer")
            if expected_size > self._upload_policy.max_bytes(bucket):
                raise StorageValidationError(
                    f"Upload exceeds the {self._upload_policy.max_bytes(bucket)} byte limit for {bucket.value}"
                )
        self._validate_expiry(expires_in)
        raise StorageValidationError(
            "Pre-signed uploads are disabled because this S3-compatible PUT interface cannot "
            "enforce a payload size range or inspect file contents before persistence; "
            "use S3Storage.upload until a quarantine-and-validation flow is available"
        )

    def generate_presigned_download_url(
        self,
        bucket: StorageBucket | str,
        object_key: str,
        *,
        expires_in: int = 300,
        private_access_authorized: bool = False,
    ) -> str:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        self._validate_expiry(expires_in)
        if bucket is StorageBucket.CHEF_CERTIFICATES and not private_access_authorized:
            raise PrivateObjectAccessDenied("Private certificate access requires prior authorization")
        try:
            return self._presign_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket.value, "Key": object_key},
                ExpiresIn=expires_in,
            )
        except (ClientError, BotoCoreError) as error:
            self._raise_storage_error("presign download", error)

    def public_url(self, bucket: StorageBucket | str, object_key: str) -> str:
        bucket = self._bucket(bucket)
        self._validate_key(object_key)
        if bucket is not StorageBucket.RECIPE_MEDIA:
            raise PrivateObjectAccessDenied("Chef certificates do not have public URLs")
        return f"{self._settings.s3_public_endpoint.rstrip('/')}/{bucket.value}/{quote(object_key, safe='/')}"

    @staticmethod
    def _validate_expiry(expires_in: int) -> None:
        if not isinstance(expires_in, int) or not 1 <= expires_in <= 604800:
            raise ValueError("Signed URL expiry must be between 1 and 604800 seconds")