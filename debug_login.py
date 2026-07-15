from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    # Check all users in database
    users = User.query.all()
    print("All users in database:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        print(f"Password hash: {user.password[:50]}..." if len(user.password) > 50 else f"Password hash: {user.password}")
        print(f"Bio: {user.bio}")
        print("---")
    
    if users:
        # Test password checking for first user
        test_user = users[0]
        print(f"\nTesting password verification for user: {test_user.username}")
        
        # Test with some common passwords
        test_passwords = ['password', 'test123', 'admin', 'user123', '12345678']
        
        for pwd in test_passwords:
            result = check_password_hash(test_user.password, pwd)
            print(f"Password '{pwd}': {result}")
        
        # Let's also test creating a new hash
        test_hash = generate_password_hash('test123')
        print(f"\nNew hash for 'test123': {test_hash}")
        print(f"Verification: {check_password_hash(test_hash, 'test123')}")
    else:
        print("No users found in database!")
