import json
import logging
import os
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ConnectionClosedError, EndpointConnectionError, ReadTimeoutError


logger = logging.getLogger(__name__)

BUCKETS = ("recipe-media", "chef-certificates")
RECIPE_MEDIA_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::recipe-media/*"],
        }
    ],
}
READINESS_ATTEMPTS = 30
READINESS_INTERVAL_SECONDS = 2


def configure_buckets(client) -> None:
    existing = {bucket["Name"] for bucket in client.list_buckets()["Buckets"]}
    for bucket in BUCKETS:
        if bucket not in existing:
            client.create_bucket(Bucket=bucket)

    client.put_bucket_policy(
        Bucket="recipe-media",
        Policy=json.dumps(RECIPE_MEDIA_POLICY),
    )


def initialize_s3(client, *, attempts: int = READINESS_ATTEMPTS) -> None:
    for attempt in range(1, attempts + 1):
        try:
            client.list_buckets()
            break
        except (ConnectionClosedError, EndpointConnectionError, ReadTimeoutError):
            if attempt == attempts:
                raise
            logger.info("Waiting for LocalStack readiness (%d/%d)", attempt, attempts)
            time.sleep(READINESS_INTERVAL_SECONDS)

    configure_buckets(client)
    logger.info("LocalStack S3 buckets are initialized")


def main() -> None:
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT", "http://localstack:4566"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY", "test"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY", "test"),
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )
    initialize_s3(client)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
