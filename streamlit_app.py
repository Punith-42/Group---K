#!/usr/bin/env python3
"""
Streamlit Application for Web Activity Agent System.
Interactive chatbot interface for natural language database queries.
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
    page_title="🤖 Web Activity Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode toggle
def toggle_dark_mode():
    """Toggle dark mode for the application."""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# Custom CSS for modern chatbot design with dark mode support
def get_css(dark_mode=False):
    """Get CSS styles based on dark mode setting."""
    if dark_mode:
        return """
        <style>
            /* Dark mode styles */
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            .chat-container {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-in;
            }
            
            .user-message {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                text-align: right;
                border-bottom-right-radius: 5px;
            }
            
            .bot-message {
                background: #2d3748;
                color: #ffffff !important;
                margin-right: auto;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
            
            .message-content {
                font-size: 16px;
                line-height: 1.5;
            }
            
            .message-time {
                font-size: 12px;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .input-container {
                background: #2d3748;
                border-radius: 25px;
                padding: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                margin-top: 20px;
            }
            
            .sql-container {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                overflow-x: auto;
                color: #ffffff !important;
            }
            
            .results-container {
                background: #2d3748;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid #4a5568;
                color: #ffffff !important;
            }
            
            .status-online {
                color: #68d391;
                font-weight: bold;
            }
            
            .status-offline {
                color: #fc8181;
                font-weight: bold;
            }
            
            /* Dark mode specific overrides */
            .stApp {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            /* Global text color for dark mode */
            .stApp * {
                color: #ffffff !important;
            }
            
            /* Override specific Streamlit components */
            .stTextInput > div > div > input {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .stSelectbox > div > div > select {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .stDataFrame {
                background-color: #2d3748;
                color: #ffffff !important;
            }
            
            .stNumberInput > div > div > input {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            /* Override Streamlit text elements */
            .stMarkdown {
                color: #ffffff !important;
            }
            
            .stMarkdown p {
                color: #ffffff !important;
            }
            
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
                color: #ffffff !important;
            }
            
            /* Override info boxes */
            .stInfo {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .stSuccess {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .stError {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .stWarning {
                background-color: #2d3748;
                color: #ffffff !important;
                border: 1px solid #4a5568;
            }
            
            .sidebar .sidebar-content {
                background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
                color: #ffffff !important;
            }
            
            /* Override sidebar text elements */
            .sidebar .stMarkdown {
                color: #ffffff !important;
            }
            
            .sidebar .stMarkdown p {
                color: #ffffff !important;
            }
            
            .sidebar .stMarkdown h1, .sidebar .stMarkdown h2, .sidebar .stMarkdown h3, .sidebar .stMarkdown h4, .sidebar .stMarkdown h5, .sidebar .stMarkdown h6 {
                color: #ffffff !important;
            }
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .loading {
                animation: pulse 1.5s infinite;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 25px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
        """
    else:
        return """
        <style>
            /* Light mode styles */
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .chat-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-in;
            }
            
            .user-message {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                text-align: right;
                border-bottom-right-radius: 5px;
            }
            
            .bot-message {
                background: white;
                color: #333;
                margin-right: auto;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .message-content {
                font-size: 16px;
                line-height: 1.5;
            }
            
            .message-time {
                font-size: 12px;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .input-container {
                background: white;
                border-radius: 25px;
                padding: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            
            .sql-container {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                overflow-x: auto;
            }
            
            .results-container {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid #e9ecef;
            }
            
            .status-online {
                color: #28a745;
                font-weight: bold;
            }
            
            .status-offline {
                color: #dc3545;
                font-weight: bold;
            }
            
            .sidebar .sidebar-content {
                background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
            }
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .loading {
                animation: pulse 1.5s infinite;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 25px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
        """

# Apply CSS based on dark mode setting
dark_mode = st.session_state.get('dark_mode', False)
st.markdown(get_css(dark_mode), unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://127.0.0.1:5001"  # Updated to port 5001
USER_ID = 1  # Default user ID

class AgentClient:
    """Client for interacting with the Flask backend."""
    
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
                "response": "I'm having trouble connecting to the agent system. Please check if the Flask server is running."
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

def display_chat_message(message: str, is_user: bool = False, timestamp: datetime = None):
    """Display a chat message with modern styling."""
    message_class = "user-message" if is_user else "bot-message"
    time_str = timestamp.strftime("%H:%M") if timestamp else datetime.now().strftime("%H:%M")
    
    st.markdown(f"""
    <div class="message {message_class}">
        <div class="message-content">{message}</div>
        <div class="message-time">{time_str}</div>
    </div>
    """, unsafe_allow_html=True)

def display_sql_query(sql_query: str):
    """Display SQL query in a formatted container."""
    st.markdown("**🔍 Generated SQL Query:**")
    st.markdown(f'<div class="sql-container">{sql_query}</div>', unsafe_allow_html=True)

def display_results(results: List[Dict[str, Any]], question: str):
    """Display query results with modern styling."""
    if not results:
        st.info("📭 No data found for your query.")
        return
    
    st.markdown(f'<div class="results-container">', unsafe_allow_html=True)
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(results)
    
    # Display basic info
    st.markdown(f"**📊 Found {len(results)} results**")
    
    # Display as table
    st.dataframe(df, width='stretch')
    
    # Create visualizations based on data
    if len(df) > 1:
        create_visualizations(df, question)
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_visualizations(df: pd.DataFrame, question: str):
    """Create visualizations based on the data."""
    st.markdown("**📈 Data Analysis:**")
    
    # Display basic statistics for numeric data
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.markdown("**📊 Numeric Data Summary:**")
        st.dataframe(df[numeric_cols].describe(), width='stretch')
    
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
    st.markdown('<h1 class="main-header">🤖 Web Activity Agent Chat</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about your web activity and GitHub data in natural language!</p>', unsafe_allow_html=True)
    
    # Initialize client
    client = AgentClient(API_BASE_URL)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.markdown("## 🔧 System Status")
        
        # Health check
        health_status = client.get_health_status()
        if health_status.get("status") == "healthy":
            st.markdown('<p class="status-online">✅ System Online</p>', unsafe_allow_html=True)
            st.info(f"🤖 Agent: {health_status.get('agent', 'Unknown')}")
            st.info(f"🗄️ Database: {health_status.get('database', 'Unknown')}")
            st.info(f"🧠 Model: {health_status.get('model', 'Unknown')}")
        else:
            st.markdown('<p class="status-offline">❌ System Offline</p>', unsafe_allow_html=True)
            st.error("Please ensure the Flask server is running on port 5001")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # Settings
        st.markdown("## ⚙️ Settings")
        user_id = st.number_input("User ID", min_value=1, value=USER_ID, step=1)
        
        # Dark mode toggle
        dark_mode_icon = "🌙" if dark_mode else "☀️"
        dark_mode_text = "Dark Mode" if dark_mode else "Light Mode"
        if st.button(f"{dark_mode_icon} Switch to {'Light' if dark_mode else 'Dark'} Mode"):
            toggle_dark_mode()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            if 'chat_history' in st.session_state:
                del st.session_state.chat_history
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            display_chat_message(
                message['content'], 
                message['is_user'], 
                message.get('timestamp', datetime.now())
            )
            
            # Display SQL query and results for bot messages
            if not message['is_user'] and message.get('sql_query'):
                display_sql_query(message['sql_query'])
            
            if not message['is_user'] and message.get('results'):
                display_results(message['results'], message.get('question', ''))
    else:
        st.markdown("👋 Welcome! Ask me anything about your web activity and GitHub data.")
        st.markdown("💡 Try asking: *'How much time did I spend on YouTube today?'*")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle example question
    if hasattr(st.session_state, 'example_question'):
        question = st.session_state.example_question
        delattr(st.session_state, 'example_question')
    else:
        # Question input
        question = st.text_input(
            "💬 Ask a question about your data:",
            placeholder="e.g., How much time did I spend on YouTube today?",
            key="question_input"
        )
    
    # Process question
    if question and st.button("🚀 Send", type="primary"):
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
                'content': f"❌ {agent_response}",
                'is_user': False,
                'question': question,
                'timestamp': datetime.now()
            })
            
            # Display error message
            st.error(f"❌ Error: {error_msg}")
        
        # Rerun to update display
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🤖 Powered by LLM Agent System | 
        🚀 Flask Backend | 
        📊 Streamlit Frontend |
        🔍 LangSmith Tracing
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()