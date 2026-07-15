from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create a test user
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User '{username}' already exists!")
    else:
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Test user created successfully!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Hashed password: {hashed_password}")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create user: {e}")
    
    # List all users
    users = User.query.all()
    print(f"\nTotal users in database: {len(users)}")
    for user in users:
        print(f"- {user.username} ({user.email})")
