"""Long-term memory and planning system for SuperAgent - Better than Devin."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()


class ProjectMemory:
    """Long-term project memory and planning (like Devin, but better)."""
    
    def __init__(self, db_path: str = "./superagent_memory.db"):
        """Initialize project memory database.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._init_database()
        logger.info(f"Project memory initialized: {self.db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                dependencies TEXT,
                result TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # Learnings table (what worked, what didn't)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # Code patterns table (reusable patterns)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_project(self, name: str, description: str = "") -> int:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO projects (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (name, description, now, now))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created project: {name} (ID: {project_id})")
        return project_id
    
    def add_task(self, project_id: int, description: str, priority: int = 0, 
                 dependencies: Optional[List[int]] = None) -> int:
        """Add a task to a project.
        
        Args:
            project_id: Project ID
            description: Task description
            priority: Task priority (higher = more important)
            dependencies: List of task IDs this task depends on
            
        Returns:
            Task ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        deps_json = json.dumps(dependencies or [])
        
        cursor.execute('''
            INSERT INTO tasks (project_id, description, priority, dependencies, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, description, priority, deps_json, now))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_next_tasks(self, project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get next tasks to execute based on priority and dependencies.
        
        Args:
            project_id: Project ID
            limit: Maximum number of tasks to return
            
        Returns:
            List of tasks ready to execute
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, description, priority, dependencies
            FROM tasks
            WHERE project_id = ? AND status = 'pending'
            ORDER BY priority DESC, created_at ASC
        ''', (project_id,))
        
        all_tasks = cursor.fetchall()
        conn.close()
        
        # Get completed task IDs
        completed_ids = self._get_completed_task_ids(project_id)
        
        # Filter tasks where all dependencies are complete
        ready_tasks = []
        for task_id, desc, priority, deps_json in all_tasks:
            dependencies = json.loads(deps_json)
            if all(dep_id in completed_ids for dep_id in dependencies):
                ready_tasks.append({
                    'id': task_id,
                    'description': desc,
                    'priority': priority,
                    'dependencies': dependencies
                })
                if len(ready_tasks) >= limit:
                    break
        
        return ready_tasks
    
    def _get_completed_task_ids(self, project_id: int) -> set:
        """Get IDs of all completed tasks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM tasks
            WHERE project_id = ? AND status = 'completed'
        ''', (project_id,))
        
        completed = {row[0] for row in cursor.fetchall()}
        conn.close()
        return completed
    
    def complete_task(self, task_id: int, result: Any):
        """Mark a task as completed.
        
        Args:
            task_id: Task ID
            result: Task result
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        result_json = json.dumps(result)
        
        cursor.execute('''
            UPDATE tasks
            SET status = 'completed', result = ?, completed_at = ?
            WHERE id = ?
        ''', (result_json, now, task_id))
        
        conn.commit()
        conn.close()
    
    def add_learning(self, project_id: Optional[int], category: str, 
                    content: str, success: bool):
        """Record a learning from project execution.
        
        Args:
            project_id: Project ID (None for global learning)
            category: Learning category (e.g., 'debugging', 'optimization')
            content: What was learned
            success: Whether this was a successful approach
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO learnings (project_id, category, content, success, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, category, content, success, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded learning: {category} - {content[:50]}...")
    
    def get_learnings(self, category: Optional[str] = None, 
                     success_only: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """Get relevant learnings from past projects.
        
        Args:
            category: Filter by category
            success_only: Only get successful learnings
            limit: Maximum number of learnings to return
            
        Returns:
            List of learnings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT category, content, success FROM learnings WHERE 1=1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if success_only:
            query += ' AND success = 1'
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {'category': cat, 'content': content, 'success': success}
            for cat, content, success in results
        ]
    
    def save_code_pattern(self, name: str, code: str, language: str, 
                         description: str = ""):
        """Save a reusable code pattern.
        
        Args:
            name: Pattern name
            code: Code snippet
            language: Programming language
            description: Pattern description
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO code_patterns (name, description, code, language, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, code, language, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved code pattern: {name}")
    
    def get_code_patterns(self, language: Optional[str] = None, 
                         limit: int = 5) -> List[Dict[str, Any]]:
        """Get reusable code patterns.
        
        Args:
            language: Filter by language
            limit: Maximum number of patterns to return
            
        Returns:
            List of code patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT name, description, code, language FROM code_patterns WHERE 1=1'
        params = []
        
        if language:
            query += ' AND language = ?'
            params.append(language)
        
        query += ' ORDER BY usage_count DESC, created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {'name': name, 'description': desc, 'code': code, 'language': lang}
            for name, desc, code, lang in results
        ]

