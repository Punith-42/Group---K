"""
API endpoints for LLM Agent System.
Provides REST API for natural language database queries.
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from agents.core.llm_agent import LLMDatabaseAgent

logger = logging.getLogger(__name__)

# Create blueprint for agent API
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# Global agent instance (will be initialized in main.py)
agent_instance = None

def init_agent(gemini_api_key: str, model_name: str = "models/gemini-2.5-pro"):
    """Initialize the global agent instance.
    
    Args:
        gemini_api_key: Google Gemini API key
        model_name: Gemini model name
    """
    global agent_instance
    try:
        agent_instance = LLMDatabaseAgent(gemini_api_key, model_name)
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

@agent_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a natural language question to the database agent."""
    try:
        if not agent_instance:
            return jsonify({
                "success": False,
                "error": "Agent not initialized"
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        question = data.get('question')
        user_id = data.get('user_id')
        
        if not question:
            return jsonify({
                "success": False,
                "error": "question parameter is required"
            }), 400
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id parameter is required"
            }), 400
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({
                    "success": False,
                    "error": "user_id must be a positive integer"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "user_id must be a valid integer"
            }), 400
        
        # Process question with agent
        result = agent_instance.process_question(question, user_id)
        
        # Return appropriate status code based on success
        status_code = 200 if result.get('success', False) else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in ask_question endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "response": "I encountered an unexpected error. Please try again."
        }), 500

@agent_bp.route('/validate-query', methods=['POST'])
def validate_query():
    """Validate a SQL query using the agent's security guards."""
    try:
        if not agent_instance:
            return jsonify({
                "success": False,
                "error": "Agent not initialized"
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        sql_query = data.get('sql_query')
        user_id = data.get('user_id')
        
        if not sql_query:
            return jsonify({
                "success": False,
                "error": "sql_query parameter is required"
            }), 400
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id parameter is required"
            }), 400
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({
                    "success": False,
                    "error": "user_id must be a positive integer"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "user_id must be a valid integer"
            }), 400
        
        # Validate query using query execution agent
        syntax_result = agent_instance.query_execution_agent.test_query_syntax(sql_query)
        
        # Additional security validation
        is_safe, reason = agent_instance.query_guard.validate_query(sql_query, user_id)
        
        return jsonify({
            "success": True,
            "is_safe": is_safe and syntax_result['syntax_valid'],
            "reason": reason,
            "syntax_valid": syntax_result['syntax_valid'],
            "sql_query": sql_query,
            "validation_details": syntax_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in validate_query endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@agent_bp.route('/info', methods=['GET'])
def get_agent_info():
    """Get information about the agent."""
    try:
        if not agent_instance:
            return jsonify({
                "success": False,
                "error": "Agent not initialized"
            }), 500
        
        info = agent_instance.get_agent_info()
        return jsonify({
            "success": True,
            "agent_info": info
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_agent_info endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@agent_bp.route('/examples', methods=['GET'])
def get_query_examples():
    """Get example queries for the database."""
    try:
        if not agent_instance:
            return jsonify({
                "success": False,
                "error": "Agent not initialized"
            }), 500
        
        examples = agent_instance.schema_agent.get_query_examples()
        return jsonify({
            "success": True,
            "examples": examples
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_query_examples endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@agent_bp.route('/health', methods=['GET'])
def agent_health():
    """Health check for the agent system."""
    try:
        if not agent_instance:
            return jsonify({
                "status": "unhealthy",
                "error": "Agent not initialized"
            }), 500
        
        # Test database connection using query execution agent
        db_healthy = agent_instance.query_execution_agent.validate_database_connection()
        
        if db_healthy:
            return jsonify({
                "status": "healthy",
                "agent": "active",
                "database": "connected",
                "model": agent_instance.model_name,
                "specialized_agents": len(agent_instance.get_agent_info()['specialized_agents'])
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "agent": "active",
                "database": "disconnected"
            }), 500
        
    except Exception as e:
        logger.error(f"Error in agent_health endpoint: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
