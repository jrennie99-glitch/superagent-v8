"""
User Management System - Admin can create/manage users with free access
"""
import os
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import psycopg2
from psycopg2.extras import RealDictCursor

class UserManager:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self._init_database()
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def _init_database(self):
        """Initialize users table with automatic migrations"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS superagent_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(256) NOT NULL,
                    access_enabled BOOLEAN DEFAULT TRUE,
                    tier VARCHAR(20) DEFAULT 'free',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(50),
                    last_login TIMESTAMP,
                    notes TEXT
                )
            """)
            
            # Create user sessions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES superagent_users(id),
                    token VARCHAR(64) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration: Add expires_at column if it doesn't exist
            cur.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='user_sessions' 
                        AND column_name='expires_at'
                    ) THEN
                        ALTER TABLE user_sessions ADD COLUMN expires_at TIMESTAMP;
                        RAISE NOTICE 'Added expires_at column to user_sessions table';
                    END IF;
                END $$;
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            print("✅ User management database initialized")
        except Exception as e:
            print(f"⚠️ Database init error: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt (industry-standard KDF with key stretching)"""
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good balance of security and performance
        pwd_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return pwd_hash.decode('utf-8')
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify password against bcrypt hash (with backward compatibility for legacy SHA-256 hashes)
        
        NOTE: This system is brand new (Phase 3, Oct 2025) with no legacy users.
        Backward compatibility is added for safety in case of future migrations.
        """
        try:
            # Try bcrypt first (modern hashing)
            if stored_hash.startswith('$2'):  # bcrypt hashes start with $2a$, $2b$, or $2y$
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            
            # Fallback: Check for legacy SHA-256 format (salt:hash)
            # This should never execute in production since this is a new system
            if ':' in stored_hash:
                print("⚠️ WARNING: Legacy SHA-256 hash detected. Please rehash this password.")
                salt, pwd_hash = stored_hash.split(":")
                import hashlib
                check_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                
                # If legacy hash matches, we should rehash it with bcrypt
                # (but we can't do that here without the user_id, so just verify for now)
                return check_hash == pwd_hash
            
            # Unknown hash format
            return False
            
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def create_user(self, username: str, password: str, tier: str = "free", 
                   created_by: str = "admin", notes: str = "") -> Dict:
        """Create a new user (admin only)"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if username exists
            cur.execute("SELECT id FROM superagent_users WHERE username = %s", (username,))
            if cur.fetchone():
                return {"success": False, "error": "Username already exists"}
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Insert user
            cur.execute("""
                INSERT INTO superagent_users 
                (username, password_hash, access_enabled, tier, created_by, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, username, tier, created_at
            """, (username, password_hash, True, tier, created_by, notes))
            
            user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            if not user:
                return {"success": False, "error": "Failed to create user"}
            
            return {
                "success": True,
                "user": dict(user),
                "message": f"User '{username}' created successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, username, password_hash, access_enabled, tier, created_at
                FROM superagent_users 
                WHERE username = %s
            """, (username,))
            
            user = cur.fetchone()
            
            if not user:
                cur.close()
                conn.close()
                return None
            
            # Check access enabled
            if not user['access_enabled']:
                cur.close()
                conn.close()
                return None
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                cur.close()
                conn.close()
                return None
            
            # Update last login
            cur.execute("""
                UPDATE superagent_users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (user['id'],))
            conn.commit()
            
            # Create session token with 30-day expiration
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=30)
            cur.execute("""
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (%s, %s, %s)
                RETURNING token
            """, (user['id'], token, expires_at))
            
            session = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            if not session:
                return None
            
            return {
                "id": user['id'],
                "username": user['username'],
                "tier": user['tier'],
                "token": session['token']
            }
        except Exception as e:
            print(f"Auth error: {e}")
            return None
    
    def verify_user_token(self, token: str) -> Optional[Dict]:
        """Verify user session token and check expiration"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT u.id, u.username, u.tier, u.access_enabled, s.expires_at
                FROM user_sessions s
                JOIN superagent_users u ON s.user_id = u.id
                WHERE s.token = %s
            """, (token,))
            
            result = cur.fetchone()
            
            # Check if token exists and user access is enabled
            if not result or not result['access_enabled']:
                cur.close()
                conn.close()
                return None
            
            # Check if token has expired
            if result['expires_at'] and datetime.now() > result['expires_at']:
                # Token expired - delete it
                cur.execute("DELETE FROM user_sessions WHERE token = %s", (token,))
                conn.commit()
                cur.close()
                conn.close()
                return None
            
            cur.close()
            conn.close()
            
            return {
                'id': result['id'],
                'username': result['username'],
                'tier': result['tier'],
                'access_enabled': result['access_enabled']
            }
        except Exception as e:
            print(f"Token verify error: {e}")
            return None
    
    def list_users(self) -> List[Dict]:
        """List all users (admin only)"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, username, access_enabled, tier, created_at, created_by, last_login, notes
                FROM superagent_users
                ORDER BY created_at DESC
            """)
            
            users = cur.fetchall()
            cur.close()
            conn.close()
            
            return [dict(user) for user in users]
        except Exception as e:
            print(f"List users error: {e}")
            return []
    
    def toggle_access(self, username: str, enabled: bool) -> Dict:
        """Enable or disable user access (admin only)"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE superagent_users 
                SET access_enabled = %s 
                WHERE username = %s
            """, (enabled, username))
            
            if cur.rowcount == 0:
                return {"success": False, "error": "User not found"}
            
            conn.commit()
            cur.close()
            conn.close()
            
            action = "enabled" if enabled else "revoked"
            return {
                "success": True,
                "message": f"Access {action} for user '{username}'"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_user(self, username: str) -> Dict:
        """Delete a user (admin only)"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Delete user sessions first
            cur.execute("""
                DELETE FROM user_sessions 
                WHERE user_id = (SELECT id FROM superagent_users WHERE username = %s)
            """, (username,))
            
            # Delete user
            cur.execute("DELETE FROM superagent_users WHERE username = %s", (username,))
            
            if cur.rowcount == 0:
                return {"success": False, "error": "User not found"}
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                "success": True,
                "message": f"User '{username}' deleted successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_user_tier(self, username: str, tier: str) -> Dict:
        """Update user tier (admin only)"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE superagent_users 
                SET tier = %s 
                WHERE username = %s
            """, (tier, username))
            
            if cur.rowcount == 0:
                return {"success": False, "error": "User not found"}
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                "success": True,
                "message": f"User '{username}' tier updated to '{tier}'"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
user_manager = UserManager()

# Admin tokens for demo/development (in production, use proper auth)
admin_tokens = ["admin-token-2024", "dev-admin-key"]
