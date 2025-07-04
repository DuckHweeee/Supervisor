#!/usr/bin/env python3
"""
Add Industry 4.0 Innovation Center web content to knowledge base
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_becamex_url_to_kb():
    """Add the Becamex Industry 4.0 URL to the knowledge base"""
    
    print("🌐 Adding Becamex Industry 4.0 Innovation Center URL to knowledge base...")
    
    try:
        from streamlit_app import SmartBuildingKnowledgeBase
        
        # Initialize knowledge base
        kb = SmartBuildingKnowledgeBase()
        
        # Add the Becamex URL
        url = "https://becamex.com.vn/en/ecosystem/industry-4-0-innovation-center-iic-at-eastern-international-university-eiu/"
        metadata = {
            'document_type': 'web_content',
            'category': 'industry_4_0_innovation_center',
            'building_system': 'innovation_center',
            'source': 'becamex_website'
        }
        
        print(f"📡 Fetching content from: {url}")
        success = kb.add_url_to_knowledge_base(url, metadata)
        
        if success:
            print("✅ Successfully added Becamex Industry 4.0 content to knowledge base")
            
            # Test a query
            print("\n🔍 Testing query about Industry 4.0 Innovation Center...")
            results = kb.search_documents("Industry 4.0 Innovation Center IIC capabilities", n_results=5)
            
            if results:
                print(f"✅ Found {len(results)} relevant results")
                for i, result in enumerate(results):
                    if 'industry' in result['content'].lower() or 'iic' in result['content'].lower():
                        print(f"   📄 Result {i+1}: {result['content'][:150]}...")
                        print(f"       Source: {result['metadata'].get('source_url', 'Local file')}")
            else:
                print("❌ No results found")
                
        else:
            print("❌ Failed to add Becamex content to knowledge base")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Process completed!")

if __name__ == "__main__":
    add_becamex_url_to_kb()
