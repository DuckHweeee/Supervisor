#!/usr/bin/env python3
"""
Smart Building AI Training Data Generator
This script extracts specific information from building data and creates training knowledge
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SmartBuildingTrainingDataGenerator:
    def __init__(self, building_data_path: str = "smart_building_data/building_data.json"):
        self.building_data_path = building_data_path
        self.training_data = {}
        self.load_building_data()
    
    def load_building_data(self):
        """Load building data from JSON file"""
        try:
            with open(self.building_data_path, 'r', encoding='utf-8') as file:
                self.building_data = json.load(file)
                print(f"✅ Loaded building data from {self.building_data_path}")
        except Exception as e:
            print(f"❌ Error loading building data: {e}")
            self.building_data = {}
    
    def extract_building_info(self) -> Dict[str, str]:
        """Extract basic building information"""
        info = self.building_data.get("smartBuildingData", {}).get("buildingInfo", {})
        
        training_info = {
            "building_overview": f"""
            Building Name: {info.get('name', 'Unknown')}
            Location: {info.get('location', {}).get('address', 'Unknown')}
            Coordinates: {info.get('location', {}).get('coordinates', 'Unknown')}
            Total Floors: {info.get('totalFloors', 'Unknown')}
            Total Rooms: {info.get('totalRooms', 'Unknown')}
            Building Type: {info.get('buildingType', 'Unknown')}
            """,
            
            "building_facts": f"""
            The building has {info.get('totalFloors', 0)} floors and {info.get('totalRooms', 0)} rooms.
            It is located at {info.get('location', {}).get('address', 'Unknown location')}.
            This is an {info.get('buildingType', 'Unknown')} facility.
            """
        }
        
        return training_info
    
    def extract_equipment_knowledge(self) -> Dict[str, str]:
        """Extract equipment-specific knowledge"""
        equipment_list = self.building_data.get("smartBuildingData", {}).get("equipment", [])
        
        # Categorize equipment by type
        equipment_by_type = {}
        equipment_status = {"active": 0, "offline": 0, "maintenance": 0}
        
        for equipment in equipment_list:
            eq_type = equipment.get("type", "Unknown")
            status = equipment.get("status", "Unknown").lower()
            
            if eq_type not in equipment_by_type:
                equipment_by_type[eq_type] = []
            equipment_by_type[eq_type].append(equipment)
            
            if status in equipment_status:
                equipment_status[status] += 1
        
        # Generate training knowledge
        training_knowledge = {}
        
        # Equipment overview
        training_knowledge["equipment_overview"] = f"""
        Total Equipment: {len(equipment_list)} devices
        Active Equipment: {equipment_status['active']} devices
        Offline Equipment: {equipment_status['offline']} devices
        Maintenance Required: {equipment_status['maintenance']} devices
        
        Equipment Categories:
        """ + "\n".join([f"- {eq_type}: {len(devices)} devices" for eq_type, devices in equipment_by_type.items()])
        
        # Specific equipment knowledge
        for eq_type, devices in equipment_by_type.items():
            active_devices = [d for d in devices if d.get("status", "").lower() == "active"]
            offline_devices = [d for d in devices if d.get("status", "").lower() == "offline"]
            maintenance_devices = [d for d in devices if d.get("status", "").lower() == "maintenance"]
            
            training_knowledge[f"{eq_type.lower()}_equipment"] = f"""
            {eq_type} Equipment Status:
            - Total {eq_type} devices: {len(devices)}
            - Active: {len(active_devices)}
            - Offline: {len(offline_devices)}
            - Maintenance required: {len(maintenance_devices)}
            
            Equipment Details:
            """ + "\n".join([f"- {d.get('equipmentName', 'Unknown')}: {d.get('status', 'Unknown')} (Target: {d.get('target', 'N/A')})" for d in devices])
        
        return training_knowledge
    
    def extract_hvac_knowledge(self) -> Dict[str, str]:
        """Extract HVAC-specific knowledge from AC data"""
        ac_data = self.building_data.get("smartBuildingData", {}).get("acData", [])
        
        # Analyze AC status
        ac_status = {"on": 0, "off": 0, "unconnectable": 0, "used_up_filter": 0}
        temperature_data = []
        setpoint_data = []
        
        for ac_unit in ac_data:
            status = ac_unit.get("status", "unknown")
            if status in ac_status:
                ac_status[status] += 1
            
            if "temperature" in ac_unit:
                temperature_data.append(ac_unit["temperature"])
            
            if "setpoint" in ac_unit:
                setpoint_data.append(ac_unit["setpoint"])
        
        # Calculate averages
        avg_temp = sum(temperature_data) / len(temperature_data) if temperature_data else 0
        avg_setpoint = sum(setpoint_data) / len(setpoint_data) if setpoint_data else 0
        
        training_knowledge = {
            "hvac_system_status": f"""
            HVAC System Overview:
            - Total AC Units: {len(ac_data)}
            - Units Online: {ac_status['on']}
            - Units Offline: {ac_status['off']}
            - Unconnectable Units: {ac_status['unconnectable']}
            - Filter Replacement Needed: {ac_status['used_up_filter']}
            
            Temperature Analysis:
            - Average Room Temperature: {avg_temp:.1f}°C
            - Average Setpoint: {avg_setpoint:.1f}°C
            - Temperature Range: {min(temperature_data) if temperature_data else 0:.1f}°C - {max(temperature_data) if temperature_data else 0:.1f}°C
            """,
            
            "hvac_recommendations": f"""
            HVAC Maintenance Recommendations:
            - {ac_status['used_up_filter']} units need filter replacement
            - {ac_status['unconnectable']} units need connectivity check
            - {ac_status['off']} units are currently offline
            - Optimal temperature setpoint: 20-22°C for energy efficiency
            - Current average temperature: {avg_temp:.1f}°C
            """
        }
        
        return training_knowledge
    
    def extract_energy_knowledge(self) -> Dict[str, str]:
        """Extract energy consumption knowledge"""
        electrical_data = self.building_data.get("smartBuildingData", {}).get("electricalData", {})
        consumption_data = self.building_data.get("smartBuildingData", {}).get("consumptionData", {})
        monetary_data = self.building_data.get("smartBuildingData", {}).get("monetaryData", {})
        
        training_knowledge = {}
        
        # Daily energy patterns
        daily_data = electrical_data.get("daily", [])
        if daily_data:
            peak_consumption = max(daily_data, key=lambda x: sum([x.get(block, 0) for block in ['block3', 'block4_5', 'block6', 'block8', 'block10', 'block11']]))
            
            training_knowledge["energy_patterns"] = f"""
            Daily Energy Consumption Patterns:
            - Peak consumption time: {peak_consumption.get('timeCheckpoint', 'Unknown')}
            - Energy consumption increases during class hours (9:00-14:00)
            - Lower consumption during early morning and evening
            - Building blocks have varying consumption patterns
            """
        
        # Room-specific consumption
        if consumption_data:
            room_consumptions = [(room, data['daily']) for room, data in consumption_data.items()]
            room_consumptions.sort(key=lambda x: x[1], reverse=True)
            
            training_knowledge["room_energy_usage"] = f"""
            Room Energy Consumption Analysis:
            - Highest consuming room: {room_consumptions[0][0]} ({room_consumptions[0][1]} kWh/day)
            - Lowest consuming room: {room_consumptions[-1][0]} ({room_consumptions[-1][1]} kWh/day)
            - Average daily consumption: {sum([data['daily'] for data in consumption_data.values()]) / len(consumption_data):.1f} kWh
            """
        
        # Energy efficiency recommendations
        training_knowledge["energy_efficiency"] = """
        Energy Efficiency Recommendations:
        - Implement smart scheduling to reduce peak demand
        - Use occupancy sensors to control lighting and HVAC
        - Optimize HVAC setpoints based on occupancy
        - Consider LED lighting upgrades for 80% energy savings
        - Monitor and analyze consumption patterns regularly
        """
        
        return training_knowledge
    
    def extract_room_knowledge(self) -> Dict[str, str]:
        """Extract room and space management knowledge"""
        rooms = self.building_data.get("smartBuildingData", {}).get("rooms", [])
        room_usage = self.building_data.get("smartBuildingData", {}).get("roomInUseChart", {})
        
        training_knowledge = {}
        
        # Room capacity analysis
        if rooms:
            total_capacity = sum([room.get("capacity", 0) for room in rooms])
            avg_capacity = total_capacity / len(rooms)
            
            room_types = {}
            for room in rooms:
                room_type = room.get("roomType", "Unknown")
                if room_type not in room_types:
                    room_types[room_type] = 0
                room_types[room_type] += 1
            
            training_knowledge["room_management"] = f"""
            Room Management Overview:
            - Total rooms analyzed: {len(rooms)}
            - Total capacity: {total_capacity} persons
            - Average room capacity: {avg_capacity:.1f} persons
            - Room types: {', '.join([f"{rtype}: {count}" for rtype, count in room_types.items()])}
            """
        
        # Room utilization
        if room_usage:
            for floor, usage_data in room_usage.items():
                in_use = next((item['rooms'] for item in usage_data if item['type'] == 'inUse'), 0)
                vacant = next((item['rooms'] for item in usage_data if item['type'] == 'vacant'), 0)
                total = in_use + vacant
                utilization = (in_use / total * 100) if total > 0 else 0
                
                training_knowledge[f"{floor.lower()}_utilization"] = f"""
                {floor} Room Utilization:
                - Total rooms: {total}
                - Rooms in use: {in_use}
                - Vacant rooms: {vacant}
                - Utilization rate: {utilization:.1f}%
                """
        
        return training_knowledge
    
    def extract_safety_security_knowledge(self) -> Dict[str, str]:
        """Extract safety and security knowledge"""
        equipment_list = self.building_data.get("smartBuildingData", {}).get("equipment", [])
        
        # Filter safety and security equipment
        safety_equipment = [eq for eq in equipment_list if eq.get("type") in ["Safety", "Security"]]
        
        safety_devices = [eq for eq in safety_equipment if eq.get("type") == "Safety"]
        security_devices = [eq for eq in safety_equipment if eq.get("type") == "Security"]
        
        training_knowledge = {
            "safety_systems": f"""
            Safety System Status:
            - Total safety devices: {len(safety_devices)}
            - Active safety devices: {len([d for d in safety_devices if d.get('status') == 'Active'])}
            - Safety devices needing maintenance: {len([d for d in safety_devices if d.get('status') == 'Maintenance'])}
            - Safety devices offline: {len([d for d in safety_devices if d.get('status') == 'Offline'])}
            
            Safety Equipment Details:
            """ + "\n".join([f"- {d.get('equipmentName', 'Unknown')}: {d.get('status', 'Unknown')}" for d in safety_devices]),
            
            "security_systems": f"""
            Security System Status:
            - Total security devices: {len(security_devices)}
            - Active security devices: {len([d for d in security_devices if d.get('status') == 'Active'])}
            - Security devices needing maintenance: {len([d for d in security_devices if d.get('status') == 'Maintenance'])}
            - Security devices offline: {len([d for d in security_devices if d.get('status') == 'Offline'])}
            
            Security Equipment Details:
            """ + "\n".join([f"- {d.get('equipmentName', 'Unknown')}: {d.get('status', 'Unknown')}" for d in security_devices])
        }
        
        return training_knowledge
    
    def generate_comprehensive_training_data(self) -> Dict[str, Any]:
        """Generate all training data"""
        print("🧠 Generating comprehensive training data...")
        
        all_training_data = {}
        
        # Extract all knowledge categories
        all_training_data.update(self.extract_building_info())
        all_training_data.update(self.extract_equipment_knowledge())
        all_training_data.update(self.extract_hvac_knowledge())
        all_training_data.update(self.extract_energy_knowledge())
        all_training_data.update(self.extract_room_knowledge())
        all_training_data.update(self.extract_safety_security_knowledge())
        
        # Generate FAQ-style training data
        faq_data = self.generate_faq_training_data()
        all_training_data.update(faq_data)
        
        return all_training_data
    
    def generate_faq_training_data(self) -> Dict[str, str]:
        """Generate FAQ-style training data for common questions"""
        faq_data = {
            "temperature_control_faq": """
            Q: How should I control the temperature in the building?
            A: Maintain temperatures between 20-22°C for optimal comfort and energy efficiency. Use smart thermostats with scheduling to reduce energy consumption by 15-25%.
            
            Q: What should I do if rooms are too hot or cold?
            A: Check HVAC system status, verify setpoints, and ensure proper ventilation. Consider occupancy levels and external weather conditions.
            """,
            
            "lighting_control_faq": """
            Q: How can I optimize lighting in the building?
            A: Use LED systems with daylight sensors and occupancy controls. Implement automated scheduling to reduce energy consumption by up to 80%.
            
            Q: What lighting settings should I use?
            A: Adjust lighting based on natural light availability and occupancy. Use motion sensors to automatically control lighting in unoccupied areas.
            """,
            
            "energy_efficiency_faq": """
            Q: How can I reduce energy consumption?
            A: Implement smart scheduling, use occupancy sensors, optimize HVAC setpoints, and upgrade to LED lighting. Monitor consumption patterns regularly.
            
            Q: What are the peak energy consumption times?
            A: Peak consumption typically occurs during class hours (9:00-14:00). Schedule non-essential equipment to run during off-peak hours.
            """,
            
            "equipment_maintenance_faq": """
            Q: How often should I maintain building equipment?
            A: Establish preventive maintenance schedules: HVAC filters every 3-6 months, safety systems monthly testing, and regular equipment inspections.
            
            Q: What should I do if equipment is offline?
            A: Check power supply, network connectivity, and reset if necessary. Contact maintenance if problems persist.
            """,
            
            "safety_security_faq": """
            Q: How do I ensure building safety?
            A: Test fire safety systems monthly, maintain clear emergency exits, and ensure all safety equipment is operational.
            
            Q: What security measures should be in place?
            A: Use access control systems, motion detectors, and surveillance cameras. Integrate security systems with building automation.
            """
        }
        
        return faq_data
    
    def save_training_data(self, filename: str = "ai_training_data.json"):
        """Save training data to file"""
        training_data = self.generate_comprehensive_training_data()
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(training_data, file, indent=2, ensure_ascii=False)
            print(f"✅ Training data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving training data: {e}")
            return False
    
    def create_training_documents(self):
        """Create individual training documents for each knowledge category"""
        training_data = self.generate_comprehensive_training_data()
        
        # Create training documents directory
        training_dir = Path("smart_building_data/training_documents")
        training_dir.mkdir(exist_ok=True)
        
        for category, content in training_data.items():
            filename = training_dir / f"{category}_training.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(f"# {category.replace('_', ' ').title()} Training Data\n\n")
                    file.write(content)
                print(f"✅ Created training document: {filename}")
            except Exception as e:
                print(f"❌ Error creating training document {filename}: {e}")
    
    def display_training_summary(self):
        """Display a summary of generated training data"""
        training_data = self.generate_comprehensive_training_data()
        
        print("\n🎓 AI TRAINING DATA SUMMARY")
        print("=" * 50)
        
        for category, content in training_data.items():
            print(f"\n📚 {category.replace('_', ' ').title()}:")
            print(f"   Content length: {len(content)} characters")
            print(f"   Preview: {content[:100]}...")
        
        print(f"\n📊 Total training categories: {len(training_data)}")
        print(f"📄 Total content length: {sum(len(content) for content in training_data.values())} characters")

def main():
    """Main function to generate training data"""
    print("🤖 Smart Building AI Training Data Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = SmartBuildingTrainingDataGenerator()
    
    # Generate and save training data
    print("\n🔄 Generating training data...")
    generator.save_training_data()
    
    # Create individual training documents
    print("\n📄 Creating training documents...")
    generator.create_training_documents()
    
    # Display summary
    generator.display_training_summary()
    
    print("\n🎉 Training data generation complete!")
    print("✅ The AI now has comprehensive knowledge about:")
    print("   • Building information and layout")
    print("   • Equipment status and maintenance")
    print("   • HVAC and temperature control")
    print("   • Energy consumption and efficiency")
    print("   • Room management and utilization")
    print("   • Safety and security systems")
    print("   • FAQ-style responses for common questions")

if __name__ == "__main__":
    main()
