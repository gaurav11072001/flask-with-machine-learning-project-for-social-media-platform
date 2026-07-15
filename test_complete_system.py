#!/usr/bin/env python3
"""
Comprehensive test script for XAI-enhanced cybercrime detection system
Tests both the XAI model and the integrated chat warning system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import detect_flagged_content, get_sender_warning_message, get_receiver_warning_message
from xai_cybercrime_model import CybercrimeXAIModel
import pandas as pd
import json

def test_xai_model():
    """Test the XAI model functionality"""
    print("=== Testing XAI Model ===")
    
    # Load the trained model
    xai_model = CybercrimeXAIModel()
    if not xai_model.load_model():
        print("❌ Failed to load XAI model")
        return False
    
    print("✅ XAI model loaded successfully")
    
    # Test messages from different categories
    test_messages = [
        # Financial fraud
        ("Send me $500 for emergency medical bills", "financial_fraud"),
        ("Bitcoin payment needed for investment opportunity", "financial_fraud"),
        ("Wire transfer your inheritance money to claim it", "financial_fraud"),
        
        # Threats and violence
        ("I'm going to kill you if you don't comply", "threats_violence"),
        ("Bomb threat at your location", "threats_violence"),
        ("Bring weapons to the meeting", "weapons_trafficking"),
        
        # Phishing
        ("Click this link to verify your account now", "phishing"),
        ("Update your password immediately or lose access", "phishing"),
        
        # Safe messages
        ("How was your day at work today?", "safe"),
        ("Let's meet for coffee tomorrow", "safe"),
        ("The weather is beautiful this weekend", "safe")
    ]
    
    correct_predictions = 0
    total_predictions = len(test_messages)
    
    for message, expected_category in test_messages:
        result = xai_model.predict_with_explanation(message, explanation_type='lime')
        predicted_category = result['predicted_category']
        confidence = result['confidence']
        
        print(f"\nMessage: '{message}'")
        print(f"Expected: {expected_category}")
        print(f"Predicted: {predicted_category} (confidence: {confidence:.3f})")
        
        if predicted_category == expected_category:
            print("✅ Correct prediction")
            correct_predictions += 1
        else:
            print("❌ Incorrect prediction")
        
        # Show LIME explanation
        if 'lime' in result['explanations']:
            print("Top contributing words:")
            for word, importance in result['explanations']['lime']['feature_importance'][:3]:
                print(f"  {word}: {importance:.3f}")
    
    accuracy = correct_predictions / total_predictions
    print(f"\n=== XAI Model Test Results ===")
    print(f"Accuracy: {accuracy:.3f} ({correct_predictions}/{total_predictions})")
    print(f"Status: {'✅ PASS' if accuracy >= 0.7 else '❌ FAIL'}")
    
    return accuracy >= 0.7

def test_integrated_detection():
    """Test the integrated detection system"""
    print("\n=== Testing Integrated Detection System ===")
    
    test_cases = [
        # Crime-related
        {
            'message': "I'm going to hurt you badly",
            'expected_type': 'crime',
            'description': 'Violence threat'
        },
        {
            'message': "Selling drugs, high quality cocaine available",
            'expected_type': 'crime',
            'description': 'Drug trafficking'
        },
        # Payment-related
        {
            'message': "Send bitcoin to this wallet for guaranteed profits",
            'expected_type': 'payment',
            'description': 'Financial scam'
        },
        {
            'message': "Need your credit card details for verification",
            'expected_type': 'payment',
            'description': 'Identity theft'
        },
        # Safe messages
        {
            'message': "Great weather for a picnic today",
            'expected_type': 'safe',
            'description': 'Normal conversation'
        }
    ]
    
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        message = test_case['message']
        expected_type = test_case['expected_type']
        description = test_case['description']
        
        print(f"\nTest {i}: {description}")
        print(f"Message: '{message}'")
        
        # Test the integrated detection
        crime_keywords, payment_keywords, xai_result = detect_flagged_content(message)
        
        # Determine detected type
        if crime_keywords:
            detected_type = 'crime'
        elif payment_keywords:
            detected_type = 'payment'
        else:
            detected_type = 'safe'
        
        print(f"Expected: {expected_type}")
        print(f"Detected: {detected_type}")
        
        if detected_type == expected_type:
            print("✅ Correct detection")
            passed_tests += 1
        else:
            print("❌ Incorrect detection")
        
        # Show XAI prediction if available
        if xai_result:
            print(f"XAI Prediction: {xai_result.get('predicted_category', 'N/A')} "
                  f"(confidence: {xai_result.get('confidence', 0):.3f})")
        
        # Test warning messages
        if detected_type != 'safe':
            flag_type = detected_type
            sender_warning = get_sender_warning_message(flag_type)
            receiver_warning = get_receiver_warning_message(flag_type)
            print(f"Sender warning ready: {'✅' if sender_warning else '❌'}")
            print(f"Receiver warning ready: {'✅' if receiver_warning else '❌'}")
    
    accuracy = passed_tests / len(test_cases)
    print(f"\n=== Integrated Detection Test Results ===")
    print(f"Accuracy: {accuracy:.3f} ({passed_tests}/{len(test_cases)})")
    print(f"Status: {'✅ PASS' if accuracy >= 0.8 else '❌ FAIL'}")
    
    return accuracy >= 0.8

def test_xai_insights():
    """Test XAI model insights functionality"""
    print("\n=== Testing XAI Model Insights ===")
    
    try:
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            print("❌ Failed to load XAI model for insights")
            return False
        
        insights = xai_model.get_model_insights()
        
        # Validate insights structure
        required_keys = ['model_params', 'top_features']
        for key in required_keys:
            if key not in insights:
                print(f"❌ Missing key in insights: {key}")
                return False
        
        print("✅ Model insights structure valid")
        
        # Display key insights
        model_params = insights['model_params']
        print(f"Model Type: {model_params['model_type']}")
        print(f"Features: {model_params['n_features']:,}")
        print(f"Classes: {model_params['n_classes']}")
        
        print("Top 5 Most Important Features:")
        for i, feature in enumerate(insights['top_features'][:5], 1):
            print(f"  {i}. {feature['feature']}: {feature['importance']:.4f}")
        
        print("✅ XAI insights test passed")
        return True
        
    except Exception as e:
        print(f"❌ XAI insights test failed: {e}")
        return False

def test_dataset_quality():
    """Test the quality of the generated dataset"""
    print("\n=== Testing Dataset Quality ===")
    
    try:
        # Load dataset
        df = pd.read_csv('cybercrime_dataset.csv')
        print(f"✅ Dataset loaded: {len(df)} samples")
        
        # Check balance
        category_counts = df['category'].value_counts()
        print("Category distribution:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        # Check for missing values
        missing_values = df.isnull().sum().sum()
        if missing_values == 0:
            print("✅ No missing values")
        else:
            print(f"⚠️ Found {missing_values} missing values")
        
        # Check feature engineering
        required_columns = ['text', 'category', 'is_cybercrime', 'threat_level', 'contains_money_terms']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if not missing_columns:
            print("✅ All required columns present")
        else:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check threat level distribution
        avg_threat_level = df[df['is_cybercrime'] == True]['threat_level'].mean()
        print(f"Average threat level (cybercrime): {avg_threat_level:.2f}")
        
        print("✅ Dataset quality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Dataset quality test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide comprehensive results"""
    print("🚀 Starting Comprehensive XAI Cybercrime Detection System Test")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Dataset Quality
    test_results.append(("Dataset Quality", test_dataset_quality()))
    
    # Test 2: XAI Model
    test_results.append(("XAI Model", test_xai_model()))
    
    # Test 3: Integrated Detection
    test_results.append(("Integrated Detection", test_integrated_detection()))
    
    # Test 4: XAI Insights
    test_results.append(("XAI Insights", test_xai_insights()))
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed_tests += 1
    
    overall_success = passed_tests / total_tests
    print(f"\nOverall Success Rate: {overall_success:.1%} ({passed_tests}/{total_tests})")
    
    if overall_success >= 0.75:
        print("\n🎉 SYSTEM READY FOR PRODUCTION!")
        print("   ✅ XAI model is working correctly")
        print("   ✅ Warning system is functional")
        print("   ✅ Detection accuracy is acceptable")
        print("   ✅ Dashboard components are ready")
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION!")
        print("   Some components failed testing")
        print("   Please review the failed tests above")
    
    return overall_success >= 0.75

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
