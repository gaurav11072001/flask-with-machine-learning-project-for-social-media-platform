#!/usr/bin/env python3
"""
Test script for vulgar content detection algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import detect_vulgar_content

def test_vulgar_detection():
    """Test the vulgar content detection with various examples"""
    
    print("🧪 Testing Vulgar Content Detection Algorithm")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        # Clean content (should pass)
        ("This is a nice photo!", False),
        ("Great post! Love it!", False),
        ("Beautiful sunset today", False),
        ("Thanks for sharing", False),
        
        # Vulgar content (should be blocked)
        ("This is fucking awesome!", True),
        ("What the hell is this?", True),
        ("You're such a bitch", True),
        ("This shit is crazy", True),
        ("Damn that's cool", True),
        
        # Leetspeak attempts (should be blocked)
        ("This is f*cking great", True),
        ("What the h*ll", True),
        ("You're a b!tch", True),
        ("This sh*t rocks", True),
        ("F**k yeah!", True),
        
        # Spacing tricks (should be blocked)
        ("f u c k this", True),
        ("s h i t happens", True),
        ("b i t c h please", True),
        
        # Repeated characters (should be blocked)
        ("fuuuuck that", True),
        ("shiiiit", True),
        ("daaaaamn", True),
        
        # Hate speech (should be blocked)
        ("You're so gay", True),
        ("Don't be retarded", True),
        ("That's stupid", True),
        
        # Threatening language (should be blocked)
        ("I'll kill you", True),
        ("Go die", True),
        ("I want to hurt someone", True),
        
        # Sexual content (should be blocked)
        ("You're so sexy", True),
        ("That's hot", True),
        ("Nice boobs", True),
        
        # Edge cases
        ("", False),  # Empty string
        ("a", False),  # Single character
        ("Hell's Kitchen", False),  # Context matters - this should pass
        ("Damn good food", True),  # But this should be blocked
    ]
    
    passed = 0
    failed = 0
    
    for i, (text, expected_blocked) in enumerate(test_cases, 1):
        is_vulgar, vulgar_words, severity_score = detect_vulgar_content(text)
        
        # Determine result
        result = "✅ PASS" if is_vulgar == expected_blocked else "❌ FAIL"
        status = "BLOCKED" if is_vulgar else "ALLOWED"
        
        print(f"Test {i:2d}: {result}")
        print(f"  Text: '{text}'")
        print(f"  Expected: {'BLOCKED' if expected_blocked else 'ALLOWED'}")
        print(f"  Actual: {status}")
        
        if is_vulgar:
            print(f"  Vulgar words: {vulgar_words}")
            print(f"  Severity: {severity_score:.2f}")
        
        print()
        
        if is_vulgar == expected_blocked:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("🎉 All tests passed! Vulgar content detection is working correctly.")
    else:
        print("⚠️ Some tests failed. Review the algorithm for improvements.")

def interactive_test():
    """Interactive testing mode"""
    print("\n🔧 Interactive Vulgar Content Detection Test")
    print("=" * 50)
    print("Enter text to test (or 'quit' to exit):")
    
    while True:
        try:
            text = input("\n> ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                print("Please enter some text to test.")
                continue
            
            is_vulgar, vulgar_words, severity_score = detect_vulgar_content(text)
            
            if is_vulgar:
                print(f"🚫 BLOCKED - Inappropriate content detected")
                print(f"   Vulgar words: {vulgar_words}")
                print(f"   Severity score: {severity_score:.2f}")
            else:
                print(f"✅ ALLOWED - Content is appropriate")
                
        except KeyboardInterrupt:
            break
    
    print("\nGoodbye! 👋")

if __name__ == "__main__":
    # Run automated tests
    test_vulgar_detection()
    
    # Ask if user wants interactive testing
    response = input("\nWould you like to test interactively? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_test()
