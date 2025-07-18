"""
Smart Building AI - Demo Script

This script demonstrates the modular Smart Building AI system
and shows how easy it is to integrate into any application.
"""

import asyncio
import json
import time
from modules import create_smart_building_system


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")


async def demo_async_ai_agent():
    """Demonstrate the async AI agent"""
    print_section("🤖 Async AI Agent Demo")
    
    # Create system
    system = create_smart_building_system()
    
    # Get async AI agent
    ai_agent = system.get_ai_agent(async_mode=True)
    await ai_agent.initialize()
    
    # Test questions
    questions = [
        "What is the optimal temperature for energy efficiency?",
        "How can I reduce lighting energy consumption?",
        "What are the benefits of smart building automation?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 Question {i}: {question}")
        response = await ai_agent.generate_response(question)
        print(f"🤖 AI Response: {response[:200]}...")
    
    print("\n✅ Async AI agent demo completed!")


def demo_sync_ai_agent():
    """Demonstrate the sync AI agent"""
    print_section("🔄 Sync AI Agent Demo")
    
    # Create system
    system = create_smart_building_system()
    
    # Get sync AI agent
    ai_agent = system.get_ai_agent(async_mode=False)
    
    # Test conversation
    question = "Explain the importance of HVAC maintenance"
    print(f"\n📝 Question: {question}")
    
    response = ai_agent.generate_response(question)
    print(f"🤖 AI Response: {response[:200]}...")
    
    print("\n✅ Sync AI agent demo completed!")


def demo_knowledge_base():
    """Demonstrate the knowledge base"""
    print_section("📚 Knowledge Base Demo")
    
    # Create system
    system = create_smart_building_system()
    
    # Get knowledge base
    kb = system.get_knowledge_base()
    
    # Add sample documents
    documents = [
        {
            "content": "HVAC systems should be maintained regularly to ensure optimal performance. Filter replacement is recommended every 3 months.",
            "metadata": {"filename": "hvac_manual.txt", "type": "maintenance"}
        },
        {
            "content": "LED lighting can reduce energy consumption by up to 75% compared to traditional incandescent bulbs.",
            "metadata": {"filename": "lighting_guide.txt", "type": "energy_efficiency"}
        },
        {
            "content": "Smart building sensors can monitor temperature, humidity, and occupancy to optimize building performance automatically.",
            "metadata": {"filename": "sensor_guide.txt", "type": "automation"}
        }
    ]
    
    print("\n📄 Adding sample documents to knowledge base...")
    for doc in documents:
        success = kb.add_document(doc["content"], doc["metadata"])
        print(f"  ✅ Added: {doc['metadata']['filename']} - {'Success' if success else 'Failed'}")
    
    # Search knowledge base
    print("\n🔍 Searching knowledge base...")
    search_queries = ["HVAC maintenance", "LED lighting", "smart sensors"]
    
    for query in search_queries:
        results = kb.search_documents(query, top_k=2)
        print(f"\n  Query: '{query}'")
        for i, result in enumerate(results, 1):
            content = result.get('content', 'No content')[:100]
            score = result.get('score', 0)
            print(f"    {i}. Score: {score:.3f} - {content}...")
    
    # Get stats
    stats = kb.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"  Documents: {stats.get('total_documents', 0)}")
    print(f"  Storage Type: {stats.get('storage_type', 'Unknown')}")
    
    print("\n✅ Knowledge base demo completed!")


def demo_weather_integration():
    """Demonstrate weather integration"""
    print_section("🌤️ Weather Integration Demo")
    
    # Create system
    system = create_smart_building_system()
    
    # Get weather integration
    weather = system.get_weather_integration()
    
    # Test locations
    locations = ["Ho Chi Minh City", "New York", "London"]
    
    for location in locations:
        print(f"\n🌍 Getting weather for {location}...")
        
        # Get weather data
        weather_data = weather.get_weather_sync(location, include_forecast=False)
        
        # Format response
        formatted = weather.format_weather_response(weather_data, include_building_recommendations=True)
        
        print(f"📊 Weather Data:")
        print(f"  Temperature: {weather_data.get('temperature', 'N/A')}")
        print(f"  Condition: {weather_data.get('condition', 'N/A')}")
        print(f"  Humidity: {weather_data.get('humidity', 'N/A')}")
        
        print(f"\n🏢 Building Recommendations:")
        recommendations = weather.get_building_recommendations(weather_data)
        for rec in recommendations[:2]:  # Show first 2 recommendations
            print(f"  • {rec}")
    
    print("\n✅ Weather integration demo completed!")


def demo_web_widgets():
    """Demonstrate web widget generation"""
    print_section("🌐 Web Widget Demo")
    
    # Create system
    system = create_smart_building_system()
    
    # Generate chat widget
    print("\n💬 Generating chat widget HTML...")
    chat_widget = system.create_chat_widget(theme="light", title="Demo AI Assistant")
    chat_html = chat_widget.generate_html("demo-chat")
    
    print(f"  Generated HTML: {len(chat_html)} characters")
    print(f"  Widget ID: demo-chat")
    print(f"  Theme: light")
    
    # Generate weather widget
    print("\n🌤️ Generating weather widget HTML...")
    weather_widget = system.create_weather_widget(default_location="San Francisco", theme="dark")
    weather_html = weather_widget.generate_html("demo-weather")
    
    print(f"  Generated HTML: {len(weather_html)} characters")
    print(f"  Widget ID: demo-weather")
    print(f"  Theme: dark")
    print(f"  Default Location: San Francisco")
    
    # Save demo HTML file
    demo_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Building AI - Widget Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .widget-section {{ margin: 40px 0; }}
        .widgets {{ display: flex; gap: 20px; flex-wrap: wrap; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Smart Building AI - Widget Demo</h1>
        <p>This demo shows the embeddable widgets in action.</p>
        
        <div class="widget-section">
            <h2>💬 Chat Widget</h2>
            <div class="widgets">
                {chat_html}
            </div>
        </div>
        
        <div class="widget-section">
            <h2>🌤️ Weather Widget</h2>
            <div class="widgets">
                {weather_html}
            </div>
        </div>
        
        <div class="widget-section">
            <h2>📖 Integration Instructions</h2>
            <p>To integrate these widgets into your website:</p>
            <ol>
                <li>Start the API server: <code>python modules/__init__.py server</code></li>
                <li>Copy the widget HTML code</li>
                <li>Paste into your website</li>
                <li>Customize themes and settings as needed</li>
            </ol>
        </div>
    </div>
</body>
</html>
    """
    
    with open("demo_widgets.html", "w", encoding="utf-8") as f:
        f.write(demo_html)
    
    print(f"\n💾 Saved demo HTML file: demo_widgets.html")
    print("  Open this file in a browser to see the widgets")
    print("  Note: Start the API server first for full functionality")
    
    print("\n✅ Web widget demo completed!")


def demo_integration_examples():
    """Show integration examples"""
    print_section("🔗 Integration Examples")
    
    # Create system
    system = create_smart_building_system()
    
    # Get integration examples
    examples = system.get_integration_examples()
    
    print("\n📋 Available Integration Examples:")
    for name, example in examples.items():
        print(f"\n  🔧 {name.replace('_', ' ').title()}:")
        lines = example.split('\n')
        for line in lines[:5]:  # Show first 5 lines
            print(f"    {line}")
        if len(lines) > 5:
            print(f"    ... ({len(lines) - 5} more lines)")
    
    print("\n💡 Integration Tips:")
    print("  • Use REST API for any programming language")
    print("  • Embed widgets for instant web integration")
    print("  • Import modules directly for Python apps")
    print("  • Check MODULAR_INTEGRATION_GUIDE.md for full examples")
    
    print("\n✅ Integration examples demo completed!")


def demo_system_info():
    """Show system information"""
    print_section("📊 System Information")
    
    # Create system
    system = create_smart_building_system()
    
    # Get system info
    info = system.get_system_info()
    
    print(f"\n🏢 {info['system']}")
    print(f"📦 Version: {info['version']}")
    
    print(f"\n🔧 Components:")
    for component, description in info['components'].items():
        print(f"  • {component}: {description}")
    
    print(f"\n⚙️ Configuration:")
    for key, value in info['configuration'].items():
        print(f"  • {key}: {value}")
    
    print(f"\n✨ Features:")
    for feature in info['features']:
        print(f"  • {feature}")
    
    print("\n✅ System information demo completed!")


async def run_full_demo():
    """Run the complete demo"""
    print_header("🏢 Smart Building AI - Modular System Demo")
    
    print("""
This demo showcases the modular Smart Building AI system and its integration capabilities.

The system has been restructured into independent modules that can be:
• Embedded as web widgets
• Integrated via REST API  
• Used directly in Python applications
• Deployed on any platform

Let's explore each component...
    """)
    
    # Demo each component
    try:
        demo_sync_ai_agent()
        time.sleep(1)
        
        await demo_async_ai_agent()
        time.sleep(1)
        
        demo_knowledge_base()
        time.sleep(1)
        
        demo_weather_integration()
        time.sleep(1)
        
        demo_web_widgets()
        time.sleep(1)
        
        demo_integration_examples()
        time.sleep(1)
        
        demo_system_info()
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is normal if some services are not running.")
    
    print_header("✅ Demo Completed Successfully!")
    
    print("""
🎉 The Smart Building AI modular system demo is complete!

🚀 Next Steps:
1. Start the API server: python modules/__init__.py server
2. Open demo_widgets.html in your browser
3. Try the integration examples
4. Read MODULAR_INTEGRATION_GUIDE.md for full documentation

📖 Key Integration Methods:
• Web Widgets: Copy/paste HTML for instant embedding
• REST API: Use from any programming language
• Direct Import: Use modules directly in Python apps

🌐 The system is now ready for integration into:
• Websites and web applications
• Mobile applications (via API)
• Desktop software
• IoT systems and platforms
• Cloud services and microservices

Happy building! 🏗️
    """)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_full_demo())
