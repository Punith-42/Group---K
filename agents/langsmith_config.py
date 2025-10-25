"""
LangSmith Configuration for Web Activity Agent System.
This module sets up LangSmith tracing for the multi-agent system.
"""

import os
from langsmith import Client

def setup_langsmith_tracing():
    """Setup LangSmith tracing configuration."""
    
    # Set environment variables for LangSmith
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "web-activity-agent-system"
    
    # Optional: Set custom endpoint if needed
    if os.getenv("LANGSMITH_ENDPOINT"):
        os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
    
    # Initialize LangSmith client
    try:
        client = Client()
        print("✅ LangSmith tracing initialized successfully")
        print(f"📊 Project: {os.getenv('LANGSMITH_PROJECT')}")
        return client
    except Exception as e:
        print(f"⚠️ LangSmith tracing setup failed: {e}")
        print("📝 Make sure to set LANGSMITH_API_KEY in your .env file")
        return None

def get_trace_url(run_id: str) -> str:
    """Get the LangSmith trace URL for a given run ID."""
    project = os.getenv("LANGSMITH_PROJECT", "web-activity-agent-system")
    return f"https://smith.langchain.com/public/{project}/r/{run_id}"

# Auto-setup when module is imported
if __name__ != "__main__":
    setup_langsmith_tracing()
