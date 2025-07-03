#!/usr/bin/env python3
"""
Smart Building AI Assistant Demo
This script demonstrates the Smart Building AI Assistant capabilities
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from AutoGenAI import (
    get_current_weather, 
    SmartBuildingKnowledgeBase,
    add_document_to_kb,
    search_building_knowledge,
    get_knowledge_base_stats
)

# Load environment variables
load_dotenv()

def demo_weather_function():
    """Demonstrate weather function with Đại học quốc tế Miền Đông location"""
    print("🌤️  Weather Function Demo")
    print("=" * 50)
    
    # Test the weather function with different location names
    test_locations = [
        "current location",
        "ho chi minh city",
        "saigon", 
        "đại học quốc tế miền đông",
        "unknown city"
    ]
    
    for location in test_locations:
        print(f"\n📍 Location: {location}")
        try:
            weather_data = get_current_weather(location)
            weather_json = json.loads(weather_data)
            
            if "temperature" in weather_json and weather_json["temperature"] != "unknown":
                print(f"  🌡️  Temperature: {weather_json['temperature']}°{weather_json.get('unit', 'F')}")
                print(f"  ☁️  Condition: {weather_json.get('condition', 'N/A')}")
                print(f"  💧 Humidity: {weather_json.get('humidity', 'N/A')}")
                if "coordinates" in weather_json:
                    print(f"  🌍 Coordinates: {weather_json['coordinates']}")
            else:
                print(f"  ❌ {weather_json.get('message', 'No data available')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def demo_knowledge_base():
    """Demonstrate knowledge base functionality"""
    print("\n\n📚 Knowledge Base Demo")
    print("=" * 50)
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Check if sample documents exist
    data_dir = Path("smart_building_data")
    if data_dir.exists():
        files = list(data_dir.glob("*.txt"))
        print(f"\n📁 Found {len(files)} document(s) in smart_building_data/")
        
        # Add documents if they exist
        for file in files:
            print(f"\n📄 Adding document: {file.name}")
            result = add_document_to_kb(str(file))
            print(f"  {result}")
    else:
        print("📁 No smart_building_data directory found")
    
    # Get knowledge base statistics
    print(f"\n📊 Knowledge Base Statistics:")
    stats = get_knowledge_base_stats()
    print(f"  {stats}")
    
    # Demo search functionality
    print(f"\n🔍 Search Demo:")
    search_queries = [
        "HVAC system maintenance",
        "lighting system specifications", 
        "emergency contacts",
        "temperature sensors"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Query: '{query}'")
        results = search_building_knowledge(query)
        if "No relevant information found" in results:
            print("  ❌ No results found")
        else:
            # Show first 200 characters of results
            preview = results[:200] + "..." if len(results) > 200 else results
            print(f"  ✅ Found results: {preview}")

def demo_file_management():
    """Demonstrate file management capabilities"""
    print("\n\n📁 File Management Demo")
    print("=" * 50)
    
    # Check smart building data directory
    data_dir = Path("smart_building_data")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        print(f"\n📂 Files in smart_building_data/:")
        for file in files:
            print(f"  📄 {file.name} ({file.suffix}) - {file.stat().st_size} bytes")
    else:
        print("📂 smart_building_data directory not found")
    
    # Check knowledge base directory
    kb_dir = Path("knowledge_base")
    if kb_dir.exists():
        print(f"\n🗄️  Knowledge base directory exists")
        print(f"  📊 Size: {sum(f.stat().st_size for f in kb_dir.rglob('*') if f.is_file())} bytes")
    else:
        print("🗄️  Knowledge base directory not found")

def main():
    """Main demo function"""
    print("🏢 Smart Building AI Assistant Demo")
    print("=" * 60)
    print("Location: Đại học quốc tế Miền Đông")
    print("Coordinates: 11.052754371982356, 106.666777616965")
    print("=" * 60)
    
    # Check if API key is configured
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("   The AI assistant features will not work without this key")
    else:
        print("✅ GROQ_API_KEY configured")
    
    # Run demos
    demo_weather_function()
    demo_knowledge_base()
    demo_file_management()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n💡 To use the Smart Building AI Assistant:")
    print("   1. Run 'python streamlit_app.py' for the web interface")
    print("   2. Or use the functions directly in your Python code")
    print("   3. Add documents to smart_building_data/ to expand the knowledge base")

if __name__ == "__main__":
    main()
