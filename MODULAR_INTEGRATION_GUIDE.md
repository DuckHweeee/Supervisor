# Smart Building AI - Modular Integration System

## 🏗️ Modular Architecture Overview

The Smart Building AI has been restructured into a modular system that can be easily integrated into any website, application, or system. Each module is self-contained and can be used independently or together.

## 📁 Module Structure

```
modules/
├── core/                    # Core AI functionality
│   ├── ai_agent.py         # Main AI agent (sync/async)
│   └── knowledge_base.py   # Document processing & storage
├── integrations/           # External service integrations
│   └── weather.py         # Weather data & recommendations
├── apis/                   # API interfaces
│   └── rest_api.py        # FastAPI REST server
├── interfaces/            # User interfaces
│   └── web_widgets.py     # Embeddable web widgets
└── __init__.py           # Main entry points & factory functions
```

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Method 1: Using the module directly
python modules/__init__.py server --port 8000

# Method 2: Using Python
python -c "from modules import quick_start_api_server; quick_start_api_server(8000)"
```

### 2. Integrate into Your Website

#### Option A: Chat Widget
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website with AI Chat</title>
</head>
<body>
    <h1>Welcome to My Website</h1>
    
    <!-- AI Chat Widget -->
    <div id="smart-building-chat"></div>
    
    <script>
    // Load the chat widget
    fetch('http://localhost:8000/widget/chat')
      .then(response => response.text())
      .then(html => {
        document.getElementById('smart-building-chat').innerHTML = html;
      });
    </script>
</body>
</html>
```

#### Option B: Direct API Integration
```javascript
// Send message to AI
async function askAI(message) {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            session_id: 'my-website-user'
        })
    });
    
    const data = await response.json();
    return data.response;
}

// Usage
const aiResponse = await askAI('What is the optimal office temperature?');
console.log('AI says:', aiResponse);
```

## 🔧 Integration Methods

### 1. Web Widget Integration

**Easiest method for websites:**

```python
from modules import create_smart_building_system

# Create system
system = create_smart_building_system()

# Generate chat widget HTML
chat_widget = system.create_chat_widget(theme="light")
html_code = chat_widget.generate_html()

# Embed this HTML in your website
print(html_code)
```

### 2. REST API Integration

**For any programming language or platform:**

```python
# Python example
import requests

def chat_with_ai(message, session_id="python-client"):
    response = requests.post('http://localhost:8000/chat', json={
        'message': message,
        'session_id': session_id
    })
    return response.json()['response']

# Usage
answer = chat_with_ai("How can I reduce energy consumption?")
print(answer)
```

```javascript
// JavaScript/Node.js example
const axios = require('axios');

async function chatWithAI(message, sessionId = 'js-client') {
    const response = await axios.post('http://localhost:8000/chat', {
        message: message,
        session_id: sessionId
    });
    return response.data.response;
}

// Usage
const answer = await chatWithAI("What are smart building best practices?");
console.log(answer);
```

### 3. Direct Module Import

**For Python applications:**

```python
from modules.core.ai_agent import SmartBuildingAI
from modules.core.knowledge_base import KnowledgeBaseManager
from modules.integrations.weather import WeatherIntegration

# Initialize components
ai_agent = SmartBuildingAI()
knowledge_base = KnowledgeBaseManager("my_kb")
weather = WeatherIntegration()

# Use directly in your app
response = ai_agent.generate_response("How to optimize HVAC?")
print(response)

# Add documents
knowledge_base.add_document("Building manual content...", 
                          {"filename": "manual.txt"})

# Get weather recommendations
weather_data = weather.get_weather_sync("New York")
recommendations = weather.format_weather_response(weather_data)
print(recommendations)
```

## 🌐 Platform-Specific Examples

### React Application

```jsx
import React, { useState, useEffect } from 'react';

function SmartBuildingChat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sessionId] = useState(`react-${Date.now()}`);

    const sendMessage = async () => {
        if (!input.trim()) return;

        // Add user message
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);

        try {
            // Send to AI
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId
                })
            });

            const data = await response.json();
            
            // Add AI response
            const aiMessage = { role: 'assistant', content: data.response };
            setMessages(prev => [...prev, aiMessage]);

        } catch (error) {
            console.error('Error:', error);
        }

        setInput('');
    };

    return (
        <div style={{ maxWidth: '500px', margin: '20px auto' }}>
            <div style={{ height: '400px', overflow: 'auto', border: '1px solid #ccc', padding: '10px' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ 
                        margin: '10px 0', 
                        padding: '8px',
                        background: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                        borderRadius: '8px'
                    }}>
                        <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                    </div>
                ))}
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask about building optimization..."
                    style={{ flex: 1, padding: '8px' }}
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default SmartBuildingChat;
```

### WordPress Plugin

```php
<?php
/*
Plugin Name: Smart Building AI Chat
Description: Adds Smart Building AI chat widget to WordPress
Version: 1.0
*/

// Add widget to footer
function smart_building_ai_widget() {
    ?>
    <div id="smart-building-ai-floating" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: #2196F3;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
    " onclick="toggleSmartBuildingChat()">
        🏢
    </div>
    
    <div id="smart-building-chat-container" style="
        position: fixed;
        bottom: 100px;
        right: 20px;
        display: none;
        z-index: 1001;
    "></div>

    <script>
    let chatLoaded = false;
    
    function toggleSmartBuildingChat() {
        const container = document.getElementById('smart-building-chat-container');
        
        if (container.style.display === 'none') {
            if (!chatLoaded) {
                // Load chat widget
                fetch('http://localhost:8000/widget/chat')
                    .then(response => response.text())
                    .then(html => {
                        container.innerHTML = html;
                        chatLoaded = true;
                    });
            }
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }
    </script>
    <?php
}

add_action('wp_footer', 'smart_building_ai_widget');
?>
```

### Flask Application

```python
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
AI_API_URL = 'http://localhost:8000'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    # Forward to Smart Building AI
    response = requests.post(f'{AI_API_URL}/chat', json={
        'message': data['message'],
        'session_id': data.get('session_id', 'flask-app')
    })
    
    return jsonify(response.json())

@app.route('/api/weather/<location>')
def weather(location):
    response = requests.post(f'{AI_API_URL}/weather', json={
        'location': location,
        'include_recommendations': True
    })
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
```

## 📋 Available API Endpoints

### Chat API
- **POST** `/chat` - Send message to AI
- **GET** `/sessions` - List active sessions
- **DELETE** `/sessions/{session_id}` - Delete session

### Knowledge Base API
- **POST** `/upload-document` - Upload document
- **GET** `/knowledge-base/stats` - Get KB statistics

### Weather API
- **POST** `/weather` - Get weather and recommendations

### System API
- **GET** `/health` - System health check
- **GET** `/` - API documentation

## 🎨 Customization Options

### Widget Themes
```python
# Light theme (default)
chat_widget = system.create_chat_widget(theme="light")

# Dark theme
chat_widget = system.create_chat_widget(theme="dark")

# Custom styling
custom_html = chat_widget.generate_html("my-chat-widget")
```

### API Configuration
```python
# Custom configuration
system = create_smart_building_system(
    knowledge_base_path="custom_kb",
    weather_server_url="http://my-weather-api:8001",
    api_port=9000
)
```

## 🔒 Security Considerations

1. **CORS Configuration**: Update CORS settings for production
2. **Authentication**: Add API keys or JWT tokens
3. **Rate Limiting**: Implement request throttling
4. **Input Validation**: Sanitize user inputs
5. **HTTPS**: Use SSL/TLS in production

## 📊 Monitoring and Analytics

```python
# Get system information
system = create_smart_building_system()
info = system.get_system_info()
print("System status:", info)

# Monitor API health
import requests
health = requests.get('http://localhost:8000/health').json()
print("API health:", health)
```

## 🆘 Troubleshooting

### Common Issues

1. **API Server Not Starting**
   ```bash
   # Check if port is in use
   netstat -an | findstr :8000
   
   # Use different port
   python modules/__init__.py server --port 8001
   ```

2. **Widget Not Loading**
   ```javascript
   // Check console for errors
   console.log('Testing API connection...');
   fetch('http://localhost:8000/health')
     .then(response => response.json())
     .then(data => console.log('API Status:', data))
     .catch(error => console.error('API Error:', error));
   ```

3. **Import Errors**
   ```python
   # Ensure modules directory is in Python path
   import sys
   import os
   sys.path.insert(0, os.path.join(os.getcwd(), 'modules'))
   ```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Source Code**: All modules are documented and self-contained
- **Examples**: Check the `modules/__init__.py` for more integration examples

## 🤝 Support

For integration help:
1. Check the API documentation at `/docs`
2. Review the example integrations above
3. Test with the health endpoint: `/health`
4. Use the widget generators for quick setup

The modular architecture makes it easy to integrate Smart Building AI into any system while maintaining full functionality and performance.
