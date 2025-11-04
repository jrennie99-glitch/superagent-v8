"""Deployment engine for multiple cloud platforms."""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from superagent.core.config import DeploymentConfig

logger = structlog.get_logger()


class DeploymentEngine:
    """Multi-platform deployment engine."""
    
    def __init__(self, config: DeploymentConfig):
        """Initialize deployment engine.
        
        Args:
            config: Deployment configuration
        """
        self.config = config
        
    async def deploy(self, project_path: Path, 
                    platform: str = "heroku") -> Dict[str, Any]:
        """Deploy project to specified platform.
        
        Args:
            project_path: Path to project
            platform: Deployment platform
            
        Returns:
            Deployment results
        """
        logger.info("Deploying project", platform=platform, path=str(project_path))
        
        if platform == "heroku":
            return await self._deploy_heroku(project_path)
        elif platform == "vercel":
            return await self._deploy_vercel(project_path)
        elif platform == "aws":
            return await self._deploy_aws(project_path)
        elif platform == "gcp":
            return await self._deploy_gcp(project_path)
        elif platform == "railway":
            return await self._deploy_railway(project_path)
        elif platform == "render":
            return await self._deploy_render(project_path)
        elif platform == "flyio":
            return await self._deploy_flyio(project_path)
        elif platform == "koyeb":
            return await self._deploy_koyeb(project_path)
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    async def _deploy_heroku(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Heroku.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Check if Heroku CLI is installed
            result = subprocess.run(
                ["heroku", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Heroku CLI not installed"}
            
            # Create Procfile if needed
            await self._create_procfile(project_path)
            
            # Initialize git if needed
            if not (project_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=project_path)
                subprocess.run(["git", "add", "."], cwd=project_path)
                subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path)
            
            # Create Heroku app
            app_name = project_path.name.replace("_", "-")
            result = subprocess.run(
                ["heroku", "create", app_name],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Deploy
            result = subprocess.run(
                ["git", "push", "heroku", "main"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                "success": result.returncode == 0,
                "platform": "heroku",
                "url": f"https://{app_name}.herokuapp.com",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"Heroku deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_vercel(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Vercel.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            result = subprocess.run(
                ["vercel", "--prod", "--yes"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                "success": result.returncode == 0,
                "platform": "vercel",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"Vercel deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_aws(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to AWS (simplified).
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        # This would require more complex AWS setup
        logger.info("AWS deployment requires additional configuration")
        return {
            "success": False,
            "error": "AWS deployment requires manual setup",
            "instructions": "Use AWS Elastic Beanstalk or Lambda for deployment"
        }
    
    async def _deploy_gcp(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Google Cloud Platform.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Create app.yaml if needed
            await self._create_app_yaml(project_path)
            
            result = subprocess.run(
                ["gcloud", "app", "deploy", "--quiet"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            return {
                "success": result.returncode == 0,
                "platform": "gcp",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"GCP deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_procfile(self, project_path: Path):
        """Create Procfile for Heroku.
        
        Args:
            project_path: Project path
        """
        procfile = project_path / "Procfile"
        if not procfile.exists():
            # Detect app type
            if (project_path / "app.py").exists():
                procfile.write_text("web: gunicorn app:app")
            elif (project_path / "main.py").exists():
                procfile.write_text("web: python main.py")
            else:
                procfile.write_text("web: python server.py")
    
    async def _create_app_yaml(self, project_path: Path):
        """Create app.yaml for GCP.
        
        Args:
            project_path: Project path
        """
        app_yaml = project_path / "app.yaml"
        if not app_yaml.exists():
            content = """runtime: python39
entrypoint: gunicorn -b :$PORT app:app

instance_class: F2

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
"""
            app_yaml.write_text(content)
    
    async def _deploy_railway(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Railway.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Check if Railway CLI is installed
            result = subprocess.run(
                ["railway", "version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Railway CLI not installed"}
            
            # Initialize Railway project if needed
            if not (project_path / "railway.json").exists():
                subprocess.run(
                    ["railway", "init"],
                    cwd=project_path,
                    input="y\n",
                    text=True
                )
            
            # Deploy to Railway
            result = subprocess.run(
                ["railway", "up", "--detach"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Get deployment URL
            url_result = subprocess.run(
                ["railway", "domain"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            deployment_url = url_result.stdout.strip() if url_result.returncode == 0 else None
            
            return {
                "success": result.returncode == 0,
                "platform": "railway",
                "url": deployment_url,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"Railway deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_render(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Render.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Create render.yaml if needed
            await self._create_render_yaml(project_path)
            
            # Initialize git if needed
            if not (project_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=project_path)
                subprocess.run(["git", "add", "."], cwd=project_path)
                subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path)
            
            # Deploy using Render CLI or API
            # Note: Render primarily uses GitHub integration, so this is a simplified version
            return {
                "success": True,
                "platform": "render",
                "message": "Render deployment configured. Connect your GitHub repository at https://dashboard.render.com",
                "instructions": [
                    "1. Push your code to GitHub",
                    "2. Go to https://dashboard.render.com",
                    "3. Create a new Web Service",
                    "4. Connect your GitHub repository",
                    "5. Render will auto-deploy using render.yaml"
                ]
            }
        except Exception as e:
            logger.error(f"Render deployment setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_flyio(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Fly.io.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Check if Fly CLI is installed
            result = subprocess.run(
                ["flyctl", "version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Fly CLI (flyctl) not installed"}
            
            # Initialize Fly app if needed
            if not (project_path / "fly.toml").exists():
                launch_result = subprocess.run(
                    ["flyctl", "launch", "--generate-name", "--no-deploy", "--yes"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if launch_result.returncode != 0:
                    return {
                        "success": False,
                        "error": "Failed to initialize Fly.io app",
                        "output": launch_result.stdout,
                        "stderr": launch_result.stderr
                    }
            
            # Deploy to Fly.io
            result = subprocess.run(
                ["flyctl", "deploy"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Get app info
            info_result = subprocess.run(
                ["flyctl", "info"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Extract URL from info output
            deployment_url = None
            if "Hostname" in info_result.stdout:
                for line in info_result.stdout.split("\n"):
                    if "Hostname" in line:
                        deployment_url = f"https://{line.split()[-1]}"
                        break
            
            return {
                "success": result.returncode == 0,
                "platform": "flyio",
                "url": deployment_url,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"Fly.io deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_koyeb(self, project_path: Path) -> Dict[str, Any]:
        """Deploy to Koyeb.
        
        Args:
            project_path: Project path
            
        Returns:
            Deployment result
        """
        try:
            # Check if Koyeb CLI is installed
            result = subprocess.run(
                ["koyeb", "version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Koyeb CLI not installed"}
            
            # Koyeb requires a remote Git repository or Docker image
            # Provide instructions for manual deployment
            return {
                "success": False,
                "platform": "koyeb",
                "error": "Koyeb requires manual setup via GitHub integration",
                "message": "Koyeb deployment requires manual configuration. Follow these steps:",
                "instructions": [
                    "1. Push your code to a GitHub repository",
                    "2. Go to https://app.koyeb.com",
                    "3. Click 'Create Service'",
                    "4. Select 'GitHub' as source",
                    "5. Connect your repository",
                    "6. Configure build/run commands (see below)",
                    "7. Koyeb will auto-deploy your app"
                ],
                "build_command": "pip install -r requirements.txt" if (project_path / "requirements.txt").exists() else "npm install",
                "run_command": "python main.py" if (project_path / "main.py").exists() else "python app.py" if (project_path / "app.py").exists() else "npm start"
            }
        except Exception as e:
            logger.error(f"Koyeb deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_render_yaml(self, project_path: Path):
        """Create render.yaml for Render deployment.
        
        Args:
            project_path: Project path
        """
        render_yaml = project_path / "render.yaml"
        if not render_yaml.exists():
            # Detect app type
            if (project_path / "requirements.txt").exists():
                content = """services:
  - type: web
    name: superagent-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
"""
            elif (project_path / "package.json").exists():
                content = """services:
  - type: web
    name: superagent-app
    env: node
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_VERSION
        value: 20
"""
            else:
                content = """services:
  - type: web
    name: superagent-app
    env: docker
    dockerfilePath: ./Dockerfile
"""
            render_yaml.write_text(content)





