"""
Command Line Interface utilities for the Screenshot News Analyzer.
Handles argument parsing and screenshot selection logic.
"""

import argparse
import sys
from typing import List
from azure_utils.storage import AzureStorageService


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for screenshot processing."""
    parser = argparse.ArgumentParser(
        description="Screenshot News Analyzer - Analyze specific screenshots for credibility",
        add_help=False  # Disable default help
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--screenshots', 
        nargs='+', 
        metavar='FILENAME',
        help='Specific screenshot filenames to process (e.g., image1.jpg image2.png)'
    )
    group.add_argument(
        '--list-available', 
        action='store_true',
        help='List all available screenshots in the container and exit'
    )
    
    return parser.parse_args()


def get_screenshots_to_process(args: argparse.Namespace, storage_service: AzureStorageService, container_name: str) -> List[str]:
    """
    Determine which screenshots to process based on command line arguments.
    
    Args:
        args: Parsed command line arguments
        storage_service: Azure Storage Service instance
        container_name: Name of the Azure container
        
    Returns:
        List of screenshot filenames to process
        
    Raises:
        SystemExit: When listing available screenshots or when no valid files found
    """
    
    if args.list_available:
        # List available screenshots and exit
        available_screenshots = storage_service.find_image_files(container_name)
        print(f"\n[INFO] Available screenshots in '{container_name}' container:")
        if available_screenshots:
            for i, screenshot in enumerate(available_screenshots, 1):
                print(f"  {i}. {screenshot}")
            print(f"\nTotal: {len(available_screenshots)} screenshot(s)")
        else:
            print("  No screenshots found in container.")
        sys.exit(0)
    
    elif args.screenshots:
        # Process specific screenshots
        print(f"[INFO] Processing {len(args.screenshots)} specific screenshot(s)...")
        
        # Validate that specified files exist in container
        available_screenshots = storage_service.find_image_files(container_name)
        valid_screenshots = []
        missing_screenshots = []
        
        for screenshot in args.screenshots:
            if screenshot in available_screenshots:
                valid_screenshots.append(screenshot)
            else:
                missing_screenshots.append(screenshot)
        
        # Report missing files
        if missing_screenshots:
            print(f"[WARNING] {len(missing_screenshots)} screenshot(s) not found in container:")
            for missing in missing_screenshots:
                print(f"   - {missing}")
        
        # Check if we have any valid files to process
        if not valid_screenshots:
            print("[ERROR] None of the specified screenshots were found in the container.")
            print(f"Available screenshots: {available_screenshots}")
            sys.exit(1)
        
        if valid_screenshots:
            print(f"[SUCCESS] Found {len(valid_screenshots)} valid screenshot(s) to process:")
            for screenshot in valid_screenshots:
                print(f"   - {screenshot}")
        
        return valid_screenshots
    
    else:
        print("[ERROR] No processing mode specified.")
        sys.exit(1)


def validate_screenshot_arguments(screenshots: List[str]) -> bool:
    """
    Validate screenshot filename arguments.
    
    Args:
        screenshots: List of screenshot filenames
        
    Returns:
        True if all filenames are valid, False otherwise
    """
    if not screenshots:
        return False
    
    # Check for valid image extensions
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
    
    for screenshot in screenshots:
        if not any(screenshot.lower().endswith(ext) for ext in valid_extensions):
            print(f"[WARNING] '{screenshot}' does not have a valid image extension")
            return False
    
    return True