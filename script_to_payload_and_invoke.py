import json
import sys
import os
import boto3

def script_to_payload(script_path):
    """Read Python script and wrap it into Lambda payload JSON"""
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    with open(script_path, "r") as f:
        code = f.read()

    return {"script": code}


def save_payload(payload, output_path):
    with open(output_path, "w") as out:
        json.dump(payload, out)
    print(f"Payload saved to {output_path}")


def invoke_lambda(function_name, payload, region="us-east-1"):
    """Invoke AWS Lambda with given payload"""
    client = boto3.client("lambda", region_name=region)

    response = client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",  # sync execution
        Payload=json.dumps(payload)
    )

    result = response["Payload"].read().decode("utf-8")
    print("✅ Lambda Response:")
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_to_payload_and_invoke.py <script.py> [payload.json] [lambda_function_name]")
        sys.exit(1)

    script_file = sys.argv[1]
    payload = script_to_payload(script_file)

    # Option 1: Save payload to file
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("arn:"):
        output_file = sys.argv[2]
        save_payload(payload, output_file)

    # Option 2: Directly invoke Lambda
    if len(sys.argv) >= 3:
        function_name = sys.argv[-1]
        if function_name.startswith("arn:") or not sys.argv[-1].endswith(".json"):
            region = os.environ.get("AWS_REGION", "us-east-1")
            invoke_lambda(function_name, payload, region)
