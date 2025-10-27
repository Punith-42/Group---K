"""
Specialized SQL Generation Agent.
Focused specifically on understanding natural language questions and generating SQL queries.
Enhanced with database schema awareness.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langsmith import traceable
import json

from agents.core.schema_agent import SchemaAwarenessAgent
from agents.core.prompt_manager import PromptManager
from agents.schemas import SQLQueryResponse

logger = logging.getLogger(__name__)

class SQLGenerationAgent:
    """Specialized agent for SQL query generation from natural language."""
    
    def __init__(self, gemini_api_key: str, model_name: str = "models/gemini-2.5-pro"):
        """Initialize the SQL generation agent.
        
        Args:
            gemini_api_key: Google Gemini API key
            model_name: Gemini model name
        """
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Initialize components
        self.schema_agent = SchemaAwarenessAgent()
        self.prompt_manager = PromptManager()
        
        # Initialize LLM
        self._setup_llm()
        
        logger.info(f"SQLGenerationAgent initialized with model: {model_name}")
    
    def _setup_llm(self):
        """Setup the Google Gemini LLM for SQL generation."""
        try:
            if not self.gemini_api_key:
                raise ValueError("Gemini API key is required")
            
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.0,  # Zero temperature for consistent SQL generation
                convert_system_message_to_human=True
            )
            self.parser = PydanticOutputParser(pydantic_object=SQLQueryResponse)
            
            logger.info("SQL Generation LLM setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup SQL Generation LLM: {e}")
            raise
    
    @traceable(name="sql_generation", project_name="web-activity-agent-system")
    def generate_sql_query(self, question: str, user_id: int, current_date: str = None) -> Optional[str]:
        """Generate SQL query from natural language question.
        
        Args:
            question: User's natural language question
            user_id: User ID for database filtering
            current_date: Current date (optional)
            
        Returns:
            Generated SQL query or None if failed
        """
        try:
            if not current_date:
                current_date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Generating SQL for user {user_id}: {question}")
            
            # Get database schema information (force refresh to get latest sample values)
            schema_info = self.schema_agent.format_schema_for_llm()
            
            # Create comprehensive prompt for SQL generation
            prompt_text = self._create_sql_prompt(question, user_id, current_date, schema_info)
            
            # Generate SQL query using Gemini
            response = self.model.invoke(prompt_text)
            
            # Parse response (Gemini returns text, not JSON)
            try:
                response_text = response.content.strip()
                logger.info(f"Raw Gemini response: {response_text}")
                
                # Try to extract SQL query from the response
                sql_query = self._extract_sql_from_response(response_text)
                
                if not sql_query:
                    logger.error("No SQL query found in response")
                    return None
                
                logger.info(f"SQL generated: {sql_query}")
                
            except Exception as e:
                logger.error(f"Failed to parse response: {e}")
                return None
            
            # Post-process to ensure %s placeholder is used
            sql_query = self._fix_user_id_placeholder(sql_query, user_id)
            
            if sql_query and self._validate_sql_structure(sql_query):
                logger.info(f"Successfully generated SQL: {sql_query}")
                return sql_query
            else:
                logger.warning(f"Generated invalid SQL: {sql_query}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return None
    
    def _create_enhanced_sql_prompt(self, question: str, user_id: int, current_date: str, schema_info: str) -> str:
        """Create an enhanced prompt for SQL generation with schema awareness."""
        return f"""You are an expert SQL developer specializing in database query generation. Your task is to convert natural language questions into precise, safe SQL queries.

{schema_info}

CRITICAL SECURITY RULES - READ ONLY DATABASE:
1. ALWAYS include "user_id = %s" in WHERE clause for security (use %s placeholder, NOT actual user_id value)
2. ONLY use SELECT queries - NO INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE
3. NEVER modify data - NO arithmetic operations like +1, -1, *2, /2 in SELECT statements
4. NEVER use SET, INCREMENT, DECREMENT, MODIFY, CHANGE operations
5. ONLY FETCH existing data - do NOT calculate new values or modify existing values
6. Use proper MySQL syntax for READ-ONLY operations
7. Return ONLY the SQL query, no explanations or markdown
8. Use parameterized queries with %s for user_id placeholder
9. For date-related queries, use proper date functions

IMPORTANT: Use %s as placeholder for user_id, NOT the actual number. Example: WHERE user_id = %s
FORBIDDEN: Do NOT generate queries that modify data like "SUM(commit_count) + 1" - only fetch existing data

COMMON PATTERNS:
- "today" = DATE(activity_date) = CURDATE()
- "this week" = WEEK(activity_date) = WEEK(CURDATE())
- "this month" = MONTH(activity_date) = MONTH(CURDATE())
- "this year" = YEAR(activity_date) = YEAR(CURDATE())
- "last week" = WEEK(activity_date) = WEEK(CURDATE()) - 1
- "last month" = MONTH(activity_date) = MONTH(CURDATE()) - 1

QUERY GENERATION GUIDELINES:
1. Analyze the user question to identify relevant tables and columns
2. Use appropriate JOINs if data from multiple tables is needed
3. Apply proper filtering based on user_id
4. Use appropriate aggregation functions (SUM, COUNT, AVG, etc.) when needed
5. Order results logically (usually by date DESC for activity data)
6. Limit results when appropriate (use LIMIT for large result sets)

USER QUESTION: {question}
CURRENT DATE: {current_date}
USER ID: {user_id}

Generate the SQL query:"""
    
    def _create_json_sql_prompt(self, question: str, user_id: int, current_date: str, schema_info: str) -> str:
        """Create a JSON-formatted prompt for SQL generation."""
        return f"""You are an expert SQL developer specializing in database query generation. Your task is to convert natural language questions into precise, safe SQL queries.

{schema_info}

CRITICAL SECURITY RULES - READ ONLY DATABASE:
1. ALWAYS include "user_id = %s" in WHERE clause for security (use %s placeholder, NOT actual user_id value)
2. ONLY use SELECT queries - NO INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE
3. NEVER modify data - NO arithmetic operations like +1, -1, *2, /2 in SELECT statements
4. NEVER use SET, INCREMENT, DECREMENT, MODIFY, CHANGE operations
5. ONLY FETCH existing data - do NOT calculate new values or modify existing values
6. Use proper MySQL syntax for READ-ONLY operations
7. Return ONLY the SQL query, no explanations or markdown
8. Use parameterized queries with %s for user_id placeholder
9. For date-related queries, use proper date functions

IMPORTANT: Use %s as placeholder for user_id, NOT the actual number. Example: WHERE user_id = %s
FORBIDDEN: Do NOT generate queries that modify data like "SUM(commit_count) + 1" - only fetch existing data

COMMON PATTERNS:
- "today" = DATE(activity_date) = CURDATE()
- "this week" = WEEK(activity_date) = WEEK(CURDATE())
- "this month" = MONTH(activity_date) = MONTH(CURDATE())
- "this year" = YEAR(activity_date) = YEAR(CURDATE())
- "last week" = WEEK(activity_date) = WEEK(CURDATE()) - 1
- "last month" = MONTH(activity_date) = MONTH(CURDATE()) - 1

QUERY GENERATION GUIDELINES:
1. Analyze the user question to identify relevant tables and columns
2. Use appropriate JOINs if data from multiple tables is needed
3. Apply proper filtering based on user_id
4. Use appropriate aggregation functions (SUM, COUNT, AVG, etc.) when needed
5. Order results logically (usually by date DESC for activity data)
6. Limit results when appropriate (use LIMIT for large result sets)

USER QUESTION: {question}
CURRENT DATE: {current_date}
USER ID: {user_id}

You must respond with a valid JSON object containing:
- "sql_query": The generated SQL query
- "reasoning": Brief explanation of the query logic
- "confidence": Confidence score between 0 and 1

Generate the SQL query:"""
    
    def _extract_sql_from_response(self, response_text: str) -> Optional[str]:
        """Extract SQL query from Gemini's text response."""
        if not response_text:
            return None
        
        # First, try to extract from code blocks
        import re
        
        # Look for SQL in code blocks
        sql_block_match = re.search(r'```sql\s*(.*?)\s*```', response_text, re.DOTALL | re.IGNORECASE)
        if sql_block_match:
            sql_query = sql_block_match.group(1).strip()
            return self._clean_sql_response(sql_query)
        
        # Look for any code block with SELECT
        code_block_match = re.search(r'```\s*(.*?SELECT.*?)\s*```', response_text, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            sql_query = code_block_match.group(1).strip()
            return self._clean_sql_response(sql_query)
        
        # If no code blocks, look for SELECT statement spanning multiple lines
        select_match = re.search(r'SELECT.*?(?=\n\n|\n$|$)', response_text, re.DOTALL | re.IGNORECASE)
        if select_match:
            sql_query = select_match.group(0).strip()
            return self._clean_sql_response(sql_query)
        
        # Fallback: look for any line starting with SELECT
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                return self._clean_sql_response(line)
        
        return None
    
    def _create_sql_prompt(self, question: str, user_id: int, current_date: str, schema_info: str) -> str:
        """Create a direct SQL generation prompt for Gemini."""
        return f"""You are an expert SQL developer. Generate a SQL query for the following question.

DATABASE SCHEMA:
{schema_info}

QUESTION: {question}
CURRENT DATE: {current_date}
USER ID: {user_id}

CRITICAL REQUIREMENTS:
1. ALWAYS include "user_id = %s" in WHERE clause for security
2. ONLY use SELECT queries - no INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE
3. Use proper MySQL syntax
4. Use parameterized queries with %s for user_id placeholder
5. For date-related queries, use proper date functions

IMPORTANT: Use Exact Database Values
- For website names: Use FULL domain names (e.g., 'youtube.com', 'github.com')
- For activity types: Use exact values (e.g., 'commit', 'pull_request', 'issue')

Generate ONLY the SQL query, nothing else:"""

    def _clean_sql_response(self, response: str) -> str:
        """Clean and validate SQL response."""
        if not response:
            return None
        
        # Remove any markdown formatting
        sql_query = response.strip()
        
        # Remove code blocks
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:]
        elif sql_query.startswith('```'):
            sql_query = sql_query[3:]
        
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Ensure it starts with SELECT
        if not sql_query.upper().startswith('SELECT'):
            logger.warning(f"Query doesn't start with SELECT: {sql_query}")
            return None
        
        return sql_query
    
    def _fix_user_id_placeholder(self, sql_query: str, user_id: int) -> str:
        """Fix user_id placeholder in SQL query."""
        if not sql_query:
            return sql_query
        
        # Replace user_id = {actual_value} with user_id = %s
        import re
        pattern = rf'user_id\s*=\s*{user_id}'
        fixed_query = re.sub(pattern, 'user_id = %s', sql_query, flags=re.IGNORECASE)
        
        if fixed_query != sql_query:
            logger.info(f"Fixed user_id placeholder: {sql_query} -> {fixed_query}")
        
        return fixed_query
    
    def _validate_sql_structure(self, sql_query: str) -> bool:
        """Basic validation of SQL query structure."""
        if not sql_query:
            return False
        
        sql_upper = sql_query.upper()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Must contain FROM
        if 'FROM' not in sql_upper:
            return False
        
        # Must contain WHERE with user_id
        if 'WHERE' not in sql_upper or 'USER_ID' not in sql_upper:
            return False
        
        # Should not contain dangerous keywords (but allow them in column names)
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            # Check if keyword appears as a standalone word, not as part of a column name
            if f' {keyword} ' in sql_upper or sql_upper.startswith(f'{keyword} '):
                logger.warning(f"Query contains dangerous keyword {keyword}: {sql_query}")
                return False
        
        return True
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the SQL agent."""
        return {
            "agent_type": "SQL Generation Agent",
            "model_name": self.model_name,
            "capabilities": [
                "Natural language to SQL conversion",
                "User-specific query filtering",
                "Date-based query generation",
                "Security validation"
            ],
            "status": "active"
        }
