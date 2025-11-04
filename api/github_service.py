"""
GitHub Integration Service for SuperAgent
Handles Git operations, repository creation, and one-click deployments
Uses Replit GitHub connection for authentication
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import json
import requests


class GitHubService:
    """Service for GitHub integration and Git operations"""
    
    def __init__(self):
        self.connection_settings = None
        
    def _get_access_token(self) -> Optional[str]:
        """
        Get GitHub access token - works both on and off Replit
        Priority: 1) Replit OAuth connection 2) Manual GITHUB_TOKEN env var
        """
        try:
            # Method 1: Try Replit GitHub connection (OAuth - automatic, secure)
            # Check if connection is still valid
            if (self.connection_settings and 
                self.connection_settings.get('settings', {}).get('expires_at')):
                from datetime import datetime
                expires_at = datetime.fromisoformat(
                    self.connection_settings['settings']['expires_at'].replace('Z', '+00:00')
                )
                if expires_at.timestamp() > datetime.now().timestamp():
                    return self.connection_settings['settings'].get('access_token')
            
            # Fetch fresh Replit connection
            hostname = os.getenv('REPLIT_CONNECTORS_HOSTNAME')
            x_replit_token = None
            
            if os.getenv('REPL_IDENTITY'):
                x_replit_token = f"repl {os.getenv('REPL_IDENTITY')}"
            elif os.getenv('WEB_REPL_RENEWAL'):
                x_replit_token = f"depl {os.getenv('WEB_REPL_RENEWAL')}"
            
            if x_replit_token and hostname:
                response = requests.get(
                    f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github",
                    headers={
                        'Accept': 'application/json',
                        'X_REPLIT_TOKEN': x_replit_token
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    if items:
                        self.connection_settings = items[0]
                        settings = self.connection_settings.get('settings', {})
                        token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
                        if token:
                            print("✓ Using Replit GitHub OAuth connection")
                            return token
            
            # Method 2: Fallback to manual environment variable (for non-Replit use)
            manual_token = os.getenv('GITHUB_TOKEN')
            if manual_token:
                print("✓ Using manual GITHUB_TOKEN from environment")
                return manual_token
            
            return None
        except Exception as e:
            print(f"Error getting GitHub access token: {e}")
            # Try fallback even if Replit connection fails
            return os.getenv('GITHUB_TOKEN')
    
    def _get_username(self) -> Optional[str]:
        """
        Get GitHub username - works both on and off Replit
        Priority: 1) Replit connection 2) Manual env var 3) Fetch from GitHub API
        """
        # Try Replit connection first
        if self.connection_settings:
            username = self.connection_settings.get('settings', {}).get('username')
            if username:
                return username
        
        # Try manual environment variable
        manual_username = os.getenv('GITHUB_USERNAME')
        if manual_username:
            return manual_username
        
        # Fetch from GitHub API if we have a token but no username
        token = self._get_access_token()
        if token:
            try:
                response = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json"
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return user_data.get('login')
            except Exception as e:
                print(f"Error fetching GitHub username: {e}")
        
        return None
        
    def is_configured(self) -> bool:
        """Check if GitHub is properly configured (needs both token AND username)"""
        token = self._get_access_token()
        username = self._get_username()
        return bool(token and username)
    
    def init_repo(self, project_path: Path) -> bool:
        """Initialize a Git repository in the project directory"""
        try:
            username = self._get_username() or "superagent"
            
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Configure user
            subprocess.run(
                ["git", "config", "user.email", f"{username}@users.noreply.github.com"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", username],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing repository: {e}")
            return False
    
    def commit_changes(self, project_path: Path, message: str = "Initial commit from SuperAgent") -> bool:
        """Commit all changes in the project"""
        try:
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False
    
    def create_github_repo(self, repo_name: str, private: bool = False) -> Optional[str]:
        """Create a new GitHub repository"""
        token = self._get_access_token()
        if not token:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            data = {
                "name": repo_name,
                "private": private,
                "auto_init": False
            }
            
            response = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                return repo_data.get("clone_url")
            else:
                print(f"Error creating repository: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating GitHub repository: {e}")
            return None
    
    def push_to_github(self, project_path: Path, repo_url: str, branch: str = "main") -> bool:
        """Push project to GitHub repository"""
        try:
            token = self._get_access_token()
            username = self._get_username() or "oauth2"
            
            if not token:
                return False
            
            # Add authenticated remote
            auth_url = repo_url.replace(
                "https://",
                f"https://{username}:{token}@"
            )
            
            subprocess.run(
                ["git", "remote", "add", "origin", auth_url],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Rename branch to main if needed
            subprocess.run(
                ["git", "branch", "-M", branch],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Push
            subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error pushing to GitHub: {e}")
            return False
    
    def one_click_deploy(
        self,
        project_path: Path,
        repo_name: str,
        commit_message: str = "Deploy from SuperAgent",
        private: bool = False
    ) -> Dict[str, any]:
        """One-click deployment to GitHub"""
        
        result = {
            "success": False,
            "repo_url": None,
            "error": None,
            "steps": []
        }
        
        # Step 1: Initialize repo
        if self.init_repo(project_path):
            result["steps"].append("✓ Initialized Git repository")
        else:
            result["error"] = "Failed to initialize repository"
            return result
        
        # Step 2: Commit changes
        if self.commit_changes(project_path, commit_message):
            result["steps"].append("✓ Committed changes")
        else:
            result["error"] = "Failed to commit changes"
            return result
        
        # Step 3: Create GitHub repo
        repo_url = self.create_github_repo(repo_name, private)
        if repo_url:
            result["repo_url"] = repo_url.replace(".git", "")  # Clean URL
            result["steps"].append(f"✓ Created GitHub repository: {repo_name}")
        else:
            result["error"] = "Failed to create GitHub repository"
            return result
        
        # Step 4: Push to GitHub
        if self.push_to_github(project_path, repo_url):
            result["steps"].append("✓ Pushed to GitHub")
            result["success"] = True
        else:
            result["error"] = "Failed to push to GitHub"
            return result
        
        return result
    
    def deploy_to_platform(
        self,
        platform: str,
        project_path: Path,
        repo_url: str
    ) -> Dict[str, str]:
        """Generate deployment instructions for various platforms"""
        
        instructions = {
            "vercel": {
                "name": "Vercel",
                "steps": [
                    "1. Visit https://vercel.com/new",
                    f"2. Import your GitHub repository: {repo_url}",
                    "3. Configure build settings (auto-detected)",
                    "4. Click 'Deploy'",
                    "5. Your app will be live in minutes!"
                ],
                "cli": f"vercel --prod"
            },
            "railway": {
                "name": "Railway",
                "steps": [
                    "1. Visit https://railway.app/new",
                    f"2. Select 'Deploy from GitHub repo'",
                    f"3. Choose: {repo_url}",
                    "4. Railway will auto-detect and deploy",
                    "5. Get your live URL from the dashboard"
                ],
                "cli": "railway up"
            },
            "render": {
                "name": "Render",
                "steps": [
                    "1. Visit https://dashboard.render.com/select-repo",
                    f"2. Connect your GitHub account and select: {repo_url}",
                    "3. Choose 'Web Service'",
                    "4. Configure build command (auto-detected from Dockerfile)",
                    "5. Click 'Create Web Service'"
                ],
                "cli": "render deploy"
            },
            "fly": {
                "name": "Fly.io",
                "steps": [
                    "1. Install Fly CLI: curl -L https://fly.io/install.sh | sh",
                    "2. Login: fly auth login",
                    f"3. Deploy: fly launch (in project directory)",
                    "4. Fly will detect Dockerfile and deploy automatically",
                    "5. Get URL: fly status"
                ],
                "cli": "fly deploy"
            },
            "replit": {
                "name": "Replit Deployments",
                "steps": [
                    "1. Import your GitHub repo to Replit",
                    "2. Click 'Deploy' button in Replit",
                    "3. Choose deployment type (Autoscale/VM)",
                    "4. Configure environment variables",
                    "5. Click 'Deploy' - live instantly!"
                ],
                "cli": "Use Replit UI"
            }
        }
        
        return instructions.get(platform, {
            "name": "Custom Platform",
            "steps": ["Use your platform's GitHub integration"],
            "cli": "See platform documentation"
        })
