#!/usr/bin/env python3
"""
Simple test to verify Azure Storage access
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.append('src')

try:
    # Direct import to avoid naming conflicts
    import sys
    sys.path.insert(0, 'src/azure_utils')
    from storage import AzureStorageService
    
    print("🧪 Testing Azure Storage connection...")
    
    # Initialize storage service
    storage_service = AzureStorageService("zetianyuhackathonsa")
    
    # Test 1: List PDFs in training-picture container
    print("\n📁 Testing PDF discovery...")
    pdf_blobs = storage_service.find_pdf_files("training-picture")
    print(f"✅ Found {len(pdf_blobs)} PDF file(s) in training-picture container:")
    for pdf in pdf_blobs:
        print(f"   - {pdf}")
    
    # Test 2: List all blobs in report container (to verify it exists)
    print("\n📊 Testing report container access...")
    try:
        report_blobs = storage_service.list_all_blobs("report")
        print(f"✅ Report container accessible. Found {len(report_blobs)} existing report(s):")
        for report in report_blobs[:5]:  # Show first 5 only
            print(f"   - {report}")
        if len(report_blobs) > 5:
            print(f"   ... and {len(report_blobs) - 5} more")
    except Exception as e:
        print(f"⚠️  Report container issue: {e}")
    
    print("\n✅ Azure Storage tests completed successfully!")
    
except Exception as e:
    print(f"❌ Storage test failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're logged into Azure: az login")
    print("2. Verify your account has access to the storage account")
    print("3. Check if the storage account name is correct")
    sys.exit(1)