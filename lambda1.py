import json
import sys
import io
import traceback
import os
import subprocess
import importlib.util

TMP_DIR = "/tmp/python_libs"

class DualWriter(io.StringIO):
    """Writes to both buffer (for response) and stdout (for CloudWatch logs)"""
    def __init__(self, buffer, stdout):
        super().__init__()
        self.buffer = buffer
        self.stdout = stdout

    def write(self, s):
        self.buffer.write(s)
        self.stdout.write(s)
        self.stdout.flush()

    def flush(self):
        self.buffer.flush()
        self.stdout.flush()


def install_package(package):
    """Install pip package into /tmp if not already installed"""
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR, exist_ok=True)

    if TMP_DIR not in sys.path:
        sys.path.insert(0, TMP_DIR)

    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--target", TMP_DIR, package
    ])
    print(f"✅ Installed {package}")


def lambda_handler(event, context):
    """
    Payload format:
    {
        "requirements": ["requests"],
        "script": "import requests\nprint('Fetching...')\nprint(requests.get('https://api.github.com').status_code)"
    }
    """
    script = event.get("script", "")
    requirements = event.get("requirements", [])
    tmp_path = "/tmp/user_script.py"

    # Step 1: Install dependencies
    for pkg in requirements:
        try:
            install_package(pkg)
        except Exception as e:
            return {"statusCode": 500, "body": json.dumps({"success": False, "error": str(e)})}

    # Step 2: Save user script
    with open(tmp_path, "w") as f:
        f.write(script)

    # Step 3: Setup dual logger
    buffer = io.StringIO()
    sys.stdout = DualWriter(buffer, sys.__stdout__)  # realtime logs + capture

    result = {"success": True, "output": "", "error": ""}

    try:
        # Step 4: Load and execute script
        spec = importlib.util.spec_from_file_location("user_script", tmp_path)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        # Optional: call main()
        if hasattr(user_module, "main"):
            user_module.main()

    except Exception:
        result["success"] = False
        result["error"] = traceback.format_exc()

    finally:
        # Restore stdout
        sys.stdout = sys.__stdout__

    # Step 5: Store captured logs
    result["output"] = buffer.getvalue()

    return {"statusCode": 200, "body": json.dumps(result)}
