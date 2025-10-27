"""
Security Guards for LLM Agent System.
Provides multiple layers of security for SQL query validation and execution.
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security validation levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QuerySecurityGuard:
    """Security guard for SQL query validation."""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """Initialize the security guard.
        
        Args:
            security_level: Level of security validation to apply
        """
        self.security_level = security_level
        
        # Dangerous SQL keywords to block
        self.dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'INFORMATION_SCHEMA',
            'SYSTEM', 'ADMIN', 'GRANT', 'REVOKE', 'SHUTDOWN'
        ]
        
        # Data modification patterns to block (even in SELECT queries)
        self.modification_patterns = [
            r'\+\s*\d+',  # Addition operations like + 1, + 5
            r'(?<![\d\'])\-\s*\d+(?![\d\'])',   # Subtraction operations like - 1, - 5 (not in dates)
            r'\*\s*\d+',  # Multiplication operations like * 2, * 3
            r'/\s*\d+',   # Division operations like / 2, / 3
            r'SET\s+',    # SET operations
            r'INCREMENT', # INCREMENT operations
            r'DECREMENT', # DECREMENT operations
            r'MODIFY',    # MODIFY operations
            r'CHANGE',    # CHANGE operations
        ]
        
        # Allowed SQL keywords (including UNION for multi-table queries)
        self.allowed_keywords = [
            'SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'GROUP', 'HAVING',
            'LIMIT', 'OFFSET', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
            'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
            'IS', 'NULL', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT',
            'DATE', 'CURDATE', 'NOW', 'INTERVAL', 'WEEK', 'MONTH', 'YEAR',
            'DATE_SUB', 'DATE_FORMAT', 'DESC', 'ASC', 'TOTAL', 'TIME',
            'SOCIAL', 'MEDIA', 'BROWSE', 'ACTIVITY', 'REPOSITORY', 'COMMIT',
            'UNION', 'UNION ALL'  # Allow UNION operations for multi-table queries
        ]
        
        logger.info(f"QuerySecurityGuard initialized with {security_level.value} security level")
    
    def validate_query(self, sql_query: str, user_id: int) -> Tuple[bool, str]:
        """Validate SQL query for security.
        
        Args:
            sql_query: SQL query to validate
            user_id: User ID for context
            
        Returns:
            Tuple of (is_safe, reason)
        """
        try:
            # Basic validation
            if not sql_query or not sql_query.strip():
                return False, "Empty query"
            
            sql_upper = sql_query.upper().strip()
            
            # Check for dangerous keywords
            dangerous_found = self._check_dangerous_keywords(sql_upper)
            if dangerous_found:
                return False, f"Dangerous keyword detected: {dangerous_found}"
            
            # Check for data modification patterns
            modification_found = self._check_modification_patterns(sql_query)
            if modification_found:
                # Instead of blocking, mark as modification request
                return True, f"MODIFICATION_REQUEST:{modification_found}"
            
            # Check for user_id filtering requirement
            if not self._check_user_id_filtering(sql_query, user_id):
                return False, "Query must include user_id filtering for security"
            
            # Check for multiple statements
            if self._check_multiple_statements(sql_query):
                return False, "Multiple statements not allowed"
            
            # Check for system table access
            if self._check_system_table_access(sql_upper):
                return False, "System table access not allowed"
            
            # Check UNION query safety
            if 'UNION' in sql_upper:
                union_safe, union_reason = self._check_union_safety(sql_query, user_id)
                if not union_safe:
                    return False, f"UNION query safety check failed: {union_reason}"
            
            # Additional checks based on security level
            if self.security_level == SecurityLevel.HIGH:
                if not self._check_allowed_keywords_only(sql_upper):
                    return False, "Query contains non-standard SQL keywords"
            
            logger.debug(f"Query validation passed for user {user_id}")
            return True, "Query is safe"
            
        except Exception as e:
            logger.error(f"Error during query validation: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _check_dangerous_keywords(self, sql_upper: str) -> str:
        """Check for dangerous SQL keywords."""
        for keyword in self.dangerous_keywords:
            # Check if keyword appears as a standalone word, not as part of a column name
            if f' {keyword} ' in sql_upper or sql_upper.startswith(f'{keyword} '):
                return keyword
        return None
    
    def _check_user_id_filtering(self, sql_query: str, user_id: int) -> bool:
        """Check if query includes user_id filtering."""
        sql_lower = sql_query.lower()
        
        # Look for user_id in WHERE clause with %s placeholder
        where_pattern = r'where.*user_id\s*[=<>]\s*%s'
        if re.search(where_pattern, sql_lower):
            return True
        
        # Look for user_id = {user_id} pattern
        user_id_pattern = f'user_id\\s*[=<>]\\s*{user_id}'
        if re.search(user_id_pattern, sql_lower):
            return True
        
        # Look for user_id in WHERE clause with any operator
        where_user_pattern = r'where.*user_id\s*[=<>!]+\s*'
        if re.search(where_user_pattern, sql_lower):
            return True
        
        # Additional check: look for user_id anywhere in the query
        if 'user_id' in sql_lower and 'where' in sql_lower:
            # Check if user_id appears after WHERE
            where_pos = sql_lower.find('where')
            user_id_pos = sql_lower.find('user_id')
            if user_id_pos > where_pos:
                return True
        
        return False
    
    def _check_modification_patterns(self, sql_query: str) -> Optional[str]:
        """Check for data modification patterns in the query.
        
        Args:
            sql_query: SQL query to check
            
        Returns:
            Description of modification pattern found, or None if safe
        """
        try:
            sql_upper = sql_query.upper()
            
            # Check for modification patterns
            for pattern in self.modification_patterns:
                if re.search(pattern, sql_upper, re.IGNORECASE):
                    if pattern == r'\+\s*\d+':
                        return "Addition operation detected (e.g., + 1, + 5)"
                    elif pattern == r'-\s*\d+':
                        return "Subtraction operation detected (e.g., - 1, - 5)"
                    elif pattern == r'\*\s*\d+':
                        return "Multiplication operation detected (e.g., * 2, * 3)"
                    elif pattern == r'/\s*\d+':
                        return "Division operation detected (e.g., / 2, / 3)"
                    elif pattern == r'SET\s+':
                        return "SET operation detected"
                    elif pattern == r'INCREMENT':
                        return "INCREMENT operation detected"
                    elif pattern == r'DECREMENT':
                        return "DECREMENT operation detected"
                    elif pattern == r'MODIFY':
                        return "MODIFY operation detected"
                    elif pattern == r'CHANGE':
                        return "CHANGE operation detected"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking modification patterns: {e}")
            return f"Modification pattern check error: {str(e)}"
    
    def _check_multiple_statements(self, sql_query: str) -> bool:
        """Check for multiple SQL statements."""
        # Count semicolons (excluding those in strings)
        semicolon_count = sql_query.count(';')
        return semicolon_count > 1
    
    def _check_system_table_access(self, sql_upper: str) -> bool:
        """Check for system table access."""
        system_tables = [
            'INFORMATION_SCHEMA', 'MYSQL', 'PERFORMANCE_SCHEMA',
            'SYS', 'SYSTEM', 'ADMIN'
        ]
        
        for table in system_tables:
            if table in sql_upper:
                return True
        
        return False
    
    def _check_union_safety(self, sql_query: str, user_id: int) -> Tuple[bool, str]:
        """Check UNION query safety.
        
        Args:
            sql_query: SQL query containing UNION
            user_id: User ID for validation
            
        Returns:
            Tuple of (is_safe, reason)
        """
        try:
            sql_lower = sql_query.lower()
            
            # Split query by UNION to check each part
            union_parts = re.split(r'\bunion\b', sql_lower)
            
            if len(union_parts) < 2:
                return False, "UNION query must have at least two SELECT statements"
            
            # Check each SELECT statement in the UNION
            for i, part in enumerate(union_parts):
                part = part.strip()
                if not part:
                    continue
                
                # Remove ORDER BY clause from the end for validation
                part_without_order = re.sub(r'\s+order\s+by\s+.*$', '', part, flags=re.IGNORECASE)
                    
                # Each part should be a SELECT statement
                if not part_without_order.startswith('select'):
                    return False, f"UNION part {i+1} must start with SELECT"
                
                # Each part must have user_id filtering
                if not self._check_user_id_filtering(part_without_order, user_id):
                    return False, f"UNION part {i+1} must include user_id filtering"
                
                # Check for dangerous keywords in each part
                part_upper = part_without_order.upper()
                dangerous_found = self._check_dangerous_keywords(part_upper)
                if dangerous_found:
                    return False, f"Dangerous keyword '{dangerous_found}' found in UNION part {i+1}"
            
            # Check that UNION is not used with subqueries that could be exploited
            if 'select' in sql_lower and sql_lower.count('select') > len(union_parts):
                return False, "UNION queries with nested SELECT statements are not allowed"
            
            return True, "UNION query is safe"
            
        except Exception as e:
            logger.error(f"Error checking UNION safety: {e}")
            return False, f"UNION safety check error: {str(e)}"
    
    def _check_allowed_keywords_only(self, sql_upper: str) -> bool:
        """Check if query contains only allowed keywords (HIGH security)."""
        # Extract SQL keywords
        words = re.findall(r'\b[A-Z]+\b', sql_upper)
        
        for word in words:
            if word not in self.allowed_keywords and word not in self.dangerous_keywords:
                # Allow common SQL functions and operators
                if word in ['DATE', 'CURDATE', 'NOW', 'INTERVAL', 'WEEK', 'MONTH', 'YEAR', 'DATE_SUB', 'DATE_FORMAT']:
                    continue
                # Allow table/column names (but be more lenient)
                if word.isupper() and len(word) > 2:
                    # Check if it's likely a table/column name by looking at context
                    if not self._is_likely_table_column_name(word, sql_upper):
                        return False
        
        return True
    
    def _is_likely_table_column_name(self, word: str, sql_upper: str) -> bool:
        """Check if a word is likely a table or column name."""
        # Common patterns that suggest table/column names
        patterns = [
            f'FROM {word}',
            f'JOIN {word}',
            f'{word} =',
            f'{word} LIKE',
            f'{word} IN',
            f'ORDER BY {word}',
            f'GROUP BY {word}',
            f'SELECT.*{word}',
        ]
        
        for pattern in patterns:
            if re.search(pattern, sql_upper):
                return True
        
        return False
    
    def sanitize_query(self, sql_query: str) -> str:
        """Sanitize SQL query by removing potentially dangerous parts."""
        # Remove comments
        sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
        
        # Remove extra whitespace
        sql_query = ' '.join(sql_query.split())
        
        return sql_query.strip()

class ResponseSecurityGuard:
    """Security guard for LLM response validation."""
    
    def __init__(self):
        """Initialize response security guard."""
        # Patterns to block in responses
        self.blocked_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'data:text/html',           # Data URLs
            r'vbscript:',                # VBScript
            r'on\w+\s*=',                # Event handlers
        ]
        
        logger.info("ResponseSecurityGuard initialized")
    
    def validate_response(self, response: str) -> Tuple[bool, str]:
        """Validate LLM response for security.
        
        Args:
            response: LLM response to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        try:
            if not response or not response.strip():
                return False, "Empty response"
            
            # Check for blocked patterns
            for pattern in self.blocked_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    return False, f"Potentially malicious content detected: {pattern}"
            
            # Check response length (prevent extremely long responses)
            if len(response) > 10000:
                return False, "Response too long"
            
            logger.debug("Response validation passed")
            return True, "Response is safe"
            
        except Exception as e:
            logger.error(f"Error during response validation: {e}")
            return False, f"Validation error: {str(e)}"
    
    def sanitize_response(self, response: str) -> str:
        """Sanitize LLM response."""
        # Remove HTML tags
        response = re.sub(r'<[^>]+>', '', response)
        
        # Remove potential script content
        for pattern in self.blocked_patterns:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE)
        
        return response.strip()
