#!/usr/bin/env python3
"""
Comprehensive IIC EIU Overview Training and Verification
"""

import sys
import os
from pathlib import Path
import json
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

def extract_and_verify_iic_content():
    """Extract and verify content from IIC_EIU_Overview.docx"""
    print("📄 Extracting IIC EIU Overview Content")
    print("=" * 50)
    
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    
    if not doc_path.exists():
        print(f"❌ Document not found: {doc_path}")
        return None
    
    try:
        # Extract text from the document
        text = docx2txt.process(str(doc_path))
        
        if not text or len(text.strip()) < 100:
            print("❌ Document appears to be empty or has insufficient content")
            return None
        
        print(f"✅ Successfully extracted {len(text)} characters from document")
        print(f"📄 Content preview (first 500 chars):")
        print("-" * 30)
        print(text[:500])
        print("-" * 30)
        
        # Check for key terms
        key_terms = ['IIC', 'EIU', 'Eastern International University', 'Innovation Center', 'Industry 4.0']
        found_terms = []
        
        for term in key_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        print(f"✅ Found key terms: {', '.join(found_terms) if found_terms else 'None'}")
        
        return text
        
    except Exception as e:
        print(f"❌ Error extracting content: {e}")
        return None

def train_iic_with_verification():
    """Train the AI on IIC document with comprehensive verification"""
    print("🤖 Training AI on IIC EIU Overview with Verification")
    print("=" * 60)
    
    # First, extract and verify content
    content = extract_and_verify_iic_content()
    if not content:
        print("❌ Cannot proceed without valid content")
        return False
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Add the document with detailed metadata
    doc_path = Path("smart_building_data/IIC_EIU_Overview.docx")
    
    metadata = {
        "document_type": "university_overview",
        "source": "IIC EIU Overview",
        "category": "institutional",
        "subcategory": "university_information",
        "training_date": datetime.now().isoformat(),
        "manually_added": True,
        "file_size": len(content),
        "source_file": "IIC_EIU_Overview.docx",
        "content_verified": True,
        "key_terms": ["IIC", "EIU", "Eastern International University", "Innovation Center"]
    }
    
    print(f"\n🔄 Adding document to knowledge base...")
    success = kb.add_document(str(doc_path), metadata)
    
    if success:
        print("✅ Successfully added document to knowledge base")
        
        # Verify the content was properly chunked and stored
        print(f"\n🔍 Verifying document storage...")
        
        # Search for IIC-related content
        test_queries = ["IIC", "EIU", "Eastern International University", "Innovation Center"]
        
        for query in test_queries:
            search_results = kb.search_documents(query, n_results=3)
            if search_results:
                print(f"✅ Found {len(search_results)} chunks for query: '{query}'")
                
                # Show a sample of found content
                for i, result in enumerate(search_results[:1]):  # Show first result
                    content_preview = result['content'][:200]
                    print(f"   Sample: {content_preview}...")
            else:
                print(f"❌ No chunks found for query: '{query}'")
        
        # Get knowledge base statistics
        collection_info = kb.collection.get()
        total_docs = len(collection_info.get('documents', []))
        print(f"\n📊 Knowledge base now contains {total_docs} document chunks")
        
        # Save training verification
        verification_data = {
            "training_timestamp": datetime.now().isoformat(),
            "document_path": str(doc_path),
            "success": True,
            "total_chunks": total_docs,
            "metadata": metadata,
            "content_length": len(content),
            "verification_queries": test_queries
        }
        
        with open("iic_training_verification.json", "w", encoding='utf-8') as f:
            json.dump(verification_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Training verification saved to iic_training_verification.json")
        return True
        
    else:
        print("❌ Failed to add document to knowledge base")
        return False

def test_iic_queries():
    """Test specific IIC-related queries"""
    print("\n🧪 Testing IIC-Related Queries")
    print("=" * 50)
    
    kb = SmartBuildingKnowledgeBase()
    
    test_queries = [
        "What is IIC EIU?",
        "Tell me about Eastern International University",
        "What is the Industry 4.0 Innovation Center?",
        "What does EIU offer for students?",
        "How does the Innovation Center support research?",
        "What are the facilities at Eastern International University?",
        "What is the mission of IIC?"
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        print("-" * 30)
        
        # Get context
        context = kb.get_context_for_query(query)
        
        if context:
            print("✅ Context found")
            
            # Check for IIC/EIU specific content
            iic_terms = ['iic', 'eiu', 'eastern international university', 'innovation center', 'industry 4.0']
            found_terms = [term for term in iic_terms if term in context.lower()]
            
            if found_terms:
                print(f"✅ Contains IIC/EIU terms: {', '.join(found_terms)}")
                relevance = "High"
            else:
                print("⚠️ General response, no specific IIC/EIU terms")
                relevance = "Low"
            
            # Show preview
            preview = context[:150] + "..." if len(context) > 150 else context
            print(f"📄 Preview: {preview}")
            
        else:
            print("❌ No context found")
            relevance = "None"
        
        results.append({
            "query": query,
            "has_context": bool(context),
            "relevance": relevance,
            "context_length": len(context) if context else 0
        })
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print("-" * 30)
    
    total_queries = len(results)
    with_context = len([r for r in results if r['has_context']])
    high_relevance = len([r for r in results if r['relevance'] == 'High'])
    
    print(f"Total queries tested: {total_queries}")
    print(f"Queries with context: {with_context}/{total_queries}")
    print(f"Highly relevant responses: {high_relevance}/{total_queries}")
    
    if high_relevance > 0:
        print("✅ IIC EIU content is accessible and relevant")
    else:
        print("⚠️ IIC EIU content may need better integration")
    
    # Save test results
    with open("iic_query_test_results.json", "w", encoding='utf-8') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_queries": total_queries,
                "with_context": with_context,
                "high_relevance": high_relevance
            }
        }, f, indent=2, ensure_ascii=False)
    
    print("✅ Test results saved to iic_query_test_results.json")

def main():
    """Main function"""
    print("🎓 IIC EIU Overview - Comprehensive Training & Verification")
    print("=" * 70)
    
    # Step 1: Train the AI
    print("Step 1: Training AI on IIC EIU Overview document")
    success = train_iic_with_verification()
    
    if not success:
        print("❌ Training failed, cannot proceed with testing")
        return
    
    # Step 2: Test queries
    print("\nStep 2: Testing IIC-related queries")
    test_iic_queries()
    
    print("\n🎉 Comprehensive IIC EIU training and verification complete!")
    print("💡 You can now ask the AI about IIC, EIU, and Eastern International University")

if __name__ == "__main__":
    main()
