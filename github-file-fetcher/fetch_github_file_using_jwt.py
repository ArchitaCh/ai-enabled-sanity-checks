import os
from dotenv import load_dotenv
from github import Github, Auth
from github.GithubException import GithubException, BadCredentialsException

# 4. Secure Private Key Storage
# In a production cloud environment (AWS/Azure), you would fetch the private key 
# from Secrets Manager, Key Vault, etc. instead of an environment variable.
def get_secret(secret_name: str) -> str:
    # Simulate fetching a secret from a secure vault. Fallback to env vars.
    secret = os.getenv(secret_name)
    if not secret:
        raise ValueError(f"Secret '{secret_name}' not found. Please ensure it is set.")
    return secret.replace('\\n', '\n')

def main():
    load_dotenv()

    try:
        app_id = int(get_secret("GITHUB_APP_ID"))
        private_key = get_secret("GITHUB_PRIVATE_KEY")
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # 1 & 3: Token Caching & Abstraction using PyGithub
    # Auth.AppAuth automatically handles JWT creation, token rotation, and caching.
    try:
        print("Authenticating as GitHub App...")
        app_auth = Auth.AppAuth(app_id, private_key)
        
        # Create a GitHub client as the App to find installations
        app_client = Github(auth=app_auth)
        
        # 5. Fetch all repositories the App has access to across all installations
        print("Fetching all installations for the GitHub App...")
        installations = app_client.get_app().get_installations()
        
        if installations.totalCount == 0:
            print("No installations found for this App. Please install it on a repository or organization.")
            return

        # Iterate over all accounts/organizations where the App is installed
        for installation in installations:
            print(f"\n--- Processing Installation ID: {installation.id} (Account: {installation.account.login}) ---")
            
            # Create an installation-specific client. 
            # This securely gets the installation token and caches it for 1 hour!
            inst_auth = Auth.AppInstallationAuth(app_auth, installation.id)
            inst_client = Github(auth=inst_auth)
            
            try:
                # Get all repositories accessible by this specific installation
                # Note: `installation.get_repos()` fetches the repositories the app is granted access to.
                repos = installation.get_repos()
                
                if repos.totalCount == 0:
                    print("  No repositories accessible for this installation.")
                    continue
                
                for repo in repos:
                    print(f"  * Repository found: {repo.full_name}")
                    
                    # Example connection: Attempt to fetch a file from the repository
                    file_path = "README.md"
                    try:
                        # Fetch the file using PyGithub objects
                        # This effectively 'connects' to it and fetches the content
                        file_content = inst_client.get_repo(repo.full_name).get_contents(file_path)
                        print(f"    -> Successfully fetched '{file_path}': {file_content.size} bytes.")
                        # print(file_content.decoded_content.decode('utf-8')) # Optional preview
                        
                    except GithubException as e:
                        # 2. Error Handling for specific GitHub API errors
                        if e.status == 404:
                            print(f"    -> '{file_path}' not found in {repo.full_name}.")
                        elif e.status == 403:
                            print(f"    -> Permission denied (403) accessing '{file_path}' in {repo.full_name}. Ensure App permissions allow reading repository contents.")
                        else:
                            print(f"    -> Error fetching '{file_path}' from {repo.full_name}: {e.data.get('message', e)}")

            except GithubException as e:
                 print(f"  -> Error accessing repositories for installation {installation.id}: {e.data.get('message', e)}")
                
    except BadCredentialsException:
        print("\nError: Authentication failed. Invalid App ID or Private Key.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
