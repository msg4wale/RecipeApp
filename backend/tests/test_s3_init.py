import json

from app.s3_init import BUCKETS, RECIPE_MEDIA_POLICY, configure_buckets


class FakeS3Client:
    def __init__(self, existing: set[str]) -> None:
        self.existing = existing
        self.created: list[str] = []
        self.policies: list[tuple[str, str]] = []

    def list_buckets(self) -> dict[str, list[dict[str, str]]]:
        return {"Buckets": [{"Name": name} for name in sorted(self.existing)]}

    def create_bucket(self, *, Bucket: str) -> None:
        self.created.append(Bucket)
        self.existing.add(Bucket)

    def put_bucket_policy(self, *, Bucket: str, Policy: str) -> None:
        self.policies.append((Bucket, Policy))


def test_configure_buckets_creates_missing_buckets_and_sets_public_media_policy() -> None:
    client = FakeS3Client({"recipe-media"})

    configure_buckets(client)

    assert client.created == ["chef-certificates"]
    assert len(client.policies) == 1
    bucket, policy = client.policies[0]
    assert bucket == "recipe-media"
    assert json.loads(policy) == RECIPE_MEDIA_POLICY
    assert set(client.existing) == set(BUCKETS)


def test_configure_buckets_is_idempotent() -> None:
    client = FakeS3Client(set(BUCKETS))

    configure_buckets(client)

    assert client.created == []
    assert len(client.policies) == 1
