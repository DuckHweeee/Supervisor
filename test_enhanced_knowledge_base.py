#!/usr/bin/env python3
"""
Test script to verify enhanced knowledge base functionality
Tests that the system provides specific, actionable answers without raw data
"""

import json
from pathlib import Path
import sys
import os

# Add the current directory to the path to import AutoGenAI
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AutoGenAI import (
    kb, 
    search_building_knowledge, 
    get_current_weather,
    assistant,
    user_proxy
)

def test_knowledge_base_synthesis():
    """Test that knowledge base provides synthesized information"""
    print("🧪 Testing Knowledge Base Synthesis...")
    print("=" * 50)
    
    # Test different types of queries
    test_queries = [
        "HVAC temperature control",
        "LED lighting efficiency",
        "Energy consumption optimization",
        "Building safety procedures",
        "Smart building automation"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        
        # Test direct knowledge base search
        result = search_building_knowledge(query)
        print(f"📚 Knowledge Base Result:\n{result}")
        
        # Check if result contains raw data (should not)
        if any(indicator in result.lower() for indicator in ['document', 'filename', 'raw', 'source', 'chunk']):
            print("❌ WARNING: Result may contain raw data indicators")
        else:
            print("✅ Result appears to be synthesized")
        
        print("\n" + "="*50)

def test_ai_assistant_responses():
    """Test that AI assistant provides specific, actionable responses"""
    print("\n🤖 Testing AI Assistant Responses...")
    print("=" * 50)
    
    # Test queries that should trigger knowledge base search
    test_queries = [
        "How should I set HVAC temperature for energy efficiency?",
        "What are the best lighting recommendations for the building?",
        "How can I reduce energy consumption in the building?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        
        try:
            # Create a conversation
            user_proxy.initiate_chat(
                assistant,
                message=query,
                max_turns=1
            )
            
            # Get the last message from the conversation
            last_message = user_proxy.chat_messages[assistant][-1]['content']
            print(f"🤖 AI Response:\n{last_message}")
            
            # Check if response is actionable
            actionable_indicators = [
                'recommendation', 'set to', 'adjust to', 'implement',
                'consider', 'optimize', 'maintain', 'monitor'
            ]
            
            if any(indicator in last_message.lower() for indicator in actionable_indicators):
                print("✅ Response appears to be actionable")
            else:
                print("❓ Response may not be sufficiently actionable")
            
        except Exception as e:
            print(f"❌ Error testing AI response: {e}")
        
        print("\n" + "="*50)

def test_weather_integration():
    """Test weather integration with building recommendations"""
    print("\n🌤️ Testing Weather Integration...")
    print("=" * 50)
    
    try:
        # Test weather function
        weather_result = get_current_weather("Đại học quốc tế Miền Đông")
        weather_data = json.loads(weather_result)
        
        print(f"📊 Weather Data: {weather_data}")
        
        # Test if weather data provides building recommendations
        if 'temperature' in weather_data and weather_data['temperature'] != 'unknown':
            print("✅ Weather data successfully retrieved")
            
            # Test weather-based query
            weather_query = "What HVAC settings should I use based on current weather?"
            
            try:
                user_proxy.initiate_chat(
                    assistant,
                    message=weather_query,
                    max_turns=1
                )
                
                last_message = user_proxy.chat_messages[assistant][-1]['content']
                print(f"🌡️ Weather-based Response:\n{last_message}")
                
                # Check if response includes specific recommendations
                if any(term in last_message.lower() for term in ['°c', 'temperature', 'humidity', 'hvac']):
                    print("✅ Response includes weather-based recommendations")
                else:
                    print("❓ Response may not include sufficient weather-based recommendations")
                    
            except Exception as e:
                print(f"❌ Error testing weather-based response: {e}")
        else:
            print("❌ Weather data not available")
            
    except Exception as e:
        print(f"❌ Error testing weather integration: {e}")

def test_knowledge_base_stats():
    """Test knowledge base statistics and content"""
    print("\n📊 Testing Knowledge Base Statistics...")
    print("=" * 50)
    
    try:
        # Check if knowledge base has content
        collection_info = kb.collection.get()
        doc_count = len(collection_info['documents'])
        
        print(f"📚 Total document chunks: {doc_count}")
        
        if doc_count > 0:
            print("✅ Knowledge base has content")
            
            # Show a sample of how information is stored (first chunk only)
            sample_content = collection_info['documents'][0][:100] + "..."
            print(f"📄 Sample content: {sample_content}")
            
            # Test that synthesis works
            print("\n🔄 Testing synthesis with sample content...")
            sample_query = "building management"
            synthesized_result = kb.get_context_for_query(sample_query)
            
            print(f"🎯 Synthesized result: {synthesized_result}")
            
            # Check if synthesized result is different from raw content
            if synthesized_result != sample_content and synthesized_result:
                print("✅ Synthesis appears to be working")
            else:
                print("❓ Synthesis may not be working correctly")
                
        else:
            print("❌ Knowledge base is empty")
            
    except Exception as e:
        print(f"❌ Error testing knowledge base: {e}")

def main():
    """Run all tests"""
    print("🧪 Enhanced Knowledge Base Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_knowledge_base_synthesis()
    test_weather_integration()
    test_knowledge_base_stats()
    test_ai_assistant_responses()
    
    print("\n✅ Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
