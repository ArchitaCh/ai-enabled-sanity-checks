import requests
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def fetch_github_file(owner, repo, file_path, token):
    """
    Fetches the raw content of a specific file from a GitHub repository.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        
        print(f"--- Successfully fetched: {file_path} ---\n")
        print(response.text)
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"Error: File '{file_path}' not found in {owner}/{repo}.")
        elif response.status_code == 401:
            print("Error: Authentication failed. Please check your GitHub Token.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    # Fetch configuration from environment variables
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = os.getenv("REPO_OWNER")
    REPO_NAME = os.getenv("REPO_NAME")
    FILE_PATH = os.getenv("FILE_PATH")

    # Validate that the necessary variables are present
    if not all([GITHUB_TOKEN, REPO_OWNER, REPO_NAME, FILE_PATH]):
        print("Error: Missing required environment variables. Please check your .env file.")
    else:
        fetch_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, GITHUB_TOKEN)