"""
Query Execution Agent.
Specialized agent for safely executing SQL queries and handling database operations.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from backend.database.db_manager import DatabaseManager
from agents.guards.security_guards import QuerySecurityGuard

logger = logging.getLogger(__name__)

class QueryExecutionAgent:
    """Specialized agent for executing SQL queries safely."""
    
    def __init__(self):
        """Initialize the query execution agent."""
        self.db_manager = DatabaseManager()
        self.query_guard = QuerySecurityGuard()
        
        logger.info("QueryExecutionAgent initialized")
    
    def execute_query(self, sql_query: str, user_id: int) -> Dict[str, Any]:
        """Execute a SQL query safely with comprehensive validation.
        
        Args:
            sql_query: SQL query to execute
            user_id: User ID for security validation
            
        Returns:
            Dictionary containing execution results and metadata
        """
        try:
            logger.info(f"Executing query for user {user_id}: {sql_query}")
            
            # Step 1: Security validation
            is_safe, reason = self.query_guard.validate_query(sql_query, user_id)
            if not is_safe:
                logger.warning(f"Query blocked by security guard: {reason}")
                return {
                    "success": False,
                    "error": f"Query blocked for security: {reason}",
                    "query": sql_query,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Step 1.5: Check for modification requests (handle gracefully)
            if reason and reason.startswith("MODIFICATION_REQUEST:"):
                modification_reason = reason.replace("MODIFICATION_REQUEST:", "")
                logger.info(f"Modification request detected: {modification_reason}")
                return {
                    "success": True,  # Return success but with modification flag
                    "is_modification_request": True,
                    "modification_reason": modification_reason,
                    "query": sql_query,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "results": [],  # No actual data results
                    "row_count": 0,
                    "columns": []
                }
            
            # Step 2: Prepare query parameters
            safe_query, params = self._prepare_query_parameters(sql_query, user_id)
            
            # Step 3: Execute query with validation
            execution_result = self.db_manager.execute_query_with_validation(safe_query, params)
            
            # Step 4: Process results
            if execution_result["success"]:
                processed_results = self._process_query_results(execution_result["results"])
                
                logger.info(f"Query executed successfully, returned {execution_result['row_count']} rows")
                return {
                    "success": True,
                    "results": processed_results,
                    "raw_results": execution_result["results"],
                    "row_count": execution_result["row_count"],
                    "columns": execution_result["columns"],
                    "query": sql_query,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": datetime.now().isoformat()
                }
            else:
                logger.error(f"Query execution failed: {execution_result['error']}")
                return {
                    "success": False,
                    "error": execution_result["error"],
                    "query": sql_query,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": sql_query,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_multiple_queries(self, queries: List[str], user_id: int) -> List[Dict[str, Any]]:
        """Execute multiple queries safely.
        
        Args:
            queries: List of SQL queries to execute
            user_id: User ID for security validation
            
        Returns:
            List of execution results
        """
        results = []
        
        for i, query in enumerate(queries):
            logger.info(f"Executing query {i+1}/{len(queries)} for user {user_id}")
            result = self.execute_query(query, user_id)
            result["query_index"] = i
            results.append(result)
            
            # Stop execution if any query fails
            if not result["success"]:
                logger.warning(f"Stopping execution after query {i+1} failed")
                break
        
        return results
    
    def test_query_syntax(self, sql_query: str) -> Dict[str, Any]:
        """Test query syntax without executing it.
        
        Args:
            sql_query: SQL query to test
            
        Returns:
            Dictionary containing syntax validation results
        """
        try:
            # Basic syntax validation
            sql_upper = sql_query.upper().strip()
            
            # Check for dangerous keywords
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            found_dangerous = [kw for kw in dangerous_keywords if kw in sql_upper]
            
            # Check for SELECT statement
            has_select = sql_upper.startswith('SELECT')
            
            # Check for FROM clause
            has_from = 'FROM' in sql_upper
            
            # Check for WHERE clause
            has_where = 'WHERE' in sql_upper
            
            # Check for user_id filtering
            has_user_id = 'USER_ID' in sql_upper
            
            syntax_valid = has_select and has_from and not found_dangerous
            
            return {
                "syntax_valid": syntax_valid,
                "has_select": has_select,
                "has_from": has_from,
                "has_where": has_where,
                "has_user_id": has_user_id,
                "dangerous_keywords": found_dangerous,
                "query": sql_query,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing query syntax: {e}")
            return {
                "syntax_valid": False,
                "error": str(e),
                "query": sql_query,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_query_statistics(self, sql_query: str, user_id: int) -> Dict[str, Any]:
        """Get statistics about a query without returning actual data.
        
        Args:
            sql_query: SQL query to analyze
            user_id: User ID for security validation
            
        Returns:
            Dictionary containing query statistics
        """
        try:
            # Execute query with LIMIT 0 to get metadata only
            stats_query = f"SELECT COUNT(*) as total_rows FROM ({sql_query}) as subquery"
            
            # Replace user_id placeholder
            safe_query, params = self._prepare_query_parameters(stats_query, user_id)
            
            result = self.db_manager.execute_query_with_validation(safe_query, params)
            
            if result["success"]:
                total_rows = result["results"][0]["total_rows"] if result["results"] else 0
                
                return {
                    "success": True,
                    "total_rows": total_rows,
                    "estimated_size": self._estimate_result_size(total_rows, result["columns"]),
                    "columns": result["columns"],
                    "query": sql_query,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "query": sql_query,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting query statistics: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": sql_query,
                "timestamp": datetime.now().isoformat()
            }
    
    def _prepare_query_parameters(self, sql_query: str, user_id: int) -> Tuple[str, Tuple]:
        """Prepare query parameters for safe execution.
        
        Args:
            sql_query: SQL query with placeholders
            user_id: User ID to substitute
            
        Returns:
            Tuple of (safe_query, params)
        """
        # Replace user_id placeholder with parameter
        safe_query = sql_query.replace('{user_id}', '%s')
        
        # Escape % characters in string literals to prevent them from being treated as placeholders
        import re
        # Find string literals (content between single quotes) and escape % characters
        def escape_string_literal(match):
            content = match.group(1)
            escaped_content = content.replace('%', '%%')
            return f"'{escaped_content}'"
        
        safe_query = re.sub(r"'([^']*)'", escape_string_literal, safe_query)
        
        # Count only %s placeholders that are not inside string literals
        # Split by single quotes and count %s in odd-indexed parts (outside strings)
        parts = safe_query.split("'")
        placeholder_count = 0
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are outside string literals
                placeholder_count += part.count('%s')
        
        # Create parameters tuple with the right number of parameters
        params = (user_id,) * placeholder_count
        
        return safe_query, params
    
    def _check_for_data_modification(self, sql_query: str) -> Optional[str]:
        """Check if the query attempts to modify data.
        
        Args:
            sql_query: SQL query to check
            
        Returns:
            Description of modification attempt, or None if safe
        """
        try:
            sql_upper = sql_query.upper()
            
            # Check for arithmetic operations that modify data
            modification_patterns = [
                (r'\+\s*\d+', "Addition operation detected (e.g., + 1, + 5)"),
                (r'(?<![\d\'])\-\s*\d+(?![\d\'])', "Subtraction operation detected (e.g., - 1, - 5)"),
                (r'\*\s*\d+', "Multiplication operation detected (e.g., * 2, * 3)"),
                (r'/\s*\d+', "Division operation detected (e.g., / 2, / 3)"),
                (r'SET\s+', "SET operation detected"),
                (r'INCREMENT', "INCREMENT operation detected"),
                (r'DECREMENT', "DECREMENT operation detected"),
                (r'MODIFY', "MODIFY operation detected"),
                (r'CHANGE', "CHANGE operation detected"),
            ]
            
            for pattern, description in modification_patterns:
                if re.search(pattern, sql_upper, re.IGNORECASE):
                    return description
            
            # Check for specific problematic patterns (arithmetic operations on aggregated data)
            if 'SUM(' in sql_upper:
                # Check if there are arithmetic operations outside of date functions
                if re.search(r'SUM\([^)]+\)\s*[+\-*/]\s*\d+', sql_upper):
                    return "Arithmetic operations on aggregated data detected - this modifies data"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking for data modification: {e}")
            return f"Data modification check error: {str(e)}"
    
    def _process_query_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process query results for better presentation.
        
        Args:
            results: Raw query results
            
        Returns:
            Processed results
        """
        if not results:
            return []
        
        processed_results = []
        
        for row in results:
            processed_row = {}
            
            for key, value in row.items():
                # Convert datetime objects to strings
                if isinstance(value, datetime):
                    processed_row[key] = value.isoformat()
                # Convert other non-serializable objects
                elif hasattr(value, 'isoformat'):
                    processed_row[key] = value.isoformat()
                else:
                    processed_row[key] = value
            
            processed_results.append(processed_row)
        
        return processed_results
    
    def _estimate_result_size(self, row_count: int, columns: List[str]) -> str:
        """Estimate the size of query results.
        
        Args:
            row_count: Number of rows
            columns: List of column names
            
        Returns:
            Size estimation string
        """
        if row_count == 0:
            return "No data"
        elif row_count < 10:
            return "Small dataset"
        elif row_count < 100:
            return "Medium dataset"
        elif row_count < 1000:
            return "Large dataset"
        else:
            return "Very large dataset"
    
    def validate_database_connection(self) -> bool:
        """Validate database connection.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            return self.db_manager.test_connection()
        except Exception as e:
            logger.error(f"Database connection validation failed: {e}")
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the query execution agent."""
        return {
            "agent_type": "Query Execution Agent",
            "capabilities": [
                "Safe SQL query execution",
                "Security validation",
                "Query syntax testing",
                "Result processing",
                "Multi-query execution",
                "Query statistics"
            ],
            "database_connected": self.validate_database_connection(),
            "status": "active"
        }
