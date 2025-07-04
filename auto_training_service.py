#!/usr/bin/env python3
"""
Smart Building AI - Background Auto-Training Service
Run this script to enable automatic AI training when documents are updated
"""

import os
import sys
import time
import json
import signal
from pathlib import Path
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from auto_training import start_auto_training_watcher, train_on_iic_eiu_overview
    print("✅ Auto-training modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing auto-training modules: {e}")
    sys.exit(1)

class AutoTrainingService:
    """Background service for automatic AI training"""
    
    def __init__(self):
        self.running = False
        self.service_started = False
        
    def start_service(self):
        """Start the auto-training background service"""
        print("🚀 Smart Building AI - Auto-Training Service")
        print("=" * 60)
        
        # Check if IIC document exists and train on it first
        self.initial_training()
        
        # Start the file watcher
        print("\n🔍 Starting automatic file monitoring...")
        self.running = True
        self.service_started = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.stop_service)
        signal.signal(signal.SIGTERM, self.stop_service)
        
        try:
            # This will run the auto-training watcher
            start_auto_training_watcher()
        except KeyboardInterrupt:
            self.stop_service()
        except Exception as e:
            print(f"❌ Service error: {e}")
            self.stop_service()
    
    def initial_training(self):
        """Perform initial training on key documents"""
        print("📚 Performing initial training...")
        
        # Train on IIC_EIU_Overview.docx if it exists
        iic_doc = Path("smart_building_data/IIC_EIU_Overview.docx")
        if iic_doc.exists():
            print("🎯 Training on IIC_EIU_Overview.docx...")
            try:
                success = train_on_iic_eiu_overview()
                if success:
                    print("✅ Initial training on IIC document completed")
                else:
                    print("⚠️ Initial training on IIC document failed")
            except Exception as e:
                print(f"⚠️ Error during initial training: {e}")
        else:
            print("ℹ️ IIC_EIU_Overview.docx not found, skipping initial training")
        
        # Check for other important documents
        data_dir = Path("smart_building_data")
        if data_dir.exists():
            important_docs = [
                "building_overview.pdf",
                "hvac_manual.pdf", 
                "security_guide.pdf",
                "energy_management.pdf"
            ]
            
            found_docs = []
            for doc in important_docs:
                if (data_dir / doc).exists():
                    found_docs.append(doc)
            
            if found_docs:
                print(f"📄 Found {len(found_docs)} additional documents ready for training")
                print("💡 These will be automatically processed when modified")
            else:
                print("ℹ️ No additional documents found for initial training")
        
        print("✅ Initial training setup complete")
    
    def stop_service(self, signum=None, frame=None):
        """Stop the auto-training service"""
        if self.running:
            print(f"\n🛑 Stopping auto-training service...")
            self.running = False
            
            # Save service log
            self.save_service_log()
            
            print("✅ Auto-training service stopped")
        
        sys.exit(0)
    
    def save_service_log(self):
        """Save service operation log"""
        try:
            log_data = {
                "service_stop_time": datetime.now().isoformat(),
                "service_started": self.service_started,
                "uptime_seconds": time.time() - getattr(self, 'start_time', time.time())
            }
            
            with open("service_log.json", "w", encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Could not save service log: {e}")

def create_startup_script():
    """Create a startup script for Windows"""
    startup_script = """@echo off
cd /d "d:\\Supervisor"
echo Starting Smart Building AI Auto-Training Service...
python auto_training_service.py
pause
"""
    
    try:
        with open("start_auto_training.bat", "w") as f:
            f.write(startup_script)
        print("✅ Created start_auto_training.bat for easy startup")
    except Exception as e:
        print(f"⚠️ Could not create startup script: {e}")

def main():
    """Main function"""
    print("🤖 Smart Building AI - Auto-Training Service")
    print("=" * 60)
    print("This service will automatically train the AI when documents are updated")
    print("Press Ctrl+C to stop the service")
    print("")
    
    # Create startup script
    create_startup_script()
    
    # Initialize and start service
    service = AutoTrainingService()
    service.start_time = time.time()
    
    try:
        service.start_service()
    except KeyboardInterrupt:
        service.stop_service()
    except Exception as e:
        print(f"❌ Service failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
