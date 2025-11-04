#!/usr/bin/env python3
"""Push workspace to GitHub using OAuth connection"""
import os
import sys
import requests
import base64
from pathlib import Path

# Get GitHub token from SuperAgent service
def get_github_token():
    from api.github_service import GitHubService
    service = GitHubService()
    token = service._get_access_token()
    username = service._get_username()
    return token, username

def create_or_update_file(token, username, repo_name, file_path, content):
    """Create or update a file in GitHub repository"""
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    # Check if file exists
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get('sha')
    
    # Encode content
    encoded_content = base64.b64encode(content.encode()).decode()
    
    # Create/update file
    data = {
        "message": f"Add/update {file_path}",
        "content": encoded_content
    }
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

def main():
    print("🚀 Pushing workspace to GitHub...")
    
    # Get credentials
    token, username = get_github_token()
    if not token or not username:
        print("❌ GitHub not configured. Please connect GitHub first.")
        sys.exit(1)
    
    print(f"✓ Connected as: {username}")
    
    repo_name = "superagent-best-super-upgrade"
    
    # Files to push (important ones only)
    files_to_push = [
        "api/index.py",
        "api/advanced_agent.py",
        "api/github_service.py",
        "api/user_management.py",
        "api/project_importer.py",
        "api/context_manager.py",
        "mobile.html",
        "memory.html",
        "project-manager.html",
        "index.html",
        "replit.md",
        "SECURITY.md",
        "push_to_github.sh",
        ".gitignore",
        "README.md"
    ]
    
    print(f"\n📦 Pushing {len(files_to_push)} files to {repo_name}...")
    
    success_count = 0
    for file_path in files_to_push:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            if create_or_update_file(token, username, repo_name, file_path, content):
                print(f"  ✓ {file_path}")
                success_count += 1
            else:
                print(f"  ✗ {file_path} (failed)")
        else:
            print(f"  - {file_path} (not found)")
    
    print(f"\n✅ Successfully pushed {success_count} files!")
    print(f"🌐 View at: https://github.com/{username}/{repo_name}")

if __name__ == "__main__":
    main()
