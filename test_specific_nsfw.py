#!/usr/bin/env python3
"""
Test script to check NSFW detection with different types of images
"""

import os
import sys
from PIL import Image, ImageDraw
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nudenet_categories():
    """Test what categories NudeNet can detect"""
    try:
        from nudenet import NudeDetector
        
        detector = NudeDetector()
        
        print("🔍 NudeNet Detection Categories:")
        print("=" * 50)
        
        # Create a simple test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            test_image_path = tmp_file.name
        
        # Create a simple image
        img = Image.new('RGB', (400, 400), (255, 255, 255))
        img.save(test_image_path, 'JPEG')
        
        # Test detection
        results = detector.detect(test_image_path)
        print(f"📊 Detection results for white image: {results}")
        
        # Clean up
        os.unlink(test_image_path)
        
        # Print what categories NudeNet looks for
        print("\n🏷️ Categories that NudeNet typically detects:")
        categories = [
            'EXPOSED_ANUS', 'EXPOSED_ARMPITS', 'EXPOSED_BELLY', 'EXPOSED_BUTTOCKS',
            'EXPOSED_BREAST_F', 'EXPOSED_BREAST_M', 'EXPOSED_GENITALIA_F', 
            'EXPOSED_GENITALIA_M', 'EXPOSED_THIGHS_F', 'EXPOSED_THIGHS_M',
            'FACE_F', 'FACE_M', 'FEET_F', 'FEET_M'
        ]
        
        for category in categories:
            print(f"   - {category}")
            
        print("\n💡 Note: For male torso images like the one you uploaded,")
        print("   NudeNet should detect 'EXPOSED_BREAST_M' if the chest is visible.")
        print("   The current threshold is set to 0.3 for better sensitivity.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing NudeNet categories: {e}")
        return False

def test_current_detection_logic():
    """Test the current detection logic from app.py"""
    try:
        from app import detect_nsfw_content
        
        print("\n🧪 Testing Current Detection Logic")
        print("=" * 50)
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            test_image_path = tmp_file.name
        
        # Create a simple image
        img = Image.new('RGB', (400, 400), (255, 255, 255))
        img.save(test_image_path, 'JPEG')
        
        # Test our detection function
        is_nsfw, confidence = detect_nsfw_content(test_image_path)
        
        print(f"🎯 Our detection result: is_nsfw={is_nsfw}, confidence={confidence}")
        
        # Clean up
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing detection logic: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run NSFW detection tests"""
    print("🚀 Testing NSFW Detection with Different Scenarios")
    print("=" * 60)
    
    # Test NudeNet categories
    test1_passed = test_nudenet_categories()
    
    # Test current detection logic
    test2_passed = test_current_detection_logic()
    
    print("\n📊 Test Results")
    print("=" * 50)
    print(f"NudeNet Categories Test: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Detection Logic Test: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n💡 Troubleshooting Tips:")
        print("1. Make sure the app is restarted after code changes")
        print("2. Check the console output when uploading images")
        print("3. The image you uploaded (shirtless male) should trigger 'EXPOSED_BREAST_M'")
        print("4. Current threshold is 0.3 - very sensitive")
        print("5. Look for debug messages in the console during upload")
    
if __name__ == '__main__':
    main()
