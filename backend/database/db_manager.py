"""
Database Manager for LLM Agent System.
Handles safe database connections and query execution.
"""

import pymysql
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and query execution."""
    
    def __init__(self):
        """Initialize database manager."""
        self.config = DATABASE_CONFIG
        logger.info("DatabaseManager initialized")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = None
        try:
            conn = pymysql.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=int(self.config['port']),
                charset='utf8mb4'
            )
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, sql_query: str, params: Tuple = None) -> Optional[List[Dict[str, Any]]]:
        """Execute a SELECT query safely.
        
        Args:
            sql_query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of dictionaries containing query results, or None if error
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                if params:
                    cursor.execute(sql_query, params)
                else:
                    cursor.execute(sql_query)
                
                results = cursor.fetchall()
                cursor.close()
                
                logger.debug(f"Query executed successfully, returned {len(results)} rows")
                return results
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def execute_query_with_validation(self, sql_query: str, params: Tuple = None) -> Dict[str, Any]:
        """Execute query with additional validation and metadata.
        
        Args:
            sql_query: SQL query to execute
            params: Query parameters
            
        Returns:
            Dictionary with results and metadata
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                if params:
                    cursor.execute(sql_query, params)
                else:
                    cursor.execute(sql_query)
                
                results = cursor.fetchall()
                
                # Get query metadata
                row_count = cursor.rowcount
                description = cursor.description
                
                cursor.close()
                
                return {
                    "success": True,
                    "results": results,
                    "row_count": row_count,
                    "columns": [desc[0] for desc in description] if description else [],
                    "query": sql_query
                }
                
        except Exception as e:
            logger.error(f"Error executing validated query: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": None,
                "row_count": 0
            }
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                logger.info("Database connection test successful")
                return True
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get table structure information.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of dictionaries containing column information
        """
        try:
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            
            results = self.execute_query(query, (self.config['database'], table_name))
            return results
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return None
    
    def get_database_schema(self) -> Dict[str, Any]:
        """Get complete database schema information."""
        try:
            schema_info = {}
            
            # Get list of tables
            tables_query = """
                SELECT TABLE_NAME, TABLE_COMMENT 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
            """
            
            tables = self.execute_query(tables_query, (self.config['database'],))
            
            if tables:
                for table in tables:
                    table_name = table['TABLE_NAME']
                    schema_info[table_name] = {
                        "comment": table['TABLE_COMMENT'],
                        "columns": self.get_table_info(table_name)
                    }
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {}
    
    def get_query_examples(self) -> List[Dict[str, str]]:
        """Get example queries for the database."""
        return [
            {
                "question": "Show my web activity for today",
                "sql": "SELECT * FROM web_activity WHERE user_id = %s AND activity_date = CURDATE() ORDER BY created_at DESC"
            },
            {
                "question": "How much time did I spend on youtube.com this week?",
                "sql": "SELECT SUM(time_spent) as total_time FROM web_activity WHERE user_id = %s AND website_name = 'youtube.com' AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
            },
            {
                "question": "What are my most active GitHub repositories?",
                "sql": "SELECT repository_name, COUNT(*) as activity_count FROM github_activity WHERE user_id = %s GROUP BY repository_name ORDER BY activity_count DESC LIMIT 10"
            },
            {
                "question": "Show my GitHub commits for this month",
                "sql": "SELECT * FROM github_activity WHERE user_id = %s AND activity_type = 'commit' AND activity_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01') ORDER BY activity_date DESC"
            },
            {
                "question": "How much time did I spend on github.com yesterday?",
                "sql": "SELECT SUM(time_spent) as total_time FROM web_activity WHERE user_id = %s AND website_name = 'github.com' AND activity_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
            },
            {
                "question": "Show my commits for the past 5 days",
                "sql": "SELECT * FROM github_activity WHERE user_id = %s AND activity_type = 'commit' AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 5 DAY) ORDER BY activity_date DESC"
            },
            {
                "question": "Show all my activity from both web and GitHub today",
                "sql": "SELECT 'web' as platform, website_name as source, time_spent, activity_date FROM web_activity WHERE user_id = %s AND activity_date = CURDATE() UNION ALL SELECT 'github' as platform, repository_name as source, 0 as time_spent, activity_date FROM github_activity WHERE user_id = %s AND activity_date = CURDATE() ORDER BY activity_date DESC"
            },
            {
                "question": "What are my most active platforms overall?",
                "sql": "SELECT 'web' as platform, COUNT(*) as activity_count FROM web_activity WHERE user_id = %s GROUP BY 'web' UNION ALL SELECT 'github' as platform, COUNT(*) as activity_count FROM github_activity WHERE user_id = %s GROUP BY 'github' ORDER BY activity_count DESC"
            },
            {
                "question": "Show my total time spent across all platforms this week",
                "sql": "SELECT 'web' as platform, SUM(time_spent) as total_time FROM web_activity WHERE user_id = %s AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY 'web' UNION ALL SELECT 'github' as platform, COUNT(*) * 5 as total_time FROM github_activity WHERE user_id = %s AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY 'github'"
            },
            {
                "question": "Show all my repositories and websites I have been active on",
                "sql": "SELECT DISTINCT repository_name as name, 'repository' as type FROM github_activity WHERE user_id = %s AND repository_name IS NOT NULL UNION ALL SELECT DISTINCT website_name as name, 'website' as type FROM web_activity WHERE user_id = %s AND website_name IS NOT NULL ORDER BY name"
            }
        ]
