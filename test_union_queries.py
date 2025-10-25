#!/usr/bin/env python3
"""
Test script for UNION query functionality.
Tests the security guards and SQL generation with UNION queries.
"""

import sys
import os
sys.path.append('.')

from agents.guards.security_guards import QuerySecurityGuard, SecurityLevel

def test_union_security():
    """Test UNION query security validation."""
    print("🧪 Testing UNION Query Security...")
    
    guard = QuerySecurityGuard(SecurityLevel.MEDIUM)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid UNION query",
            "query": "SELECT 'web' as platform, website_name FROM web_activity WHERE user_id = %s UNION ALL SELECT 'github' as platform, repository_name FROM github_activity WHERE user_id = %s",
            "user_id": 1,
            "expected": True
        },
        {
            "name": "UNION without user_id filtering",
            "query": "SELECT website_name FROM web_activity UNION ALL SELECT repository_name FROM github_activity",
            "user_id": 1,
            "expected": False
        },
        {
            "name": "UNION with dangerous keyword",
            "query": "SELECT website_name FROM web_activity WHERE user_id = %s UNION ALL DROP TABLE test",
            "user_id": 1,
            "expected": False
        },
        {
            "name": "Single SELECT (no UNION)",
            "query": "SELECT * FROM web_activity WHERE user_id = %s",
            "user_id": 1,
            "expected": True
        },
        {
            "name": "UNION with nested SELECT",
            "query": "SELECT * FROM web_activity WHERE user_id = %s UNION ALL SELECT * FROM (SELECT * FROM github_activity WHERE user_id = %s) as sub",
            "user_id": 1,
            "expected": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        
        is_safe, reason = guard.validate_query(test_case['query'], test_case['user_id'])
        
        if is_safe == test_case['expected']:
            print(f"✅ PASS - {reason}")
        else:
            print(f"❌ FAIL - Expected: {test_case['expected']}, Got: {is_safe}")
            print(f"Reason: {reason}")

def test_union_examples():
    """Test UNION query examples from database manager."""
    print("\n🧪 Testing UNION Query Examples...")
    
    from backend.database.db_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    examples = db_manager.get_query_examples()
    
    union_examples = [ex for ex in examples if 'UNION' in ex['sql']]
    
    print(f"📊 Found {len(union_examples)} UNION examples:")
    
    for i, example in enumerate(union_examples, 1):
        print(f"\n{i}. Question: {example['question']}")
        print(f"   SQL: {example['sql']}")
        
        # Test the query with security guard
        guard = QuerySecurityGuard(SecurityLevel.MEDIUM)
        is_safe, reason = guard.validate_query(example['sql'], 1)
        
        if is_safe:
            print(f"   ✅ Security check: PASS - {reason}")
        else:
            print(f"   ❌ Security check: FAIL - {reason}")

if __name__ == "__main__":
    print("🚀 UNION Query Functionality Test")
    print("=" * 50)
    
    try:
        test_union_security()
        test_union_examples()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
