#!/usr/bin/env python3
"""
Training Questions Generator for Smart Building AI
Generates comprehensive questions for training and testing the AI system
"""

import json
import random
from datetime import datetime
from pathlib import Path

def generate_iic_eiu_questions():
    """Generate questions related to IIC and EIU content"""
    return [
        # Basic Information Questions
        "What is IIC?",
        "What does IIC stand for?",
        "Tell me about the Innovation Industry Center",
        "What is Eastern International University?",
        "Where is Eastern International University located?",
        "What is EIU?",
        "What does EIU stand for?",
        
        # Detailed Information Questions
        "Tell me about the IIC Innovation Center at EIU",
        "What programs does Eastern International University offer?",
        "What facilities are available at the IIC Innovation Center?",
        "How does the Innovation Industry Center support students?",
        "What research activities are conducted at IIC?",
        "What is the mission of Eastern International University?",
        "What makes the IIC Innovation Center unique?",
        
        # Location and Infrastructure Questions
        "Where is the IIC Innovation Center located?",
        "What is the address of Eastern International University?",
        "How can I visit the IIC Innovation Center?",
        "What are the facilities at EIU campus?",
        "Tell me about the infrastructure at Eastern International University",
        "What building houses the Innovation Industry Center?",
        
        # Programs and Services Questions
        "What academic programs are offered at EIU?",
        "What innovation programs are available at IIC?",
        "How can students access IIC facilities?",
        "What research opportunities are available at the Innovation Center?",
        "What technology resources are available at IIC?",
        "What collaboration opportunities exist at the Innovation Center?",
        
        # Industry 4.0 and Technology Questions
        "How does IIC support Industry 4.0 initiatives?",
        "What Industry 4.0 technologies are used at the Innovation Center?",
        "How does EIU integrate technology in education?",
        "What smart technologies are implemented at the campus?",
        "How does the Innovation Center promote digital transformation?",
        "What IoT applications are used at EIU?",
        
        # Partnership and Collaboration Questions
        "What partnerships does IIC have with industry?",
        "How does EIU collaborate with other institutions?",
        "What companies work with the Innovation Industry Center?",
        "How can businesses partner with IIC?",
        "What international collaborations does EIU have?",
        "How does the Innovation Center support startups?"
    ]

def generate_smart_building_questions():
    """Generate questions about smart building management"""
    return [
        # HVAC System Questions
        "How do I control the HVAC system?",
        "What is the optimal temperature setting for energy efficiency?",
        "How can I troubleshoot HVAC issues?",
        "What are the maintenance requirements for HVAC systems?",
        "How do smart thermostats work in building automation?",
        "What sensors are used in HVAC monitoring?",
        "How can I reduce energy consumption in HVAC systems?",
        "What are the best practices for HVAC scheduling?",
        
        # Lighting Control Questions
        "How do I control building lighting systems?",
        "What are the benefits of smart lighting?",
        "How can I set up automated lighting schedules?",
        "What sensors are used for lighting control?",
        "How do I optimize lighting for energy efficiency?",
        "What are the maintenance requirements for LED lighting?",
        "How do occupancy sensors work with lighting systems?",
        "What are the best practices for daylight harvesting?",
        
        # Security System Questions
        "How do I manage building security systems?",
        "What types of access control systems are available?",
        "How do I monitor security cameras?",
        "What are the emergency procedures for security incidents?",
        "How do I manage visitor access?",
        "What are the best practices for building security?",
        "How do I integrate security with other building systems?",
        "What alarm systems are recommended for smart buildings?",
        
        # Energy Management Questions
        "How can I monitor building energy consumption?",
        "What are the best strategies for energy optimization?",
        "How do I set up energy monitoring systems?",
        "What renewable energy options are available?",
        "How can I reduce peak energy demand?",
        "What are the benefits of energy storage systems?",
        "How do I implement demand response programs?",
        "What energy efficiency measures should I prioritize?",
        
        # Building Automation Questions
        "What is building automation system (BAS)?",
        "How do I integrate different building systems?",
        "What protocols are used in building automation?",
        "How can I set up automated building schedules?",
        "What are the benefits of centralized building control?",
        "How do I troubleshoot automation system issues?",
        "What maintenance is required for automation systems?",
        "How can I upgrade existing building systems to smart systems?",
        
        # IoT and Smart Technology Questions
        "What IoT devices are used in smart buildings?",
        "How do I implement IoT sensors in building management?",
        "What data analytics are available for smart buildings?",
        "How can I use machine learning for building optimization?",
        "What wireless technologies are best for smart buildings?",
        "How do I ensure cybersecurity in smart building systems?",
        "What cloud platforms are suitable for building data?",
        "How can I integrate mobile apps with building systems?"
    ]

def generate_industry_4_0_questions():
    """Generate questions about Industry 4.0 and digital transformation"""
    return [
        # Industry 4.0 Basics
        "What is Industry 4.0?",
        "What are the key technologies in Industry 4.0?",
        "How does Industry 4.0 impact building management?",
        "What are the benefits of digital transformation in buildings?",
        "How do cyber-physical systems work in smart buildings?",
        "What is the Industrial Internet of Things (IIoT)?",
        "How does artificial intelligence enhance building operations?",
        "What role does machine learning play in smart buildings?",
        
        # Digital Technologies
        "How are digital twins used in building management?",
        "What is edge computing in smart building context?",
        "How does 5G technology benefit smart buildings?",
        "What are the applications of augmented reality in building maintenance?",
        "How can virtual reality be used for building training?",
        "What blockchain applications exist for smart buildings?",
        "How do predictive analytics improve building performance?",
        "What is the role of big data in building optimization?",
        
        # Implementation Questions
        "How do I start implementing Industry 4.0 in my building?",
        "What are the challenges of digital transformation in buildings?",
        "How can I ensure data quality in smart building systems?",
        "What standards should I follow for Industry 4.0 implementation?",
        "How do I train staff for Industry 4.0 technologies?",
        "What are the costs associated with smart building upgrades?",
        "How can I measure ROI of Industry 4.0 investments?",
        "What are the best practices for digital transformation planning?"
    ]

def generate_maintenance_safety_questions():
    """Generate questions about maintenance and safety"""
    return [
        # Maintenance Questions
        "What are the preventive maintenance procedures for smart buildings?",
        "How do I create a maintenance schedule for building systems?",
        "What tools are needed for smart building maintenance?",
        "How can predictive maintenance reduce costs?",
        "What are the common maintenance issues in smart buildings?",
        "How do I troubleshoot communication issues between systems?",
        "What spare parts should I keep for building systems?",
        "How can I extend the lifespan of building equipment?",
        
        # Safety Questions
        "What are the safety procedures for building emergencies?",
        "How do I ensure fire safety in smart buildings?",
        "What are the electrical safety requirements for IoT devices?",
        "How do I implement emergency evacuation procedures?",
        "What safety training is required for building operators?",
        "How can I ensure data privacy in smart building systems?",
        "What cybersecurity measures are needed for building networks?",
        "How do I handle hazardous materials in building maintenance?",
        
        # Compliance Questions
        "What building codes apply to smart building installations?",
        "How do I ensure compliance with energy efficiency standards?",
        "What environmental regulations affect building operations?",
        "How do I obtain certifications for green buildings?",
        "What accessibility requirements must be met in smart buildings?",
        "How do I comply with data protection regulations?",
        "What insurance considerations exist for smart buildings?",
        "How do I document compliance for building inspections?"
    ]

def generate_operational_questions():
    """Generate questions about day-to-day building operations"""
    return [
        # Daily Operations
        "How do I monitor building systems daily?",
        "What daily checks should be performed on building systems?",
        "How do I respond to system alarms and alerts?",
        "What are the procedures for system startups and shutdowns?",
        "How do I manage occupant comfort complaints?",
        "What are the steps for emergency system overrides?",
        "How do I coordinate with different building service providers?",
        "What reports should be generated for building performance?",
        
        # Optimization Questions
        "How can I optimize building performance for different seasons?",
        "What strategies work best for reducing operational costs?",
        "How do I balance energy efficiency with occupant comfort?",
        "What are the best practices for space utilization?",
        "How can I improve indoor air quality?",
        "What measures can reduce water consumption in buildings?",
        "How do I optimize cleaning and janitorial schedules?",
        "What are effective strategies for waste management?",
        
        # Technology Integration
        "How do I integrate new technologies with existing systems?",
        "What are the steps for system commissioning?",
        "How do I ensure interoperability between different vendors?",
        "What documentation is needed for system integration?",
        "How can I future-proof building technology investments?",
        "What are the best practices for technology upgrades?",
        "How do I manage software updates for building systems?",
        "What backup systems are recommended for critical operations?"
    ]

def generate_training_questions_dataset():
    """Generate comprehensive training questions dataset"""
    
    # Collect all questions by category
    questions_by_category = {
        "IIC_EIU": generate_iic_eiu_questions(),
        "Smart_Building": generate_smart_building_questions(),
        "Industry_4_0": generate_industry_4_0_questions(),
        "Maintenance_Safety": generate_maintenance_safety_questions(),
        "Operations": generate_operational_questions()
    }
    
    # Create comprehensive dataset
    training_dataset = {
        "metadata": {
            "generated_date": datetime.now().isoformat(),
            "total_questions": sum(len(q) for q in questions_by_category.values()),
            "categories": list(questions_by_category.keys()),
            "purpose": "Training and testing Smart Building AI Assistant",
            "version": "1.0"
        },
        "question_categories": questions_by_category,
        "all_questions": []
    }
    
    # Flatten all questions with metadata
    question_id = 1
    for category, questions in questions_by_category.items():
        for question in questions:
            training_dataset["all_questions"].append({
                "id": question_id,
                "question": question,
                "category": category,
                "difficulty": classify_question_difficulty(question),
                "keywords": extract_keywords(question),
                "question_type": classify_question_type(question)
            })
            question_id += 1
    
    return training_dataset

def classify_question_difficulty(question):
    """Classify question difficulty based on complexity"""
    question_lower = question.lower()
    
    # Basic questions (what, where, simple definitions)
    if any(word in question_lower for word in ["what is", "where is", "what does", "tell me about"]):
        return "basic"
    
    # Intermediate questions (how to, procedures)
    elif any(word in question_lower for word in ["how do i", "how can i", "what are the steps", "procedures"]):
        return "intermediate"
    
    # Advanced questions (optimization, integration, best practices)
    elif any(word in question_lower for word in ["optimize", "integrate", "best practices", "strategies", "implementation"]):
        return "advanced"
    
    else:
        return "intermediate"

def classify_question_type(question):
    """Classify the type of question"""
    question_lower = question.lower()
    
    if question_lower.startswith("what"):
        return "definition"
    elif question_lower.startswith("how"):
        return "procedure"
    elif question_lower.startswith("where"):
        return "location"
    elif question_lower.startswith("why"):
        return "explanation"
    elif "tell me about" in question_lower:
        return "information"
    elif "best practices" in question_lower:
        return "best_practice"
    else:
        return "general"

def extract_keywords(question):
    """Extract key terms from questions"""
    # Common smart building keywords
    keywords = []
    keyword_map = {
        "hvac": ["hvac", "heating", "cooling", "ventilation", "air conditioning"],
        "lighting": ["lighting", "lights", "led", "illumination"],
        "security": ["security", "access control", "cameras", "alarms"],
        "energy": ["energy", "power", "consumption", "efficiency"],
        "automation": ["automation", "control", "smart", "automated"],
        "iot": ["iot", "sensors", "devices", "connectivity"],
        "maintenance": ["maintenance", "repair", "troubleshoot", "service"],
        "safety": ["safety", "emergency", "fire", "evacuation"],
        "iic": ["iic", "innovation", "center"],
        "eiu": ["eiu", "eastern", "international", "university"],
        "industry_4_0": ["industry 4.0", "digital", "transformation", "ai", "machine learning"]
    }
    
    question_lower = question.lower()
    for category, terms in keyword_map.items():
        if any(term in question_lower for term in terms):
            keywords.append(category)
    
    return keywords

def create_question_test_scenarios():
    """Create test scenarios for evaluating AI responses"""
    return [
        {
            "scenario": "New Building Manager",
            "description": "Questions a new building manager might ask",
            "sample_questions": [
                "What are my daily responsibilities as a building manager?",
                "How do I monitor building systems?",
                "What should I do in case of an emergency?",
                "How do I manage energy consumption?",
                "What maintenance schedules should I follow?"
            ]
        },
        {
            "scenario": "IIC Student Inquiry",
            "description": "Questions from students interested in IIC programs",
            "sample_questions": [
                "What is the Innovation Industry Center?",
                "How can I access IIC facilities?",
                "What programs are available at IIC?",
                "How do I apply for research opportunities at IIC?",
                "What technology resources are available?"
            ]
        },
        {
            "scenario": "Energy Optimization",
            "description": "Questions focused on energy efficiency",
            "sample_questions": [
                "How can I reduce building energy consumption?",
                "What are the most effective energy-saving measures?",
                "How do I implement demand response programs?",
                "What renewable energy options are available?",
                "How can I monitor and analyze energy usage?"
            ]
        },
        {
            "scenario": "Technology Integration",
            "description": "Questions about implementing new technologies",
            "sample_questions": [
                "How do I integrate IoT devices with existing systems?",
                "What are the best practices for smart building upgrades?",
                "How can I ensure cybersecurity in smart buildings?",
                "What Industry 4.0 technologies should I prioritize?",
                "How do I future-proof my building technology?"
            ]
        },
        {
            "scenario": "Troubleshooting",
            "description": "Questions about solving problems",
            "sample_questions": [
                "My HVAC system is not responding, what should I do?",
                "How do I troubleshoot lighting control issues?",
                "What are common causes of system communication failures?",
                "How do I resolve security system malfunctions?",
                "What steps should I take when sensors give incorrect readings?"
            ]
        }
    ]

def main():
    """Generate and save training questions"""
    print("🎯 Generating Training Questions for Smart Building AI")
    print("=" * 60)
    
    # Generate comprehensive dataset
    dataset = generate_training_questions_dataset()
    
    # Create test scenarios
    scenarios = create_question_test_scenarios()
    
    # Add scenarios to dataset
    dataset["test_scenarios"] = scenarios
    
    # Save to file
    output_file = Path("training_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    # Display summary
    print(f"📊 Generated Training Questions Summary:")
    print(f"   • Total questions: {dataset['metadata']['total_questions']}")
    print(f"   • Categories: {len(dataset['metadata']['categories'])}")
    print(f"   • Test scenarios: {len(scenarios)}")
    print()
    
    # Show breakdown by category
    print("📋 Questions by Category:")
    for category, questions in dataset['question_categories'].items():
        print(f"   • {category}: {len(questions)} questions")
    
    print()
    
    # Show difficulty distribution
    difficulties = {}
    question_types = {}
    
    for q in dataset['all_questions']:
        diff = q['difficulty']
        qtype = q['question_type']
        difficulties[diff] = difficulties.get(diff, 0) + 1
        question_types[qtype] = question_types.get(qtype, 0) + 1
    
    print("📈 Difficulty Distribution:")
    for diff, count in difficulties.items():
        print(f"   • {diff}: {count} questions")
    
    print()
    print("🏷️ Question Types:")
    for qtype, count in question_types.items():
        print(f"   • {qtype}: {count} questions")
    
    print(f"\n✅ Training questions saved to: {output_file}")
    print("💡 Use these questions to test and improve your AI training!")

if __name__ == "__main__":
    main()
