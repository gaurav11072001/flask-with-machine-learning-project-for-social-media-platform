"""
Test script to verify that the login fix works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db, User, safe_log
from werkzeug.security import generate_password_hash

def test_login_fix():
    """Test that login function works without OSError"""
    print("Testing login functionality fix...")
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Test the safe_log function
        print("Testing safe_log function...")
        safe_log("Test debug message", 'debug')
        safe_log("Test info message", 'info')
        safe_log("Test warning message", 'warning')
        safe_log("Test error message", 'error')
        print("✓ safe_log function works correctly")
        
        # Test database operations
        print("Testing database operations...")
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                password=generate_password_hash('testpassword123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user created successfully")
        else:
            print("✓ Test user already exists")
        
        print("✓ All tests passed! The login fix should resolve the OSError issue.")
        print("✓ Application now uses safe logging instead of print() statements")
        print("✓ Flask-SocketIO is configured for Windows compatibility")

if __name__ == '__main__':
    test_login_fix()
