import boto3
import os
import json
from boto3 import client as boto3_client

s3 = boto3_client("s3")
sts = boto3_client("sts")

ACCOUNT_ID = sts.get_caller_identity()["Account"]
BUCKET = "my-metadata-demo-bucket-1234567"  # Must be globally unique
REGION = os.environ.get("AWS_REGION", "us-east-1")

def lambda_handler(event, context=None):
    """
    Payload Examples:
    
    # Create metadata config
    {
        "action": "create"
    }
    
    # Delete metadata config
    {
        "action": "delete"
    }
    """
    
    action = event.get("action", "create")  # default is create
    
    # Ensure bucket exists (only for create action)
    if action == "create":
        try:
            if REGION == "us-east-1":
                s3.create_bucket(Bucket=BUCKET)
            else:
                s3.create_bucket(
                    Bucket=BUCKET,
                    CreateBucketConfiguration={"LocationConstraint": REGION}
                )
            print(f"Bucket created or exists: {BUCKET}")
        except Exception as e:
            print(f"Error creating bucket: {e}")

        # Metadata config
        config = {
            "Bucket": BUCKET,
            "MetadataConfiguration": {
                "JournalTableConfiguration": {
                    "RecordExpiration": {"Expiration": "ENABLED", "Days": 30},
                    "EncryptionConfiguration": {"SseAlgorithm": "AES256"}
                },
                "InventoryTableConfiguration": {
                    "ConfigurationState": "ENABLED",
                    "EncryptionConfiguration": {"SseAlgorithm": "AES256"}
                }
            }
        }

        try:
            s3.create_bucket_metadata_configuration(**config)
            print("S3 Metadata configuration created")
        except Exception as e:
            print(f"Error creating metadata configuration: {e}")
    
    elif action == "delete":
        try:
            s3.delete_bucket_metadata_configuration(Bucket=BUCKET)
            print("S3 Metadata configuration deleted")
        except Exception as e:
            print(f"Error deleting metadata configuration: {e}")
    
    else:
        print(f"Invalid action: {action}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({"bucket": BUCKET, "action": action})
    }

lambda_handler(    {
        "action": "delete"
    })