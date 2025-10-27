"""
Response Formatting Agent.
Specialized agent for converting query results into natural language responses.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langsmith import traceable
import json

from agents.core.prompt_manager import PromptManager
from agents.guards.security_guards import ResponseSecurityGuard
from agents.schemas import DataAnalysisResponse, TimeAnalysisResult, AggregationResult

logger = logging.getLogger(__name__)

class ResponseFormattingAgent:
    """Specialized agent for formatting query results into natural language responses."""
    
    def __init__(self, gemini_api_key: str, model_name: str = "models/gemini-2.5-pro"):
        """Initialize the response formatting agent.
        
        Args:
            gemini_api_key: Google Gemini API key
            model_name: Gemini model name
        """
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Initialize components
        self.prompt_manager = PromptManager()
        self.response_guard = ResponseSecurityGuard()
        
        # Initialize LLM
        self._setup_llm()
        
        logger.info(f"ResponseFormattingAgent initialized with model: {model_name}")
    
    def _setup_llm(self):
        """Setup the Google Gemini LLM for response formatting."""
        try:
            if not self.gemini_api_key:
                raise ValueError("Gemini API key is required")
            
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.gemini_api_key,
                temperature=0.3,  # Slightly higher temperature for more natural responses
                convert_system_message_to_human=True
            )
            self.parser = PydanticOutputParser(pydantic_object=DataAnalysisResponse)
            
            logger.info("Response Formatting LLM setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup Response Formatting LLM: {e}")
            raise
    
    @traceable(name="response_formatting", project_name="web-activity-agent-system")
    def format_response(self, question: str, query_results: Dict[str, Any], sql_query: str = None) -> Dict[str, Any]:
        """Format query results into a structured JSON response.
        
        Args:
            question: Original user question
            query_results: Query execution results
            sql_query: SQL query that was executed (optional)
            
        Returns:
            Dictionary containing response and results or None if failed
        """
        try:
            logger.info(f"Formatting response for question: {question}")
            
            # Check if this is a modification request
            if query_results.get("is_modification_request", False):
                return self._format_modification_response(question, query_results)
            
            # Extract relevant information from query results
            results_data = self._extract_results_data(query_results)
            
            # Create comprehensive prompt for response formatting
            prompt_text = self._create_response_prompt(question, results_data, sql_query)
            
            # Generate formatted response using Gemini
            try:
                response = self.model.invoke(prompt_text)
                
                # Parse Gemini text response
                try:
                    response_text = response.content.strip()
                    logger.info(f"Raw Gemini response: {response_text[:200]}...")
                    
                    # Extract structured response from text
                    formatted_response, structured_results, summary, metadata = self._parse_gemini_response(response_text, results_data)
                    
                    logger.info(f"LLM response generated successfully: {formatted_response[:100]}...")
                    
                except Exception as e:
                    logger.error(f"Failed to parse Gemini response: {e}")
                    # Fallback to simple response
                    formatted_response = self._create_fallback_aggregation_response(question, results_data)
                    structured_results = results_data.get("data", [])
                    summary = {}
                    metadata = {}
                
            except Exception as llm_error:
                logger.error(f"LLM response generation failed: {llm_error}")
                # Fallback response for aggregation queries
                if any(keyword in question.lower() for keyword in ['how much', 'total', 'sum', 'count', 'average']):
                    formatted_response = self._create_fallback_aggregation_response(question, results_data)
                    structured_results = results_data.get("data", [])
                else:
                    formatted_response = "I found some data but couldn't format a proper response."
                    structured_results = results_data.get("data", [])
                summary = {}
                metadata = {}
            
            # Sanitize and validate response
            formatted_response = self.response_guard.sanitize_response(formatted_response)
            
            # Additional validation
            is_safe, reason = self.response_guard.validate_response(formatted_response)
            if not is_safe:
                logger.warning(f"Response blocked by security guard: {reason}")
                formatted_response = "I found some data but couldn't provide a safe response due to security restrictions."
            
            logger.info("Response formatted successfully")
            return {
                "response": formatted_response,
                "results": structured_results,
                "summary": summary,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return {
                "response": "I encountered an error while formatting the response.",
                "results": [],
                "summary": {},
                "metadata": {}
            }
    
    def format_error_response(self, question: str, error_message: str, error_type: str = "general") -> str:
        """Format error responses in a user-friendly way.
        
        Args:
            question: Original user question
            error_message: Error message from the system
            error_type: Type of error (sql, security, database, etc.)
            
        Returns:
            User-friendly error response
        """
        try:
            error_responses = {
                "sql": "I had trouble understanding your question. Could you try rephrasing it?",
                "security": "I can't execute that query for security reasons. Please try a different question.",
                "database": "I encountered an issue accessing the database. Please try again in a moment.",
                "timeout": "The query took too long to execute. Please try a more specific question.",
                "general": "I encountered an unexpected error. Please try again."
            }
            
            base_response = error_responses.get(error_type, error_responses["general"])
            
            # Add helpful suggestions based on error type
            if error_type == "sql":
                base_response += " Try asking about specific data like 'Show my activity today' or 'What are my most active repositories?'"
            elif error_type == "security":
                base_response += " I can only show you your own data."
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error formatting error response: {e}")
            return "I encountered an unexpected error. Please try again."
    
    def format_empty_results_response(self, question: str) -> str:
        """Format response when no results are found.
        
        Args:
            question: Original user question
            
        Returns:
            User-friendly response for empty results
        """
        try:
            # Analyze the question to provide contextual empty result responses
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['today', 'this week', 'this month']):
                return "I don't see any activity for that time period. You might not have any recorded activity yet."
            elif any(word in question_lower for word in ['github', 'repository', 'commit']):
                return "I don't see any GitHub activity in your data. This might be because no GitHub activity has been recorded yet."
            elif any(word in question_lower for word in ['website', 'web', 'browsing']):
                return "I don't see any web activity in your data. This might be because no web activity has been recorded yet."
            else:
                return "I don't see any data matching your question. This might be because no relevant activity has been recorded yet."
                
        except Exception as e:
            logger.error(f"Error formatting empty results response: {e}")
            return "I don't see any data matching your question."
    
    def _format_modification_response(self, question: str, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format a response for modification requests that can't be executed.
        
        Args:
            question: Original user question
            query_results: Query results with modification flag
            
        Returns:
            Dictionary containing modification response
        """
        try:
            logger.info(f"Formatting modification response for: {question}")
            
            # Create a polite response explaining we can't modify data
            modification_reason = query_results.get("modification_reason", "Data modification detected")
            
            # Generate a helpful response using LLM
            prompt_text = f"""You are a helpful database assistant. A user asked: "{question}"

The user's request involves modifying or updating data in the database, but this system is designed for READ-ONLY operations only. 

Please provide a polite, helpful response that:
1. Acknowledges their request
2. Explains that this is a read-only system
3. Suggests alternative ways to get the information they need
4. Remains friendly and helpful

Do not mention technical details about SQL or security. Keep it conversational and helpful.

Response:"""

            try:
                response = self.model.invoke(prompt_text)
                formatted_response = response.content.strip()
            except Exception as e:
                logger.error(f"Failed to generate modification response: {e}")
                formatted_response = f"I understand you'd like to modify your data, but I can only help you view and analyze your existing information. I can show you your current data and help you understand patterns, but I cannot make changes to the database. Is there something specific you'd like to know about your current data?"
            
            # Sanitize response
            formatted_response = self.response_guard.sanitize_response(formatted_response)
            
            return {
                "success": True,
                "response": formatted_response,
                "results": [],  # No data results for modification requests
                "sql_query": query_results.get("query", ""),
                "timestamp": datetime.now().isoformat(),
                "user_id": query_results.get("user_id", 0),
                "agents_used": ["SQL Generation", "Query Execution", "Response Formatting"],
                "is_modification_request": True
            }
            
        except Exception as e:
            logger.error(f"Error formatting modification response: {e}")
            return {
                "success": True,
                "response": "I understand you'd like to modify your data, but I can only help you view and analyze your existing information. I can show you your current data and help you understand patterns, but I cannot make changes to the database.",
                "results": [],
                "sql_query": query_results.get("query", ""),
                "timestamp": datetime.now().isoformat(),
                "user_id": query_results.get("user_id", 0),
                "agents_used": ["SQL Generation", "Query Execution", "Response Formatting"],
                "is_modification_request": True
            }
    
    def _extract_results_data(self, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from query results for formatting.
        
        Args:
            query_results: Query execution results
            
        Returns:
            Processed results data
        """
        try:
            if not query_results or not query_results.get("success"):
                return {
                    "has_data": False,
                    "row_count": 0,
                    "data": [],
                    "columns": []
                }
            
            results = query_results.get("results", [])
            columns = query_results.get("columns", [])
            row_count = query_results.get("row_count", 0)
            
            return {
                "has_data": len(results) > 0,
                "row_count": row_count,
                "data": results,
                "columns": columns,
                "data_summary": self._summarize_data(results, columns)
            }
            
        except Exception as e:
            logger.error(f"Error extracting results data: {e}")
            return {
                "has_data": False,
                "row_count": 0,
                "data": [],
                "columns": []
            }
    
    def _summarize_data(self, data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
        """Create a summary of the data for better context.
        
        Args:
            data: Query results data
            columns: Column names
            
        Returns:
            Data summary dictionary
        """
        try:
            if not data:
                return {"summary": "No data found"}
            
            summary = {
                "total_records": len(data),
                "date_range": None,
                "numeric_columns": [],
                "text_columns": []
            }
            
            # Analyze columns
            for column in columns:
                if any(keyword in column.lower() for keyword in ['date', 'time', 'created', 'updated']):
                    summary["date_range"] = self._get_date_range(data, column)
                elif any(keyword in column.lower() for keyword in ['count', 'amount', 'time_spent', 'number']):
                    summary["numeric_columns"].append(column)
                else:
                    summary["text_columns"].append(column)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing data: {e}")
            return {"summary": "Data analysis failed"}
    
    def _get_date_range(self, data: List[Dict[str, Any]], date_column: str) -> Optional[Dict[str, str]]:
        """Get date range from data.
        
        Args:
            data: Query results data
            date_column: Name of the date column
            
        Returns:
            Dictionary with min and max dates
        """
        try:
            dates = []
            for row in data:
                if date_column in row and row[date_column]:
                    dates.append(row[date_column])
            
            if dates:
                return {
                    "earliest": min(dates),
                    "latest": max(dates)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return None
    
    def _create_response_prompt(self, question: str, results_data: Dict[str, Any], sql_query: str = None) -> str:
        """Create a comprehensive prompt for response formatting.
        
        Args:
            question: Original user question
            results_data: Processed results data
            sql_query: SQL query that was executed (optional)
            
        Returns:
            Formatted prompt string
        """
        prompt_text = f"""You are a helpful data analyst assistant. Your task is to format database query results into clear, natural language responses.

ORIGINAL USER QUESTION: {question}

QUERY RESULTS:
- Total records found: {results_data.get('row_count', 0)}
- Has data: {results_data.get('has_data', False)}

DATA SUMMARY:
{json.dumps(results_data.get('data_summary', {}), indent=2, default=str, ensure_ascii=False)}

ACTUAL DATA (first 10 records):
{json.dumps(results_data.get('data', [])[:10], indent=2, default=str, ensure_ascii=False)}

RESPONSE GUIDELINES:
1. Provide a direct answer to the user's question
2. Include relevant numbers and insights from the data
3. If no data found, explain what that means in context
4. Keep the response conversational and helpful
5. Highlight interesting patterns or trends if present
6. Use specific numbers when available
7. Keep response concise but informative
8. IMPORTANT: If the data shows time_spent or total_time values, these are in MINUTES, not hours
9. For time-related queries, always specify the unit (minutes, hours, etc.)

RESPONSE FORMAT:
Provide a natural, helpful response that directly answers the user's question:"""

        return prompt_text
    
    def _create_json_response_prompt(self, question: str, results_data: Dict[str, Any], sql_query: str = None) -> str:
        """Create a JSON-formatted prompt for response formatting."""
        return f"""You are a helpful data analyst assistant. Your task is to format database query results into clear, natural language responses with structured data.

ORIGINAL USER QUESTION: {question}

QUERY RESULTS:
- Total records found: {results_data.get('row_count', 0)}
- Has data: {results_data.get('has_data', False)}

DATA SUMMARY:
{json.dumps(results_data.get('data_summary', {}), indent=2, default=str, ensure_ascii=False)}

ACTUAL DATA (first 10 records):
{json.dumps(results_data.get('data', [])[:10], indent=2, default=str, ensure_ascii=False)}

RESPONSE GUIDELINES:
1. Provide a direct answer to the user's question
2. Include relevant numbers and insights from the data
3. If no data found, explain what that means in context
4. Keep the response conversational and helpful
5. Highlight interesting patterns or trends if present
6. Use specific numbers when available
7. Keep response concise but informative
8. IMPORTANT: If the data shows time_spent or total_time values, these are in MINUTES, not hours
9. For time-related queries, always specify the unit (minutes, hours, etc.)

You must respond with a valid JSON object containing:
- "response": Natural language response to the user's question
- "results": Structured array of the actual data results
- "summary": Object with summary statistics and insights
- "metadata": Object with additional metadata about the analysis

For time analysis queries (like "how much time on GitHub vs games"), structure the results like:
{{
  "response": "Based on the data, you spent a total of 80 minutes on GitHub yesterday. However, there is no record of time spent playing games...",
  "results": [
    {{
      "github_time": "80",
      "games_time": null
    }}
  ],
  "summary": {{
    "total_time": "80",
    "most_active_platform": "GitHub",
    "time_distribution": {{"GitHub": 80, "Games": 0}}
  }},
  "metadata": {{
    "analysis_type": "time_comparison",
    "date_range": "yesterday",
    "confidence": 0.95
  }}
}}

Provide a natural, helpful response:"""
    
    def _create_fallback_aggregation_response(self, question: str, results_data: Dict[str, Any]) -> str:
        """Create a fallback response for aggregation queries when LLM fails.
        
        Args:
            question: Original user question
            results_data: Processed results data
            
        Returns:
            Simple fallback response
        """
        try:
            if not results_data.get("has_data"):
                return "I don't see any data matching your question."
            
            data = results_data.get("data", [])
            if not data:
                return "I found no data matching your question."
            
            # Handle single row aggregation results
            if len(data) == 1:
                row = data[0]
                # Look for numeric values
                for key, value in row.items():
                    if isinstance(value, (int, float)) and value is not None:
                        if 'time' in question.lower() and ('time_spent' in key.lower() or 'total_time' in key.lower()):
                            return f"You spent {value} minutes on that activity."
                        elif 'count' in key.lower():
                            return f"The count is {value}."
                        elif 'total' in key.lower():
                            return f"The total is {value}."
                        else:
                            return f"The result is {value}."
            
            return f"I found {len(data)} records matching your question."
            
        except Exception as e:
            logger.error(f"Error creating fallback response: {e}")
            return "I found some data but couldn't format a proper response."
    
    def _parse_gemini_response(self, response_text: str, results_data: Dict[str, Any]) -> Tuple[str, List[Dict], Dict, Dict]:
        """Parse Gemini's text response into structured format."""
        try:
            # For now, use the entire response as the formatted response
            formatted_response = response_text.strip()
            
            # Extract structured results from the actual data
            structured_results = results_data.get("data", [])
            
            # Create basic summary
            summary = {
                "total_records": results_data.get("row_count", 0),
                "has_data": results_data.get("has_data", False)
            }
            
            # Create basic metadata
            metadata = {
                "query_type": "natural_language",
                "data_source": "database",
                "timestamp": datetime.now().isoformat()
            }
            
            return formatted_response, structured_results, summary, metadata
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            # Fallback
            return response_text, results_data.get("data", []), {}, {}
    
    def _create_response_prompt(self, question: str, results_data: Dict[str, Any], sql_query: str = None) -> str:
        """Create a direct response formatting prompt for Gemini."""
        return f"""You are a helpful data analyst assistant. Format the database query results into a clear, natural language response.

ORIGINAL USER QUESTION: {question}

QUERY RESULTS:
- Total records found: {results_data.get('row_count', 0)}
- Has data: {results_data.get('has_data', False)}

DATA SUMMARY:
{json.dumps(results_data.get('data_summary', {}), indent=2, default=str, ensure_ascii=False)}

ACTUAL DATA (first 10 records):
{json.dumps(results_data.get('data', [])[:10], indent=2, default=str, ensure_ascii=False)}

RESPONSE GUIDELINES:
1. Provide a direct answer to the user's question
2. Include relevant numbers and insights from the data
3. If no data found, explain what that means in context
4. Keep the response conversational and helpful
5. Highlight interesting patterns or trends if present
6. Use specific numbers when available
7. Keep response concise but informative
8. IMPORTANT: If the data shows time_spent or total_time values, these are in MINUTES, not hours
9. For time-related queries, always specify the unit (minutes, hours, etc.)

Generate a natural language response:"""

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the response formatting agent."""
        return {
            "agent_type": "Response Formatting Agent",
            "model_name": self.model_name,
            "capabilities": [
                "Natural language response generation",
                "Data summarization",
                "Error response formatting",
                "Empty results handling",
                "Security validation",
                "Context-aware responses"
            ],
            "status": "active"
        }
