#!/usr/bin/env python3
"""
FastAPI Startup Script for Web Activity Agent System.
This script starts the FastAPI server with proper configuration.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI server."""
    
    # Get configuration
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    
    print("🚀 Starting Web Activity Tracker with FastAPI...")
    print("=" * 60)
    print("📊 FastAPI Server Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print("=" * 60)
    print("📚 API Documentation:")
    print(f"   Swagger UI: http://{host}:{port}/docs")
    print(f"   ReDoc: http://{host}:{port}/redoc")
    print(f"   OpenAPI JSON: http://{host}:{port}/openapi.json")
    print("=" * 60)
    print("🔗 Available Endpoints:")
    print("   POST /api/agent/ask          - Ask natural language questions")
    print("   POST /api/agent/validate-query - Validate SQL queries")
    print("   GET  /api/agent/info         - Agent system information")
    print("   GET  /api/agent/examples     - Query examples")
    print("   GET  /api/agent/health       - Health check")
    print("   GET  /api/health             - Basic health check")
    print("   GET  /api/status             - System status")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "main_fastapi:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
