def generate_client_snippet(app_id, api_url="http://localhost:5000"):
    """
    Generates a Python client script for license validation.

    Args:
        app_id (str): The ID of the application.
        api_url (str): The base URL of the KeyPilot API.

    Returns:
        str: The complete Python client code.
    """
    snippet = f"""import requests
import subprocess
import platform
import uuid
import jwt
import json
import sys

# Configuration
API_URL = "{api_url}"
APP_ID = "{app_id}"

def get_hwid():
    \"\"\"
    Retrieves the Hardware ID (HWID) of the machine.
    Uses wmic on Windows, and falls back to uuid.getnode() on other platforms.
    \"\"\"
    try:
        if platform.system() == "Windows":
            cmd = "wmic csproduct get uuid"
            # Run command, decode output, split by newline and take the second line (the UUID)
            uuid_str = subprocess.check_output(cmd, shell=True).decode().split('\\n')[1].strip()
            return uuid_str
        else:
            # Fallback for Linux/Mac
            return str(uuid.getnode())
    except Exception:
        return str(uuid.getnode())

def validate_license(license_key):
    \"\"\"
    Validates the license key against the KeyPilot API.
    \"\"\"
    hwid = get_hwid()
    url = f"{{API_URL}}/api/v1/license/validate"

    payload = {{
        "app_id": APP_ID,
        "license_key": license_key,
        "hwid": hwid
    }}

    print(f"Validating license for HWID: {{hwid}}...")

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get('token')

            if token:
                # Decode without verification (client doesn't have the secret key)
                # The server's 200 OK response is the primary validation.
                decoded = jwt.decode(token, options={{"verify_signature": False}})
                print(f"License Valid! Data: {{decoded}}")
                return True, decoded
            else:
                print("Error: No token received.")
                return False, None
        else:
            error_msg = response.json().get('error', 'Unknown error')
            print(f"License Invalid: {{error_msg}}")
            return False, None

    except Exception as e:
        print(f"Connection Error: {{e}}")
        return False, None

if __name__ == "__main__":
    print("--- KeyPilot Client ---")
    if len(sys.argv) < 2:
        print("Usage: python client_snippet.py <license_key>")
        sys.exit(1)

    key = sys.argv[1]
    is_valid, data = validate_license(key)

    if is_valid:
        sys.exit(0)
    else:
        sys.exit(1)
"""
    return snippet
