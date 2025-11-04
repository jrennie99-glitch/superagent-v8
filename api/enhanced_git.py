"""
Enhanced Git Operations - Full git functionality
"""
import subprocess
from pathlib import Path
from typing import Dict, List

class EnhancedGit:
    """Enhanced git operations beyond basic commit"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
    
    def get_diff(self, staged: bool = False) -> Dict:
        """Get git diff"""
        try:
            cmd = ['git', 'diff']
            if staged:
                cmd.append('--staged')
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": True,
                "diff": result.stdout,
                "staged": staged
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_branches(self) -> Dict:
        """List all branches"""
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            branches = [
                line.strip().replace('* ', '').replace('remotes/origin/', '')
                for line in result.stdout.split('\n')
                if line.strip()
            ]
            
            return {
                "success": True,
                "branches": list(set(branches)),
                "total": len(branches)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_log(self, max_count: int = 10) -> Dict:
        """Get git commit history"""
        try:
            result = subprocess.run(
                ['git', 'log', f'--max-count={max_count}', '--pretty=format:%H|%an|%ae|%ad|%s'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            commits = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
            
            return {
                "success": True,
                "commits": commits,
                "total": len(commits)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict:
        """Get detailed git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            files = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                
                status = line[:2]
                filename = line[3:]
                
                if 'M' in status:
                    files["modified"].append(filename)
                elif 'A' in status:
                    files["added"].append(filename)
                elif 'D' in status:
                    files["deleted"].append(filename)
                elif '?' in status:
                    files["untracked"].append(filename)
            
            return {
                "success": True,
                "files": files,
                "total_changes": sum(len(v) for v in files.values())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
