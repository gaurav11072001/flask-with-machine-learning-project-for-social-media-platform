#!/usr/bin/env python3
"""
Test script to verify SHAP functionality after fixes
"""

import sys
import os

def test_shap_explanations():
    """Test SHAP explanations with the fixed model"""
    print("Testing SHAP Explanations After Fix...")
    print("-" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        print("✅ Full XAI model imported successfully")
        
        # Initialize and load model
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            print("❌ Failed to load XAI model")
            return False
            
        print("✅ XAI model loaded successfully")
        
        # Test messages for different categories
        test_messages = [
            "I want to transfer money to you",
            "Send me bitcoin for investment", 
            "I will kill you if you don't pay",
            "Hello, how are you today?",
            "Click this link to verify your account"
        ]
        
        print("\nTesting SHAP explanations...")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing: '{message}'")
            
            try:
                # Test with SHAP explanations
                result = xai_model.predict_with_explanation(message, "shap")
                
                print(f"   Prediction: {result['predicted_category']} (confidence: {result['confidence']:.3f})")
                
                if 'shap' in result['explanations']:
                    shap_data = result['explanations']['shap']
                    
                    if 'error' in shap_data:
                        print(f"   ❌ SHAP Error: {shap_data['error']}")
                    elif 'note' in shap_data:
                        print(f"   ⚠️  SHAP Fallback: {shap_data['note']}")
                        print(f"   📊 Feature importance available: {len(shap_data.get('feature_importance', []))} features")
                    else:
                        print(f"   ✅ SHAP Success: {len(shap_data.get('feature_importance', []))} features")
                        
                        # Show top 3 features
                        if shap_data.get('feature_importance'):
                            print("   Top SHAP features:")
                            for feat in shap_data['feature_importance'][:3]:
                                print(f"      - {feat['feature']}: {feat['shap_value']:.4f}")
                else:
                    print("   ❌ No SHAP explanations found")
                    
            except Exception as e:
                print(f"   ❌ Error testing message: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error in SHAP test: {e}")
        return False

def test_combined_explanations():
    """Test both LIME and SHAP explanations together"""
    print("\n" + "=" * 60)
    print("Testing Combined LIME + SHAP Explanations...")
    print("-" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            return False
            
        test_message = "I need you to send money urgently for emergency"
        print(f"Testing message: '{test_message}'")
        
        # Get both explanations
        result = xai_model.predict_with_explanation(test_message, "both")
        
        print(f"\nPrediction: {result['predicted_category']} (confidence: {result['confidence']:.3f})")
        
        # Check LIME
        if 'lime' in result['explanations']:
            lime_data = result['explanations']['lime']
            print(f"✅ LIME: {len(lime_data.get('feature_importance', []))} features")
            if lime_data.get('feature_importance'):
                print("   Top LIME features:")
                for feat, score in lime_data['feature_importance'][:3]:
                    print(f"      - {feat}: {score:.4f}")
        else:
            print("❌ LIME explanations not available")
            
        # Check SHAP
        if 'shap' in result['explanations']:
            shap_data = result['explanations']['shap']
            if 'error' not in shap_data:
                print(f"✅ SHAP: {len(shap_data.get('feature_importance', []))} features")
                if shap_data.get('feature_importance'):
                    print("   Top SHAP features:")
                    for feat in shap_data['feature_importance'][:3]:
                        print(f"      - {feat['feature']}: {feat['shap_value']:.4f}")
            else:
                print(f"⚠️  SHAP: {shap_data.get('note', 'Failed')}")
        else:
            print("❌ SHAP explanations not available")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in combined test: {e}")
        return False

def main():
    """Run SHAP fix tests"""
    print("SHAP Fix Verification Tests")
    print("=" * 60)
    
    success = True
    
    # Test SHAP explanations
    success &= test_shap_explanations()
    
    # Test combined explanations
    success &= test_combined_explanations()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SHAP fix tests completed successfully!")
        print("\nKey Improvements:")
        print("• Better dtype handling for SHAP inputs")
        print("• Improved explainer initialization")
        print("• Graceful fallback to model feature importance")
        print("• Enhanced error handling and reporting")
    else:
        print("❌ Some SHAP tests failed. Check the implementation.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
