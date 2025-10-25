#!/usr/bin/env python3
"""
Test script for the SQL Generation Agent.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from agents.core.sql_agent import SQLGenerationAgent

def test_sql_agent():
    """Test the SQL generation agent."""
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            return False
        
        print(f"✅ OpenAI API Key found: {openai_api_key[:20]}...")
        
        # Initialize SQL agent
        sql_agent = SQLGenerationAgent(openai_api_key, "gpt-3.5-turbo")
        print("✅ SQL Agent initialized successfully")
        
        # Test cases
        test_cases = [
            {
                "question": "Show my web activity for today",
                "user_id": 1,
                "expected_keywords": ["SELECT", "web_activity", "user_id", "WHERE"]
            },
            {
                "question": "What websites did I visit this week?",
                "user_id": 1,
                "expected_keywords": ["SELECT", "web_activity", "user_id", "WHERE"]
            },
            {
                "question": "Show my GitHub activity",
                "user_id": 1,
                "expected_keywords": ["SELECT", "github_activity", "user_id", "WHERE"]
            }
        ]
        
        print("\n🧪 Testing SQL Generation:")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['question']}")
            print("-" * 30)
            
            try:
                sql_query = sql_agent.generate_sql_query(
                    test_case["question"], 
                    test_case["user_id"]
                )
                
                if sql_query:
                    print(f"✅ Generated SQL: {sql_query}")
                    
                    # Check for expected keywords
                    sql_upper = sql_query.upper()
                    missing_keywords = []
                    for keyword in test_case["expected_keywords"]:
                        if keyword.upper() not in sql_upper:
                            missing_keywords.append(keyword)
                    
                    if missing_keywords:
                        print(f"⚠️  Missing keywords: {missing_keywords}")
                    else:
                        print("✅ All expected keywords present")
                        
                else:
                    print("❌ Failed to generate SQL query")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 SQL Agent testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize SQL agent: {e}")
        return False

if __name__ == "__main__":
    test_sql_agent()





