"""
Database Manager Module - PostgreSQL management
"""
import os
from typing import Dict, List
import asyncio

class DatabaseManager:
    """Manage PostgreSQL database operations"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.available = self.db_url is not None
    
    async def execute_query(self, query: str) -> Dict:
        """Execute SQL query"""
        if not self.available:
            return {
                "success": False,
                "error": "Database not configured. Set DATABASE_URL environment variable."
            }
        
        try:
            import asyncpg
            
            conn = await asyncpg.connect(self.db_url)
            
            if query.strip().upper().startswith('SELECT'):
                result = await conn.fetch(query)
                rows = [dict(row) for row in result]
                await conn.close()
                return {
                    "success": True,
                    "query": query,
                    "rows": rows,
                    "count": len(rows)
                }
            else:
                result = await conn.execute(query)
                await conn.close()
                return {
                    "success": True,
                    "query": query,
                    "result": result,
                    "message": "Query executed successfully"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def list_tables(self) -> Dict:
        """List all tables in database"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        return await self.execute_query(query)
    
    async def describe_table(self, table_name: str) -> Dict:
        """Describe table structure"""
        query = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
        return await self.execute_query(query)
    
    async def create_table(self, table_name: str, columns: Dict[str, str]) -> Dict:
        """Create a new table"""
        column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
        return await self.execute_query(query)
