import io
import os
from uuid import uuid4

import boto3
import pytest
from botocore.config import Config
from botocore.exceptions import ClientError, ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError

from app.config import Settings, get_settings
from app.storage import (
    PrivateObjectAccessDenied,
    S3Storage,
    StorageBucket,
    StorageObjectNotFound,
    StorageOperationError,
    StorageUnavailable,
    StorageValidationError,
    UploadMetadata,
    UploadPolicy,
)

VALID_JPEG = b"\xff\xd8\xffphoto"
VALID_PDF = b"%PDF-1.7\n"


class FakeS3Client:
    def __init__(self, endpoint: str = "http://localhost:9000") -> None:
        self.endpoint = endpoint
        self.objects: dict[tuple[str, str], tuple[bytes, str]] = {}
        self.calls: list[tuple[str, dict]] = []
        self.fail_download: Exception | None = None

    def put_object(self, **kwargs) -> None:
        self.calls.append(("put_object", kwargs))
        body = kwargs["Body"].read() if hasattr(kwargs["Body"], "read") else kwargs["Body"]
        self.objects[(kwargs["Bucket"], kwargs["Key"])] = (body, kwargs["ContentType"])

    def get_object(self, **kwargs) -> dict:
        self.calls.append(("get_object", kwargs))
        if self.fail_download is not None:
            raise self.fail_download
        body, _ = self.objects[(kwargs["Bucket"], kwargs["Key"])]
        return {"Body": io.BytesIO(body)}

    def delete_object(self, **kwargs) -> None:
        self.calls.append(("delete_object", kwargs))
        self.objects.pop((kwargs["Bucket"], kwargs["Key"]), None)

    def generate_presigned_url(self, operation: str, *, Params: dict, ExpiresIn: int) -> str:
        self.calls.append(("generate_presigned_url", {"operation": operation, "Params": Params, "ExpiresIn": ExpiresIn}))
        return f"{self.endpoint}/{Params['Bucket']}/{Params['Key']}?signed={operation}"


def make_storage(
    *,
    validation_hook=None,
    endpoint: str = "http://localhost:4566",
    upload_policy: UploadPolicy | None = None,
) -> tuple[S3Storage, FakeS3Client, FakeS3Client]:
    settings = Settings(s3_endpoint=endpoint, s3_public_endpoint="http://public.test:9000")
    client = FakeS3Client(endpoint)
    presign_client = FakeS3Client(settings.s3_public_endpoint)
    storage = S3Storage(
        settings,
        client=client,
        presign_client=presign_client,
        validation_hook=validation_hook,
        upload_policy=upload_policy,
    )
    return storage, client, presign_client


def test_upload_download_and_delete_use_the_selected_bucket() -> None:
    storage, client, _ = make_storage()

    storage.upload(StorageBucket.RECIPE_MEDIA, "recipes/42/photo.jpg", VALID_JPEG, "image/jpeg")
    assert storage.download(StorageBucket.RECIPE_MEDIA, "recipes/42/photo.jpg") == VALID_JPEG
    storage.delete(StorageBucket.RECIPE_MEDIA, "recipes/42/photo.jpg")

    assert [call[0] for call in client.calls] == ["put_object", "get_object", "delete_object"]
    assert all(call[1]["Bucket"] == "recipe-media" for call in client.calls)
    assert not client.objects


def test_upload_validation_hook_receives_metadata_before_storage() -> None:
    seen: list[UploadMetadata] = []
    storage, client, _ = make_storage(validation_hook=seen.append)

    storage.upload(
        StorageBucket.CHEF_CERTIFICATES,
        "applications/1/certificate.pdf",
        VALID_PDF,
        "application/pdf",
    )

    assert seen == [
        UploadMetadata(
            StorageBucket.CHEF_CERTIFICATES,
            "applications/1/certificate.pdf",
            "application/pdf",
            len(VALID_PDF),
        )
    ]
    assert client.calls[0][0] == "put_object"


def test_validation_hook_can_reject_before_object_is_written() -> None:
    def reject(_metadata: UploadMetadata) -> None:
        raise StorageValidationError("Upload rejected by policy")

    storage, client, _ = make_storage(validation_hook=reject)

    with pytest.raises(StorageValidationError, match="Upload rejected"):
        storage.upload(StorageBucket.RECIPE_MEDIA, "photo.jpg", VALID_JPEG, "image/jpeg")

    assert not client.calls


def test_presigned_upload_fails_closed_without_pre_persistence_content_validation() -> None:
    storage, _, presign_client = make_storage()

    with pytest.raises(StorageValidationError, match="Pre-signed uploads are disabled"):
        storage.generate_presigned_upload_url(
            StorageBucket.RECIPE_MEDIA,
            "recipes/42/photo.jpg",
            "image/jpeg",
            expected_size=len(VALID_JPEG),
        )

    assert not presign_client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type", "body"),
    [
        (StorageBucket.RECIPE_MEDIA, "application/pdf", VALID_PDF),
        (StorageBucket.CHEF_CERTIFICATES, "video/mp4", b"0000ftypisom"),
    ],
)
def test_upload_rejects_disallowed_content_type_before_storage(bucket, content_type, body) -> None:
    storage, client, _ = make_storage()

    with pytest.raises(StorageValidationError, match="not allowed"):
        storage.upload(bucket, "upload.bin", body, content_type)

    assert not client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type", "body"),
    [
        (StorageBucket.RECIPE_MEDIA, "image/jpeg", VALID_PDF),
        (StorageBucket.CHEF_CERTIFICATES, "application/pdf", VALID_JPEG),
    ],
)
def test_upload_rejects_content_that_does_not_match_declared_format(bucket, content_type, body) -> None:
    storage, client, _ = make_storage()

    with pytest.raises(StorageValidationError, match="do not match"):
        storage.upload(bucket, "upload.bin", body, content_type)

    assert not client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type", "body"),
    [
        (StorageBucket.RECIPE_MEDIA, "image/jpeg", VALID_JPEG + b"x" * 8),
        (StorageBucket.CHEF_CERTIFICATES, "application/pdf", VALID_PDF + b"x" * 8),
    ],
)
def test_upload_rejects_oversize_body_before_storage(bucket, content_type, body) -> None:
    small_limits = UploadPolicy(certificate_max_bytes=8, recipe_media_max_bytes=8)
    storage, client, _ = make_storage(upload_policy=small_limits)

    with pytest.raises(StorageValidationError, match="exceeds"):
        storage.upload(bucket, "upload.bin", body, content_type)

    assert not client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type", "body"),
    [
        (StorageBucket.RECIPE_MEDIA, "image/jpeg", VALID_JPEG + b"x" * 8),
        (StorageBucket.CHEF_CERTIFICATES, "application/pdf", VALID_PDF + b"x" * 8),
    ],
)
def test_upload_measures_stream_instead_of_trusting_expected_size(bucket, content_type, body) -> None:
    small_limits = UploadPolicy(certificate_max_bytes=8, recipe_media_max_bytes=8)
    storage, client, _ = make_storage(upload_policy=small_limits)

    with pytest.raises(StorageValidationError, match="exceeds"):
        storage.upload(bucket, "upload.bin", io.BytesIO(body), content_type, expected_size=1)

    assert not client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type"),
    [
        (StorageBucket.RECIPE_MEDIA, "image/jpeg"),
        (StorageBucket.CHEF_CERTIFICATES, "application/pdf"),
    ],
)
def test_presigned_upload_rejects_disallowed_content_type(bucket, content_type) -> None:
    storage, client, presign_client = make_storage()
    disallowed_type = "application/pdf" if bucket is StorageBucket.RECIPE_MEDIA else "video/mp4"

    with pytest.raises(StorageValidationError, match="not allowed"):
        storage.generate_presigned_upload_url(bucket, "upload.bin", disallowed_type, expected_size=4)

    assert not client.calls
    assert not presign_client.calls


@pytest.mark.parametrize(
    ("bucket", "content_type"),
    [
        (StorageBucket.RECIPE_MEDIA, "image/jpeg"),
        (StorageBucket.CHEF_CERTIFICATES, "application/pdf"),
    ],
)
def test_presigned_upload_rejects_oversize_before_signing(bucket, content_type) -> None:
    small_limits = UploadPolicy(certificate_max_bytes=8, recipe_media_max_bytes=8)
    storage, client, presign_client = make_storage(upload_policy=small_limits)

    with pytest.raises(StorageValidationError, match="exceeds"):
        storage.generate_presigned_upload_url(bucket, "upload.bin", content_type, expected_size=9)

    assert not client.calls
    assert not presign_client.calls


def test_private_certificate_url_requires_explicit_prior_authorization() -> None:
    storage, _, presign_client = make_storage()

    with pytest.raises(PrivateObjectAccessDenied):
        storage.generate_presigned_download_url(StorageBucket.CHEF_CERTIFICATES, "applications/1/cert.pdf")

    url = storage.generate_presigned_download_url(
        StorageBucket.CHEF_CERTIFICATES,
        "applications/1/cert.pdf",
        private_access_authorized=True,
    )
    assert "chef-certificates" in url
    assert len(presign_client.calls) == 1


def test_private_bucket_cannot_be_converted_to_a_public_url() -> None:
    storage, _, _ = make_storage()

    with pytest.raises(PrivateObjectAccessDenied):
        storage.public_url(StorageBucket.CHEF_CERTIFICATES, "applications/1/cert.pdf")


def test_public_recipe_url_encodes_key_without_exposing_credentials() -> None:
    storage, _, _ = make_storage()

    url = storage.public_url(StorageBucket.RECIPE_MEDIA, "recipes/42/a photo.jpg")

    assert url == "http://public.test:9000/recipe-media/recipes/42/a%20photo.jpg"
    assert "test:test@" not in url


def test_missing_download_has_a_specific_error() -> None:
    storage, client, _ = make_storage()
    client.fail_download = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "GetObject"
    )

    with pytest.raises(StorageObjectNotFound, match="not found"):
        storage.download(StorageBucket.RECIPE_MEDIA, "missing.jpg")


def test_other_s3_errors_are_reported_as_operation_errors() -> None:
    storage, client, _ = make_storage()
    client.fail_download = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "denied"}}, "GetObject"
    )

    with pytest.raises(StorageOperationError, match=r"download failed \(AccessDenied\)"):
        storage.download(StorageBucket.RECIPE_MEDIA, "private.jpg")


def test_connection_failures_are_reported_as_unavailable() -> None:
    storage, client, _ = make_storage()
    client.fail_download = EndpointConnectionError(endpoint_url="http://localstack:4566")

    with pytest.raises(StorageUnavailable, match="storage unavailable"):
        storage.download(StorageBucket.RECIPE_MEDIA, "photo.jpg")


@pytest.mark.parametrize("invalid_expiry", [0, -1, 604801])
def test_signed_url_rejects_invalid_expiry(invalid_expiry: int) -> None:
    storage, _, _ = make_storage()

    with pytest.raises(ValueError, match="expiry"):
        storage.generate_presigned_download_url(StorageBucket.RECIPE_MEDIA, "photo.jpg", expires_in=invalid_expiry)


@pytest.mark.skipif(os.getenv("RUN_S3_INTEGRATION") != "1", reason="Set RUN_S3_INTEGRATION=1 to enable LocalStack S3 tests")
def test_localstack_s3_upload_download_delete_round_trip() -> None:
    settings = get_settings()
    probe = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )
    try:
        for bucket in StorageBucket:
            probe.head_bucket(Bucket=bucket.value)
    except (ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError) as error:
        pytest.skip(f"LocalStack S3 and provisioned buckets are unavailable: {error}")

    storage = S3Storage(settings)
    for bucket in StorageBucket:
        body, content_type, extension = (
            (VALID_JPEG, "image/jpeg", "jpg")
            if bucket is StorageBucket.RECIPE_MEDIA
            else (VALID_PDF, "application/pdf", "pdf")
        )
        object_key = f"integration-tests/{uuid4()}.{extension}"
        storage.upload(bucket, object_key, body, content_type)
        assert storage.download(bucket, object_key) == body
        storage.delete(bucket, object_key)