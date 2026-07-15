#!/usr/bin/env python3
"""
Test script to understand when phishing detection is triggered
"""

import sys
import os

def test_phishing_patterns():
    """Test various phishing patterns to see what triggers detection"""
    print("Testing Phishing Detection Patterns")
    print("=" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        
        # Initialize and load model
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            print("❌ Failed to load XAI model")
            return False
            
        print("✅ XAI model loaded successfully")
        
        # Phishing test messages based on common patterns
        phishing_tests = [
            # Classic phishing patterns from dataset
            "Click this link to verify your account immediately",
            "Your password will expire, update it now", 
            "Suspicious activity detected, confirm your identity",
            "Account locked, provide login details to unlock",
            "Banking security update required, enter credentials",
            "Free gift card, just enter your personal information",
            "Tax refund available, submit SSN and bank details",
            "PayPal account suspended, confirm payment details",
            "Amazon package delivery failed, update address and payment",
            "Microsoft security alert, verify Windows license",
            "Google account compromised, reset password here",
            "iPhone winner selected, claim prize with personal info",
            "Social media account hacked, secure it now",
            
            # Variations and edge cases
            "Please verify your account by clicking here",
            "Your account has been compromised, reset now",
            "Update your payment information immediately",
            "Confirm your identity to avoid account suspension",
            "Security alert: unusual activity on your account",
            "Your subscription will expire, renew now",
            "Verify your email address to continue",
            "Account verification required within 24 hours",
            
            # Non-phishing messages for comparison
            "Hello, how are you today?",
            "Let's meet for coffee tomorrow",
            "I'm running late for the meeting",
            "Thanks for your help with the project",
            "The weather is nice today",
        ]
        
        print(f"\nTesting {len(phishing_tests)} messages for phishing detection...")
        print("-" * 60)
        
        phishing_detected = 0
        safe_detected = 0
        
        for i, message in enumerate(phishing_tests, 1):
            try:
                result = xai_model.predict_with_explanation(message, "lime")
                
                category = result['predicted_category']
                confidence = result['confidence']
                is_cybercrime = result['is_cybercrime']
                
                if category == 'phishing':
                    status = "🎯 PHISHING"
                    phishing_detected += 1
                elif is_cybercrime:
                    status = f"⚠️  {category.upper()}"
                else:
                    status = "✅ SAFE"
                    safe_detected += 1
                
                print(f"{i:2d}. {status} (conf: {confidence:.3f})")
                print(f"    Message: '{message[:60]}{'...' if len(message) > 60 else ''}'")
                
                # Show top features if available
                if 'lime' in result['explanations'] and result['explanations']['lime'].get('feature_importance'):
                    top_features = result['explanations']['lime']['feature_importance'][:3]
                    print(f"    Key features: {', '.join([f'{feat}: {score:.3f}' for feat, score in top_features])}")
                
                print()
                
            except Exception as e:
                print(f"{i:2d}. ❌ ERROR: {e}")
                print(f"    Message: '{message}'")
                print()
                
        print("=" * 60)
        print("SUMMARY:")
        print(f"Total messages tested: {len(phishing_tests)}")
        print(f"Detected as PHISHING: {phishing_detected}")
        print(f"Detected as SAFE: {safe_detected}")
        print(f"Detected as OTHER CYBERCRIME: {len(phishing_tests) - phishing_detected - safe_detected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in phishing test: {e}")
        return False

def analyze_phishing_keywords():
    """Analyze what keywords are associated with phishing"""
    print("\n" + "=" * 60)
    print("Analyzing Phishing Keywords from Dataset")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        # Read the dataset
        df = pd.read_csv('cybercrime_dataset.csv')
        
        # Filter phishing entries
        phishing_data = df[df['category'] == 'phishing']
        
        print(f"Found {len(phishing_data)} phishing examples in dataset")
        print("\nCommon phishing message patterns:")
        
        # Show some examples
        for i, row in phishing_data.head(10).iterrows():
            print(f"  • {row['text']}")
            
        # Analyze common words
        all_phishing_text = ' '.join(phishing_data['text'].str.lower())
        
        # Common phishing keywords based on dataset
        phishing_keywords = [
            'account', 'verify', 'click', 'link', 'password', 'expire',
            'suspicious', 'activity', 'confirm', 'identity', 'locked',
            'login', 'details', 'unlock', 'security', 'update', 'credentials',
            'banking', 'gift', 'card', 'personal', 'information', 'refund',
            'submit', 'ssn', 'bank', 'credit', 'paypal', 'suspended',
            'amazon', 'delivery', 'failed', 'address', 'payment', 'microsoft',
            'alert', 'license', 'google', 'compromised', 'reset', 'iphone',
            'winner', 'selected', 'claim', 'prize', 'social', 'media', 'hacked'
        ]
        
        print(f"\nKey phishing indicators found in dataset:")
        keyword_counts = {}
        for keyword in phishing_keywords:
            count = all_phishing_text.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
                
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        for keyword, count in sorted_keywords[:15]:
            print(f"  • '{keyword}': appears {count} times")
            
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing phishing keywords: {e}")
        return False

def test_specific_phishing_scenarios():
    """Test specific phishing scenarios that should definitely be detected"""
    print("\n" + "=" * 60)
    print("Testing Specific Phishing Scenarios")
    print("=" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            return False
        
        # High-confidence phishing scenarios
        high_risk_phishing = [
            "URGENT: Click this link to verify your account immediately or it will be suspended",
            "Your password expires in 24 hours. Update now: http://secure-bank-login.com",
            "Security Alert: Suspicious activity detected on your PayPal account. Confirm identity here",
            "Account locked due to failed login attempts. Provide login details to unlock immediately",
            "Amazon package delivery failed. Update your address and payment info to receive package",
            "You've won an iPhone! Click here and enter your personal information to claim prize",
            "Google account compromised. Reset your password here before hackers access your data",
            "Microsoft Windows license expired. Verify now to avoid losing your data",
            "Tax refund of $1,234 available. Submit your SSN and bank details to process refund",
            "FREE $100 gift card! Just enter your credit card information for verification"
        ]
        
        print("Testing high-risk phishing scenarios...")
        detected_count = 0
        
        for i, message in enumerate(high_risk_phishing, 1):
            result = xai_model.predict_with_explanation(message, "lime")
            
            category = result['predicted_category']
            confidence = result['confidence']
            
            if category == 'phishing':
                print(f"✅ {i:2d}. DETECTED as phishing (confidence: {confidence:.3f})")
                detected_count += 1
            elif result['is_cybercrime']:
                print(f"⚠️  {i:2d}. Detected as {category} (confidence: {confidence:.3f})")
            else:
                print(f"❌ {i:2d}. NOT detected as cybercrime (confidence: {confidence:.3f})")
                
        print(f"\nHigh-risk phishing detection rate: {detected_count}/{len(high_risk_phishing)} ({detected_count/len(high_risk_phishing)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in specific phishing test: {e}")
        return False

def main():
    """Run all phishing detection tests"""
    print("Phishing Detection Analysis")
    print("=" * 80)
    
    success = True
    
    # Test general phishing patterns
    success &= test_phishing_patterns()
    
    # Analyze keywords from dataset
    success &= analyze_phishing_keywords()
    
    # Test specific high-risk scenarios
    success &= test_specific_phishing_scenarios()
    
    if success:
        print("\n" + "🎉 Phishing detection analysis completed!")
        print("\nKey Findings:")
        print("• Phishing detection is based on trained patterns from the dataset")
        print("• Common triggers: verify, account, click, link, password, suspicious, etc.")
        print("• Model looks for urgency, credential requests, and suspicious links")
        print("• Detection accuracy depends on similarity to training examples")
    else:
        print("\n❌ Some tests failed.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
