from azure_utils.storage import AzureStorageService
from config import config
import os
from ocr.screenshot_extractor import extract_content_from_screenshot, validate_screenshot
from ocr.image_processor import extract_images_from_screenshot, process_screenshot_for_images
from analysis.text_analyzer import analyze_text
from analysis.image_analyzer import analyze_image
from analysis.consistency_analyzer import analyze_consistency
from report.generator import generate_report

def main():
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed. Please check your settings.")
        return
    
    # Print current configuration
    config.print_config()
    
    # Initialize Azure Storage Service using config
    storage_service = AzureStorageService(config.AZURE_STORAGE_ACCOUNT_NAME)
    container_name = config.AZURE_STORAGE_CONTAINER_NAME  # Changed from training-picture to screenshots
    
    # Find all image files in the container
    image_blobs = storage_service.find_image_files(container_name)
    
    if not image_blobs:
        print("No screenshot images found in the container.")
        return
    
    print(f"Found {len(image_blobs)} screenshot(s): {image_blobs}")
    
    # Process each screenshot
    for image_name in image_blobs:
        print(f"\nProcessing screenshot: {image_name}")
        
        image_path = f"./{image_name}"
        
        try:
            # Download screenshot from Azure Blob Storage
            storage_service.download_image_blob(container_name, image_name, image_path)
            
            # Read screenshot data
            with open(image_path, 'rb') as f:
                screenshot_bytes = f.read()
            
            # Validate screenshot
            if not validate_screenshot(screenshot_bytes):
                print(f"Skipping invalid screenshot: {image_name}")
                continue
            
            print("Extracting content using OCR...")
            # Extract content from screenshot using GPT-4o OCR
            text_content, image_regions, layout_info = extract_content_from_screenshot(screenshot_bytes)
            
            if not text_content or len(text_content.strip()) < 20:
                print(f"Insufficient text content extracted from {image_name}")
                continue
            
            print(f"Extracted text length: {len(text_content)}")
            print(f"Detected {len(image_regions)} image region(s)")
            print(f"Source type: {layout_info.get('source_type', 'unknown')}")
            
            # Process images within the screenshot
            print("Processing embedded images...")
            image_analysis = process_screenshot_for_images(screenshot_bytes)
            
            # For analysis, we'll use the screenshot itself as the "image" since we can't extract sub-images precisely
            images_for_analysis = []
            if image_regions:
                # Create focused analysis requests for each image region
                for region in image_regions:
                    images_for_analysis.append(screenshot_bytes)
            
            # Analyze text content
            print("Analyzing text credibility...")
            text_score, text_details = analyze_text(text_content)
            
            # Analyze images (using screenshot with region focus)
            print("Analyzing image authenticity...")
            if images_for_analysis:
                image_results = [analyze_image(img) for img in images_for_analysis[:3]]  # Limit to 3 for efficiency
                image_scores = [result[0] for result in image_results]
                image_details_list = [result[1] for result in image_results]
                image_score = sum(image_scores) / len(image_scores)
                image_details = {
                    "average_score": image_score,
                    "individual_analyses": image_details_list,
                    "total_images": len(image_regions),
                    "screenshot_analysis": image_analysis
                }
            else:
                image_score = 50  # Neutral score when no images detected
                image_details = {
                    "message": "No embedded images found in screenshot", 
                    "total_images": 0,
                    "screenshot_analysis": image_analysis
                }
            
            # Analyze consistency between text and images
            print("Analyzing text-image consistency...")
            consistency_score, consistency_details = analyze_consistency(text_content, images_for_analysis)
            
            # Generate comprehensive report
            print("Generating analysis report...")
            report = generate_report(
                image_score=image_score,
                text_score=text_score,
                consistency_score=consistency_score,
                screenshot_name=image_name,
                image_details=image_details,
                text_details=text_details,
                consistency_details=consistency_details,
                layout_info=layout_info
            )
            
            print(f"✅ Analysis completed for {image_name}")
            print(f"Final Score: {report.get('final_score', 'N/A')}")
            print(f"Verdict: {report.get('verdict', 'N/A')}")
            
        except ValueError as e:
            print(f"⚠️  Validation error for {image_name}: {str(e)}")
        except RuntimeError as e:
            print(f"❌ Processing error for {image_name}: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error processing {image_name}: {str(e)}")
        
        finally:
            # Clean up the downloaded screenshot
            if os.path.exists(image_path):
                os.remove(image_path)

if __name__ == "__main__":
    main()