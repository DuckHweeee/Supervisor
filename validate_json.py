#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Validation and AI Training Data Test Script for Smart Building
"""

import json
from pathlib import Path
import sys

def validate_json_file(file_path):
    """Validate JSON file format and structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"✅ JSON file '{file_path}' is valid!")
        return data
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in '{file_path}': {e}")
        return None
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def analyze_smart_building_data(data):
    """Analyze the structure of smart building data for AI training"""
    if not data or "smartBuildingData" not in data:
        print("❌ Missing 'smartBuildingData' root element")
        return
    
    smart_data = data["smartBuildingData"]
    
    print("\n📊 Smart Building Data Analysis:")
    print("=" * 50)
    
    # Building Info
    if "buildingInfo" in smart_data:
        building_info = smart_data["buildingInfo"]
        print(f"🏢 Building: {building_info.get('name', 'N/A')}")
        print(f"📍 Location: {building_info.get('location', {}).get('address', 'N/A')}")
        print(f"🌍 Coordinates: {building_info.get('location', {}).get('coordinates', 'N/A')}")
        print(f"🏗️  Floors: {building_info.get('totalFloors', 'N/A')}")
        print(f"🚪 Total Rooms: {building_info.get('totalRooms', 'N/A')}")
    
    # Equipment Analysis
    if "equipment" in smart_data:
        equipment = smart_data["equipment"]
        print(f"\n⚙️  Equipment Count: {len(equipment)}")
        
        # Group by type and status
        equipment_types = {}
        equipment_status = {}
        
        for item in equipment:
            eq_type = item.get('type', 'Unknown')
            eq_status = item.get('status', 'Unknown')
            
            equipment_types[eq_type] = equipment_types.get(eq_type, 0) + 1
            equipment_status[eq_status] = equipment_status.get(eq_status, 0) + 1
        
        print("   Equipment Types:")
        for eq_type, count in equipment_types.items():
            print(f"   - {eq_type}: {count}")
        
        print("   Equipment Status:")
        for status, count in equipment_status.items():
            print(f"   - {status}: {count}")
    
    # Room Analysis
    if "rooms" in smart_data:
        rooms = smart_data["rooms"]
        print(f"\n🏠 Room Count: {len(rooms)}")
        
        total_capacity = sum(room.get('capacity', 0) for room in rooms)
        print(f"👥 Total Capacity: {total_capacity} people")
        
        # Materials summary
        total_materials = 0
        for room in rooms:
            total_materials += len(room.get('materials', []))
        print(f"📦 Total Material Types: {total_materials}")
    
    # AC Data Analysis
    if "acData" in smart_data:
        ac_data = smart_data["acData"]
        print(f"\n❄️  AC Units: {len(ac_data)}")
        
        ac_status = {}
        for ac in ac_data:
            status = ac.get('status', 'Unknown')
            ac_status[status] = ac_status.get(status, 0) + 1
        
        print("   AC Status Distribution:")
        for status, count in ac_status.items():
            print(f"   - {status}: {count}")
    
    # Energy Data Analysis
    if "electricalData" in smart_data:
        electrical = smart_data["electricalData"]
        print(f"\n⚡ Electrical Data Available:")
        if "daily" in electrical:
            print(f"   - Daily readings: {len(electrical['daily'])}")
        if "monthly" in electrical:
            print(f"   - Monthly readings: {len(electrical['monthly'])}")
    
    print("\n✅ Data structure is suitable for AI training!")
    return True

def generate_training_summary(data):
    """Generate a summary for AI training purposes"""
    if not data or "smartBuildingData" not in data:
        return
    
    print("\n🤖 AI Training Data Summary:")
    print("=" * 50)
    
    smart_data = data["smartBuildingData"]
    
    training_categories = [
        "Building Information and Location",
        "Equipment Management and Status",
        "Room Configuration and Materials", 
        "HVAC and Climate Control",
        "Energy Consumption and Monitoring",
        "Safety and Security Systems",
        "Material and Resource Management"
    ]
    
    print("📚 Training Categories Available:")
    for i, category in enumerate(training_categories, 1):
        print(f"   {i}. {category}")
    
    print("\n💡 AI Assistant Can Answer Questions About:")
    questions = [
        "What equipment is currently offline?",
        "How many people can Room 201 accommodate?",
        "What is the current temperature in specific rooms?",
        "Which rooms have PCs available?",
        "What is the energy consumption pattern?",
        "Who are the technicians responsible for maintenance?",
        "What safety equipment needs maintenance?"
    ]
    
    for question in questions:
        print(f"   • {question}")

def main():
    """Main function to validate and analyze JSON data"""
    print("🏢 Smart Building JSON Validator and AI Training Data Analyzer")
    print("=" * 70)
    
    # Check both files
    json_files = [
        "smart_building_data/building_data.json",
        "smart_building_data/mockData.json"
    ]
    
    valid_data = None
    
    for json_file in json_files:
        if Path(json_file).exists():
            print(f"\n📄 Validating: {json_file}")
            data = validate_json_file(json_file)
            
            if data:
                valid_data = data
                analyze_smart_building_data(data)
                generate_training_summary(data)
                break
        else:
            print(f"⚠️  File not found: {json_file}")
    
    if not valid_data:
        print("\n❌ No valid JSON files found for AI training!")
        return False
    
    print(f"\n🎉 JSON data is ready for AI training!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
