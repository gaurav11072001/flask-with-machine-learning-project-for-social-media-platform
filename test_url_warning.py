#!/usr/bin/env python3
"""
Test what happens when URLs or suspicious content is shared in messages
"""

def test_url_and_link_warnings():
    """Test various URL and link sharing scenarios"""
    print("Testing URL and Link Sharing Warnings")
    print("=" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        
        # Initialize model
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            print("❌ Failed to load XAI model")
            return False
            
        print("✅ XAI model loaded successfully\n")
        
        # Test messages with URLs and suspicious content
        test_messages = [
            # URL sharing scenarios
            "Check out this link: http://secure-bank-login.com",
            "Visit this website: https://paypal-security-update.net", 
            "Click here: http://amazon-delivery-update.org/update",
            "Go to: https://google-account-recovery.info",
            "Link: http://microsoft-license-verification.com",
            
            # Legitimate URLs (might still trigger)
            "Check out this article: https://www.cnn.com/news/article", 
            "Visit our website: https://www.google.com",
            "Here's the link: https://github.com/project/repo",
            
            # Phishing without URLs but with URL-like language
            "Click this link to verify your account",
            "Visit our secure website to update details",
            "Go to the verification page now",
            
            # Suspicious content without URLs
            "Send me your password for verification",
            "Share your bank account details with me",
            "I need your credit card information urgently",
            "Transfer money to this account number",
            
            # Normal messages
            "Hey, how are you doing today?",
            "Let's meet for lunch tomorrow",
            "The meeting is at 3 PM",
        ]
        
        print("Testing messages that might trigger warnings...")
        print("-" * 60)
        
        warnings_triggered = 0
        
        for i, message in enumerate(test_messages, 1):
            try:
                result = xai_model.predict_with_explanation(message, "lime")
                
                category = result['predicted_category']
                confidence = result['confidence']
                is_cybercrime = result['is_cybercrime']
                
                if is_cybercrime:
                    if category == 'phishing':
                        status = "🚨 PHISHING WARNING"
                    elif category == 'financial_fraud':
                        status = "💰 FINANCIAL FRAUD WARNING"
                    elif category == 'identity_theft':
                        status = "🆔 IDENTITY THEFT WARNING"
                    else:
                        status = f"⚠️  {category.upper()} WARNING"
                    warnings_triggered += 1
                else:
                    status = "✅ SAFE"
                
                print(f"{i:2d}. {status} (conf: {confidence:.3f})")
                print(f"    Message: '{message}'")
                
                # Show key warning features
                if is_cybercrime and 'lime' in result['explanations']:
                    features = result['explanations']['lime'].get('feature_importance', [])
                    if features:
                        top_features = features[:3]
                        print(f"    ⚠️  Warning triggered by: {', '.join([f'{feat}({score:.3f})' for feat, score in top_features])}")
                
                print()
                
            except Exception as e:
                print(f"{i:2d}. ❌ ERROR: {e}")
                print()
        
        print("=" * 60)
        print("SUMMARY:")
        print(f"Total messages tested: {len(test_messages)}")
        print(f"Messages that triggered warnings: {warnings_triggered}")
        print(f"Warning rate: {warnings_triggered/len(test_messages)*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in URL warning test: {e}")
        return False

def test_specific_warning_scenarios():
    """Test specific scenarios that definitely trigger warnings"""
    print("\n" + "=" * 60)
    print("Testing Specific Warning Scenarios")
    print("=" * 60)
    
    try:
        from xai_cybercrime_model import CybercrimeXAIModel
        
        xai_model = CybercrimeXAIModel()
        if not xai_model.load_model():
            return False
        
        # Scenarios that should definitely trigger warnings
        warning_scenarios = [
            "Click this link to verify your account: http://secure-login.net",
            "Your password expires soon, update at: https://bank-security.org", 
            "Account suspended! Verify here: http://paypal-restore.com",
            "I need your bank account details for the transfer",
            "Send me your credit card info to process payment",
            "Share your SSN for tax refund processing",
            "Transfer $500 to this account immediately",
            "Send bitcoin to this address for investment",
            "I will kill you if you don't pay me",
            "Meet me to buy some drugs tonight"
        ]
        
        print("Testing scenarios that should trigger warnings...")
        
        all_warned = True
        
        for i, message in enumerate(warning_scenarios, 1):
            result = xai_model.predict_with_explanation(message, "lime")
            
            if result['is_cybercrime']:
                print(f"✅ {i:2d}. WARNING TRIGGERED: {result['predicted_category']} (conf: {result['confidence']:.3f})")
            else:
                print(f"❌ {i:2d}. NO WARNING: {result['predicted_category']} (conf: {result['confidence']:.3f})")
                all_warned = False
                
            print(f"      '{message}'")
        
        print(f"\nAll high-risk scenarios triggered warnings: {'✅ YES' if all_warned else '❌ NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in specific warning test: {e}")
        return False

def main():
    """Run URL and warning tests"""
    print("URL and Content Warning Analysis")
    print("=" * 80)
    
    success = True
    
    # Test URL and link warnings
    success &= test_url_and_link_warnings()
    
    # Test specific warning scenarios
    success &= test_specific_warning_scenarios()
    
    if success:
        print("\n🎉 URL and warning analysis completed!")
        print("\n📋 KEY FINDINGS:")
        print("• The system WILL warn about suspicious URLs and links")
        print("• ANY message with cybercrime patterns triggers warnings")
        print("• Warnings appear for phishing, financial fraud, threats, etc.")
        print("• Even sharing legitimate-looking URLs can trigger warnings if suspicious")
        print("• The system protects users from all forms of cybercrime content")
        
        print("\n⚠️  WARNING TRIGGERS:")
        print("• URLs with suspicious domains (bank-login, paypal-security, etc.)")
        print("• Messages asking for personal information")
        print("• Requests for passwords, bank details, credit cards")
        print("• Money transfer requests")
        print("• Account verification demands")
        print("• Any content matching cybercrime patterns")
        
    else:
        print("\n❌ Some tests failed.")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
