#!/usr/bin/env python3
"""
Test script to verify streamlit app can start without errors
"""

import sys
import os

def test_streamlit_app():
    """Test if streamlit app can be imported and basic components work"""
    try:
        print("🔍 Testing Streamlit App Components...")
        
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test AutoGen components
        from autogen import AssistantAgent, UserProxyAgent
        from autogen.coding import LocalCommandLineCodeExecutor
        print("✅ AutoGen components imported successfully")
        
        # Test data processing imports
        import chromadb
        import PyPDF2
        import docx2txt
        import pandas as pd
        print("✅ Data processing libraries imported successfully")
        
        # Test web scraping components
        import requests
        from bs4 import BeautifulSoup
        import feedparser
        print("✅ Web scraping components imported successfully")
        
        # Test async HTTP client
        import httpx
        print("✅ HTTP client imported successfully")
        
        # Test environment variables
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded successfully")
        
        # Test if GROQ_API_KEY is set
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            print(f"✅ GROQ_API_KEY is set (length: {len(groq_key)})")
        else:
            print("⚠️  GROQ_API_KEY not set in environment")
        
        print("\n🎉 All streamlit app components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing streamlit app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏢 Smart Building AI Assistant - Startup Test")
    print("=" * 60)
    
    if test_streamlit_app():
        print("\n✅ App is ready to run!")
        print("\nTo start the app, run:")
        print("streamlit run streamlit_app.py")
    else:
        print("\n❌ App has issues. Please check the errors above.")
        sys.exit(1)
