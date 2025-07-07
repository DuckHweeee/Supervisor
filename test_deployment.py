#!/usr/bin/env python3
"""
Final deployment test for the Smart Building AI Assistant
Tests all critical components and fallback mechanisms
"""

import os
import sys
import traceback

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing critical imports...")
    
    try:
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test AutoGen imports
        from autogen import AssistantAgent, UserProxyAgent
        from autogen.coding import LocalCommandLineCodeExecutor
        print("✅ AutoGen components imported successfully")
        
        # Test ChromaDB with fallback
        import chromadb
        print("✅ ChromaDB imported successfully")
        
        # Test other dependencies
        import requests
        from bs4 import BeautifulSoup
        import httpx
        print("✅ Web scraping dependencies imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_chromadb_fallback():
    """Test ChromaDB fallback mechanism"""
    print("\n🔍 Testing ChromaDB fallback mechanism...")
    
    try:
        # Try to import the SmartBuildingKnowledgeBase
        sys.path.insert(0, '.')
        from streamlit_app import SmartBuildingKnowledgeBase
        
        # Test initialization
        kb = SmartBuildingKnowledgeBase()
        
        if kb.use_fallback:
            print("✅ ChromaDB fallback mechanism activated successfully")
            print("📝 Using in-memory storage for knowledge base")
        else:
            print("✅ ChromaDB initialized successfully")
            print("🗄️ Using persistent storage for knowledge base")
            
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB fallback test failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic app functionality"""
    print("\n🔍 Testing basic app functionality...")
    
    try:
        sys.path.insert(0, '.')
        from streamlit_app import SmartBuildingKnowledgeBase
        
        # Test knowledge base initialization
        kb = SmartBuildingKnowledgeBase()
        
        # Test simple embedding
        test_text = "This is a test document about HVAC systems"
        embedding = kb.simple_embedding(test_text)
        print(f"✅ Simple embedding generated: {len(embedding)} dimensions")
        
        # Test text chunking
        chunks = kb.chunk_text(test_text, chunk_size=50, overlap=10)
        print(f"✅ Text chunking works: {len(chunks)} chunks created")
        
        # Test search (should work with both ChromaDB and fallback)
        results = kb.search_documents("HVAC", n_results=3)
        print(f"✅ Document search works: {len(results)} results returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("🚀 Smart Building AI Assistant - Deployment Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("ChromaDB Fallback Test", test_chromadb_fallback),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The app is ready for deployment.")
        print("\n🚀 Deployment Commands:")
        print("   pip install -r requirements.txt")
        print("   streamlit run streamlit_app.py")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
