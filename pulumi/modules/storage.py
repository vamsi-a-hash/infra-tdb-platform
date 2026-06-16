"""
storage.py — GCS buckets for TalkingDB.

Creates:
  - talkingdb-app-dev-talkingdb-40099   → uploaded documents, processed outputs
  - talkingdb-logs-dev-talkingdb-40099  → structured service logs

GCS bucket names are globally unique across all of GCP, so we suffix
with the project ID to avoid collisions.
"""

import pulumi
import pulumi_gcp as gcp


def create_storage(env: str, project: str) -> dict:

    # App bucket — documents, model outputs, processed files
    app_bucket = gcp.storage.Bucket(
        f"talkingdb-app-{env}",
        name=f"talkingdb-app-{env}-{project}",
        location="ASIA-SOUTH1",
        uniform_bucket_level_access=True,
        versioning=gcp.storage.BucketVersioningArgs(enabled=True),
        lifecycle_rules=[
            gcp.storage.BucketLifecycleRuleArgs(
                action=gcp.storage.BucketLifecycleRuleActionArgs(
                    type="Delete"),
                condition=gcp.storage.BucketLifecycleRuleConditionArgs(age=90),
            )
        ],
        labels={"env": env, "app": "talkingdb"},
    )

    # Logs bucket — service logs from module-talkingdb and other services
    logs_bucket = gcp.storage.Bucket(
        f"talkingdb-logs-{env}",
        name=f"talkingdb-logs-{env}-{project}",
        location="ASIA-SOUTH1",
        uniform_bucket_level_access=True,
        lifecycle_rules=[
            gcp.storage.BucketLifecycleRuleArgs(
                action=gcp.storage.BucketLifecycleRuleActionArgs(
                    type="Delete"),
                condition=gcp.storage.BucketLifecycleRuleConditionArgs(age=30),
            )
        ],
        labels={"env": env, "app": "talkingdb", "type": "logs"},
    )

    pulumi.export(f"app_bucket_{env}", app_bucket.url)
    pulumi.export(f"logs_bucket_{env}", logs_bucket.url)

    return {"app": app_bucket, "logs": logs_bucket}
