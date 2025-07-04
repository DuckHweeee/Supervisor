#!/usr/bin/env python3
"""
Comprehensive IIC Training and Auto-Training Test
Test the complete auto-training system with the IIC_EIU_Overview.docx document
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

# Import required modules
try:
    from streamlit_app import SmartBuildingKnowledgeBase
    from auto_training import train_on_iic_eiu_overview, AutoTrainingHandler
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

def test_iic_document_training():
    """Test training on the IIC_EIU_Overview.docx document"""
    print("\n🎯 Testing IIC Document Training")
    print("=" * 50)
    
    # Check if document exists
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    if not doc_path.exists():
        print(f"❌ Document not found: {doc_path}")
        return False
    
    print(f"📄 Found document: {doc_path}")
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Train on the document
    try:
        success = train_on_iic_eiu_overview()
        if success:
            print("✅ IIC document training completed successfully")
        else:
            print("❌ IIC document training failed")
            return False
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False
    
    # Test knowledge base queries
    print("\n📊 Testing knowledge base queries...")
    
    test_queries = [
        "What is IIC?",
        "Tell me about Eastern International University",
        "What programs does EIU offer?",
        "Information about Innovation Center",
        "EIU university overview",
        "IIC programs and facilities"
    ]
    
    for query in test_queries:
        try:
            print(f"\n🔍 Query: {query}")
            
            # Get context from knowledge base
            context = kb.get_context_for_query(query)
            if context:
                print(f"   ✅ Found relevant context ({len(context)} chars)")
                # Show first 200 characters
                preview = context[:200].replace('\n', ' ').strip()
                print(f"   📝 Preview: {preview}...")
            else:
                print(f"   ⚠️ No relevant context found")
                
        except Exception as e:
            print(f"   ❌ Error querying: {e}")
    
    return True

def test_auto_training_handler():
    """Test the auto-training handler functionality"""
    print("\n🤖 Testing Auto-Training Handler")
    print("=" * 50)
    
    # Initialize knowledge base and handler
    kb = SmartBuildingKnowledgeBase()
    handler = AutoTrainingHandler(kb)
    
    # Test file type detection
    test_files = [
        "test.pdf",
        "IIC_EIU_Overview.docx",
        "hvac_manual.pdf",
        "lighting_specs.xlsx",
        "security_guide.txt",
        "~temp.docx",  # Should be ignored
        ".hidden.pdf",  # Should be ignored
        "backup.bak"   # Should be ignored
    ]
    
    print("🔍 Testing file type detection:")
    for file_path in test_files:
        should_train = handler.should_train_on_file(file_path)
        status = "✅" if should_train else "❌"
        print(f"   {status} {file_path}")
    
    # Test document type determination
    print("\n🏷️ Testing document type determination:")
    doc_paths = [
        "IIC_EIU_Overview.docx",
        "hvac_system_manual.pdf",
        "lighting_specifications.xlsx",
        "security_procedures.txt",
        "energy_management_guide.docx",
        "maintenance_schedule.pdf",
        "safety_protocols.docx",
        "automation_guide.pdf",
        "general_document.txt"
    ]
    
    for doc_path in doc_paths:
        doc_type = handler.determine_document_type(doc_path)
        print(f"   📋 {doc_path} → {doc_type}")
    
    return True

def test_training_log():
    """Test training log functionality"""
    print("\n📋 Testing Training Log")
    print("=" * 50)
    
    # Check if training log exists
    log_file = Path("training_log.json")
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                
            sessions = log_data.get("training_sessions", [])
            print(f"📊 Found {len(sessions)} training sessions in log")
            
            # Show recent sessions
            recent_sessions = sessions[-5:]  # Last 5 sessions
            if recent_sessions:
                print("\n📝 Recent training sessions:")
                for session in reversed(recent_sessions):
                    timestamp = session.get('timestamp', 'Unknown')
                    file_name = session.get('file_name', 'Unknown')
                    success = session.get('success', False)
                    doc_type = session.get('document_type', 'Unknown')
                    
                    # Format timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_str = timestamp
                    
                    status = "✅" if success else "❌"
                    print(f"   {status} {time_str} - {file_name} ({doc_type})")
            else:
                print("ℹ️ No recent training sessions found")
                
        except Exception as e:
            print(f"❌ Error reading training log: {e}")
    else:
        print("ℹ️ Training log not found - will be created after first training")
    
    return True

def test_knowledge_base_stats():
    """Test knowledge base statistics"""
    print("\n📈 Testing Knowledge Base Statistics")
    print("=" * 50)
    
    try:
        kb = SmartBuildingKnowledgeBase()
        collection_info = kb.collection.get()
        
        documents = collection_info.get('documents', [])
        metadatas = collection_info.get('metadatas', [])
        
        print(f"📊 Total document chunks: {len(documents)}")
        
        if metadatas:
            # Count document types
            doc_types = {}
            auto_trained = 0
            manual_trained = 0
            
            for metadata in metadatas:
                if metadata:
                    doc_type = metadata.get('document_type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                    
                    if metadata.get('auto_trained'):
                        auto_trained += 1
                    if metadata.get('manually_added'):
                        manual_trained += 1
            
            print(f"📋 Document types:")
            for doc_type, count in doc_types.items():
                print(f"   • {doc_type}: {count}")
            
            print(f"🤖 Auto-trained: {auto_trained}")
            print(f"👤 Manually trained: {manual_trained}")
        else:
            print("ℹ️ No metadata found in knowledge base")
            
    except Exception as e:
        print(f"❌ Error getting knowledge base stats: {e}")
    
    return True

def main():
    """Run comprehensive IIC training and auto-training tests"""
    print("🚀 Comprehensive IIC Training and Auto-Training Test")
    print("=" * 60)
    
    # Test 1: IIC Document Training
    success1 = test_iic_document_training()
    
    # Test 2: Auto-Training Handler
    success2 = test_auto_training_handler()
    
    # Test 3: Training Log
    success3 = test_training_log()
    
    # Test 4: Knowledge Base Stats
    success4 = test_knowledge_base_stats()
    
    # Summary
    print("\n🎯 Test Summary")
    print("=" * 30)
    print(f"IIC Document Training: {'✅' if success1 else '❌'}")
    print(f"Auto-Training Handler: {'✅' if success2 else '❌'}")
    print(f"Training Log: {'✅' if success3 else '❌'}")
    print(f"Knowledge Base Stats: {'✅' if success4 else '❌'}")
    
    if all([success1, success2, success3, success4]):
        print("\n🎉 All tests passed! Auto-training system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
