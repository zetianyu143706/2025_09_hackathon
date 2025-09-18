"""
Background analysis processor for the Screenshot News Analyzer
This module integrates the existing analysis pipeline with the web interface
"""
import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import from src
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

# Import existing analysis modules
from ocr.screenshot_extractor import extract_content_from_screenshot, validate_screenshot
from ocr.image_processor import process_screenshot_for_images
from analysis.text_analyzer import analyze_text
from analysis.image_analyzer import analyze_image
from analysis.consistency_analyzer import analyze_consistency
from report.generator import generate_report
from azure_utils.storage import AzureStorageService
from config import config


class AnalysisProcessor:
    """Handles background processing of screenshot analysis"""
    
    def __init__(self):
        self.storage_service = AzureStorageService(config.AZURE_STORAGE_ACCOUNT_NAME)
        self.container_name = config.AZURE_STORAGE_CONTAINER_NAME
    
    async def process_screenshot_async(self, job_id: str, file_bytes: bytes, filename: str, job_tracker):
        """
        Process a screenshot asynchronously using the existing analysis pipeline
        
        Args:
            job_id: Unique job identifier
            file_bytes: Raw image data
            filename: Original filename
            job_tracker: JobTracker instance for status updates
        """
        try:
            from web.models.job import JobStatus
            
            # Update job status to processing
            job_tracker.update_job(job_id, JobStatus.PROCESSING, "Starting analysis...", 5)
            
            # Step 1: Validate screenshot
            if not validate_screenshot(file_bytes):
                raise ValueError("Invalid screenshot format or corrupted file")
            
            # Step 2: Upload to Azure Storage
            job_tracker.update_job(job_id, JobStatus.PROCESSING, "Uploading to Azure Storage...", 10)
            
            # Generate unique filename for storage
            timestamp = int(time.time())
            storage_filename = f"{timestamp}_{filename}"
            
            # Upload to Azure Storage
            self.storage_service.upload_blob(
                container_name=self.container_name,
                blob_name=storage_filename,
                data=file_bytes,
                content_type="image/jpeg"  # Default, could be detected
            )
            
            # Step 3: Extract content using OCR
            job_tracker.update_job(job_id, JobStatus.EXTRACTING_TEXT, "Extracting text content using OCR...", 20)
            
            text_content, image_regions, layout_info = extract_content_from_screenshot(file_bytes)
            
            if not text_content or len(text_content.strip()) < 20:
                raise ValueError("Insufficient text content extracted from screenshot")
            
            # Step 4: Process images within the screenshot
            job_tracker.update_job(job_id, JobStatus.PROCESSING, "Processing embedded images...", 35)
            
            image_analysis = process_screenshot_for_images(file_bytes)
            
            # Prepare images for analysis
            images_for_analysis = []
            if image_regions:
                # Use the screenshot itself for each region (simplified approach)
                for region in image_regions[:3]:  # Limit to 3 for efficiency
                    images_for_analysis.append(file_bytes)
            
            # Step 5: Analyze text content
            job_tracker.update_job(job_id, JobStatus.ANALYZING_TEXT, "Analyzing text credibility...", 50)
            
            text_score, text_details = analyze_text(text_content)
            
            # Step 6: Analyze images
            job_tracker.update_job(job_id, JobStatus.ANALYZING_IMAGES, "Analyzing image authenticity...", 70)
            
            if images_for_analysis:
                image_results = []
                for img in images_for_analysis:
                    result = analyze_image(img)
                    image_results.append(result)
                
                image_scores = [result[0] for result in image_results]
                image_details_list = [result[1] for result in image_results]
                image_score = sum(image_scores) / len(image_scores) if image_scores else 50
                
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
            
            # Step 7: Analyze consistency between text and images
            job_tracker.update_job(job_id, JobStatus.PROCESSING, "Analyzing text-image consistency...", 85)
            
            consistency_score, consistency_details = analyze_consistency(text_content, images_for_analysis)
            
            # Step 8: Generate comprehensive report
            job_tracker.update_job(job_id, JobStatus.GENERATING_REPORT, "Generating final report...", 95)
            
            report = generate_report(
                image_score=image_score,
                text_score=text_score,
                consistency_score=consistency_score,
                screenshot_name=storage_filename,
                image_details=image_details,
                text_details=text_details,
                consistency_details=consistency_details,
                layout_info=layout_info
            )
            
            # Upload report to Azure Storage (use same container for now)
            report_filename = f"report_{timestamp}_{filename}.json"
            import json
            try:
                self.storage_service.upload_blob(
                    container_name=self.container_name,  # Use same container
                    blob_name=report_filename,
                    data=json.dumps(report, indent=2),
                    content_type="application/json"
                )
                print(f"Report uploaded as: {report_filename}")
            except Exception as e:
                print(f"Warning: Failed to upload report: {e}")
                # Continue anyway - we have the results in memory
            
            # Step 9: Complete the job
            job_tracker.update_job(
                job_id, 
                JobStatus.COMPLETED, 
                "Analysis completed successfully!", 
                100,
                results=report
            )
            
            # Clean up temporary file
            job = job_tracker.get_job(job_id)
            if job and job.temp_path and os.path.exists(job.temp_path):
                try:
                    os.unlink(job.temp_path)
                    job.temp_path = None
                except Exception as e:
                    print(f"Warning: Failed to delete temp file: {e}")
            
            print(f"[SUCCESS] Analysis completed for job {job_id}")
            print(f"Final Score: {report.get('final_score', 'N/A')}")
            print(f"Verdict: {report.get('verdict', 'N/A')}")
            
        except ValueError as e:
            job_tracker.update_job(job_id, JobStatus.ERROR, f"Validation error: {str(e)}", error=str(e))
        except RuntimeError as e:
            job_tracker.update_job(job_id, JobStatus.ERROR, f"Processing error: {str(e)}", error=str(e))
        except Exception as e:
            job_tracker.update_job(job_id, JobStatus.ERROR, f"Unexpected error: {str(e)}", error=str(e))

# Global processor instance
processor = AnalysisProcessor()


async def process_screenshot_background(job_id: str, file_bytes: bytes, filename: str, job_tracker):
    """
    Background task wrapper for screenshot processing
    """
    await processor.process_screenshot_async(job_id, file_bytes, filename, job_tracker)