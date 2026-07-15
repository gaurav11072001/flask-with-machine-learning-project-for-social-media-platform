#!/usr/bin/env python3
"""
Database migration script to add is_admin column to User table.
This script safely adds the admin functionality to existing databases.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, User
    print("✓ Successfully imported app modules")
except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    sys.exit(1)

def backup_database():
    """Create a backup of the current database"""
    db_path = 'social_media.db'
    if not os.path.exists(db_path):
        print("✓ No existing database found - will create new one")
        return True
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'social_media_backup_{timestamp}.db'
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to backup database: {e}")
        return False

def check_admin_column_exists():
    """Check if is_admin column already exists"""
    try:
        with app.app_context():
            # Try to query the is_admin column
            result = db.session.execute(db.text("SELECT is_admin FROM user LIMIT 1"))
            print("✓ is_admin column already exists")
            return True
    except Exception:
        print("ℹ is_admin column does not exist - will add it")
        return False

def add_admin_column():
    """Add is_admin column to User table"""
    try:
        with app.app_context():
            # Add the column with default value FALSE
            db.session.execute(db.text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("✓ Successfully added is_admin column")
            return True
    except Exception as e:
        print(f"✗ Failed to add is_admin column: {e}")
        return False

def migrate_database():
    """Main migration function"""
    print("\n" + "="*50)
    print("DATABASE MIGRATION - ADDING ADMIN SUPPORT")
    print("="*50)
    
    # Step 1: Backup existing database
    if not backup_database():
        return False
    
    # Step 2: Check if migration is needed
    if check_admin_column_exists():
        print("✓ Database already has admin support")
        return True
    
    # Step 3: Add admin column
    if not add_admin_column():
        return False
    
    # Step 4: Verify migration
    with app.app_context():
        try:
            # Test that we can query the new column
            db.session.execute(db.text("SELECT COUNT(*) FROM user WHERE is_admin = 0")).scalar()
            print("✓ Migration completed successfully")
            return True
        except Exception as e:
            print(f"✗ Migration verification failed: {e}")
            return False

def create_fresh_database():
    """Create fresh database with all tables"""
    try:
        with app.app_context():
            # Drop all tables and recreate them
            db.drop_all()
            db.create_all()
            print("✓ Created fresh database with admin support")
            return True
    except Exception as e:
        print(f"✗ Failed to create fresh database: {e}")
        return False

def main():
    """Main function"""
    print("CYBERCRIME DETECTION SYSTEM - Database Migration")
    print("This script adds admin functionality to your database.")
    
    while True:
        print("\n" + "="*40)
        print("MIGRATION OPTIONS")
        print("="*40)
        print("1. Migrate Existing Database (Recommended)")
        print("2. Create Fresh Database (WARNING: Data Loss)")
        print("3. Check Database Status")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            if migrate_database():
                print("\n✓ Database migration completed!")
                print("You can now run create_admin_user.py to set up admin access.")
                break
            else:
                print("\n✗ Migration failed. Please check the errors above.")
                
        elif choice == '2':
            confirm = input("\n⚠️ WARNING: This will delete ALL existing data! Continue? (type 'yes' to confirm): ")
            if confirm.lower() == 'yes':
                if create_fresh_database():
                    print("\n✓ Fresh database created!")
                    print("You can now run create_admin_user.py to set up admin access.")
                    break
                else:
                    print("\n✗ Failed to create fresh database.")
            else:
                print("✓ Operation cancelled.")
                
        elif choice == '3':
            print("\nChecking database status...")
            if check_admin_column_exists():
                print("✓ Database has admin support")
            else:
                print("ℹ Database needs migration to add admin support")
                
            # Show table info
            try:
                with app.app_context():
                    total_users = db.session.execute(db.text("SELECT COUNT(*) FROM user")).scalar()
                    total_posts = db.session.execute(db.text("SELECT COUNT(*) FROM post")).scalar()
                    print(f"✓ Current data: {total_users} users, {total_posts} posts")
            except Exception as e:
                print(f"ℹ Could not check data: {e}")
                
        elif choice == '4':
            print("\n✓ Migration tool closed.")
            break
        else:
            print("✗ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Migration cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("Please check your setup and try again.")
