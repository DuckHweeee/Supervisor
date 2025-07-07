#!/usr/bin/env python3
"""
Smart Building AI Assistant Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🏢 Smart Building AI Assistant")
    print("=" * 50)
    
    # Check if we're in the correct directory
    current_dir = Path.cwd()
    app_file = current_dir / "streamlit_app.py"
    
    if not app_file.exists():
        print("❌ streamlit_app.py not found in current directory")
        print(f"Current directory: {current_dir}")
        print("Please run this script from the directory containing streamlit_app.py")
        sys.exit(1)
    
    # Check if environment variables are set
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not found in environment variables")
        print("Please set your GROQ API key in a .env file or environment variables")
        print("Example .env file content:")
        print("GROQ_API_KEY=your_api_key_here")
        print("\nContinuing anyway...")
    
    print("🚀 Starting Smart Building AI Assistant...")
    print("📱 The app will open in your default web browser")
    print("🔧 Use Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Smart Building AI Assistant...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
