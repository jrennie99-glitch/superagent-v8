"""
Web Dashboard Module
Provides API endpoints for the interactive web dashboard
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    owner_id: str
    status: str  # draft, active, archived
    team_id: Optional[str] = None


class DashboardAPI:
    """Web Dashboard API"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.projects: Dict[str, Project] = {}
        self.teams: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self.activity_log: List[Dict] = []
    
    async def create_project(
        self,
        name: str,
        description: str,
        owner_id: str,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project"""
        
        try:
            project_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            project = Project(
                id=project_id,
                name=name,
                description=description,
                created_at=now,
                updated_at=now,
                owner_id=owner_id,
                status="draft",
                team_id=team_id
            )
            
            self.projects[project_id] = project
            
            # Log activity
            await self._log_activity(owner_id, "project_created", {"project_id": project_id, "name": name})
            
            print(f"✅ Project created: {name}")
            
            return {
                "success": True,
                "project": project.dict(),
                "message": f"Project '{name}' created successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_projects(self, owner_id: str) -> Dict[str, Any]:
        """Get all projects for a user"""
        
        try:
            user_projects = [
                p.dict() for p in self.projects.values()
                if p.owner_id == owner_id
            ]
            
            return {
                "success": True,
                "projects": user_projects,
                "total": len(user_projects)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects[project_id]
            
            return {
                "success": True,
                "project": project.dict(),
                "statistics": await self._get_project_stats(project_id),
                "recent_activity": await self._get_project_activity(project_id, limit=10)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_project(
        self,
        project_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update project"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects[project_id]
            
            # Update allowed fields
            for key in ["name", "description", "status"]:
                if key in kwargs:
                    setattr(project, key, kwargs[key])
            
            project.updated_at = datetime.utcnow().isoformat()
            
            await self._log_activity(project.owner_id, "project_updated", {"project_id": project_id})
            
            return {
                "success": True,
                "project": project.dict(),
                "message": "Project updated successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete project"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects.pop(project_id)
            
            await self._log_activity(project.owner_id, "project_deleted", {"project_id": project_id})
            
            return {
                "success": True,
                "message": "Project deleted successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_dashboard_stats(self, owner_id: str) -> Dict[str, Any]:
        """Get dashboard statistics"""
        
        try:
            user_projects = [p for p in self.projects.values() if p.owner_id == owner_id]
            
            stats = {
                "total_projects": len(user_projects),
                "active_projects": len([p for p in user_projects if p.status == "active"]),
                "draft_projects": len([p for p in user_projects if p.status == "draft"]),
                "archived_projects": len([p for p in user_projects if p.status == "archived"]),
                "total_deployments": 0,  # Would be calculated from database
                "total_team_members": 0,  # Would be calculated from database
                "recent_activity": await self._get_user_activity(owner_id, limit=5),
            }
            
            return {
                "success": True,
                "statistics": stats
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_team(
        self,
        name: str,
        owner_id: str,
        members: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a team"""
        
        try:
            team_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            team = {
                "id": team_id,
                "name": name,
                "owner_id": owner_id,
                "members": members or [owner_id],
                "created_at": now,
                "updated_at": now,
                "permissions": {
                    "owner": ["read", "write", "delete", "invite", "manage_roles"],
                    "admin": ["read", "write", "delete", "invite"],
                    "member": ["read", "write"],
                    "viewer": ["read"],
                }
            }
            
            self.teams[team_id] = team
            
            await self._log_activity(owner_id, "team_created", {"team_id": team_id, "name": name})
            
            return {
                "success": True,
                "team": team,
                "message": f"Team '{name}' created successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def invite_team_member(
        self,
        team_id: str,
        user_email: str,
        role: str = "member"
    ) -> Dict[str, Any]:
        """Invite member to team"""
        
        try:
            if team_id not in self.teams:
                return {"success": False, "error": "Team not found"}
            
            team = self.teams[team_id]
            
            # In production, send email invitation
            invitation = {
                "id": str(uuid.uuid4()),
                "team_id": team_id,
                "email": user_email,
                "role": role,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            }
            
            return {
                "success": True,
                "invitation": invitation,
                "message": f"Invitation sent to {user_email}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_team_members(self, team_id: str) -> Dict[str, Any]:
        """Get team members"""
        
        try:
            if team_id not in self.teams:
                return {"success": False, "error": "Team not found"}
            
            team = self.teams[team_id]
            
            return {
                "success": True,
                "members": team.get("members", []),
                "total": len(team.get("members", []))
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def deploy_project(
        self,
        project_id: str,
        target: str = "railway"
    ) -> Dict[str, Any]:
        """Deploy project"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.projects[project_id]
            
            deployment = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "target": target,
                "status": "deploying",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://{project.name.lower()}.{target}.app",
            }
            
            await self._log_activity(project.owner_id, "deployment_started", {
                "project_id": project_id,
                "target": target
            })
            
            return {
                "success": True,
                "deployment": deployment,
                "message": f"Deployment to {target} started"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_deployment_history(self, project_id: str) -> Dict[str, Any]:
        """Get deployment history"""
        
        try:
            # In production, fetch from database
            deployments = [
                {
                    "id": str(uuid.uuid4()),
                    "project_id": project_id,
                    "target": "railway",
                    "status": "success",
                    "created_at": datetime.utcnow().isoformat(),
                    "url": "https://example.railway.app",
                }
            ]
            
            return {
                "success": True,
                "deployments": deployments,
                "total": len(deployments)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_project_settings(self, project_id: str) -> Dict[str, Any]:
        """Get project settings"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            settings = {
                "project_id": project_id,
                "environment_variables": {},
                "deployment_targets": ["railway", "render", "fly.io", "vercel"],
                "notifications": {
                    "deployment_success": True,
                    "deployment_failure": True,
                    "team_invitations": True,
                },
                "git_integration": {
                    "enabled": False,
                    "repository": None,
                },
                "api_keys": [],
            }
            
            return {
                "success": True,
                "settings": settings
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_project_settings(
        self,
        project_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update project settings"""
        
        try:
            if project_id not in self.projects:
                return {"success": False, "error": "Project not found"}
            
            # In production, save to database
            await self._log_activity(
                self.projects[project_id].owner_id,
                "settings_updated",
                {"project_id": project_id}
            )
            
            return {
                "success": True,
                "message": "Settings updated successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get project statistics"""
        
        return {
            "total_deployments": 5,
            "successful_deployments": 4,
            "failed_deployments": 1,
            "total_team_members": 3,
            "last_deployment": datetime.utcnow().isoformat(),
        }
    
    async def _get_project_activity(self, project_id: str, limit: int = 10) -> List[Dict]:
        """Get project activity"""
        
        return [
            {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "action": "deployment_success",
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Deployment to Railway completed successfully",
            }
        ]
    
    async def _get_user_activity(self, owner_id: str, limit: int = 5) -> List[Dict]:
        """Get user activity"""
        
        return [
            {
                "id": str(uuid.uuid4()),
                "user_id": owner_id,
                "action": "project_created",
                "timestamp": datetime.utcnow().isoformat(),
                "details": "Created new project",
            }
        ]
    
    async def _log_activity(self, user_id: str, action: str, details: Dict) -> None:
        """Log activity"""
        
        activity = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.activity_log.append(activity)


# Global instance
dashboard_api = DashboardAPI()
