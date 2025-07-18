"""
Smart Building AI - Modular System Entry Points

This module provides the main entry points and factory functions for 
integrating the Smart Building AI into any system or website.
"""

import os
import sys
from typing import Dict, Any, Optional, Union
import asyncio

# Add the modules directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import core modules
from core.ai_agent import SmartBuildingAI, AsyncSmartBuildingAI
from core.knowledge_base import KnowledgeBaseManager
from integrations.weather import WeatherIntegration, create_weather_tool
from apis.rest_api import create_api
from interfaces.web_widgets import ChatWidget, WeatherWidget, generate_integration_guide


class SmartBuildingSystem:
    """
    Complete Smart Building AI System for easy integration
    """
    
    def __init__(self, 
                 knowledge_base_path: str = "knowledge_base",
                 weather_server_url: str = "http://localhost:8001",
                 api_port: int = 8000):
        """
        Initialize the complete system
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            weather_server_url: Weather API server URL
            api_port: Port for the REST API server
        """
        self.knowledge_base_path = knowledge_base_path
        self.weather_server_url = weather_server_url
        self.api_port = api_port
        
        # Component instances
        self.ai_agent = None
        self.async_ai_agent = None
        self.knowledge_base = None
        self.weather_integration = None
        self.api_app = None
    
    def get_ai_agent(self, async_mode: bool = False) -> Union[SmartBuildingAI, AsyncSmartBuildingAI]:
        """
        Get AI agent instance (sync or async)
        
        Args:
            async_mode: Whether to return async version
            
        Returns:
            AI agent instance
        """
        if async_mode:
            if self.async_ai_agent is None:
                self.async_ai_agent = AsyncSmartBuildingAI()
            return self.async_ai_agent
        else:
            if self.ai_agent is None:
                self.ai_agent = SmartBuildingAI()
            return self.ai_agent
    
    def get_knowledge_base(self) -> KnowledgeBaseManager:
        """Get knowledge base manager instance"""
        if self.knowledge_base is None:
            self.knowledge_base = KnowledgeBaseManager(self.knowledge_base_path)
        return self.knowledge_base
    
    def get_weather_integration(self) -> WeatherIntegration:
        """Get weather integration instance"""
        if self.weather_integration is None:
            self.weather_integration = WeatherIntegration(self.weather_server_url)
        return self.weather_integration
    
    def get_api_app(self):
        """Get FastAPI application instance"""
        if self.api_app is None:
            self.api_app = create_api(self.knowledge_base_path, self.weather_server_url)
        return self.api_app
    
    def create_chat_widget(self, 
                          theme: str = "light",
                          title: str = "Smart Building AI Assistant") -> ChatWidget:
        """
        Create a chat widget for web integration
        
        Args:
            theme: Widget theme ('light' or 'dark')
            title: Widget title
            
        Returns:
            ChatWidget instance
        """
        api_url = f"http://localhost:{self.api_port}"
        return ChatWidget(api_base_url=api_url, theme=theme, title=title)
    
    def create_weather_widget(self, 
                             default_location: str = "Ho Chi Minh City",
                             theme: str = "light") -> WeatherWidget:
        """
        Create a weather widget for web integration
        
        Args:
            default_location: Default location for weather data
            theme: Widget theme ('light' or 'dark')
            
        Returns:
            WeatherWidget instance
        """
        api_url = f"http://localhost:{self.api_port}"
        return WeatherWidget(api_base_url=api_url, 
                           default_location=default_location, 
                           theme=theme)
    
    def start_api_server(self, host: str = "0.0.0.0", reload: bool = False):
        """
        Start the REST API server
        
        Args:
            host: Host address
            reload: Enable auto-reload for development
        """
        import uvicorn
        
        app = self.get_api_app()
        
        print(f"🚀 Starting Smart Building AI API server on port {self.api_port}...")
        print(f"📖 API Documentation: http://localhost:{self.api_port}/docs")
        print(f"🔗 API Root: http://localhost:{self.api_port}/")
        
        uvicorn.run(app, host=host, port=self.api_port, reload=reload)
    
    def get_integration_examples(self) -> Dict[str, str]:
        """
        Get integration examples for different platforms
        
        Returns:
            Dictionary of integration examples
        """
        api_url = f"http://localhost:{self.api_port}"
        
        return {
            "simple_chat": f"""
<!-- Simple Chat Integration -->
<div id="ai-chat"></div>
<script>
fetch('{api_url}/chat', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{message: 'Hello!', session_id: 'web-user'}})
}})
.then(response => response.json())
.then(data => {{
    document.getElementById('ai-chat').innerHTML = 
        '<div><strong>AI:</strong> ' + data.response + '</div>';
}});
</script>
            """.strip(),
            
            "react_component": f"""
// React Component Example
import React, {{ useState }} from 'react';

function SmartBuildingChat() {{
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    
    const sendMessage = async () => {{
        const res = await fetch('{api_url}/chat', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{message, session_id: 'react-app'}})
        }});
        const data = await res.json();
        setResponse(data.response);
    }};
    
    return (
        <div>
            <input 
                value={{message}} 
                onChange={{e => setMessage(e.target.value)}}
                placeholder="Ask AI..."
            />
            <button onClick={{sendMessage}}>Send</button>
            <div>{{response}}</div>
        </div>
    );
}}
            """.strip(),
            
            "python_client": f"""
# Python Client Example
import requests

class SmartBuildingClient:
    def __init__(self):
        self.api_url = '{api_url}'
        self.session_id = 'python-client'
    
    def chat(self, message):
        response = requests.post(f'{{self.api_url}}/chat', json={{
            'message': message,
            'session_id': self.session_id
        }})
        return response.json()['response']
    
    def get_weather(self, location):
        response = requests.post(f'{{self.api_url}}/weather', json={{
            'location': location,
            'include_recommendations': True
        }})
        return response.json()

# Usage
client = SmartBuildingClient()
ai_response = client.chat('How can I optimize HVAC efficiency?')
weather_info = client.get_weather('New York')
            """.strip(),
            
            "curl_examples": f"""
# cURL Examples

# Chat with AI
curl -X POST {api_url}/chat \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "What is optimal lighting for offices?", "session_id": "curl-test"}}'

# Get weather data
curl -X POST {api_url}/weather \\
  -H "Content-Type: application/json" \\
  -d '{{"location": "San Francisco", "include_recommendations": true}}'

# Upload document
curl -X POST {api_url}/upload-document \\
  -H "Content-Type: application/json" \\
  -d '{{"content": "Building manual content...", "filename": "manual.txt"}}'

# Check API health
curl {api_url}/health
            """.strip()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and status"""
        return {
            "system": "Smart Building AI - Modular System",
            "version": "1.0.0",
            "components": {
                "ai_agent": "Core AI agent with AutoGen integration",
                "knowledge_base": "Document processing and vector storage",
                "weather_integration": "Real-time weather data and recommendations",
                "rest_api": "FastAPI server for external integration",
                "web_widgets": "Embeddable web components"
            },
            "configuration": {
                "knowledge_base_path": self.knowledge_base_path,
                "weather_server_url": self.weather_server_url,
                "api_port": self.api_port
            },
            "features": [
                "Modular architecture for easy integration",
                "Sync and async API support",
                "Web widgets for instant embedding",
                "REST API for any platform",
                "Comprehensive documentation",
                "Real-time weather integration",
                "Document knowledge base",
                "Building optimization recommendations"
            ]
        }


# Factory functions for quick setup

def create_smart_building_system(knowledge_base_path: str = "knowledge_base",
                               weather_server_url: str = "http://localhost:8001",
                               api_port: int = 8000) -> SmartBuildingSystem:
    """
    Create a complete Smart Building AI system
    
    Args:
        knowledge_base_path: Path to knowledge base directory
        weather_server_url: Weather API server URL
        api_port: Port for the REST API server
        
    Returns:
        SmartBuildingSystem instance
    """
    return SmartBuildingSystem(knowledge_base_path, weather_server_url, api_port)


def quick_start_api_server(port: int = 8000):
    """
    Quick start API server with default configuration
    
    Args:
        port: Port number for the server
    """
    system = create_smart_building_system(api_port=port)
    system.start_api_server()


def generate_widget_html(widget_type: str = "chat", 
                        api_port: int = 8000,
                        theme: str = "light") -> str:
    """
    Generate HTML for embedding widgets
    
    Args:
        widget_type: Type of widget ('chat' or 'weather')
        api_port: API server port
        theme: Widget theme
        
    Returns:
        HTML code string
    """
    system = create_smart_building_system(api_port=api_port)
    
    if widget_type == "chat":
        widget = system.create_chat_widget(theme=theme)
        return widget.generate_html()
    elif widget_type == "weather":
        widget = system.create_weather_widget(theme=theme)
        return widget.generate_html()
    else:
        return f"<!-- Unknown widget type: {widget_type} -->"


# CLI interface for quick operations
def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Building AI - Modular System")
    parser.add_argument("command", choices=["server", "widget", "info"], 
                       help="Command to execute")
    parser.add_argument("--port", type=int, default=8000, 
                       help="API server port")
    parser.add_argument("--widget-type", choices=["chat", "weather"], default="chat",
                       help="Widget type to generate")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                       help="Widget theme")
    
    args = parser.parse_args()
    
    if args.command == "server":
        print("🚀 Starting Smart Building AI API server...")
        quick_start_api_server(args.port)
    
    elif args.command == "widget":
        print(f"📋 Generating {args.widget_type} widget HTML...")
        html = generate_widget_html(args.widget_type, args.port, args.theme)
        print(html)
    
    elif args.command == "info":
        system = create_smart_building_system()
        info = system.get_system_info()
        print("📊 Smart Building AI System Information:")
        import json
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
