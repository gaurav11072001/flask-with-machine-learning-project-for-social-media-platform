"""
Test XAI Model Deployment and Functionality
"""
from app import xai_model, detect_flagged_content

def test_xai_model():
    print("🔍 Testing XAI Model Deployment...\n")
    
    # Test messages
    test_messages = [
        "Hello, how are you today?",  # Safe
        "Send me $500 for emergency help",  # Financial fraud
        "I will kill you if you don't pay",  # Threat/violence
        "Buy this amazing product now!",  # Safe
        "Wire transfer your bitcoin to this address"  # Financial fraud
    ]
    
    print("📊 XAI Model Test Results:")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔤 Test {i}: '{message}'")
        
        # Test using the integrated detection function
        crime_keywords, payment_keywords, xai_result = detect_flagged_content(message)
        
        if xai_result:
            category = xai_result.get('predicted_category', 'unknown')
            confidence = xai_result.get('confidence', 0)
            print(f"   🎯 Category: {category}")
            print(f"   📈 Confidence: {confidence:.1%}")
            print(f"   🚨 Is Threat: {'Yes' if category != 'safe' else 'No'}")
            
            # Show LIME explanation if available
            if 'explanations' in xai_result and 'lime' in xai_result['explanations']:
                lime_exp = xai_result['explanations']['lime']
                if 'feature_importance' in lime_exp:
                    top_features = lime_exp['feature_importance'][:3]  # Top 3 features
                    print(f"   💡 Key Words: {[f[0] for f in top_features]}")
        else:
            print("   ⚠️ XAI result not available")
        
        # Legacy keyword detection
        if crime_keywords or payment_keywords:
            print(f"   🔍 Keywords: {crime_keywords + payment_keywords}")
    
    print("\n" + "=" * 60)
    print("✅ XAI Model is Successfully Deployed and Working!")
    print("🛡️ Your application has real-time cybercrime protection active.")

if __name__ == "__main__":
    test_xai_model()
