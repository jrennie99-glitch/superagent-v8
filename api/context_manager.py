"""
Advanced Context Management System
Maintains conversation memory with semantic search
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

# Note: For production, you'd use a proper vector database like Pinecone or Qdrant
# For now, we'll use a simple in-memory system with SQLite fallback

class ContextManager:
    """Manages conversation context and memory"""
    
    def __init__(self, db_path: str = "data/context.db"):
        self.db_path = db_path
        self.current_context: List[Dict] = []
        self.max_context_length = 10  # Keep last 10 messages
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistent storage"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                user_message TEXT,
                assistant_response TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_context (
                key TEXT PRIMARY KEY,
                value TEXT,
                last_updated TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to current context"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.current_context.append(message)
        
        # Trim context if too long
        if len(self.current_context) > self.max_context_length * 2:
            self.current_context = self.current_context[-self.max_context_length * 2:]
    
    def save_conversation(self, user_message: str, assistant_response: str, metadata: Optional[Dict] = None):
        """Save a conversation turn to persistent storage"""
        conversation_id = hashlib.sha256(
            f"{user_message}{assistant_response}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (id, timestamp, user_message, assistant_response, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            datetime.now().isoformat(),
            user_message,
            assistant_response,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple keyword-based conversation search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple LIKE search (in production, use vector search)
        cursor.execute("""
            SELECT timestamp, user_message, assistant_response, metadata
            FROM conversations
            WHERE user_message LIKE ? OR assistant_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "user_message": row[1],
                "assistant_response": row[2],
                "metadata": json.loads(row[3])
            })
        
        conn.close()
        return results
    
    def get_project_context(self, key: str) -> Optional[str]:
        """Get project-specific context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM project_context WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def set_project_context(self, key: str, value: str):
        """Set project-specific context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO project_context (key, value, last_updated)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_context_summary(self) -> str:
        """Get a summary of current context"""
        if not self.current_context:
            return "No active context"
        
        summary = f"Context: {len(self.current_context)} messages in current session\n"
        
        # Count by role
        user_count = sum(1 for m in self.current_context if m["role"] == "user")
        assistant_count = sum(1 for m in self.current_context if m["role"] == "assistant")
        
        summary += f"User messages: {user_count}, Assistant messages: {assistant_count}"
        
        return summary
    
    def clear_context(self):
        """Clear current context"""
        self.current_context = []
    
    def export_context(self) -> str:
        """Export current context as JSON"""
        return json.dumps(self.current_context, indent=2)
    
    def import_context(self, context_json: str):
        """Import context from JSON"""
        self.current_context = json.loads(context_json)


class SmartContextRetrieval:
    """Intelligent context retrieval based on relevance"""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
    
    def get_relevant_context(self, query: str, max_messages: int = 5) -> List[Dict]:
        """
        Get most relevant context for a query
        
        In production, this would use embeddings and vector similarity
        For now, uses keyword matching
        """
        # Get all context
        all_context = self.context_manager.current_context
        
        if not all_context:
            return []
        
        # Score each message by keyword overlap
        query_words = set(query.lower().split())
        scored_messages = []
        
        for message in all_context:
            content_words = set(message["content"].lower().split())
            overlap = len(query_words & content_words)
            
            scored_messages.append({
                "message": message,
                "score": overlap
            })
        
        # Sort by score and recency (newer messages get slight boost)
        scored_messages.sort(
            key=lambda x: (x["score"], x["message"]["timestamp"]),
            reverse=True
        )
        
        # Return top messages
        return [item["message"] for item in scored_messages[:max_messages]]
