"""
Database Schema Awareness Agent.
Provides comprehensive database schema information to other agents.
"""

import logging
from typing import Dict, Any, Optional, List
from backend.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class SchemaAwarenessAgent:
    """Agent responsible for providing database schema information."""
    
    def __init__(self):
        """Initialize the schema awareness agent."""
        self.db_manager = DatabaseManager()
        self._schema_cache = {}
        self._cache_timestamp = None
        
        logger.info("SchemaAwarenessAgent initialized")
    
    def get_database_schema(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get complete database schema information.
        
        Args:
            force_refresh: Force refresh of cached schema
            
        Returns:
            Dictionary containing complete database schema
        """
        try:
            # Use cache if available and not forcing refresh
            if not force_refresh and self._schema_cache:
                logger.debug("Returning cached schema")
                return self._schema_cache
            
            logger.info("Fetching fresh database schema")
            schema_info = self.db_manager.get_database_schema()
            
            # Cache the schema
            self._schema_cache = schema_info
            self._cache_timestamp = self._get_current_timestamp()
            
            logger.info(f"Schema fetched successfully: {len(schema_info)} tables")
            return schema_info
            
        except Exception as e:
            logger.error(f"Error fetching database schema: {e}")
            return {}
    
    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table schema or None if not found
        """
        try:
            schema = self.get_database_schema()
            return schema.get(table_name)
            
        except Exception as e:
            logger.error(f"Error getting table schema for {table_name}: {e}")
            return None
    
    def get_column_info(self, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific column.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            
        Returns:
            Dictionary containing column information or None if not found
        """
        try:
            table_schema = self.get_table_schema(table_name)
            if not table_schema or 'columns' not in table_schema:
                return None
            
            for column in table_schema['columns']:
                if column['COLUMN_NAME'] == column_name:
                    return column
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting column info for {table_name}.{column_name}: {e}")
            return None
    
    def get_related_tables(self, table_name: str) -> List[str]:
        """Get tables that might be related to the given table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of related table names
        """
        try:
            schema = self.get_database_schema()
            related_tables = []
            
            # Simple heuristic: tables with similar names or common patterns
            for other_table in schema.keys():
                if other_table != table_name:
                    # Check for common prefixes or patterns
                    if (table_name.split('_')[0] in other_table or 
                        other_table.split('_')[0] in table_name):
                        related_tables.append(other_table)
            
            return related_tables
            
        except Exception as e:
            logger.error(f"Error getting related tables for {table_name}: {e}")
            return []
    
    def get_query_examples(self) -> List[Dict[str, str]]:
        """Get example queries for the database.
        
        Returns:
            List of example queries with questions and SQL
        """
        try:
            return self.db_manager.get_query_examples()
        except Exception as e:
            logger.error(f"Error getting query examples: {e}")
            return []
    
    def format_schema_for_llm(self) -> str:
        """Format database schema in a way that's useful for LLM consumption.
        
        Returns:
            Formatted string describing the database schema
        """
        try:
            schema = self.get_database_schema()
            if not schema:
                return "No database schema information available."
            
            schema_text = "DATABASE SCHEMA:\n\n"
            
            for table_name, table_info in schema.items():
                schema_text += f"Table: {table_name}\n"
                
                if table_info.get('comment'):
                    schema_text += f"Description: {table_info['comment']}\n"
                
                schema_text += "Columns:\n"
                
                if table_info.get('columns'):
                    for column in table_info['columns']:
                        col_name = column['COLUMN_NAME']
                        col_type = column['DATA_TYPE']
                        nullable = "NULL" if column['IS_NULLABLE'] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {column['COLUMN_DEFAULT']}" if column['COLUMN_DEFAULT'] else ""
                        comment = f" -- {column['COLUMN_COMMENT']}" if column['COLUMN_COMMENT'] else ""
                        
                        schema_text += f"  - {col_name}: {col_type} {nullable}{default}{comment}\n"
                
                schema_text += "\n"
            
            # Add example queries
            examples = self.get_query_examples()
            if examples:
                schema_text += "EXAMPLE QUERIES:\n\n"
                for example in examples[:5]:  # Limit to 5 examples
                    schema_text += f"Question: {example['question']}\n"
                    schema_text += f"SQL: {example['sql']}\n\n"
            
            return schema_text
            
        except Exception as e:
            logger.error(f"Error formatting schema for LLM: {e}")
            return "Error retrieving database schema information."
    
    def validate_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            schema = self.get_database_schema()
            return table_name in schema
        except Exception as e:
            logger.error(f"Error validating table existence for {table_name}: {e}")
            return False
    
    def validate_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            
        Returns:
            True if column exists, False otherwise
        """
        try:
            table_schema = self.get_table_schema(table_name)
            if not table_schema or 'columns' not in table_schema:
                return False
            
            for column in table_schema['columns']:
                if column['COLUMN_NAME'] == column_name:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating column existence for {table_name}.{column_name}: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for cache management."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the schema agent."""
        return {
            "agent_type": "Schema Awareness Agent",
            "capabilities": [
                "Database schema retrieval",
                "Table structure analysis",
                "Column information lookup",
                "Query example generation",
                "Schema validation"
            ],
            "cached_tables": len(self._schema_cache),
            "status": "active"
        }
