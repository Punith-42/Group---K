#!/usr/bin/env python3
"""
Streamlit Application for Web Activity Agent System.
Interactive chat interface for natural language database queries.
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="🤖 Web Activity Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .agent-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .sql-query {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://127.0.0.1:5000"
USER_ID = 1  # Default user ID

class AgentClient:
    """Client for interacting with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def ask_question(self, question: str, user_id: int = USER_ID) -> Dict[str, Any]:
        """Ask a question to the agent system."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/agent/ask",
                json={"question": question, "user_id": user_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API Error: {str(e)}",
                "response": "I'm having trouble connecting to the agent system. Please check if the FastAPI server is running."
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            response = self.session.get(f"{self.base_url}/api/agent/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"status": "unhealthy", "error": "Cannot connect to API"}
    
    def get_examples(self) -> List[Dict[str, str]]:
        """Get example queries."""
        try:
            response = self.session.get(f"{self.base_url}/api/agent/examples", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("examples", [])
        except requests.exceptions.RequestException:
            return []

def display_chat_message(message: str, is_user: bool = False):
    """Display a chat message with appropriate styling."""
    css_class = "user-message" if is_user else "agent-message"
    st.markdown(f'<div class="chat-message {css_class}">{message}</div>', unsafe_allow_html=True)

def display_sql_query(sql_query: str):
    """Display SQL query in a formatted code block."""
    st.markdown("**🔍 Generated SQL Query:**")
    st.markdown(f'<div class="sql-query">{sql_query}</div>', unsafe_allow_html=True)

def display_results(results: List[Dict[str, Any]], question: str):
    """Display query results in various formats."""
    if not results:
        st.info("No data found for your query.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(results)
    
    # Display basic info
    st.markdown(f"**📊 Found {len(results)} results**")
    
    # Display as table
    st.dataframe(df, use_container_width=True)
    
    # Create visualizations based on data
    if len(df) > 1:
        create_visualizations(df, question)

def create_visualizations(df: pd.DataFrame, question: str):
    """Create simple visualizations based on the data."""
    st.markdown("**📈 Data Analysis:**")
    
    # Display basic statistics for numeric data
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.markdown("**📊 Numeric Data Summary:**")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
    # Display charts for categorical data
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        st.markdown("**📋 Categorical Data Charts:**")
        
        # Create columns for charts
        chart_cols = st.columns(min(len(categorical_cols), 2))
        
        for i, col in enumerate(categorical_cols[:2]):  # Show first 2 categorical columns
            if df[col].nunique() <= 15:  # Only show if not too many unique values
                with chart_cols[i % 2]:
                    st.markdown(f"**{col.replace('_', ' ').title()} Distribution:**")
                    value_counts = df[col].value_counts().head(10)
                    st.bar_chart(value_counts)
            elif i == 0:  # Show first column even if many values
                with chart_cols[0]:
                    st.markdown(f"**{col.replace('_', ' ').title()} (Top 10):**")
                    value_counts = df[col].value_counts().head(10)
                    st.bar_chart(value_counts)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Web Activity Agent System</h1>', unsafe_allow_html=True)
    st.markdown("**Ask questions about your web activity and GitHub data in natural language!**")
    
    # Initialize client
    client = AgentClient(API_BASE_URL)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 System Status")
        
        # Health check
        health_status = client.get_health_status()
        if health_status.get("status") == "healthy":
            st.success("✅ System Online")
            st.info(f"🤖 Agent: {health_status.get('agent', 'Unknown')}")
            st.info(f"🗄️ Database: {health_status.get('database', 'Unknown')}")
            st.info(f"🧠 Model: {health_status.get('model', 'Unknown')}")
        else:
            st.error("❌ System Offline")
            st.error("Please ensure the FastAPI server is running on port 5000")
        
        st.markdown("---")
        
        # Example queries
        st.markdown("## 💡 Example Questions")
        examples = client.get_examples()
        
        if examples:
            for i, example in enumerate(examples[:5]):  # Show first 5 examples
                if st.button(f"💬 {example['question']}", key=f"example_{i}"):
                    st.session_state.example_question = example['question']
                    st.rerun()
        else:
            st.info("No examples available")
        
        st.markdown("---")
        
        # Settings
        st.markdown("## ⚙️ Settings")
        user_id = st.number_input("User ID", min_value=1, value=USER_ID, step=1)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            if 'chat_history' in st.session_state:
                del st.session_state.chat_history
            st.rerun()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Main chat interface
    st.markdown("## 💬 Chat with Your Data")
    
    # Display chat history
    for message in st.session_state.chat_history:
        display_chat_message(message['content'], message['is_user'])
    
    # Handle example question
    if hasattr(st.session_state, 'example_question'):
        question = st.session_state.example_question
        delattr(st.session_state, 'example_question')
    else:
        # Question input
        question = st.text_input(
            "Ask a question about your data:",
            placeholder="e.g., How much time did I spend on YouTube today?",
            key="question_input"
        )
    
    # Process question
    if question and st.button("🚀 Ask Question", type="primary"):
        # Add user message to history
        st.session_state.chat_history.append({
            'content': question,
            'is_user': True,
            'timestamp': datetime.now()
        })
        
        # Show loading spinner
        with st.spinner("🤖 Thinking..."):
            # Get response from agent
            response = client.ask_question(question, user_id)
        
        # Process response
        if response.get('success'):
            # Success response
            agent_response = response.get('response', 'No response generated')
            results = response.get('results', [])
            sql_query = response.get('sql_query', '')
            
            # Add agent response to history
            st.session_state.chat_history.append({
                'content': agent_response,
                'is_user': False,
                'question': question,
                'results': results,
                'sql_query': sql_query,
                'timestamp': datetime.now()
            })
            
            # Display success message
            st.success("✅ Query executed successfully!")
            
        else:
            # Error response
            error_msg = response.get('error', 'Unknown error occurred')
            agent_response = response.get('response', 'I encountered an error processing your request.')
            
            # Add error to history
            st.session_state.chat_history.append({
                'content': f"❌ Error: {error_msg}\n\n{agent_response}",
                'is_user': False,
                'question': question,
                'timestamp': datetime.now()
            })
            
            # Display error message
            st.error(f"❌ Error: {error_msg}")
        
        # Rerun to update display
        st.rerun()
    
    # Display all results and visualizations at the end
    st.markdown("---")
    st.markdown("## 📊 Results & Visualizations")
    
    # Collect all results from chat history
    all_results = []
    for message in st.session_state.chat_history:
        if not message['is_user'] and message.get('results'):
            all_results.append({
                'question': message.get('question', ''),
                'results': message['results'],
                'sql_query': message.get('sql_query', ''),
                'timestamp': message.get('timestamp', datetime.now())
            })
    
    # Display results in reverse chronological order (newest first)
    for i, result_data in enumerate(reversed(all_results)):
        if i > 0:  # Add separator between different queries
            st.markdown("---")
        
        # Use expander for each query result
        with st.expander(f"🔍 Query {len(all_results) - i}: {result_data['question'][:50]}{'...' if len(result_data['question']) > 50 else ''}", expanded=(i == 0)):
            # Show SQL query if available
            if result_data['sql_query']:
                display_sql_query(result_data['sql_query'])
            
            # Show results
            display_results(result_data['results'], result_data['question'])
    
    if not all_results:
        st.info("No results to display yet. Ask a question to see data visualizations!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🤖 Powered by LLM Agent System | 
        🚀 FastAPI Backend | 
        📊 Streamlit Frontend |
        🔍 LangSmith Tracing
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
