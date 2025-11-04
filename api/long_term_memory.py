"""
Long-Term Memory - SQLite-based project memory
Learns from past projects and provides context
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class LongTermMemory:
    """Store and retrieve project history for learning and context"""
    
    def __init__(self, db_path: str = "superagent_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instruction TEXT NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                verification_score INTEGER,
                performance_grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_learned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                lesson TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_project(self, instruction: str, language: str, code: str, 
                     verification_score: Optional[int] = None,
                     performance_grade: Optional[str] = None,
                     tags: List[str] = None) -> int:
        """Store a completed project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (instruction, language, code, verification_score, performance_grade, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (instruction, language, code, verification_score, performance_grade, 
              json.dumps(tags) if tags else None))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_similar_projects(self, instruction: str, language: str, limit: int = 5) -> List[Dict]:
        """Find similar past projects for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple similarity: same language + keyword matching
        keywords = instruction.lower().split()[:5]
        
        query = """
            SELECT id, instruction, code, verification_score, performance_grade, created_at
            FROM projects
            WHERE language = ?
            AND success = TRUE
        """
        
        params = [language]
        
        # Build LIKE clauses with parameterized queries to prevent SQL injection
        for keyword in keywords:
            query += " AND LOWER(instruction) LIKE ?"
            params.append(f'%{keyword}%')
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "instruction": row[1],
                "code": row[2],
                "verification_score": row[3],
                "performance_grade": row[4],
                "created_at": row[5]
            })
        
        conn.close()
        return results
    
    def get_learnings(self, limit: int = 10) -> List[Dict]:
        """Get lessons learned from past projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, project_id, lesson, category, created_at
            FROM lessons_learned
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "project_id": row[1],
                "lesson": row[2],
                "category": row[3],
                "created_at": row[4]
            })
        
        conn.close()
        return results
    
    def store_lesson(self, project_id: int, lesson: str, category: str = "general"):
        """Store a lesson learned from a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO lessons_learned (project_id, lesson, category)
            VALUES (?, ?, ?)
        """, (project_id, lesson, category))
        
        conn.commit()
        conn.close()
    
    def get_lessons(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retrieve lessons learned"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT lesson, category, created_at
                FROM lessons_learned
                WHERE category = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT lesson, category, created_at
                FROM lessons_learned
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "lesson": row[0],
                "category": row[1],
                "created_at": row[2]
            })
        
        conn.close()
        return results
    
    def track_pattern(self, pattern_type: str, pattern_data: Dict):
        """Track common patterns for optimization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pattern_json = json.dumps(pattern_data)
        
        cursor.execute("""
            SELECT id, frequency FROM patterns
            WHERE pattern_type = ? AND pattern_data = ?
        """, (pattern_type, pattern_json))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE patterns
                SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (existing[0],))
        else:
            cursor.execute("""
                INSERT INTO patterns (pattern_type, pattern_data)
                VALUES (?, ?)
            """, (pattern_type, pattern_json))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM lessons_learned")
        total_lessons = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patterns")
        total_patterns = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(verification_score) FROM projects
            WHERE verification_score IS NOT NULL
        """)
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_projects": total_projects,
            "total_lessons": total_lessons,
            "total_patterns": total_patterns,
            "average_verification_score": round(avg_score, 1)
        }
