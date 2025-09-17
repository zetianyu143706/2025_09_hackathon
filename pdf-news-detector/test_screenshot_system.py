#!/usr/bin/env python3
"""
Test utilities for screenshot processing system
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.append('src')

def test_screenshot_system():
    print("🧪 Testing Screenshot Analysis System...")
    
    try:
        # Test imports
        from ocr.screenshot_extractor import extract_content_from_screenshot, validate_screenshot
        from ocr.image_processor import process_screenshot_for_images
        from preprocessing.screenshot_handler import preprocess_screenshot, detect_screenshot_type
        from azure_utils.storage import AzureStorageService
        
        print("✅ All modules imported successfully")
        
        # Test storage configuration
        print("\n🗄️  Testing Storage Configuration...")
        storage_service = AzureStorageService("zetianyuhackathonsa")
        
        # Test finding image files instead of PDFs
        try:
            container_name = "screenshots"  # Changed from training-picture
            image_files = storage_service.find_image_files(container_name)
            print(f"✅ Found {len(image_files)} screenshot(s) in '{container_name}' container")
            if image_files:
                print(f"   Sample files: {image_files[:3]}")
        except Exception as e:
            print(f"⚠️  Storage access error: {str(e)}")
        
        # Test environment configuration
        print("\n⚙️  Testing Environment Configuration...")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        vision_deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4.1")
        
        if azure_endpoint:
            print(f"✅ Azure OpenAI endpoint: {azure_endpoint}")
            print(f"✅ Vision deployment: {vision_deployment}")
        else:
            print("⚠️  AZURE_OPENAI_ENDPOINT not set")
        
        # Test screenshot validation
        print("\n🖼️  Testing Screenshot Validation...")
        
        # Test with minimal valid image data (JPEG header)
        minimal_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 1000
        is_valid = validate_screenshot(minimal_jpeg)
        print(f"   Minimal JPEG validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test with insufficient data
        invalid_data = b'invalid'
        is_valid = validate_screenshot(invalid_data)
        print(f"   Invalid data validation: {'✅ Correctly rejected' if not is_valid else '❌ False positive'}")
        
        # Test preprocessing functionality
        print("\n🔧 Testing Preprocessing...")
        try:
            characteristics = detect_screenshot_type(minimal_jpeg)
            if "error" not in characteristics:
                print(f"   ✅ Screenshot type detection working")
                print(f"      Detected: {characteristics.get('layout_type', 'unknown')} layout")
            else:
                print(f"   ⚠️  Screenshot type detection: {characteristics['error']}")
        except Exception as e:
            print(f"   ⚠️  Preprocessing test error: {str(e)}")
        
        print("\n📊 System Capabilities:")
        print("   • OCR text extraction from screenshots using GPT-4.1")
        print("   • Image region detection and analysis")
        print("   • Layout analysis (mobile, desktop, tablet)")
        print("   • Source detection (social media, news sites)")
        print("   • Multi-modal consistency analysis")
        print("   • Comprehensive credibility reporting")
        
        print("\n📁 Expected Container Structure:")
        print("   • screenshots/ - Input screenshot files")
        print("   • report/ - Generated analysis reports")
        
        print("\n🎯 Supported File Types:")
        print("   • .jpg, .jpeg - JPEG images")
        print("   • .png - PNG images") 
        print("   • .webp - WebP images")
        print("   • .bmp, .tiff - Other formats")
        
        print("\n✅ Screenshot analysis system ready!")
        print("\nTo run analysis:")
        print("1. Upload screenshots to 'screenshots' container in Azure Storage")
        print("2. Run: python src/main.py")
        print("3. Check 'report' container for analysis results")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Install missing dependencies: pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_screenshot_system()