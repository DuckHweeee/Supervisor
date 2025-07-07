#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly.
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    import streamlit as st
    print("✅ Streamlit imported successfully")
    
    # Test AutoGen imports
    from autogen import AssistantAgent, UserProxyAgent
    print("✅ AutoGen agents imported successfully")
    
    from autogen.coding import LocalCommandLineCodeExecutor
    print("✅ LocalCommandLineCodeExecutor imported successfully")
    
    # Test other dependencies
    import chromadb
    print("✅ ChromaDB imported successfully")
    
    import requests
    print("✅ Requests imported successfully")
    
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup imported successfully")
    
    import httpx
    print("✅ HTTPX imported successfully")
    
    print("\n🎉 All imports successful! The Streamlit app should work correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install missing dependencies.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
