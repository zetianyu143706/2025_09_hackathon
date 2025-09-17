#!/usr/bin/env python3
"""
Test script for the new coherence analyzer
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.append('src')

try:
    from analysis.coherence_analyzer import analyze_coherence, analyze_single_image_coherence
    
    print("🧪 Testing Coherence Analyzer...")
    
    # Test 1: Basic functionality with mock data
    print("\n📝 Test 1: Basic coherence analysis with sample text")
    sample_text = """
    Breaking News: Local Fire Department Responds to Kitchen Fire
    
    Yesterday evening, the Springfield Fire Department successfully contained a kitchen fire 
    at 123 Oak Street. The fire started around 6:30 PM when a cooking pot was left unattended. 
    Firefighters arrived within minutes and prevented the fire from spreading to other parts 
    of the house. No injuries were reported, and the family was safely evacuated.
    
    Fire Chief Johnson stated, "This incident serves as a reminder to always stay in the 
    kitchen while cooking and to keep pot handles turned inward."
    """
    
    # Test with empty image list
    try:
        score, details = analyze_coherence(sample_text, [])
        print(f"✅ Coherence analysis completed successfully")
        print(f"   Score: {score}")
        print(f"   Status: {details.get('warning', 'No warning')}")
        
        if 'text_only_analysis' in details:
            print("   ℹ️  Correctly handled no-image scenario")
        
    except Exception as e:
        print(f"❌ Error in coherence analysis: {e}")
    
    # Test 2: Text validation
    print("\n📝 Test 2: Input validation")
    
    # Test with insufficient text
    try:
        score, details = analyze_coherence("short text", [])
        print(f"✅ Short text validation: Score = {score}")
        if "error" in details:
            print("   ℹ️  Correctly detected insufficient text")
    except Exception as e:
        print(f"❌ Error in text validation: {e}")
    
    # Test 3: Configuration check
    print("\n⚙️  Test 3: Environment configuration")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    vision_deployment = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4o")
    
    if azure_endpoint:
        print(f"✅ Azure OpenAI endpoint configured: {azure_endpoint}")
        print(f"✅ Vision deployment: {vision_deployment}")
        print("   ℹ️  Ready for live API calls when images are provided")
    else:
        print("⚠️  AZURE_OPENAI_ENDPOINT not set - API calls will fail")
        print("   To fix: Set environment variable AZURE_OPENAI_ENDPOINT")
    
    print("\n✅ Coherence analyzer tests completed!")
    print("\nNext steps:")
    print("1. Run the full pipeline with: python src/main.py")
    print("2. Check generated reports for coherence analysis results")
    print("3. Look for 'coherence_analysis' section in JSON reports")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)