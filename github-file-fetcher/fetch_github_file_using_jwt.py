import jwt
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
# The private key content should be in your .env or a file
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY").replace('\\n', '\n') 
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")

def get_installation_access_token():
    # 1. Generate JWT
    payload = {
        "iat": int(time.time()) - 60,  # Issued 60s ago to avoid clock drift
        "exp": int(time.time()) + (10 * 60), # Max 10 min expiry
        "iss": APP_ID
    }
    
    encoded_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

    # 2. Exchange JWT for Installation Access Token
    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]

def fetch_file_with_app(owner, repo, file_path):
    token = get_installation_access_token()
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    headers = {
        "Authorization": f"token {token}", # Note: apps often use 'token' or 'Bearer'
        "Accept": "application/vnd.github.v3.raw"
    }
    
    res = requests.get(url, headers=headers)
    print(res.text)

# Usage
fetch_file_with_app("owner-name", "repo-name", "path/to/file.py")