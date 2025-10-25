"""
LLM Agent for Database Query Processing.
Enhanced orchestration system with specialized agents for different tasks.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from agents.core.sql_agent import SQLGenerationAgent
from agents.core.query_execution_agent import QueryExecutionAgent
from agents.core.response_formatting_agent import ResponseFormattingAgent
from agents.core.schema_agent import SchemaAwarenessAgent
from agents.guards.security_guards import QuerySecurityGuard, ResponseSecurityGuard
from agents.schemas import AgentResponse

logger = logging.getLogger(__name__)

class LLMDatabaseAgent:
    """LLM-powered database agent for natural language queries."""
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        """Initialize the LLM database agent with specialized agents.
        
        Args:
            openai_api_key: OpenAI API key
            model_name: OpenAI model name
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        
        # Initialize specialized agents
        self.schema_agent = SchemaAwarenessAgent()
        self.sql_agent = SQLGenerationAgent(openai_api_key, model_name)
        self.query_execution_agent = QueryExecutionAgent()
        self.response_formatting_agent = ResponseFormattingAgent(openai_api_key, model_name)
        
        # Initialize security guards
        self.query_guard = QuerySecurityGuard()
        self.response_guard = ResponseSecurityGuard()
        
        # Initialize main LLM for orchestration
        self._setup_llm()
        
        logger.info(f"LLMDatabaseAgent initialized with model: {model_name}")
        logger.info("Specialized agents: Schema, SQL Generation, Query Execution, Response Formatting")
    
    def _setup_llm(self):
        """Setup the OpenAI LLM."""
        try:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required")
            
            self.model = ChatOpenAI(
                api_key=self.openai_api_key,
                model_name=self.model_name,
                temperature=0.1  # Low temperature for consistent SQL generation
            )
            self.parser = StrOutputParser()
            
            logger.info("OpenAI LLM setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup OpenAI LLM: {e}")
            raise
    
    def process_question(self, question: str, user_id: int) -> Dict[str, Any]:
        """Process a natural language question using specialized agents.
        
        Args:
            question: User's natural language question
            user_id: User ID for database filtering
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            logger.info(f"Processing question for user {user_id}: {question}")
            
            # Step 1: Generate SQL query using SQL Generation Agent
            sql_query = self._generate_sql_query(question, user_id)
            if not sql_query:
                return {
                    "success": False,
                    "error": "Failed to generate SQL query",
                    "response": self.response_formatting_agent.format_error_response(
                        question, "SQL generation failed", "sql"
                    )
                }
            
            # Step 2: Execute query using Query Execution Agent
            query_results = self.query_execution_agent.execute_query(sql_query, user_id)
            if not query_results["success"]:
                return {
                    "success": False,
                    "error": query_results["error"],
                    "response": self.response_formatting_agent.format_error_response(
                        question, query_results["error"], "database"
                    )
                }
            
            # Step 3: Format response using Response Formatting Agent
            if query_results["row_count"] == 0:
                formatted_response = self.response_formatting_agent.format_empty_results_response(question)
                structured_response = {
                    "response": formatted_response,
                    "results": [],
                    "summary": {},
                    "metadata": {}
                }
            else:
                structured_response = self.response_formatting_agent.format_response(
                    question, query_results, sql_query
                )
            
            if not structured_response or not structured_response.get("response"):
                return {
                    "success": False,
                    "error": "Failed to format response",
                    "response": "I found the data but couldn't format a proper response.",
                    "results": []
                }
            
            logger.info(f"Successfully processed question for user {user_id}")
            return {
                "success": True,
                "response": structured_response["response"],
                "results": structured_response["results"],
                "sql_query": sql_query,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "agents_used": ["SQL Generation", "Query Execution", "Response Formatting"]
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": self.response_formatting_agent.format_error_response(
                    question, str(e), "general"
                )
            }
    
    def _generate_sql_query(self, question: str, user_id: int) -> Optional[str]:
        """Generate SQL query from natural language question using specialized SQL agent."""
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            sql_query = self.sql_agent.generate_sql_query(question, user_id, current_date)
            
            if sql_query:
                logger.debug(f"Generated SQL query: {sql_query}")
                return sql_query
            else:
                logger.warning("SQL agent failed to generate query")
                return None
                
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return None
    
    def validate_query_with_llm(self, sql_query: str) -> bool:
        """Use LLM to validate SQL query (additional security layer)."""
        try:
            # Render validation prompt
            prompt_text = self.prompt_manager.render_query_validation_prompt(sql_query)
            
            # Create prompt template
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=[]
            )
            
            # Get validation response
            response = (prompt | self.model | self.parser).invoke({})
            
            # Check if LLM says query is safe
            return "SAFE" in response.upper()
            
        except Exception as e:
            logger.error(f"Error in LLM query validation: {e}")
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent and all specialized agents."""
        return {
            "main_agent": {
                "model_name": self.model_name,
                "status": "active",
                "type": "LLM Database Orchestrator"
            },
            "specialized_agents": {
                "schema_agent": self.schema_agent.get_agent_info(),
                "sql_generation_agent": self.sql_agent.get_agent_info(),
                "query_execution_agent": self.query_execution_agent.get_agent_info(),
                "response_formatting_agent": self.response_formatting_agent.get_agent_info()
            },
            "security_level": self.query_guard.security_level.value,
            "capabilities": [
                "Natural language to SQL conversion",
                "Safe query execution",
                "Response formatting",
                "Database schema awareness",
                "Multi-agent orchestration"
            ]
        }
