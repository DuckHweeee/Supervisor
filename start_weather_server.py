#!/usr/bin/env python3
"""
Start the Weather API Server for the Smart Building Assistant
"""

import subprocess
import sys
import os

def start_weather_server():
    """Start the Weather API server"""
    print("Starting Weather API Server...")
    print("Server will be available at http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, 
            "weather_api_server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    start_weather_server()
