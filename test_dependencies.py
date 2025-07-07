#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

import sys
import importlib

# List of required packages
required_packages = [
    'streamlit',
    'autogen',
    'groq',
    'dotenv',  # python-dotenv
    'PyPDF2',
    'docx2txt',
    'openpyxl',
    'pandas',
    'chromadb',
    'requests',
    'bs4',  # beautifulsoup4
    'feedparser',
    'urllib3',
    'certifi',
    'httpx',
    'fastapi',
    'uvicorn',
    'pydantic'
]

def test_imports():
    """Test importing all required packages"""
    print("Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} packages: {failed_imports}")
        return False
    else:
        print(f"\n✅ All {len(required_packages)} packages imported successfully!")
        return True

def test_streamlit_app():
    """Test if streamlit app can be imported"""
    try:
        # Test basic streamlit functionality
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test AutoGen
        from autogen import AssistantAgent, UserProxyAgent
        print("✅ AutoGen import successful")
        
        # Test ChromaDB
        import chromadb
        print("✅ ChromaDB import successful")
        
        # Test HTTP client
        import httpx
        print("✅ HTTPX import successful")
        
        return True
    except Exception as e:
        print(f"❌ Error testing streamlit app components: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Dependency Test Report")
    print("=" * 50)
    
    # Test basic imports
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    
    # Test streamlit app components
    app_ok = test_streamlit_app()
    
    print("\n" + "=" * 50)
    
    if imports_ok and app_ok:
        print("🎉 All tests passed! Your environment is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
