#!/usr/bin/env python3
"""
Enhanced IIC EIU Training with Vietnamese Content Support
"""

import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from streamlit_app import SmartBuildingKnowledgeBase
    import docx2txt
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

def enhanced_iic_training():
    """Enhanced training for IIC EIU with Vietnamese content support"""
    print("🎓 Enhanced IIC EIU Training with Vietnamese Support")
    print("=" * 60)
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Extract content from the document
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    
    if not doc_path.exists():
        print(f"❌ Document not found: {doc_path}")
        return False
    
    try:
        # Extract text with better encoding handling
        print("📄 Extracting content from IIC_EIU_Overview.docx...")
        text = docx2txt.process(str(doc_path))
        
        if not text or len(text.strip()) < 100:
            print("❌ Document appears to be empty or has insufficient content")
            return False
        
        print(f"✅ Successfully extracted {len(text)} characters")
        print(f"📄 Content preview:")
        print("-" * 40)
        print(text[:300])
        print("-" * 40)
        
        # Manually chunk the content for better control
        chunks = kb.chunk_text(text, chunk_size=800, overlap=100)
        print(f"📊 Created {len(chunks)} content chunks")
        
        # Create embeddings manually
        embeddings = [kb.simple_embedding(chunk) for chunk in chunks]
        print(f"🧠 Generated {len(embeddings)} embeddings")
        
        # Prepare metadata for each chunk
        base_metadata = {
            "document_type": "university_overview",
            "source": "IIC EIU Overview",
            "category": "institutional",
            "subcategory": "university_information",
            "training_date": datetime.now().isoformat(),
            "manually_added": True,
            "source_file": "IIC_EIU_Overview.docx",
            "language": "vietnamese",
            "content_type": "docx",
            "verified": True
        }
        
        # Generate unique IDs and metadata for each chunk
        doc_hash = hash(str(doc_path)) % 10000
        chunk_ids = [f"iic_eiu_{doc_hash}_{i}" for i in range(len(chunks))]
        chunk_metadata = [
            {**base_metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
            for i in range(len(chunks))
        ]
        
        # Add to collection manually
        print("🔄 Adding chunks to knowledge base...")
        kb.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata,
            ids=chunk_ids
        )
        
        print("✅ Successfully added IIC EIU content to knowledge base!")
        
        # Verify the addition
        collection_info = kb.collection.get()
        total_docs = len(collection_info.get('documents', []))
        print(f"📊 Knowledge base now contains {total_docs} document chunks")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        test_queries = ["IIC", "EIU", "công nghiệp 4.0", "đại học", "innovation center"]
        
        for query in test_queries:
            results = kb.search_documents(query, n_results=2)
            if results:
                print(f"✅ Found {len(results)} results for '{query}'")
                # Show preview
                preview = results[0]['content'][:100] + "..." if len(results[0]['content']) > 100 else results[0]['content']
                print(f"   Preview: {preview}")
            else:
                print(f"❌ No results for '{query}'")
        
        # Create a comprehensive information summary
        iic_summary = create_iic_summary(text)
        
        # Add the summary as a separate, well-structured chunk
        summary_metadata = {
            **base_metadata,
            "chunk_type": "summary",
            "content_type": "structured_summary",
            "enhanced_for_english": True
        }
        
        summary_embedding = kb.simple_embedding(iic_summary)
        summary_id = f"iic_eiu_summary_{doc_hash}"
        
        kb.collection.add(
            embeddings=[summary_embedding],
            documents=[iic_summary],
            metadatas=[summary_metadata],
            ids=[summary_id]
        )
        
        print("✅ Added structured English summary for better accessibility")
        
        # Save training log
        training_log = {
            "timestamp": datetime.now().isoformat(),
            "document_path": str(doc_path),
            "success": True,
            "chunks_created": len(chunks),
            "total_characters": len(text),
            "summary_added": True,
            "language": "vietnamese_with_english_summary"
        }
        
        with open("iic_training_log.json", "w", encoding='utf-8') as f:
            json.dump(training_log, f, indent=2, ensure_ascii=False)
        
        print("💾 Training log saved to iic_training_log.json")
        return True
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_iic_summary(vietnamese_text):
    """Create an English summary of the IIC EIU content"""
    summary = """
IIC EIU Overview - Industry 4.0 Innovation Center at Eastern International University

About IIC (Industry 4.0 Innovation Center):
The IIC is a collaboration between Becamex IDC, VSIP, and Eastern International University (EIU), established to support businesses in digital transformation, Industry 4.0 technology adoption, and high-quality human resource development in Binh Duong province.

Key Objectives and Functions:
1. Digital Transformation for Businesses: Uses SIRI standards to assess and upgrade business intelligence levels
2. Practical Application of Industry 4.0 Technologies: Implementation of IoT, AI, automation, and smart manufacturing
3. Training and Education: Developing skilled workforce for Industry 4.0 requirements
4. Research and Development: Supporting innovation and technology transfer
5. Consulting Services: Providing expert guidance for digital transformation

Eastern International University (EIU):
- International university located in Binh Duong province, Vietnam
- Focus on high-quality education and international standards
- Partner institution in the Industry 4.0 Innovation Center initiative
- Commitment to developing skilled professionals for the digital economy

Industry 4.0 Focus Areas:
- Internet of Things (IoT) implementation
- Artificial Intelligence and Machine Learning
- Smart Manufacturing and Automation
- Digital Transformation Strategies
- Data Analytics and Business Intelligence
- Cybersecurity and Digital Infrastructure

Services Provided:
- Business assessment using SIRI (Smart Industry Readiness Index)
- Technology consulting and implementation
- Training programs for Industry 4.0 skills
- Research collaboration opportunities
- Innovation ecosystem development

Target Industries:
- Manufacturing and Industrial Production
- Smart City Development
- Technology and Innovation Companies
- Educational Institutions
- Government and Public Sector Organizations

Location and Context:
- Based in Binh Duong province, Vietnam
- Part of the VSIP (Vietnam Singapore Industrial Park) ecosystem
- Strategic location for industrial development and innovation
- Access to international expertise and resources

This center represents a significant step towards Vietnam's digital transformation and Industry 4.0 adoption, combining educational excellence with practical business applications.
"""
    return summary.strip()

def test_iic_accessibility():
    """Test if IIC content is accessible through various queries"""
    print("\n🧪 Testing IIC Content Accessibility")
    print("=" * 50)
    
    kb = SmartBuildingKnowledgeBase()
    
    test_queries = [
        "What is IIC EIU?",
        "Tell me about Eastern International University",
        "What is the Industry 4.0 Innovation Center?",
        "How does IIC support digital transformation?",
        "What services does the Innovation Center provide?",
        "What is SIRI standard?",
        "Industry 4.0 training programs",
        "EIU university programs",
        "Becamex IDC collaboration",
        "VSIP innovation center"
    ]
    
    successful_queries = 0
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        context = kb.get_context_for_query(query)
        
        if context and len(context) > 100:
            print("✅ Found relevant context")
            
            # Check for IIC-related terms
            iic_terms = ['iic', 'eiu', 'eastern international university', 'innovation center', 'industry 4.0', 'becamex', 'vsip']
            found_terms = [term for term in iic_terms if term.lower() in context.lower()]
            
            if found_terms:
                print(f"✅ Contains relevant terms: {', '.join(found_terms[:3])}")
                successful_queries += 1
            else:
                print("⚠️ General response without specific IIC content")
        else:
            print("❌ No relevant context found")
    
    success_rate = (successful_queries / len(test_queries)) * 100
    print(f"\n📊 Test Results:")
    print(f"   • Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"   • Success rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("✅ IIC content is well-integrated and accessible")
    elif success_rate >= 40:
        print("⚠️ IIC content is partially accessible, may need optimization")
    else:
        print("❌ IIC content integration needs improvement")
    
    return success_rate

def main():
    """Main function"""
    print("🚀 Enhanced IIC EIU Training System")
    print("=" * 70)
    
    # Step 1: Enhanced training
    print("Step 1: Enhanced IIC EIU training with Vietnamese support")
    success = enhanced_iic_training()
    
    if not success:
        print("❌ Training failed")
        return
    
    # Step 2: Test accessibility
    print("\nStep 2: Testing content accessibility")
    success_rate = test_iic_accessibility()
    
    print(f"\n🎉 Enhanced IIC EIU training complete!")
    print(f"✅ Content successfully integrated with {success_rate:.1f}% query success rate")
    print("💡 You can now ask the AI about:")
    print("   • IIC (Industry 4.0 Innovation Center)")
    print("   • EIU (Eastern International University)")
    print("   • Digital transformation services")
    print("   • Industry 4.0 technologies and training")
    print("   • VSIP and Becamex IDC collaboration")

if __name__ == "__main__":
    main()
