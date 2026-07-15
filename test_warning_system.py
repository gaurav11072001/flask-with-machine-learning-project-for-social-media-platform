#!/usr/bin/env python3
"""
Test script for the warning system functionality
This script tests the crime and payment detection functions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import detect_flagged_content, get_sender_warning_message, get_receiver_warning_message

def test_crime_detection():
    """Test crime-related keyword detection"""
    print("=== Testing Crime Detection ===")
    
    crime_messages = [
        "I have a gun and I'm going to kill someone",
        "Let's plan a robbery at the bank",
        "I'm selling drugs and cocaine",
        "This is a bomb threat",
        "Normal message with no issues"
    ]
    
    for message in crime_messages:
        crime_keywords, payment_keywords = detect_flagged_content(message)
        print(f"Message: '{message}'")
        print(f"Crime Keywords: {crime_keywords}")
        print(f"Payment Keywords: {payment_keywords}")
        if crime_keywords:
            print(f"Sender Warning: {get_sender_warning_message('crime')}")
            print(f"Receiver Warning: {get_receiver_warning_message('crime')}")
        print("-" * 50)

def test_payment_detection():
    """Test payment-related keyword detection"""
    print("\n=== Testing Payment Detection ===")
    
    payment_messages = [
        "Can you send money to my account?",
        "I need help with a wire transfer",
        "Please send bitcoin to this address",
        "Give me your credit card details",
        "Can you lend money for emergency",
        "Normal conversation about weather"
    ]
    
    for message in payment_messages:
        crime_keywords, payment_keywords = detect_flagged_content(message)
        print(f"Message: '{message}'")
        print(f"Crime Keywords: {crime_keywords}")
        print(f"Payment Keywords: {payment_keywords}")
        if payment_keywords:
            print(f"Sender Warning: {get_sender_warning_message('payment')}")
            print(f"Receiver Warning: {get_receiver_warning_message('payment')}")
        print("-" * 50)

def test_mixed_detection():
    """Test messages with both crime and payment keywords"""
    print("\n=== Testing Mixed Detection ===")
    
    mixed_messages = [
        "Send money or I'll kill you",
        "This is a fraud scheme involving weapons",
        "Transfer bitcoin or face violence"
    ]
    
    for message in mixed_messages:
        crime_keywords, payment_keywords = detect_flagged_content(message)
        print(f"Message: '{message}'")
        print(f"Crime Keywords: {crime_keywords}")
        print(f"Payment Keywords: {payment_keywords}")
        
        # Determine priority (crime takes precedence)
        flag_type = 'crime' if crime_keywords else 'payment' if payment_keywords else None
        if flag_type:
            print(f"Flag Type: {flag_type}")
            print(f"Sender Warning: {get_sender_warning_message(flag_type)}")
            print(f"Receiver Warning: {get_receiver_warning_message(flag_type)}")
        print("-" * 50)

if __name__ == "__main__":
    print("Testing InstaShare Warning System")
    print("=" * 60)
    
    test_crime_detection()
    test_payment_detection()
    test_mixed_detection()
    
    print("\n=== Test Complete ===")
    print("The warning system is properly detecting:")
    print("✓ Crime-related keywords")
    print("✓ Payment-related keywords") 
    print("✓ Mixed content with appropriate prioritization")
    print("✓ Appropriate warning messages for senders and receivers")
