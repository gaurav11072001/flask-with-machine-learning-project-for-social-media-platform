#!/usr/bin/env python3
"""
Retroactive NSFW check for existing posts.
This script will check all existing posts that haven't been NSFW-checked yet.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def retroactive_nsfw_check():
    """Check existing posts for NSFW content"""
    try:
        from app import app, db, Post, detect_nsfw_content
        
        with app.app_context():
            # Find posts that haven't been NSFW checked (confidence = 0.0)
            unchecked_posts = Post.query.filter_by(nsfw_confidence=0.0).all()
            
            print(f"🔍 Found {len(unchecked_posts)} posts to check for NSFW content")
            
            blocked_count = 0
            
            for post in unchecked_posts:
                print(f"\n📋 Checking Post ID {post.id}: {post.image_filename}")
                
                # Build full path to image
                image_path = os.path.join('uploads', 'posts', post.image_filename)
                
                if not os.path.exists(image_path):
                    print(f"⚠️ Image file not found: {image_path}")
                    continue
                
                # Run NSFW detection
                is_nsfw, confidence = detect_nsfw_content(image_path)
                
                # Update post with NSFW results
                post.is_nsfw = is_nsfw
                post.nsfw_confidence = confidence
                
                if is_nsfw:
                    print(f"🚫 NSFW DETECTED - Blocking post {post.id}")
                    print(f"   Confidence: {confidence:.3f}")
                    print(f"   Caption: {post.caption}")
                    
                    # Optionally delete the image file
                    try:
                        os.remove(image_path)
                        print(f"🗑️ Deleted NSFW image: {image_path}")
                    except Exception as e:
                        print(f"⚠️ Could not delete image: {e}")
                    
                    blocked_count += 1
                else:
                    print(f"✅ Post {post.id} is safe (confidence: {confidence:.3f})")
            
            # Save changes to database
            db.session.commit()
            
            print(f"\n📊 Retroactive NSFW Check Complete:")
            print(f"   - Posts checked: {len(unchecked_posts)}")
            print(f"   - Posts blocked: {blocked_count}")
            print(f"   - Posts safe: {len(unchecked_posts) - blocked_count}")
            
            if blocked_count > 0:
                print(f"\n🎯 {blocked_count} NSFW posts have been blocked and removed!")
            else:
                print(f"\n✅ All existing posts are safe!")
                
    except Exception as e:
        print(f"❌ Error during retroactive NSFW check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Starting Retroactive NSFW Check...")
    retroactive_nsfw_check()
