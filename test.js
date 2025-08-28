import {
  S3Client,
  CreateBucketCommand,
  CreateBucketMetadataConfigurationCommand
} from "@aws-sdk/client-s3";
import { STSClient, GetCallerIdentityCommand } from "@aws-sdk/client-sts";

// AWS clients
const region = process.env.AWS_REGION || "us-east-1";
const s3 = new S3Client({ region });
const sts = new STSClient({ region });

const BUCKET = "my-metadata-demo-bucket-12345678"; // Must be globally unique

async function lambdaHandler() {
  try {
    // Get Account ID
    const identity = await sts.send(new GetCallerIdentityCommand({}));
    const ACCOUNT_ID = identity.Account;
    console.log(`Account ID: ${ACCOUNT_ID}`);

    // Create the bucket (if not exists)
    const bucketParams = {
      Bucket: BUCKET,
      ...(region !== "us-east-1" && {
        CreateBucketConfiguration: { LocationConstraint: region },
      }),
    };

    try {
      await s3.send(new CreateBucketCommand(bucketParams));
      console.log(`Bucket created: ${BUCKET}`);
    } catch (err) {
      if (err.Code === "BucketAlreadyOwnedByYou") {
        console.log(`ℹBucket already exists: ${BUCKET}`);
      } else {
        console.error("Error creating bucket:", err);
      }
    }

    // Configure S3 Metadata
    const metadataConfig = {
      Bucket: BUCKET,
      MetadataConfiguration: {
        JournalTableConfiguration: {
          RecordExpiration: { Expiration: "ENABLED", Days: 30 },
          EncryptionConfiguration: { SseAlgorithm: "AES256" },
        },
        InventoryTableConfiguration: {
          ConfigurationState: "ENABLED",
          EncryptionConfiguration: { SseAlgorithm: "AES256" },
        },
      },
    };

    try {
      await s3.send(new CreateBucketMetadataConfigurationCommand(metadataConfig));
      console.log("S3 Metadata configuration created");
    } catch (err) {
      console.error("Error creating metadata configuration:", err);
    }
  } catch (err) {
    console.error("Lambda handler failed:", err);
  }
}

lambdaHandler()
