#!/usr/bin/env python3
"""
Smart Building AI - Training System Summary
Shows current state and usage instructions
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from streamlit_app import SmartBuildingKnowledgeBase
    print("✅ Knowledge base loaded successfully")
except ImportError as e:
    print(f"❌ Error importing knowledge base: {e}")
    sys.exit(1)

def show_current_state():
    """Show the current state of the training system"""
    print("🔍 Current Training System State")
    print("=" * 50)
    
    # Check if IIC document exists
    iic_doc = Path("smart_building_data/IIC_EIU_Overview.docx")
    if iic_doc.exists():
        print(f"✅ IIC Document: {iic_doc.name} ({iic_doc.stat().st_size} bytes)")
    else:
        print("❌ IIC Document: Not found")
    
    # Check smart_building_data directory
    data_dir = Path("smart_building_data")
    if data_dir.exists():
        # Count documents
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx']
        doc_count = 0
        for ext in supported_extensions:
            doc_count += len(list(data_dir.glob(f"*{ext}")))
        
        print(f"📁 Data Directory: {doc_count} documents")
        
        # List documents
        if doc_count > 0:
            print("   📄 Documents:")
            for ext in supported_extensions:
                files = list(data_dir.glob(f"*{ext}"))
                for file in files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"      • {file.name} ({size_mb:.1f} MB)")
    else:
        print("❌ Data Directory: smart_building_data not found")
    
    # Check training scripts
    scripts = [
        "auto_training.py",
        "auto_training_service.py", 
        "enhanced_training.py",
        "simple_auto_trainer.py"
    ]
    
    print(f"\n🛠️ Training Scripts:")
    for script in scripts:
        if Path(script).exists():
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script}")
    
    # Check logs
    logs = [
        "training_log.json",
        "iic_training_log.json",
        "auto_training_log.json"
    ]
    
    print(f"\n📋 Training Logs:")
    for log in logs:
        log_path = Path(log)
        if log_path.exists():
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    sessions = log_data.get("training_sessions", [])
                    print(f"   ✅ {log} ({len(sessions)} sessions)")
            except:
                print(f"   ⚠️ {log} (corrupted)")
        else:
            print(f"   ❌ {log}")

def show_knowledge_base_status():
    """Show knowledge base status"""
    print("\n📊 Knowledge Base Status")
    print("=" * 50)
    
    try:
        kb = SmartBuildingKnowledgeBase()
        collection_info = kb.collection.get()
        
        documents = collection_info.get('documents', [])
        metadatas = collection_info.get('metadatas', [])
        
        print(f"📈 Total document chunks: {len(documents)}")
        
        if metadatas:
            # Count by document type
            doc_types = {}
            sources = {}
            training_methods = {}
            
            for metadata in metadatas:
                if metadata:
                    # Document types
                    doc_type = metadata.get('document_type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                    
                    # Sources
                    source = metadata.get('source', metadata.get('source_file', 'unknown'))
                    sources[source] = sources.get(source, 0) + 1
                    
                    # Training methods
                    if metadata.get('auto_trained'):
                        training_methods['auto_trained'] = training_methods.get('auto_trained', 0) + 1
                    elif metadata.get('manually_added'):
                        training_methods['manually_added'] = training_methods.get('manually_added', 0) + 1
                    elif metadata.get('batch_trained'):
                        training_methods['batch_trained'] = training_methods.get('batch_trained', 0) + 1
                    else:
                        training_methods['other'] = training_methods.get('other', 0) + 1
            
            print(f"\n🏷️ Document Types:")
            for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {doc_type}: {count}")
            
            print(f"\n🔧 Training Methods:")
            for method, count in sorted(training_methods.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {method}: {count}")
            
            # Show IIC-specific content
            iic_count = sum(1 for m in metadatas if m and ('iic' in str(m.get('source_file', '')).lower() or 
                                                           'eiu' in str(m.get('source_file', '')).lower() or
                                                           m.get('document_type') == 'university_overview'))
            
            if iic_count > 0:
                print(f"\n🎯 IIC/EIU Content: {iic_count} chunks")
        
    except Exception as e:
        print(f"❌ Error accessing knowledge base: {e}")

def show_usage_instructions():
    """Show usage instructions"""
    print("\n📖 Usage Instructions")
    print("=" * 50)
    
    print("🎯 **Training on IIC Document:**")
    print("   python enhanced_training.py --iic")
    print("   python simple_auto_trainer.py --train-existing")
    print()
    
    print("📚 **Batch Training on All Documents:**")
    print("   python enhanced_training.py --batch")
    print("   python enhanced_training.py --all")
    print()
    
    print("🔄 **Auto-Training (Watch for Changes):**")
    print("   python simple_auto_trainer.py")
    print("   python auto_training_service.py")
    print()
    
    print("🌐 **Using Streamlit App:**")
    print("   streamlit run streamlit_app.py")
    print("   - Use 'Train on IIC_EIU_Overview' button")
    print("   - Use 'Train on All Documents' button")
    print("   - Check training status in the app")
    print()
    
    print("💡 **Adding New Content:**")
    print("   1. Add documents to smart_building_data/ folder")
    print("   2. Run auto-trainer to watch for changes:")
    print("      python simple_auto_trainer.py")
    print("   3. Or manually train using:")
    print("      python enhanced_training.py --batch")
    print()
    
    print("🔍 **Testing AI Knowledge:**")
    print("   - Ask questions in Streamlit app")
    print("   - Test queries: 'What is IIC?', 'Tell me about EIU'")
    print("   - Check training logs for recent updates")

def test_iic_queries():
    """Test some IIC-related queries"""
    print("\n🧪 Testing IIC Knowledge")
    print("=" * 50)
    
    try:
        kb = SmartBuildingKnowledgeBase()
        
        test_queries = [
            "What is IIC?",
            "Tell me about Eastern International University",
            "EIU Innovation Center",
            "IIC programs and facilities"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            try:
                context = kb.get_context_for_query(query)
                if context:
                    print(f"   ✅ Found relevant context ({len(context)} chars)")
                    # Show first 100 characters
                    preview = context[:100].replace('\n', ' ').strip()
                    print(f"   📝 Preview: {preview}...")
                else:
                    print(f"   ⚠️ No relevant context found")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error testing queries: {e}")

def main():
    """Main function"""
    print("🚀 Smart Building AI - Training System Summary")
    print("=" * 60)
    
    # Show current state
    show_current_state()
    
    # Show knowledge base status
    show_knowledge_base_status()
    
    # Show usage instructions
    show_usage_instructions()
    
    # Test IIC queries
    test_iic_queries()
    
    print("\n🎉 Training System Summary Complete!")
    print("💡 Use the instructions above to train and update your AI assistant")

if __name__ == "__main__":
    main()
