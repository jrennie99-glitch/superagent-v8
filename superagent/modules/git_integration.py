"""Git integration module for version control."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import git
import structlog

logger = structlog.get_logger()


class GitManager:
    """Git integration for automated version control."""
    
    def __init__(self, project_path: Path):
        """Initialize Git manager.
        
        Args:
            project_path: Path to project
        """
        self.project_path = project_path
        self.repo: Optional[git.Repo] = None
        
    def initialize(self) -> bool:
        """Initialize Git repository.
        
        Returns:
            True if successful
        """
        try:
            if (self.project_path / ".git").exists():
                self.repo = git.Repo(self.project_path)
                logger.info("Git repository loaded")
            else:
                self.repo = git.Repo.init(self.project_path)
                logger.info("Git repository initialized")
            
            return True
        except Exception as e:
            logger.error(f"Git initialization failed: {e}")
            return False
    
    def add_files(self, patterns: List[str] = None) -> bool:
        """Add files to staging.
        
        Args:
            patterns: File patterns (default: all files)
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            if patterns:
                for pattern in patterns:
                    self.repo.index.add(pattern)
            else:
                self.repo.git.add(A=True)
            
            logger.info("Files added to staging")
            return True
        except Exception as e:
            logger.error(f"Git add failed: {e}")
            return False
    
    def commit(self, message: str, author: Optional[str] = None) -> bool:
        """Commit staged changes.
        
        Args:
            message: Commit message
            author: Author name and email
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            if author:
                self.repo.index.commit(message, author=author)
            else:
                self.repo.index.commit(message)
            
            logger.info(f"Committed: {message}")
            return True
        except Exception as e:
            logger.error(f"Git commit failed: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch.
        
        Args:
            branch_name: Name of the branch
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            self.repo.create_head(branch_name)
            logger.info(f"Branch created: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"Branch creation failed: {e}")
            return False
    
    def checkout(self, branch_name: str) -> bool:
        """Checkout a branch.
        
        Args:
            branch_name: Name of the branch
            
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            self.repo.git.checkout(branch_name)
            logger.info(f"Checked out: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"Checkout failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get repository status.
        
        Returns:
            Status information
        """
        if not self.repo:
            return {"error": "No repository"}
        
        try:
            return {
                "branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked": self.repo.untracked_files,
                "modified": [item.a_path for item in self.repo.index.diff(None)],
                "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}
    
    def get_commit_history(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """Get commit history.
        
        Args:
            max_count: Maximum number of commits
            
        Returns:
            List of commits
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append({
                    "sha": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat()
                })
            return commits
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    def auto_commit_changes(self, message: str = "Auto-commit by SuperAgent") -> bool:
        """Automatically add and commit all changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        if not self.initialize():
            return False
        
        if not self.add_files():
            return False
        
        return self.commit(message)





