#!/usr/bin/env python3
"""
Script to create or promote a user to admin in the cybercrime detection system.
Run this script to set up admin access for the admin panel.
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, User
    print("✓ Successfully imported app modules")
except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    sys.exit(1)

def create_or_promote_admin():
    """Create a new admin user or promote existing user to admin"""
    
    with app.app_context():
        print("\n" + "="*50)
        print("CYBERCRIME DETECTION ADMIN USER SETUP")
        print("="*50)
        
        # Get username
        username = input("\nEnter admin username: ").strip()
        if not username:
            print("✗ Username cannot be empty")
            return False
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            print(f"\nUser '{username}' already exists!")
            if existing_user.is_admin:
                print(f"✓ User '{username}' is already an admin")
                return True
            else:
                promote = input("Would you like to promote this user to admin? (y/n): ").lower()
                if promote == 'y':
                    existing_user.is_admin = True
                    db.session.commit()
                    print(f"✓ User '{username}' has been promoted to admin!")
                    return True
                else:
                    print("✗ Admin promotion cancelled")
                    return False
        
        # Create new admin user
        print(f"\nCreating new admin user: {username}")
        
        # Get password
        password = input("Enter admin password (minimum 8 characters): ").strip()
        if len(password) < 8:
            print("✗ Password must be at least 8 characters long")
            return False
        
        # Get email (optional)
        email = input("Enter admin email (optional): ").strip()
        
        try:
            # Create new admin user
            hashed_password = generate_password_hash(password)
            new_admin = User(
                username=username,
                email=email if email else None,
                password=hashed_password,
                is_admin=True,
                bio="System Administrator",
                created_at=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            
            db.session.add(new_admin)
            db.session.commit()
            
            print(f"✓ Admin user '{username}' created successfully!")
            print(f"✓ Admin privileges: Enabled")
            if email:
                print(f"✓ Email: {email}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating admin user: {e}")
            return False

def list_admin_users():
    """List all admin users"""
    
    with app.app_context():
        print("\n" + "="*40)
        print("CURRENT ADMIN USERS")
        print("="*40)
        
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("No admin users found")
            return
        
        for i, admin in enumerate(admin_users, 1):
            print(f"\n{i}. Username: {admin.username}")
            print(f"   Email: {admin.email or 'Not provided'}")
            print(f"   Created: {admin.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Last seen: {admin.last_seen.strftime('%Y-%m-%d %H:%M:%S') if admin.last_seen else 'Never'}")
            print(f"   Posts: {admin.posts_count()}")
            print(f"   Followers: {admin.followers_count()}")

def verify_admin_access():
    """Verify admin setup and display access information"""
    
    with app.app_context():
        admin_count = User.query.filter_by(is_admin=True).count()
        total_users = User.query.count()
        
        print("\n" + "="*40)
        print("ADMIN ACCESS VERIFICATION")
        print("="*40)
        print(f"✓ Total users: {total_users}")
        print(f"✓ Admin users: {admin_count}")
        
        if admin_count > 0:
            print(f"✓ Admin panel available at: http://localhost:5000/admin/login")
            print(f"✓ Main site available at: http://localhost:5000/")
            print(f"\nAdmin Features Available:")
            print(f"  • User Management")
            print(f"  • Post Moderation")
            print(f"  • Message Monitoring")
            print(f"  • System Analytics")
            print(f"  • XAI Model Insights")
        else:
            print("✗ No admin users configured")
            return False
        
        return True

def main():
    """Main function"""
    print("CYBERCRIME DETECTION SYSTEM - Admin Setup")
    print("This script helps you create or manage admin users.")
    
    while True:
        print("\n" + "="*30)
        print("OPTIONS")
        print("="*30)
        print("1. Create/Promote Admin User")
        print("2. List Current Admin Users")
        print("3. Verify Admin Setup")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            create_or_promote_admin()
        elif choice == '2':
            list_admin_users()
        elif choice == '3':
            verify_admin_access()
        elif choice == '4':
            print("\n✓ Admin setup complete!")
            print("You can now start the application and access the admin panel.")
            break
        else:
            print("✗ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("Please check your setup and try again.")
