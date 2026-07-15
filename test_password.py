from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    # Test the testuser specifically
    user = User.query.filter_by(username='testuser').first()
    if user:
        print(f"Testing password for user: {user.username}")
        
        # Test the password we used when creating the user
        test_password = 'password123'
        result = check_password_hash(user.password, test_password)
        print(f"Password '{test_password}': {result}")
        
        print(f"\nUser details:")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Password hash: {user.password}")
    else:
        print("No testuser found!")
    
    # Also test the ghij user
    user2 = User.query.filter_by(username='ghij').first()
    if user2:
        print(f"\nTesting user: {user2.username}")
        # We don't know ghij's password, but let's test some common ones
        test_passwords = ['12345678', 'password', 'ghij1234']
        for pwd in test_passwords:
            result = check_password_hash(user2.password, pwd)
            print(f"Password '{pwd}': {result}")
