"""
Web Widget Interface for Smart Building AI

This module provides embeddable web components and widgets for integrating
the Smart Building AI into websites and web applications.
"""

import json
from typing import Dict, Any, Optional


class ChatWidget:
    """
    Embeddable chat widget for websites
    """
    
    def __init__(self, 
                 api_base_url: str = "http://localhost:8000",
                 theme: str = "light",
                 title: str = "Smart Building AI Assistant",
                 width: str = "400px",
                 height: str = "600px"):
        """
        Initialize chat widget
        
        Args:
            api_base_url: Base URL of the REST API
            theme: Widget theme ('light' or 'dark')
            title: Widget title
            width: Widget width (CSS value)
            height: Widget height (CSS value)
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.theme = theme
        self.title = title
        self.width = width
        self.height = height
    
    def generate_html(self, container_id: str = "smart-building-chat") -> str:
        """
        Generate HTML code for the chat widget
        
        Args:
            container_id: HTML element ID for the widget container
            
        Returns:
            HTML code string
        """
        theme_colors = {
            "light": {
                "bg": "#ffffff",
                "text": "#333333",
                "primary": "#2196F3",
                "secondary": "#f5f5f5",
                "border": "#e0e0e0"
            },
            "dark": {
                "bg": "#2d2d2d",
                "text": "#ffffff",
                "primary": "#64B5F6",
                "secondary": "#424242",
                "border": "#555555"
            }
        }
        
        colors = theme_colors.get(self.theme, theme_colors["light"])
        
        return f"""
        <!-- Smart Building AI Chat Widget -->
        <div id="{container_id}" style="
            width: {self.width};
            height: {self.height};
            border: 1px solid {colors['border']};
            border-radius: 10px;
            background: {colors['bg']};
            color: {colors['text']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <!-- Header -->
            <div style="
                background: {colors['primary']};
                color: white;
                padding: 15px;
                font-weight: bold;
                text-align: center;
                border-radius: 10px 10px 0 0;
            ">
                🏢 {self.title}
            </div>
            
            <!-- Messages Container -->
            <div id="{container_id}-messages" style="
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: {colors['bg']};
            ">
                <div style="
                    background: {colors['secondary']};
                    padding: 10px;
                    border-radius: 10px;
                    margin-bottom: 10px;
                    font-size: 14px;
                ">
                    👋 Hello! I'm your Smart Building AI assistant. Ask me about energy efficiency, HVAC optimization, lighting control, or any building management questions.
                </div>
            </div>
            
            <!-- Input Container -->
            <div style="
                padding: 15px;
                border-top: 1px solid {colors['border']};
                background: {colors['bg']};
                display: flex;
                gap: 10px;
                border-radius: 0 0 10px 10px;
            ">
                <input
                    id="{container_id}-input"
                    type="text"
                    placeholder="Ask about building optimization..."
                    style="
                        flex: 1;
                        padding: 10px;
                        border: 1px solid {colors['border']};
                        border-radius: 20px;
                        background: {colors['secondary']};
                        color: {colors['text']};
                        outline: none;
                        font-size: 14px;
                    "
                    onkeypress="if(event.key==='Enter') SmartBuildingChat.sendMessage('{container_id}')"
                >
                <button
                    onclick="SmartBuildingChat.sendMessage('{container_id}')"
                    style="
                        background: {colors['primary']};
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        border-radius: 20px;
                        cursor: pointer;
                        font-size: 14px;
                        min-width: 60px;
                    "
                    onmouseover="this.style.opacity='0.8'"
                    onmouseout="this.style.opacity='1'"
                >
                    Send
                </button>
            </div>
        </div>
        
        <script>
        // Smart Building Chat Widget JavaScript
        window.SmartBuildingChat = window.SmartBuildingChat || {{
            apiUrl: '{self.api_base_url}',
            sessionId: 'widget_' + Date.now(),
            
            sendMessage: function(containerId) {{
                const input = document.getElementById(containerId + '-input');
                const messagesContainer = document.getElementById(containerId + '-messages');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                this.addMessage(messagesContainer, message, 'user');
                input.value = '';
                
                // Show loading
                const loadingId = this.addMessage(messagesContainer, '🤔 Thinking...', 'assistant');
                
                // Send to API
                fetch(this.apiUrl + '/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        message: message,
                        session_id: this.sessionId
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    // Remove loading message
                    document.getElementById(loadingId).remove();
                    
                    // Add AI response
                    this.addMessage(messagesContainer, data.response, 'assistant');
                }})
                .catch(error => {{
                    // Remove loading message
                    document.getElementById(loadingId).remove();
                    
                    // Add error message
                    this.addMessage(messagesContainer, 'Sorry, I encountered an error. Please try again.', 'assistant');
                    console.error('Chat error:', error);
                }});
            }},
            
            addMessage: function(container, message, sender) {{
                const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                const isUser = sender === 'user';
                
                const messageDiv = document.createElement('div');
                messageDiv.id = messageId;
                messageDiv.style.cssText = `
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 10px;
                    font-size: 14px;
                    line-height: 1.4;
                    max-width: 85%;
                    word-wrap: break-word;
                    ${{isUser ? 
                        'background: {colors["primary"]}; color: white; margin-left: auto; text-align: right;' : 
                        'background: {colors["secondary"]}; color: {colors["text"]};'
                    }}
                `;
                
                // Convert markdown-like formatting
                const formattedMessage = message
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                    .replace(/`(.*?)`/g, '<code style="background: rgba(0,0,0,0.1); padding: 2px 4px; border-radius: 3px;">$1</code>')
                    .replace(/\\n/g, '<br>');
                
                messageDiv.innerHTML = formattedMessage;
                container.appendChild(messageDiv);
                container.scrollTop = container.scrollHeight;
                
                return messageId;
            }}
        }};
        </script>
        """
    
    def generate_minimal_html(self, container_id: str = "smart-building-chat-minimal") -> str:
        """
        Generate minimal HTML code for a compact chat widget
        
        Args:
            container_id: HTML element ID for the widget container
            
        Returns:
            Minimal HTML code string
        """
        return f"""
        <!-- Minimal Smart Building AI Chat -->
        <div id="{container_id}" style="max-width: 500px; margin: 20px auto; font-family: Arial, sans-serif;">
            <div id="{container_id}-messages" style="
                border: 1px solid #ddd;
                height: 300px;
                overflow-y: auto;
                padding: 10px;
                background: #f9f9f9;
                margin-bottom: 10px;
            ">
                <div style="background: white; padding: 8px; border-radius: 5px; margin-bottom: 5px;">
                    🏢 Smart Building AI: How can I help with your building management needs?
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <input id="{container_id}-input" type="text" placeholder="Ask me anything..." 
                       style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"
                       onkeypress="if(event.key==='Enter') sendMinimalMessage('{container_id}')">
                <button onclick="sendMinimalMessage('{container_id}')" 
                        style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Send
                </button>
            </div>
        </div>
        
        <script>
        function sendMinimalMessage(containerId) {{
            const input = document.getElementById(containerId + '-input');
            const messages = document.getElementById(containerId + '-messages');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            messages.innerHTML += `<div style="background: #007bff; color: white; padding: 8px; border-radius: 5px; margin: 5px 0; text-align: right;">You: ${{message}}</div>`;
            input.value = '';
            
            // Send to API
            fetch('{self.api_base_url}/chat', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{message: message, session_id: 'minimal_' + Date.now()}})
            }})
            .then(response => response.json())
            .then(data => {{
                messages.innerHTML += `<div style="background: white; padding: 8px; border-radius: 5px; margin: 5px 0;">🏢 AI: ${{data.response}}</div>`;
                messages.scrollTop = messages.scrollHeight;
            }})
            .catch(error => {{
                messages.innerHTML += `<div style="background: #ffebee; padding: 8px; border-radius: 5px; margin: 5px 0;">Error: Unable to connect</div>`;
            }});
        }}
        </script>
        """


class WeatherWidget:
    """
    Embeddable weather widget with building recommendations
    """
    
    def __init__(self, 
                 api_base_url: str = "http://localhost:8000",
                 default_location: str = "Ho Chi Minh City",
                 theme: str = "light"):
        """
        Initialize weather widget
        
        Args:
            api_base_url: Base URL of the REST API
            default_location: Default location for weather data
            theme: Widget theme ('light' or 'dark')
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.default_location = default_location
        self.theme = theme
    
    def generate_html(self, container_id: str = "smart-building-weather") -> str:
        """
        Generate HTML code for the weather widget
        
        Args:
            container_id: HTML element ID for the widget container
            
        Returns:
            HTML code string
        """
        theme_colors = {
            "light": {"bg": "#ffffff", "text": "#333333", "border": "#e0e0e0"},
            "dark": {"bg": "#2d2d2d", "text": "#ffffff", "border": "#555555"}
        }
        
        colors = theme_colors.get(self.theme, theme_colors["light"])
        
        return f"""
        <!-- Smart Building Weather Widget -->
        <div id="{container_id}" style="
            max-width: 400px;
            border: 1px solid {colors['border']};
            border-radius: 10px;
            background: {colors['bg']};
            color: {colors['text']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <div style="padding: 20px;">
                <h3 style="margin: 0 0 15px 0; color: {colors['text']};">🌤️ Weather & Building Status</h3>
                <div id="{container_id}-content">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 24px;">🔄</div>
                        <div>Loading weather data...</div>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <input id="{container_id}-location" type="text" value="{self.default_location}" 
                           style="padding: 8px; border: 1px solid {colors['border']}; border-radius: 4px; margin-right: 10px; background: {colors['bg']}; color: {colors['text']};">
                    <button onclick="SmartBuildingWeather.updateWeather('{container_id}')"
                            style="padding: 8px 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Update
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        window.SmartBuildingWeather = window.SmartBuildingWeather || {{
            apiUrl: '{self.api_base_url}',
            
            updateWeather: function(containerId) {{
                const locationInput = document.getElementById(containerId + '-location');
                const contentDiv = document.getElementById(containerId + '-content');
                const location = locationInput.value.trim() || '{self.default_location}';
                
                contentDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><div style="font-size: 24px;">🔄</div><div>Loading...</div></div>';
                
                fetch(this.apiUrl + '/weather', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        location: location,
                        include_forecast: false,
                        include_recommendations: true
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    const formatted = data.formatted_response
                        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                        .replace(/\\n/g, '<br>');
                    contentDiv.innerHTML = `<div style="font-size: 14px; line-height: 1.5;">${{formatted}}</div>`;
                }})
                .catch(error => {{
                    contentDiv.innerHTML = '<div style="color: #f44336; text-align: center;">Error loading weather data</div>';
                }});
            }},
            
            init: function(containerId) {{
                this.updateWeather(containerId);
            }}
        }};
        
        // Auto-load weather data
        document.addEventListener('DOMContentLoaded', function() {{
            SmartBuildingWeather.init('{container_id}');
        }});
        </script>
        """


def generate_integration_guide() -> str:
    """
    Generate a complete integration guide with examples
    
    Returns:
        HTML integration guide
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Building AI - Integration Guide</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 40px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .section { margin: 40px 0; }
            .code-block { background: #f5f5f5; padding: 20px; border-radius: 8px; overflow-x: auto; }
            .widget-demo { border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .highlight { background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 Smart Building AI Integration Guide</h1>
            
            <div class="section">
                <h2>🚀 Quick Start</h2>
                <p>Integrate Smart Building AI into your website or application in three easy steps:</p>
                
                <div class="highlight">
                    <strong>Step 1:</strong> Start the API server<br>
                    <strong>Step 2:</strong> Copy the widget code<br>
                    <strong>Step 3:</strong> Paste into your HTML
                </div>
            </div>
            
            <div class="section">
                <h2>💬 Chat Widget Integration</h2>
                <p>Add an AI chat assistant to any webpage:</p>
                
                <div class="code-block">
                    <pre>&lt;!-- Copy this code into your HTML --&gt;
&lt;div id="smart-building-chat"&gt;&lt;/div&gt;
&lt;script&gt;
// Load the chat widget
fetch('http://localhost:8000/widget/chat')
  .then(response => response.text())
  .then(html => {
    document.getElementById('smart-building-chat').innerHTML = html;
  });
&lt;/script&gt;</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>🌤️ Weather Widget Integration</h2>
                <p>Display weather data with building recommendations:</p>
                
                <div class="code-block">
                    <pre>&lt;!-- Weather widget code --&gt;
&lt;div id="smart-building-weather"&gt;&lt;/div&gt;
&lt;script&gt;
// Load the weather widget
fetch('http://localhost:8000/widget/weather')
  .then(response => response.text())
  .then(html => {
    document.getElementById('smart-building-weather').innerHTML = html;
  });
&lt;/script&gt;</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>🔌 Direct API Integration</h2>
                <p>For custom integrations, use the REST API directly:</p>
                
                <div class="code-block">
                    <pre>// JavaScript example
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is the optimal temperature setting?',
    session_id: 'my-app-session'
  })
});

const data = await response.json();
console.log('AI Response:', data.response);</pre>
                </div>
                
                <div class="code-block">
                    <pre># Python example
import requests

response = requests.post('http://localhost:8000/chat', json={
    'message': 'How can I reduce energy consumption?',
    'session_id': 'python-client'
})

data = response.json()
print('AI Response:', data['response'])</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>⚙️ Configuration Options</h2>
                <ul>
                    <li><strong>API Base URL:</strong> Change server location</li>
                    <li><strong>Theme:</strong> Light or dark mode</li>
                    <li><strong>Size:</strong> Customize widget dimensions</li>
                    <li><strong>Session Management:</strong> Track user conversations</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📱 Mobile-Friendly</h2>
                <p>All widgets are responsive and work on mobile devices. Add this meta tag for optimal mobile experience:</p>
                
                <div class="code-block">
                    <pre>&lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;</pre>
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 Advanced Integration</h2>
                <p>For advanced use cases:</p>
                <ul>
                    <li>Custom styling with CSS</li>
                    <li>Event handling and callbacks</li>
                    <li>Multi-language support</li>
                    <li>Custom tools and integrations</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📖 API Documentation</h2>
                <p>Complete API documentation is available at:</p>
                <ul>
                    <li><a href="http://localhost:8000/docs">Interactive Documentation (Swagger UI)</a></li>
                    <li><a href="http://localhost:8000/redoc">Alternative Documentation (ReDoc)</a></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """


# Factory functions
def create_chat_widget(api_base_url: str = "http://localhost:8000", 
                      theme: str = "light") -> ChatWidget:
    """Create a chat widget instance"""
    return ChatWidget(api_base_url=api_base_url, theme=theme)


def create_weather_widget(api_base_url: str = "http://localhost:8000",
                         default_location: str = "Ho Chi Minh City",
                         theme: str = "light") -> WeatherWidget:
    """Create a weather widget instance"""
    return WeatherWidget(api_base_url=api_base_url, 
                        default_location=default_location, 
                        theme=theme)


# Example usage
if __name__ == "__main__":
    # Create widgets
    chat_widget = create_chat_widget()
    weather_widget = create_weather_widget()
    
    # Generate example HTML
    print("=== CHAT WIDGET HTML ===")
    print(chat_widget.generate_html())
    
    print("\n=== WEATHER WIDGET HTML ===")
    print(weather_widget.generate_html())
    
    print("\n=== INTEGRATION GUIDE ===")
    print("Generated integration guide available")
