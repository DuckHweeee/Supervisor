#!/usr/bin/env python3
"""
Start the Weather MCP Server in HTTP mode for easy integration with the AI Assistant
"""

import asyncio
import subprocess
import sys
import os

def start_mcp_server():
    """Start the MCP server in HTTP mode"""
    print("Starting Weather MCP Server...")
    print("Server will be available at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, 
            "mcp_weather_server.py", 
            "--http"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    start_mcp_server()
