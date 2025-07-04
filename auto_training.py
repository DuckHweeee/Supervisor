#!/usr/bin/env python3
"""
Auto-training script for Smart Building AI Assistant
Automatically trains the AI when new content is added or updated
"""

import os
import sys
import time
import json
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

class AutoTrainingHandler(FileSystemEventHandler):
    """Handler for file system events to trigger auto-training"""
    
    def __init__(self, kb):
        self.kb = kb
        self.last_training = {}
        self.training_delay = 5  # seconds delay to avoid rapid re-training
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        # Check if it's a file we should train on
        if self.should_train_on_file(file_path):
            current_time = time.time()
            
            # Avoid rapid re-training of the same file
            if file_path in self.last_training:
                if current_time - self.last_training[file_path] < self.training_delay:
                    return
            
            self.last_training[file_path] = current_time
            print(f"🔄 File modified: {file_name}")
            self.train_on_file(file_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        if self.should_train_on_file(file_path):
            print(f"📄 New file detected: {file_name}")
            time.sleep(1)  # Wait a moment for file to be fully written
            self.train_on_file(file_path)
    
    def should_train_on_file(self, file_path):
        """Check if we should train on this file"""
        # Supported file extensions
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx']
        
        # Check extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in supported_extensions:
            return False
        
        # Skip temporary files
        file_name = os.path.basename(file_path)
        if file_name.startswith('~') or file_name.startswith('.'):
            return False
        
        # Skip backup files
        if '.bak' in file_name or '.tmp' in file_name:
            return False
        
        return True
    
    def train_on_file(self, file_path):
        """Train the AI on a specific file"""
        try:
            file_name = os.path.basename(file_path)
            print(f"🤖 Training AI on: {file_name}")
            
            # Determine document type based on file name and location
            document_type = self.determine_document_type(file_path)
            
            # Add document to knowledge base
            success = self.kb.add_document(file_path, {
                "document_type": document_type,
                "auto_trained": True,
                "training_date": datetime.now().isoformat(),
                "source_file": file_name
            })
            
            if success:
                print(f"✅ Successfully trained AI on: {file_name}")
                
                # Log the training
                self.log_training(file_path, document_type, success)
                
                # Get some quick stats
                self.show_knowledge_base_stats()
            else:
                print(f"❌ Failed to train on: {file_name}")
                
        except Exception as e:
            print(f"❌ Error training on {file_path}: {e}")
    
    def determine_document_type(self, file_path):
        """Determine the document type based on file name and content"""
        file_name = os.path.basename(file_path).lower()
        
        # Check for specific document types
        if 'iic' in file_name or 'eiu' in file_name:
            return "university_overview"
        elif 'hvac' in file_name:
            return "hvac_manual"
        elif 'lighting' in file_name:
            return "lighting_specifications"
        elif 'security' in file_name:
            return "security_manual"
        elif 'energy' in file_name:
            return "energy_management"
        elif 'maintenance' in file_name:
            return "maintenance_guide"
        elif 'safety' in file_name:
            return "safety_procedures"
        elif 'automation' in file_name:
            return "automation_guide"
        elif 'manual' in file_name:
            return "technical_manual"
        elif 'specification' in file_name:
            return "system_specification"
        else:
            return "general_documentation"
    
    def log_training(self, file_path, document_type, success):
        """Log training activities"""
        log_file = Path("training_log.json")
        
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
            "training_method": "auto_training"
        }
        
        log_data["training_sessions"].append(log_entry)
        
        # Keep only last 100 entries
        if len(log_data["training_sessions"]) > 100:
            log_data["training_sessions"] = log_data["training_sessions"][-100:]
        
        # Save log
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save training log: {e}")
    
    def show_knowledge_base_stats(self):
        """Show quick knowledge base statistics"""
        try:
            collection_info = self.kb.collection.get()
            total_docs = len(collection_info.get('documents', []))
            
            # Count different source types
            metadata_list = collection_info.get('metadatas', [])
            source_types = {}
            auto_trained_count = 0
            
            for metadata in metadata_list:
                if metadata:
                    source_type = metadata.get('document_type', 'unknown')
                    source_types[source_type] = source_types.get(source_type, 0) + 1
                    
                    if metadata.get('auto_trained'):
                        auto_trained_count += 1
            
            print(f"📊 Knowledge Base Stats:")
            print(f"   • Total documents: {total_docs}")
            print(f"   • Auto-trained documents: {auto_trained_count}")
            print(f"   • Document types: {len(source_types)}")
            
        except Exception as e:
            print(f"⚠️ Could not get KB stats: {e}")

def train_on_iic_eiu_overview():
    """Train the AI on the IIC_EIU_Overview.docx document"""
    print("🚀 Training AI on IIC_EIU_Overview.docx")
    print("=" * 50)
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Path to the document
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    
    if not doc_path.exists():
        print(f"❌ Document not found: {doc_path}")
        return False
    
    try:
        # Add the document to knowledge base
        metadata = {
            "document_type": "university_overview",
            "source": "IIC EIU Overview",
            "category": "institutional",
            "training_date": datetime.now().isoformat(),
            "manually_added": True
        }
        
        success = kb.add_document(str(doc_path), metadata)
        
        if success:
            print(f"✅ Successfully trained AI on IIC_EIU_Overview.docx")
            
            # Show knowledge base stats
            try:
                collection_info = kb.collection.get()
                total_docs = len(collection_info.get('documents', []))
                print(f"📊 Knowledge base now contains {total_docs} document chunks")
            except Exception as e:
                print(f"⚠️ Could not get stats: {e}")
            
            return True
        else:
            print(f"❌ Failed to train on IIC_EIU_Overview.docx")
            return False
            
    except Exception as e:
        print(f"❌ Error training on document: {e}")
        return False

def start_auto_training_watcher():
    """Start the automatic training watcher"""
    print("🔍 Starting Auto-Training Watcher")
    print("=" * 50)
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Create handler
    handler = AutoTrainingHandler(kb)
    
    # Create observer
    observer = Observer()
    
    # Watch directories
    watch_dirs = [
        "smart_building_data",
        "documents",
        ".",  # Current directory
    ]
    
    for watch_dir in watch_dirs:
        if os.path.exists(watch_dir):
            observer.schedule(handler, watch_dir, recursive=True)
            print(f"👁️ Watching: {os.path.abspath(watch_dir)}")
    
    # Start watching
    observer.start()
    print("✅ Auto-training watcher started!")
    print("💡 The AI will automatically train on new or updated documents")
    print("📁 Supported formats: PDF, DOCX, DOC, TXT, JSON, MD, CSV, XLSX")
    print("⏹️ Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping auto-training watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Auto-training watcher stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-training for Smart Building AI")
    parser.add_argument('--train-iic', action='store_true', 
                       help='Train on IIC_EIU_Overview.docx document')
    parser.add_argument('--watch', action='store_true', 
                       help='Start auto-training watcher')
    parser.add_argument('--train-all', action='store_true', 
                       help='Train on all documents in smart_building_data folder')
    
    args = parser.parse_args()
    
    if args.train_iic:
        train_on_iic_eiu_overview()
    elif args.watch:
        start_auto_training_watcher()
    elif args.train_all:
        train_all_documents()
    else:
        # Default: Train on IIC document and start watcher
        print("🤖 Smart Building AI Auto-Training System")
        print("=" * 60)
        
        # First, train on the IIC document
        print("\n1️⃣ Training on IIC_EIU_Overview.docx...")
        train_on_iic_eiu_overview()
        
        print("\n2️⃣ Starting auto-training watcher...")
        start_auto_training_watcher()

def train_all_documents():
    """Train on all documents in smart_building_data folder"""
    print("📚 Training on All Documents")
    print("=" * 50)
    
    kb = SmartBuildingKnowledgeBase()
    data_dir = Path("smart_building_data")
    
    if not data_dir.exists():
        print("❌ smart_building_data directory not found")
        return
    
    # Get all supported files
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx']
    files_to_train = []
    
    for ext in supported_extensions:
        files_to_train.extend(data_dir.glob(f"*{ext}"))
    
    if not files_to_train:
        print("❌ No supported documents found")
        return
    
    print(f"📄 Found {len(files_to_train)} documents to train on:")
    for file in files_to_train:
        print(f"   • {file.name}")
    
    trained_count = 0
    for file_path in files_to_train:
        try:
            print(f"\n🤖 Training on: {file_path.name}")
            
            # Determine document type
            handler = AutoTrainingHandler(kb)
            document_type = handler.determine_document_type(str(file_path))
            
            metadata = {
                "document_type": document_type,
                "training_date": datetime.now().isoformat(),
                "batch_trained": True,
                "source_file": file_path.name
            }
            
            success = kb.add_document(str(file_path), metadata)
            
            if success:
                print(f"✅ Successfully trained on: {file_path.name}")
                trained_count += 1
            else:
                print(f"❌ Failed to train on: {file_path.name}")
                
        except Exception as e:
            print(f"❌ Error training on {file_path.name}: {e}")
    
    print(f"\n🎉 Training complete!")
    print(f"✅ Successfully trained on {trained_count}/{len(files_to_train)} documents")

if __name__ == "__main__":
    main()
