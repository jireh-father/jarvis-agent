# -*- coding: utf-8 -*-
"""
Exa Search Test Script
"""
import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv is not installed. Using environment variables only.\n")

from app.services.search import ExaSearch, create_search_tool

def test_exa_search():
    """ExaSearch class test"""
    print("=== ExaSearch Test ===")
    try:
        # Check EXA_API_KEY
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            print("[FAIL] EXA_API_KEY environment variable is not set.")
            print("       Please add EXA_API_KEY to .env file.")
            return False
        
        # Create ExaSearch instance
        search = ExaSearch(api_key=api_key)
        print("[OK] ExaSearch instance created successfully")
        
        # Simple search query
        print("\nSearch query: 'weather today'")
        results = search.search(query="weather today", num_results=3)
        
        print(f"[OK] Search completed - {len(results)} results")
        
        # Print results
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result['title']}")
            print(f"  URL: {result['url']}")
            if result['text']:
                print(f"  Text: {result['text'][:100]}...")
        
        # LLM formatting test
        print("\n=== LLM Formatting Test ===")
        formatted = search.format_results_for_llm(results)
        print(formatted[:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False


def test_langchain_tool():
    """LangChain Tool wrapping test"""
    print("\n\n=== LangChain Tool Test ===")
    try:
        # Create tool
        tool = create_search_tool()
        print("[OK] LangChain Tool created successfully")
        print(f"   Tool name: {tool.name}")
        print(f"   Tool description: {tool.description}")
        
        # Execute tool
        print("\nSearch execution: 'python programming language'")
        result = tool.invoke("python programming language")
        print("[OK] Search completed")
        print(f"Result:\n{result[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Exa Search Implementation Verification Test\n")
    
    # ExaSearch class test
    test1_passed = test_exa_search()
    
    # LangChain Tool test
    test2_passed = test_langchain_tool()
    
    # Summary
    print("\n\n=== Test Results Summary ===")
    print(f"ExaSearch class test: {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"LangChain Tool test: {'[PASS]' if test2_passed else '[FAIL]'}")
    
    if test1_passed and test2_passed:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed")
