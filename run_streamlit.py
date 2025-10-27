#!/usr/bin/env python3
"""
Script to run the Streamlit application.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit application."""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1",
            "--theme.base", "light",
            "--theme.primaryColor", "#667eea",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f8f9fa",
            "--theme.textColor", "#333333"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped!")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

if __name__ == "__main__":
    main()
