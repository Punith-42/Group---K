#!/usr/bin/env python3
"""
FastAPI Application for Web Activity Tracker with LLM Agent System.
This file provides a modern REST API with automatic Swagger UI documentation.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from agents.core.llm_agent import LLMDatabaseAgent
from agents.langsmith_config import setup_langsmith_tracing
from config import Config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Web Activity Agent System",
    description="""
    🚀 **LLM-Powered Database Query System**
    
    This API provides natural language to SQL conversion using specialized AI agents:
    
    * **SQL Generation Agent**: Converts natural language to SQL queries
    * **Query Execution Agent**: Safely executes database queries
    * **Response Formatting Agent**: Formats results into natural language
    * **Schema Awareness Agent**: Provides database schema information
    
    ## Features
    - 🔒 **Secure**: User isolation and SQL injection protection
    - 📊 **Traced**: Full LangSmith tracing for debugging
    - 🎯 **Accurate**: Database schema awareness for precise queries
    - 📝 **Documented**: Automatic API documentation with Swagger UI
    """,
    version="1.0.0",
    contact={
        "name": "Web Activity Agent System",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            "description": "Development server"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent_instance: Optional[LLMDatabaseAgent] = None

# Pydantic Models for Request/Response
class AgentRequest(BaseModel):
    """Request model for agent queries."""
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="Natural language question about your data",
        example="How much time did I spend on YouTube today?"
    )
    user_id: int = Field(
        ..., 
        gt=0,
        description="User ID for data filtering and security",
        example=1
    )

class SQLValidationRequest(BaseModel):
    """Request model for SQL validation."""
    sql_query: str = Field(
        ...,
        min_length=1,
        description="SQL query to validate",
        example="SELECT * FROM web_activity WHERE user_id = 1"
    )
    user_id: int = Field(
        ...,
        gt=0,
        description="User ID for security validation",
        example=1
    )

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="System health status")
    agent: str = Field(..., description="Agent status")
    database: str = Field(..., description="Database connection status")
    model: Optional[str] = Field(None, description="LLM model name")
    specialized_agents: Optional[int] = Field(None, description="Number of specialized agents")
    timestamp: str = Field(..., description="Health check timestamp")

class SystemInfoResponse(BaseModel):
    """System information response model."""
    success: bool
    system_info: Dict[str, Any]

class QueryExamplesResponse(BaseModel):
    """Query examples response model."""
    success: bool
    examples: List[Dict[str, str]]

# Dependency to get agent instance
async def get_agent() -> LLMDatabaseAgent:
    """Dependency to get the agent instance."""
    if not agent_instance:
        raise HTTPException(
            status_code=500, 
            detail="Agent not initialized. Please check system configuration."
        )
    return agent_instance

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup."""
    global agent_instance
    
    try:
        logger.info("Starting Web Activity Tracker with LLM Agent System...")
        
        # Get Gemini API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return
        
    # Get model name
    model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-pro")
        
        # Initialize LangSmith tracing
        langsmith_client = setup_langsmith_tracing()
        
        # Initialize the agent
        agent_instance = LLMDatabaseAgent(gemini_api_key, model_name)
        
        logger.info("✅ Agent system initialized successfully")
        logger.info(f"📊 Model: {model_name}")
        logger.info(f"🔍 LangSmith tracing: {'Enabled' if langsmith_client else 'Disabled'}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent system: {e}")
        agent_instance = None

# Root endpoint
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with system information."""
    return {
        "message": "🚀 Web Activity Agent System",
        "description": "LLM-powered database query system with natural language processing",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/agent/health"
    }

# Agent endpoints
@app.post("/api/agent/ask", response_model=Dict[str, Any])
async def ask_question(
    request: AgentRequest,
    agent: LLMDatabaseAgent = Depends(get_agent)
):
    """
    Ask a natural language question to the database agent.
    
    This endpoint processes natural language questions and returns structured responses
    with SQL queries, results, and formatted answers.
    """
    try:
        logger.info(f"Processing question for user {request.user_id}: {request.question}")
        
        # Process question with agent
        result = agent.process_question(request.question, request.user_id)
        
        # Return appropriate status code based on success
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_question endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Internal server error",
                "response": "I encountered an unexpected error. Please try again."
            }
        )

@app.post("/api/agent/validate-query", response_model=Dict[str, Any])
async def validate_query(
    request: SQLValidationRequest,
    agent: LLMDatabaseAgent = Depends(get_agent)
):
    """
    Validate a SQL query using the agent's security guards.
    
    This endpoint checks SQL queries for security issues and validates
    their structure before execution.
    """
    try:
        logger.info(f"Validating SQL query for user {request.user_id}")
        
        # Validate query using security guards
        is_safe, reason = agent.query_guard.validate_query(request.sql_query, request.user_id)
        
        return {
            "success": True,
            "is_safe": is_safe,
            "reason": reason,
            "sql_query": request.sql_query,
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in validate_query endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Internal server error"
            }
        )

@app.get("/api/agent/info", response_model=SystemInfoResponse)
async def get_agent_info(agent: LLMDatabaseAgent = Depends(get_agent)):
    """
    Get detailed information about the agent system.
    
    Returns information about all specialized agents, their capabilities,
    and system configuration.
    """
    try:
        info = agent.get_agent_info()
        return SystemInfoResponse(
            success=True,
            system_info=info
        )
        
    except Exception as e:
        logger.error(f"Error in get_agent_info endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Internal server error"
            }
        )

@app.get("/api/agent/examples", response_model=QueryExamplesResponse)
async def get_query_examples(agent: LLMDatabaseAgent = Depends(get_agent)):
    """
    Get example queries for the database.
    
    Returns a list of example natural language questions and their
    corresponding SQL queries for reference.
    """
    try:
        examples = agent.schema_agent.get_query_examples()
        return QueryExamplesResponse(
            success=True,
            examples=examples
        )
        
    except Exception as e:
        logger.error(f"Error in get_query_examples endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Internal server error"
            }
        )

@app.get("/api/agent/health", response_model=HealthResponse)
async def agent_health(agent: LLMDatabaseAgent = Depends(get_agent)):
    """
    Health check for the agent system.
    
    Checks the status of the agent system, database connection,
    and all specialized agents.
    """
    try:
        # Test database connection
        db_healthy = agent.query_execution_agent.validate_database_connection()
        
        agent_info = agent.get_agent_info()
        
        return HealthResponse(
            status="healthy" if db_healthy else "unhealthy",
            agent="active",
            database="connected" if db_healthy else "disconnected",
            model=agent.model_name,
            specialized_agents=len(agent_info['specialized_agents']),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in agent_health endpoint: {e}")
        return HealthResponse(
            status="unhealthy",
            agent="inactive",
            database="unknown",
            timestamp=datetime.now().isoformat()
        )

# Basic health check
@app.get("/api/health", response_model=Dict[str, str])
async def basic_health():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Web Activity Agent System"
    }

# System status
@app.get("/api/status", response_model=Dict[str, Any])
async def system_status():
    """Get system status information."""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "database": Config.DATABASE_NAME,
        "host": Config.DATABASE_HOST,
        "agent_initialized": agent_instance is not None,
        "langsmith_enabled": os.getenv("LANGSMITH_API_KEY") is not None
    }

# Redirect root to docs
@app.get("/docs")
async def redirect_to_docs():
    """Redirect to Swagger UI documentation."""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info("🚀 Starting FastAPI server...")
    logger.info(f"📊 Host: {host}:{port}")
    logger.info(f"📚 Swagger UI: http://{host}:{port}/docs")
    logger.info(f"📖 ReDoc: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "main_fastapi:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
