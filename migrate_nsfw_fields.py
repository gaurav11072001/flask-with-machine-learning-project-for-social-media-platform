#!/usr/bin/env python3
"""
Database migration script to add NSFW detection fields to existing posts.
Run this script after updating the Post model to include is_nsfw and nsfw_confidence fields.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///social_media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def migrate_nsfw_fields():
    """Add NSFW fields to existing Post table"""
    try:
        with app.app_context():
            # Check if columns already exist
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(post)"))
                columns = [row[1] for row in result]
                
                if 'is_nsfw' not in columns:
                    print("Adding is_nsfw column to Post table...")
                    conn.execute(text("ALTER TABLE post ADD COLUMN is_nsfw BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("✓ is_nsfw column added successfully")
                else:
                    print("✓ is_nsfw column already exists")
                
                if 'nsfw_confidence' not in columns:
                    print("Adding nsfw_confidence column to Post table...")
                    conn.execute(text("ALTER TABLE post ADD COLUMN nsfw_confidence FLOAT DEFAULT 0.0"))
                    conn.commit()
                    print("✓ nsfw_confidence column added successfully")
                else:
                    print("✓ nsfw_confidence column already exists")
                
                # Update existing posts to have default NSFW values
                print("Updating existing posts with default NSFW values...")
                conn.execute(text("UPDATE post SET is_nsfw = 0, nsfw_confidence = 0.0 WHERE is_nsfw IS NULL"))
                conn.commit()
            print("✓ Existing posts updated successfully")
            
            print("\n✅ NSFW fields migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting NSFW fields migration...")
    migrate_nsfw_fields()
