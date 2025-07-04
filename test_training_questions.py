#!/usr/bin/env python3
"""
Training Questions Test Script
Tests the AI with generated training questions and evaluates responses
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
    from AutoGenAI import SmartBuildingAssistant
    print("✅ AI modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing AI modules: {e}")
    sys.exit(1)

class TrainingQuestionTester:
    """Test AI responses to training questions"""
    
    def __init__(self):
        self.kb = SmartBuildingKnowledgeBase()
        self.assistant = SmartBuildingAssistant()
        self.test_results = []
        
    def load_training_questions(self):
        """Load training questions from JSON file"""
        questions_file = Path("training_questions.json")
        
        if not questions_file.exists():
            print("❌ Training questions file not found. Run generate_training_questions.py first.")
            return None
        
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading training questions: {e}")
            return None
    
    def test_single_question(self, question_data):
        """Test AI response to a single question"""
        question = question_data['question']
        category = question_data['category']
        
        print(f"🔍 Testing: {question}")
        
        try:
            # Get context from knowledge base
            start_time = time.time()
            context = self.kb.get_context_for_query(question)
            context_time = time.time() - start_time
            
            # Generate AI response
            start_time = time.time()
            try:
                response = self.assistant.get_response(question)
            except:
                # Fallback if assistant method not available
                response = f"Context found: {bool(context)}" if context else "No relevant context found"
            response_time = time.time() - start_time
            
            # Evaluate response quality
            evaluation = self.evaluate_response(question, context, response, category)
            
            result = {
                "question": question,
                "category": category,
                "difficulty": question_data.get('difficulty', 'unknown'),
                "question_type": question_data.get('question_type', 'unknown'),
                "keywords": question_data.get('keywords', []),
                "context_found": bool(context),
                "context_length": len(context) if context else 0,
                "response_length": len(response) if response else 0,
                "context_time": context_time,
                "response_time": response_time,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
            # Show results
            status = "✅" if evaluation['has_context'] else "⚠️"
            print(f"   {status} Context: {evaluation['context_quality']}")
            print(f"   📊 Response: {evaluation['response_quality']}")
            print(f"   ⏱️ Time: {context_time:.2f}s context, {response_time:.2f}s response")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "question": question,
                "category": category,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def evaluate_response(self, question, context, response, category):
        """Evaluate the quality of AI response"""
        evaluation = {
            "has_context": bool(context),
            "context_quality": "none",
            "response_quality": "none",
            "relevance_score": 0,
            "completeness_score": 0
        }
        
        if context:
            # Evaluate context quality
            context_length = len(context)
            if context_length > 1000:
                evaluation["context_quality"] = "excellent"
                evaluation["relevance_score"] += 3
            elif context_length > 500:
                evaluation["context_quality"] = "good"
                evaluation["relevance_score"] += 2
            elif context_length > 100:
                evaluation["context_quality"] = "fair"
                evaluation["relevance_score"] += 1
            else:
                evaluation["context_quality"] = "poor"
            
            # Check if context contains relevant keywords
            question_lower = question.lower()
            context_lower = context.lower()
            
            # Category-specific keyword matching
            category_keywords = {
                "IIC_EIU": ["iic", "eiu", "eastern", "international", "university", "innovation", "center"],
                "Smart_Building": ["hvac", "lighting", "security", "energy", "automation", "building"],
                "Industry_4_0": ["industry 4.0", "iot", "digital", "smart", "automation", "ai"],
                "Maintenance_Safety": ["maintenance", "safety", "emergency", "repair", "procedure"],
                "Operations": ["operation", "management", "control", "monitoring", "optimization"]
            }
            
            relevant_keywords = category_keywords.get(category, [])
            keyword_matches = sum(1 for keyword in relevant_keywords if keyword in context_lower)
            
            if keyword_matches >= 3:
                evaluation["relevance_score"] += 2
            elif keyword_matches >= 1:
                evaluation["relevance_score"] += 1
        
        # Evaluate response quality
        if response:
            response_length = len(response)
            if response_length > 500:
                evaluation["response_quality"] = "comprehensive"
                evaluation["completeness_score"] += 3
            elif response_length > 200:
                evaluation["response_quality"] = "good"
                evaluation["completeness_score"] += 2
            elif response_length > 50:
                evaluation["response_quality"] = "basic"
                evaluation["completeness_score"] += 1
            else:
                evaluation["response_quality"] = "minimal"
        
        return evaluation
    
    def test_category(self, questions_data, category, max_questions=10):
        """Test questions from a specific category"""
        print(f"\n📋 Testing {category} Questions")
        print("=" * 50)
        
        category_questions = questions_data['question_categories'].get(category, [])
        
        if not category_questions:
            print(f"❌ No questions found for category: {category}")
            return []
        
        # Limit number of questions to test
        test_questions = category_questions[:max_questions]
        results = []
        
        for i, question_text in enumerate(test_questions, 1):
            print(f"\n[{i}/{len(test_questions)}]", end=" ")
            
            # Find question data
            question_data = None
            for q in questions_data['all_questions']:
                if q['question'] == question_text and q['category'] == category:
                    question_data = q
                    break
            
            if question_data:
                result = self.test_single_question(question_data)
                results.append(result)
            else:
                print(f"❌ Question data not found: {question_text}")
        
        return results
    
    def test_scenarios(self, questions_data):
        """Test specific scenarios"""
        print(f"\n🎭 Testing Scenarios")
        print("=" * 50)
        
        scenario_results = []
        scenarios = questions_data.get('test_scenarios', [])
        
        for scenario in scenarios:
            print(f"\n📘 Scenario: {scenario['scenario']}")
            print(f"📝 Description: {scenario['description']}")
            
            scenario_result = {
                "scenario": scenario['scenario'],
                "description": scenario['description'],
                "questions_tested": [],
                "summary": {}
            }
            
            for question_text in scenario['sample_questions']:
                print(f"\n   🔍 {question_text}")
                
                # Create question data for testing
                question_data = {
                    "question": question_text,
                    "category": "scenario",
                    "difficulty": "intermediate",
                    "question_type": "scenario",
                    "keywords": []
                }
                
                result = self.test_single_question(question_data)
                scenario_result["questions_tested"].append(result)
            
            # Calculate scenario summary
            total_questions = len(scenario_result["questions_tested"])
            context_found = sum(1 for r in scenario_result["questions_tested"] if r.get('context_found', False))
            
            scenario_result["summary"] = {
                "total_questions": total_questions,
                "context_found": context_found,
                "success_rate": (context_found / total_questions * 100) if total_questions > 0 else 0
            }
            
            scenario_results.append(scenario_result)
            
            print(f"   📊 Scenario Summary: {context_found}/{total_questions} questions had relevant context")
        
        return scenario_results
    
    def generate_test_report(self, all_results):
        """Generate comprehensive test report"""
        report = {
            "test_metadata": {
                "test_date": datetime.now().isoformat(),
                "total_questions_tested": len(all_results),
                "categories_tested": list(set(r.get('category', 'unknown') for r in all_results))
            },
            "summary_statistics": {},
            "category_performance": {},
            "detailed_results": all_results,
            "recommendations": []
        }
        
        # Calculate summary statistics
        successful_tests = [r for r in all_results if r.get('context_found', False)]
        failed_tests = [r for r in all_results if not r.get('context_found', False)]
        
        report["summary_statistics"] = {
            "total_tests": len(all_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests) / len(all_results) * 100) if all_results else 0,
            "average_context_time": sum(r.get('context_time', 0) for r in all_results) / len(all_results) if all_results else 0,
            "average_response_time": sum(r.get('response_time', 0) for r in all_results) / len(all_results) if all_results else 0
        }
        
        # Calculate category performance
        categories = set(r.get('category', 'unknown') for r in all_results)
        for category in categories:
            category_results = [r for r in all_results if r.get('category') == category]
            category_successful = [r for r in category_results if r.get('context_found', False)]
            
            report["category_performance"][category] = {
                "total_questions": len(category_results),
                "successful_questions": len(category_successful),
                "success_rate": (len(category_successful) / len(category_results) * 100) if category_results else 0
            }
        
        # Generate recommendations
        recommendations = []
        
        if report["summary_statistics"]["success_rate"] < 70:
            recommendations.append("Consider adding more training data to improve overall success rate")
        
        for category, performance in report["category_performance"].items():
            if performance["success_rate"] < 50:
                recommendations.append(f"Category '{category}' needs more training data or better content")
        
        if report["summary_statistics"]["average_context_time"] > 2.0:
            recommendations.append("Consider optimizing knowledge base for faster context retrieval")
        
        report["recommendations"] = recommendations
        
        return report
    
    def run_comprehensive_test(self, max_per_category=5):
        """Run comprehensive test across all categories"""
        print("🚀 Running Comprehensive Training Questions Test")
        print("=" * 60)
        
        # Load questions
        questions_data = self.load_training_questions()
        if not questions_data:
            return
        
        print(f"📊 Loaded {questions_data['metadata']['total_questions']} training questions")
        print(f"📋 Categories: {', '.join(questions_data['metadata']['categories'])}")
        
        all_results = []
        
        # Test each category
        for category in questions_data['metadata']['categories']:
            category_results = self.test_category(questions_data, category, max_per_category)
            all_results.extend(category_results)
        
        # Test scenarios
        scenario_results = self.test_scenarios(questions_data)
        
        # Generate and save report
        report = self.generate_test_report(all_results)
        report["scenario_results"] = scenario_results
        
        # Save results
        results_file = Path("training_questions_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Display summary
        print(f"\n📊 Test Results Summary")
        print("=" * 40)
        print(f"✅ Total tests: {report['summary_statistics']['total_tests']}")
        print(f"🎯 Success rate: {report['summary_statistics']['success_rate']:.1f}%")
        print(f"⏱️ Avg context time: {report['summary_statistics']['average_context_time']:.2f}s")
        print(f"⏱️ Avg response time: {report['summary_statistics']['average_response_time']:.2f}s")
        
        print(f"\n📋 Category Performance:")
        for category, performance in report['category_performance'].items():
            print(f"   • {category}: {performance['success_rate']:.1f}% ({performance['successful_questions']}/{performance['total_questions']})")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        print(f"\n✅ Detailed results saved to: {results_file}")

def main():
    """Main function"""
    tester = TrainingQuestionTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Quick test with fewer questions
            tester.run_comprehensive_test(max_per_category=3)
        elif sys.argv[1] == "--full":
            # Full test with more questions
            tester.run_comprehensive_test(max_per_category=10)
        else:
            print("Usage: python test_training_questions.py [--quick|--full]")
    else:
        # Default test
        tester.run_comprehensive_test(max_per_category=5)

if __name__ == "__main__":
    main()
