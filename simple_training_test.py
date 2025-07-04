#!/usr/bin/env python3
"""
Simple Training Questions Test
Tests the knowledge base with generated training questions
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the supervisor directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from streamlit_app import SmartBuildingKnowledgeBase
    print("✅ Knowledge base loaded successfully")
except ImportError as e:
    print(f"❌ Error importing knowledge base: {e}")
    sys.exit(1)

def test_questions_simple():
    """Simple test of training questions with knowledge base"""
    print("🚀 Testing Training Questions with Knowledge Base")
    print("=" * 60)
    
    # Load training questions
    questions_file = Path("training_questions.json")
    if not questions_file.exists():
        print("❌ Training questions file not found. Run generate_training_questions.py first.")
        return
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return
    
    # Initialize knowledge base
    kb = SmartBuildingKnowledgeBase()
    
    # Test results
    test_results = {
        "test_date": datetime.now().isoformat(),
        "category_results": {},
        "overall_stats": {}
    }
    
    total_tested = 0
    total_with_context = 0
    
    # Test each category
    for category, questions in questions_data['question_categories'].items():
        print(f"\n📋 Testing {category} Questions")
        print("-" * 40)
        
        category_results = {
            "total_questions": len(questions),
            "tested_questions": 0,
            "questions_with_context": 0,
            "sample_results": []
        }
        
        # Test first 3 questions from each category
        test_questions = questions[:3]
        
        for i, question in enumerate(test_questions, 1):
            print(f"[{i}/3] 🔍 {question}")
            
            try:
                start_time = time.time()
                context = kb.get_context_for_query(question)
                response_time = time.time() - start_time
                
                has_context = bool(context)
                context_length = len(context) if context else 0
                
                # Store result
                result = {
                    "question": question,
                    "has_context": has_context,
                    "context_length": context_length,
                    "response_time": response_time
                }
                
                category_results["sample_results"].append(result)
                category_results["tested_questions"] += 1
                total_tested += 1
                
                if has_context:
                    category_results["questions_with_context"] += 1
                    total_with_context += 1
                    print(f"   ✅ Found context ({context_length} chars, {response_time:.2f}s)")
                    # Show preview
                    preview = context[:100].replace('\n', ' ').strip()
                    print(f"   📝 Preview: {preview}...")
                else:
                    print(f"   ⚠️ No context found ({response_time:.2f}s)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                category_results["tested_questions"] += 1
                total_tested += 1
        
        # Calculate category success rate
        success_rate = (category_results["questions_with_context"] / category_results["tested_questions"] * 100) if category_results["tested_questions"] > 0 else 0
        category_results["success_rate"] = success_rate
        
        print(f"   📊 Category result: {category_results['questions_with_context']}/{category_results['tested_questions']} ({success_rate:.1f}%)")
        
        test_results["category_results"][category] = category_results
    
    # Test specific IIC/EIU questions
    print(f"\n🎯 Testing Specific IIC/EIU Questions")
    print("-" * 40)
    
    iic_test_questions = [
        "What is IIC?",
        "Tell me about Eastern International University",
        "Information about EIU Innovation Center",
        "What programs does EIU offer?",
        "Where is Eastern International University located?"
    ]
    
    iic_results = []
    for question in iic_test_questions:
        print(f"🔍 {question}")
        
        try:
            start_time = time.time()
            context = kb.get_context_for_query(question)
            response_time = time.time() - start_time
            
            has_context = bool(context)
            context_length = len(context) if context else 0
            
            result = {
                "question": question,
                "has_context": has_context,
                "context_length": context_length,
                "response_time": response_time
            }
            iic_results.append(result)
            
            if has_context:
                print(f"   ✅ Found context ({context_length} chars, {response_time:.2f}s)")
                # Show more detailed preview for IIC questions
                preview = context[:200].replace('\n', ' ').strip()
                print(f"   📝 Preview: {preview}...")
            else:
                print(f"   ⚠️ No context found ({response_time:.2f}s)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    test_results["iic_specific_results"] = iic_results
    
    # Calculate overall statistics
    overall_success_rate = (total_with_context / total_tested * 100) if total_tested > 0 else 0
    
    test_results["overall_stats"] = {
        "total_questions_tested": total_tested,
        "questions_with_context": total_with_context,
        "overall_success_rate": overall_success_rate,
        "categories_tested": len(test_results["category_results"])
    }
    
    # Display summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Total questions tested: {total_tested}")
    print(f"🎯 Questions with context: {total_with_context}")
    print(f"📈 Overall success rate: {overall_success_rate:.1f}%")
    
    print(f"\n📋 Category Performance:")
    for category, results in test_results["category_results"].items():
        print(f"   • {category}: {results['success_rate']:.1f}% ({results['questions_with_context']}/{results['tested_questions']})")
    
    # IIC-specific performance
    iic_with_context = sum(1 for r in iic_results if r['has_context'])
    iic_success_rate = (iic_with_context / len(iic_results) * 100) if iic_results else 0
    print(f"   • IIC Specific: {iic_success_rate:.1f}% ({iic_with_context}/{len(iic_results)})")
    
    # Save results
    results_file = Path("simple_training_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💡 Analysis and Recommendations:")
    if overall_success_rate >= 80:
        print("   ✅ Excellent performance! The AI has good coverage of training questions.")
    elif overall_success_rate >= 60:
        print("   👍 Good performance. Consider adding more training data for better coverage.")
    elif overall_success_rate >= 40:
        print("   ⚠️ Fair performance. More training data needed for comprehensive coverage.")
    else:
        print("   ❌ Poor performance. Significant training data gaps need to be addressed.")
    
    # Category-specific recommendations
    for category, results in test_results["category_results"].items():
        if results['success_rate'] < 50:
            print(f"   📋 {category}: Needs more training content")
    
    if iic_success_rate < 80:
        print("   🎯 IIC/EIU: Consider adding more IIC-specific training content")
    
    print(f"\n✅ Test results saved to: {results_file}")

def show_sample_questions():
    """Show sample questions from each category"""
    print("📋 Sample Training Questions by Category")
    print("=" * 50)
    
    questions_file = Path("training_questions.json")
    if not questions_file.exists():
        print("❌ Training questions file not found.")
        return
    
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return
    
    for category, questions in questions_data['question_categories'].items():
        print(f"\n🏷️ {category} ({len(questions)} questions):")
        for i, question in enumerate(questions[:5], 1):  # Show first 5
            print(f"   {i}. {question}")
        if len(questions) > 5:
            print(f"   ... and {len(questions) - 5} more questions")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sample":
            show_sample_questions()
        elif sys.argv[1] == "--test":
            test_questions_simple()
        else:
            print("Usage: python simple_training_test.py [--sample|--test]")
            print("  --sample: Show sample questions")
            print("  --test: Test AI with questions")
    else:
        # Default: run test
        test_questions_simple()

if __name__ == "__main__":
    main()
