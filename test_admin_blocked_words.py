#!/usr/bin/env python3
"""
Test script for admin blocked words functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, BlockedWord, detect_vulgar_content
from werkzeug.security import generate_password_hash

def setup_test_admin():
    """Create a test admin user and some blocked words"""
    with app.app_context():
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='testadmin').first()
        if not admin:
            admin = User(
                username='testadmin',
                email='admin@test.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Test admin user created: testadmin / admin123")
        else:
            print("✅ Test admin user already exists")
        
        # Add some test blocked words
        test_words = [
            ('spam', 'spam', 1.0),
            ('scam', 'custom', 1.5),
            ('fake', 'custom', 0.8),
            ('clickbait', 'spam', 0.6),
            ('pyramid', 'custom', 1.2)
        ]
        
        for word, category, severity in test_words:
            existing = BlockedWord.query.filter_by(word=word).first()
            if not existing:
                blocked_word = BlockedWord(
                    word=word,
                    category=category,
                    severity=severity,
                    added_by=admin.id
                )
                db.session.add(blocked_word)
        
        db.session.commit()
        print("✅ Test blocked words added")

def test_custom_blocked_words():
    """Test that custom blocked words are working"""
    with app.app_context():
        print("\n🧪 Testing Custom Blocked Words Detection")
        print("=" * 50)
        
        test_cases = [
            # Should be blocked by custom words
            ("This is a spam message", True),
            ("Don't fall for this scam", True),
            ("This is fake news", True),
            ("Click here for clickbait", True),
            ("Join my pyramid scheme", True),
            
            # Should not be blocked
            ("This is a normal message", False),
            ("I love this post", False),
            ("Great content!", False),
            
            # Should be blocked by default words
            ("This is fucking awesome", True),
            ("What the hell", True),
        ]
        
        passed = 0
        failed = 0
        
        for text, expected_blocked in test_cases:
            is_vulgar, vulgar_words, severity_score = detect_vulgar_content(text)
            
            result = "✅ PASS" if is_vulgar == expected_blocked else "❌ FAIL"
            status = "BLOCKED" if is_vulgar else "ALLOWED"
            
            print(f"{result} - '{text}' → {status}")
            if is_vulgar:
                print(f"    Words detected: {vulgar_words}")
                print(f"    Severity: {severity_score:.2f}")
            
            if is_vulgar == expected_blocked:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 Results: {passed} passed, {failed} failed")
        return failed == 0

def show_admin_instructions():
    """Show instructions for using the admin interface"""
    print("\n🎯 Admin Blocked Words Management Instructions")
    print("=" * 50)
    print("1. Start your Flask app: python app.py")
    print("2. Go to: http://localhost:5000/admin/login")
    print("3. Login with: testadmin / admin123")
    print("4. Navigate to: Admin Dashboard → Blocked Words")
    print("5. You can:")
    print("   • Add new blocked words with custom severity")
    print("   • Categorize words (profanity, hate_speech, custom, etc.)")
    print("   • Toggle words active/inactive")
    print("   • Delete words")
    print("   • Search and filter words")
    print("\n🔧 Features:")
    print("• Real-time content filtering in comments, posts, and messages")
    print("• Custom severity levels (0.1 - 2.0)")
    print("• Category-based organization")
    print("• Admin audit trail (who added what word)")
    print("• Bulk management capabilities")

if __name__ == "__main__":
    print("🚀 Setting up Admin Blocked Words Test Environment")
    print("=" * 60)
    
    # Setup test environment
    setup_test_admin()
    
    # Test the functionality
    success = test_custom_blocked_words()
    
    if success:
        print("\n🎉 All tests passed! Custom blocked words system is working.")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
    
    # Show usage instructions
    show_admin_instructions()
    
    print("\n💡 Pro Tips:")
    print("• Use severity 0.1-0.5 for mild content")
    print("• Use severity 0.6-1.0 for moderate content") 
    print("• Use severity 1.1-2.0 for severe content")
    print("• Categories help organize and manage large word lists")
    print("• Inactive words are kept in database but not used for filtering")
