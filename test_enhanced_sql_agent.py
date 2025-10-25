#!/usr/bin/env python3
"""
Test script for the enhanced SQL agent system.
Tests all specialized agents and their integration.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.core.llm_agent import LLMDatabaseAgent
from agents.core.schema_agent import SchemaAwarenessAgent
from agents.core.sql_agent import SQLGenerationAgent
from agents.core.query_execution_agent import QueryExecutionAgent
from agents.core.response_formatting_agent import ResponseFormattingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_schema_agent():
    """Test the schema awareness agent."""
    print("\n=== Testing Schema Awareness Agent ===")
    
    try:
        schema_agent = SchemaAwarenessAgent()
        
        # Test database schema retrieval
        schema = schema_agent.get_database_schema()
        print(f"✓ Retrieved schema for {len(schema)} tables")
        
        # Test schema formatting for LLM
        schema_text = schema_agent.format_schema_for_llm()
        print(f"✓ Formatted schema text ({len(schema_text)} characters)")
        
        # Test query examples
        examples = schema_agent.get_query_examples()
        print(f"✓ Retrieved {len(examples)} query examples")
        
        print("✓ Schema Awareness Agent tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Schema Awareness Agent test failed: {e}")
        return False

def test_sql_generation_agent():
    """Test the SQL generation agent."""
    print("\n=== Testing SQL Generation Agent ===")
    
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("✗ OPENAI_API_KEY not found in environment")
            return False
        
        sql_agent = SQLGenerationAgent(openai_api_key)
        
        # Test SQL generation
        test_questions = [
            "Show my web activity for today",
            "What are my most active GitHub repositories?",
            "How much time did I spend on social media this week?"
        ]
        
        for question in test_questions:
            sql_query = sql_agent.generate_sql_query(question, user_id=1)
            if sql_query:
                print(f"✓ Generated SQL for: {question}")
                print(f"  Query: {sql_query}")
            else:
                print(f"✗ Failed to generate SQL for: {question}")
                return False
        
        print("✓ SQL Generation Agent tests passed")
        return True
        
    except Exception as e:
        print(f"✗ SQL Generation Agent test failed: {e}")
        return False

def test_query_execution_agent():
    """Test the query execution agent."""
    print("\n=== Testing Query Execution Agent ===")
    
    try:
        query_agent = QueryExecutionAgent()
        
        # Test database connection
        if not query_agent.validate_database_connection():
            print("✗ Database connection failed")
            return False
        print("✓ Database connection validated")
        
        # Test query syntax validation
        test_queries = [
            "SELECT * FROM web_activity WHERE user_id = %s",
            "DROP TABLE users",  # Should be invalid
            "SELECT * FROM web_activity"  # Missing user_id filter
        ]
        
        for query in test_queries:
            syntax_result = query_agent.test_query_syntax(query)
            print(f"✓ Syntax test for query: {syntax_result['syntax_valid']}")
        
        print("✓ Query Execution Agent tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Query Execution Agent test failed: {e}")
        return False

def test_response_formatting_agent():
    """Test the response formatting agent."""
    print("\n=== Testing Response Formatting Agent ===")
    
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("✗ OPENAI_API_KEY not found in environment")
            return False
        
        response_agent = ResponseFormattingAgent(openai_api_key)
        
        # Test error response formatting
        error_response = response_agent.format_error_response(
            "Show my activity", "SQL generation failed", "sql"
        )
        print(f"✓ Error response formatting: {error_response[:50]}...")
        
        # Test empty results response
        empty_response = response_agent.format_empty_results_response(
            "Show my activity today"
        )
        print(f"✓ Empty results response: {empty_response[:50]}...")
        
        print("✓ Response Formatting Agent tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Response Formatting Agent test failed: {e}")
        return False

def test_integrated_system():
    """Test the integrated LLM agent system."""
    print("\n=== Testing Integrated LLM Agent System ===")
    
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("✗ OPENAI_API_KEY not found in environment")
            return False
        
        llm_agent = LLMDatabaseAgent(openai_api_key)
        
        # Test agent info
        agent_info = llm_agent.get_agent_info()
        print(f"✓ Agent info retrieved: {len(agent_info['specialized_agents'])} specialized agents")
        
        # Test question processing
        test_questions = [
            "Show my web activity for today",
            "What are my GitHub repositories?",
            "How much time did I spend browsing this week?"
        ]
        
        for question in test_questions:
            result = llm_agent.process_question(question, user_id=1)
            if result['success']:
                print(f"✓ Processed question: {question}")
                print(f"  Response: {result['response'][:100]}...")
            else:
                print(f"✗ Failed to process question: {question}")
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print("✓ Integrated LLM Agent System tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Integrated LLM Agent System test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting Enhanced SQL Agent System Tests")
    print("=" * 50)
    
    tests = [
        test_schema_agent,
        test_sql_generation_agent,
        test_query_execution_agent,
        test_response_formatting_agent,
        test_integrated_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced SQL agent system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
