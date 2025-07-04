#!/usr/bin/env python3
"""
Smart Building AI - Simple Auto-Training Watcher
Automatically trains AI when new content is added to smart_building_data folder
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

try:
    from streamlit_app import SmartBuildingKnowledgeBase
    print("✅ Auto-training modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

class SmartBuildingAutoTrainer(FileSystemEventHandler):
    """Simple auto-trainer that focuses on document content"""
    
    def __init__(self):
        self.kb = SmartBuildingKnowledgeBase()
        self.last_training = {}
        self.training_delay = 3  # seconds delay to avoid rapid re-training
        
        # Files to ignore (system files, logs, etc.)
        self.ignore_files = {
            'training_log.json',
            'iic_training_log.json',
            'iic_query_test_results.json',
            '.DS_Store',
            'Thumbs.db',
            'desktop.ini'
        }
        
        # File extensions to watch
        self.watch_extensions = {'.pdf', '.docx', '.doc', '.txt', '.json', '.md', '.csv', '.xlsx'}
    
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
        
        self.handle_file_event(event.src_path, "created")
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        self.handle_file_event(event.src_path, "modified")
    
    def handle_file_event(self, file_path, event_type):
        """Handle file events and train if appropriate"""
        file_name = os.path.basename(file_path)
        
        # Skip if file should be ignored
        if file_name in self.ignore_files:
            return
        
        # Skip temporary files
        if file_name.startswith('~') or file_name.startswith('.'):
            return
        
        # Check file extension
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in self.watch_extensions:
            return
        
        # Avoid rapid re-training
        current_time = time.time()
        if file_path in self.last_training:
            if current_time - self.last_training[file_path] < self.training_delay:
                return
        
        self.last_training[file_path] = current_time
        
        print(f"📄 {event_type.title()} file: {file_name}")
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Train on the file
        self.train_on_file(file_path)
    
    def train_on_file(self, file_path):
        """Train the AI on a specific file"""
        try:
            file_name = os.path.basename(file_path)
            print(f"🤖 Training AI on: {file_name}")
            
            # Determine document type and metadata
            doc_type = self.determine_document_type(file_name)
            
            metadata = {
                "document_type": doc_type,
                "source_file": file_name,
                "training_date": datetime.now().isoformat(),
                "auto_trained": True,
                "training_method": "file_watcher"
            }
            
            # Add IIC-specific metadata
            if 'iic' in file_name.lower() or 'eiu' in file_name.lower():
                metadata.update({
                    "institution": "Eastern International University",
                    "category": "institutional",
                    "priority": "high",
                    "language": "vietnamese_english"
                })
            
            success = self.kb.add_document(file_path, metadata)
            
            if success:
                print(f"✅ Successfully trained AI on: {file_name}")
                
                # Log the training
                self.log_training(file_path, doc_type, success)
                
                # Show quick stats
                self.show_stats()
            else:
                print(f"❌ Failed to train on: {file_name}")
                
        except Exception as e:
            print(f"❌ Error training on {file_path}: {e}")
    
    def determine_document_type(self, file_name):
        """Determine document type based on filename"""
        name_lower = file_name.lower()
        
        if 'iic' in name_lower or 'eiu' in name_lower:
            return "university_overview"
        elif 'hvac' in name_lower:
            return "hvac_manual"
        elif 'lighting' in name_lower:
            return "lighting_specifications"
        elif 'security' in name_lower:
            return "security_manual"
        elif 'energy' in name_lower:
            return "energy_management"
        elif 'maintenance' in name_lower:
            return "maintenance_guide"
        elif 'safety' in name_lower:
            return "safety_procedures"
        elif 'automation' in name_lower:
            return "automation_guide"
        elif 'manual' in name_lower:
            return "technical_manual"
        else:
            return "general_documentation"
    
    def log_training(self, file_path, doc_type, success):
        """Log training session"""
        log_file = Path("auto_training_log.json")
        
        # Load existing log
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {"training_sessions": []}
        else:
            log_data = {"training_sessions": []}
        
        # Add new session
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": str(file_path),
            "file_name": os.path.basename(file_path),
            "document_type": doc_type,
            "success": success,
            "training_method": "auto_watcher"
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
    
    def show_stats(self):
        """Show quick knowledge base statistics"""
        try:
            collection_info = self.kb.collection.get()
            total_docs = len(collection_info.get('documents', []))
            
            metadatas = collection_info.get('metadatas', [])
            auto_trained = sum(1 for m in metadatas if m and m.get('auto_trained'))
            
            print(f"📊 Knowledge Base: {total_docs} documents ({auto_trained} auto-trained)")
            
        except Exception as e:
            print(f"⚠️ Could not get stats: {e}")

def start_auto_training():
    """Start the auto-training file watcher"""
    print("🚀 Smart Building AI - Auto-Training Watcher")
    print("=" * 50)
    
    # Create event handler
    event_handler = SmartBuildingAutoTrainer()
    
    # Create observer
    observer = Observer()
    
    # Watch the smart_building_data directory
    data_dir = Path("smart_building_data")
    if data_dir.exists():
        observer.schedule(event_handler, str(data_dir), recursive=False)
        print(f"👁️ Watching: {data_dir.absolute()}")
    else:
        print(f"⚠️ Directory not found: {data_dir}")
        print("📁 Creating smart_building_data directory...")
        data_dir.mkdir(exist_ok=True)
        observer.schedule(event_handler, str(data_dir), recursive=False)
    
    # Start observer
    observer.start()
    
    print("✅ Auto-training watcher started!")
    print("📄 Supported formats: PDF, DOCX, DOC, TXT, JSON, MD, CSV, XLSX")
    print("💡 Add or update documents in smart_building_data/ to trigger training")
    print("⏹️ Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping auto-training watcher...")
        observer.stop()
        observer.join()
        print("✅ Auto-training watcher stopped")

def train_existing_documents():
    """Train on existing documents in smart_building_data"""
    print("📚 Training on existing documents...")
    
    trainer = SmartBuildingAutoTrainer()
    data_dir = Path("smart_building_data")
    
    if not data_dir.exists():
        print("❌ smart_building_data directory not found")
        return
    
    # Find all supported files
    files = []
    for ext in trainer.watch_extensions:
        files.extend(data_dir.glob(f"*{ext}"))
    
    if not files:
        print("ℹ️ No documents found to train on")
        return
    
    print(f"📄 Found {len(files)} documents")
    
    for file_path in files:
        if file_path.name not in trainer.ignore_files:
            trainer.train_on_file(str(file_path))
    
    print("✅ Initial training completed")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--train-existing":
        train_existing_documents()
    else:
        # Train on existing documents first
        train_existing_documents()
        print()
        # Start watcher
        start_auto_training()

if __name__ == "__main__":
    main()
