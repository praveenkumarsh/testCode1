import boto3
import random
import string
import datetime
from faker import Faker
import io

# ---------- CONFIGURATION ----------
BUCKET_NAME = "my-metadata-demo-bucket-12345678"   # Replace with your S3 bucket
NUM_FILES = 2000
REGION = "us-east-1"              # Example region
# ----------------------------------

# Initialize S3 client
s3 = boto3.client("s3", region_name=REGION)

# Faker for dummy text
fake = Faker()

# 10 Owners
owners = [f"Owner_{i}" for i in range(1, 11)]

# 20 Keywords
keywords = [f"Keyword_{i}" for i in range(1, 21)]

def generate_dummy_pdf_content(file_name):
    """Generate a fake PDF-like content (not a real PDF, but works as test data)."""
    text = f"This is a test PDF file: {file_name}\nGenerated for S3 metadata upload demo."
    return text.encode("utf-8")

for i in range(1, NUM_FILES + 1):
    # Metadata fields
    owner = random.choice(owners)
    file_keywords = random.sample(keywords, random.randint(4, 7))
    description = " ".join(fake.words(100))   # 100 words
    created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = f"report_{i}.pdf"

    # File content
    file_content = generate_dummy_pdf_content(file_name)

    # Metadata dictionary (must be string values)
    metadata = {
        "owner": owner,
        "keyword": ",".join(file_keywords),
        "description": description,
        "createdDate": created_date,
        "fileName": file_name
    }

    # Upload file with metadata
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=file_content,
        Metadata=metadata
    )

    print(f"Uploaded {file_name} with metadata {metadata}")
