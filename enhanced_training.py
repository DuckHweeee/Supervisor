#!/usr/bin/env python3
"""
Enhanced Auto-Training Script for Smart Building AI
Focuses on document content and avoids training on system files
"""

import os
import sys
import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

# Import the knowledge base
try:
    from streamlit_app import SmartBuildingKnowledgeBase
    print("✅ Successfully imported SmartBuildingKnowledgeBase")
except ImportError as e:
    print(f"❌ Error importing: {e}")
    sys.exit(1)

def enhanced_iic_training():
    """Enhanced training specifically for IIC_EIU_Overview.docx"""
    print("🎯 Enhanced IIC Document Training")
    print("=" * 50)
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Path to the document
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    
    if not doc_path.exists():
        print(f"❌ Document not found: {doc_path}")
        return False
    
    print(f"📄 Found document: {doc_path}")
    
    try:
        # Enhanced metadata for the IIC document
        metadata = {
            "document_type": "university_overview",
            "source": "IIC EIU Overview",
            "category": "institutional",
            "institution": "Eastern International University",
            "location": "Binh Duong, Vietnam",
            "training_date": datetime.now().isoformat(),
            "manually_added": True,
            "language": "vietnamese_english",
            "document_classification": "university_information",
            "priority": "high"
        }
        
        print("🤖 Training AI on IIC_EIU_Overview.docx with enhanced metadata...")
        success = kb.add_document(str(doc_path), metadata)
        
        if success:
            print("✅ Successfully trained AI on IIC_EIU_Overview.docx")
            
            # Log the training
            log_training_session(str(doc_path), "university_overview", success, "enhanced_manual_training")
            
            # Show knowledge base stats
            show_knowledge_base_stats(kb)
            
            # Test queries
            print("\n🔍 Testing queries on trained content...")
            test_queries = [
                "What is IIC?",
                "Tell me about Eastern International University",
                "Information about EIU Innovation Center",
                "What programs does EIU offer?",
                "EIU location and facilities"
            ]
            
            for query in test_queries:
                print(f"\n   📝 Query: {query}")
                try:
                    context = kb.get_context_for_query(query)
                    if context:
                        print(f"   ✅ Found context ({len(context)} chars)")
                    else:
                        print(f"   ⚠️ No context found")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            return True
        else:
            print("❌ Failed to train on IIC_EIU_Overview.docx")
            return False
            
    except Exception as e:
        print(f"❌ Error training on IIC document: {e}")
        return False

def log_training_session(file_path, document_type, success, training_method):
    """Log training session with enhanced details"""
    log_file = Path("iic_training_log.json")
    
    # Load existing log or create new
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except:
            log_data = {"training_sessions": []}
    else:
        log_data = {"training_sessions": []}
    
    # Add new training session
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "file_path": str(file_path),
        "file_name": os.path.basename(file_path),
        "document_type": document_type,
        "success": success,
        "training_method": training_method,
        "session_id": f"iic_training_{int(time.time())}"
    }
    
    log_data["training_sessions"].append(log_entry)
    
    # Keep only last 50 entries
    if len(log_data["training_sessions"]) > 50:
        log_data["training_sessions"] = log_data["training_sessions"][-50:]
    
    # Save log
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        print(f"📋 Training session logged to {log_file}")
    except Exception as e:
        print(f"⚠️ Could not save training log: {e}")

def show_knowledge_base_stats(kb):
    """Show comprehensive knowledge base statistics"""
    try:
        collection_info = kb.collection.get()
        documents = collection_info.get('documents', [])
        metadatas = collection_info.get('metadatas', [])
        
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"   • Total document chunks: {len(documents)}")
        
        if metadatas:
            # Count document types
            doc_types = {}
            sources = {}
            languages = {}
            
            for metadata in metadatas:
                if metadata:
                    # Document types
                    doc_type = metadata.get('document_type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                    
                    # Sources
                    source = metadata.get('source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1
                    
                    # Languages
                    language = metadata.get('language', 'unknown')
                    languages[language] = languages.get(language, 0) + 1
            
            print(f"   • Document types: {len(doc_types)}")
            for doc_type, count in sorted(doc_types.items()):
                print(f"     - {doc_type}: {count}")
            
            print(f"   • Sources: {len(sources)}")
            for source, count in sorted(sources.items()):
                if count > 5:  # Only show significant sources
                    print(f"     - {source}: {count}")
            
            print(f"   • Languages: {len(languages)}")
            for language, count in sorted(languages.items()):
                if language != 'unknown':
                    print(f"     - {language}: {count}")
        
    except Exception as e:
        print(f"❌ Error getting knowledge base stats: {e}")

def batch_train_documents():
    """Train on all documents in the smart_building_data directory"""
    print("\n📚 Batch Training on All Documents")
    print("=" * 50)
    
    kb = SmartBuildingKnowledgeBase()
    data_dir = Path("smart_building_data")
    
    if not data_dir.exists():
        print(f"❌ Directory not found: {data_dir}")
        return False
    
    # Supported file extensions
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx']
    
    # Find all documents
    documents = []
    for ext in supported_extensions:
        documents.extend(data_dir.glob(f"*{ext}"))
    
    if not documents:
        print("❌ No supported documents found")
        return False
    
    print(f"📄 Found {len(documents)} documents to train on")
    
    trained_count = 0
    failed_count = 0
    
    for i, doc_path in enumerate(documents, 1):
        print(f"\n[{i}/{len(documents)}] Training on: {doc_path.name}")
        
        try:
            # Determine document type and metadata
            file_name = doc_path.name.lower()
            
            if 'iic' in file_name or 'eiu' in file_name:
                doc_type = "university_overview"
                priority = "high"
            elif 'hvac' in file_name:
                doc_type = "hvac_manual"
                priority = "medium"
            elif 'lighting' in file_name:
                doc_type = "lighting_specifications"
                priority = "medium"
            elif 'security' in file_name:
                doc_type = "security_manual"
                priority = "medium"
            elif 'energy' in file_name:
                doc_type = "energy_management"
                priority = "medium"
            elif 'maintenance' in file_name:
                doc_type = "maintenance_guide"
                priority = "medium"
            elif 'safety' in file_name:
                doc_type = "safety_procedures"
                priority = "high"
            elif 'automation' in file_name:
                doc_type = "automation_guide"
                priority = "medium"
            else:
                doc_type = "general_documentation"
                priority = "low"
            
            metadata = {
                "document_type": doc_type,
                "source_file": doc_path.name,
                "training_date": datetime.now().isoformat(),
                "batch_trained": True,
                "priority": priority,
                "file_size": doc_path.stat().st_size if doc_path.exists() else 0
            }
            
            success = kb.add_document(str(doc_path), metadata)
            
            if success:
                print(f"   ✅ Success - {doc_type}")
                trained_count += 1
                
                # Log the training
                log_training_session(str(doc_path), doc_type, success, "batch_training")
            else:
                print(f"   ❌ Failed")
                failed_count += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1
    
    print(f"\n📊 Batch Training Results:")
    print(f"   ✅ Successfully trained: {trained_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📈 Success rate: {(trained_count/(trained_count+failed_count))*100:.1f}%")
    
    # Show final stats
    show_knowledge_base_stats(kb)
    
    return trained_count > 0

def main():
    """Main training function"""
    print("🚀 Enhanced Smart Building AI Training System")
    print("=" * 60)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--iic":
            enhanced_iic_training()
        elif sys.argv[1] == "--batch":
            batch_train_documents()
        elif sys.argv[1] == "--all":
            print("🎯 Running comprehensive training...")
            enhanced_iic_training()
            batch_train_documents()
        else:
            print("❌ Unknown argument. Use --iic, --batch, or --all")
    else:
        # Default: train on IIC document
        enhanced_iic_training()

if __name__ == "__main__":
    main()
