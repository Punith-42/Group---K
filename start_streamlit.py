#!/usr/bin/env python3
"""
Streamlit Startup Script for Web Activity Agent System.
This script starts the Streamlit application with proper configuration.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_fastapi_server():
    """Check if FastAPI server is running."""
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_streamlit():
    """Start the Streamlit application."""
    
    print("🚀 Starting Web Activity Agent System - Streamlit App")
    print("=" * 60)
    
    # Check if FastAPI server is running
    print("🔍 Checking FastAPI server status...")
    if not check_fastapi_server():
        print("❌ FastAPI server is not running!")
        print("📝 Please start the FastAPI server first:")
        print("   python main_fastapi.py")
        print("   or")
        print("   uvicorn main_fastapi:app --host 127.0.0.1 --port 5000 --reload")
        print()
        print("⏳ Waiting for FastAPI server to start...")
        
        # Wait for server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            if check_fastapi_server():
                print("✅ FastAPI server is now running!")
                break
            print(f"⏳ Attempt {attempt + 1}/{max_attempts} - Waiting...")
            time.sleep(2)
        else:
            print("❌ FastAPI server did not start. Please start it manually.")
            return False
    else:
        print("✅ FastAPI server is running!")
    
    print()
    print("📊 Streamlit Configuration:")
    print("   Host: localhost")
    print("   Port: 8501")
    print("   URL: http://localhost:8501")
    print()
    print("🔗 Available Services:")
    print("   FastAPI Backend: http://127.0.0.1:5000")
    print("   Streamlit Frontend: http://localhost:8501")
    print("   FastAPI Docs: http://127.0.0.1:5000/docs")
    print("=" * 60)
    
    # Start Streamlit
    try:
        print("🎨 Starting Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped.")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_streamlit()
