"""
Pydantic schemas for structured JSON responses in LLM Agent System.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

class QueryResult(BaseModel):
    """Individual query result item."""
    pass  # Will be dynamically created based on query results

class SQLQueryResponse(BaseModel):
    """Structured response for SQL query generation."""
    sql_query: str = Field(description="The generated SQL query")
    reasoning: str = Field(description="Brief explanation of the query logic")
    confidence: float = Field(description="Confidence score between 0 and 1", ge=0, le=1)

class DataAnalysisResponse(BaseModel):
    """Structured response for data analysis and formatting."""
    response: str = Field(description="Natural language response to the user's question")
    results: List[Dict[str, Any]] = Field(description="Structured data results from the query")
    summary: Dict[str, Any] = Field(description="Summary statistics and insights")
    metadata: Dict[str, Any] = Field(description="Additional metadata about the analysis")

class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str = Field(description="Error message")
    error_type: str = Field(description="Type of error (sql, database, security, etc.)")
    suggestion: str = Field(description="Suggestion for resolving the error")

class AgentResponse(BaseModel):
    """Main response structure for the agent system."""
    success: bool = Field(description="Whether the operation was successful")
    response: str = Field(description="Natural language response to the user")
    results: List[Dict[str, Any]] = Field(description="Structured query results")
    sql_query: Optional[str] = Field(description="The SQL query that was executed", default=None)
    agents_used: List[str] = Field(description="List of agents that were used in processing")
    timestamp: str = Field(description="Timestamp of the response")
    user_id: int = Field(description="User ID for the query")
    execution_time: Optional[str] = Field(description="Query execution time", default=None)
    error: Optional[str] = Field(description="Error message if any", default=None)

class WebActivityResult(BaseModel):
    """Structured result for web activity queries."""
    website_name: Optional[str] = None
    time_spent: Optional[int] = None
    activity_date: Optional[str] = None
    total_time: Optional[int] = None
    visit_count: Optional[int] = None

class GitHubActivityResult(BaseModel):
    """Structured result for GitHub activity queries."""
    repository_name: Optional[str] = None
    activity_type: Optional[str] = None
    commit_count: Optional[int] = None
    activity_date: Optional[str] = None
    total_commits: Optional[int] = None
    total_activities: Optional[int] = None

class TimeAnalysisResult(BaseModel):
    """Structured result for time analysis queries."""
    github_time: Optional[str] = None
    games_time: Optional[str] = None
    youtube_time: Optional[str] = None
    total_time: Optional[str] = None
    website_name: Optional[str] = None
    time_spent: Optional[int] = None

class AggregationResult(BaseModel):
    """Structured result for aggregation queries."""
    total_time: Optional[str] = None
    total_count: Optional[int] = None
    average_time: Optional[float] = None
    max_time: Optional[int] = None
    min_time: Optional[int] = None
    website_name: Optional[str] = None
    activity_type: Optional[str] = None
