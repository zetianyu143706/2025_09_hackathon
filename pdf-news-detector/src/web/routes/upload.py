"""
File upload routes for the Screenshot News Analyzer
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
import tempfile
import os
from typing import Dict, Any
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from src
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

try:
    # Try absolute imports first
    from web.dependencies import get_storage_service, get_container_name
    from web.services.processor import process_screenshot_background
    from web.models.job import job_tracker, JobStatus
except ImportError:
    # Fall back to relative imports
    from ..dependencies import get_storage_service, get_container_name
    from ..services.processor import process_screenshot_background
    from ..models.job import job_tracker, JobStatus

router = APIRouter()

# Allowed file types and size limits
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 
    'image/webp', 'image/bmp', 'image/tiff'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}"
    
    return True, "Valid file"


async def save_temp_file(file: UploadFile) -> tuple[str, bytes]:
    """Save uploaded file temporarily and return path and content"""
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # Create temporary file
    file_ext = Path(file.filename).suffix.lower()
    temp_fd, temp_path = tempfile.mkstemp(suffix=file_ext)
    
    try:
        with os.fdopen(temp_fd, 'wb') as temp_file:
            temp_file.write(content)
        return temp_path, content
    except Exception as e:
        # Clean up on error
        try:
            os.unlink(temp_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@router.post("/upload")
async def upload_screenshot(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a screenshot for analysis
    
    Returns:
        - job_id: Unique identifier for tracking the analysis
        - status: Current status of the job
        - message: Human-readable status message
        - filename: Original filename
    """
    try:
        # Validate file
        is_valid, message = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save file temporarily and get content
        temp_path, file_content = await save_temp_file(file)
        
        # Create job in tracker
        job = job_tracker.create_job(job_id, file.filename, len(file_content), temp_path)
        
        # Start background processing
        background_tasks.add_task(process_screenshot_background, job_id, file_content, file.filename, job_tracker)
        
        return JSONResponse(
            status_code=200,
            content={
                "job_id": job_id,
                "status": "uploaded",
                "message": "File uploaded successfully. Processing will begin shortly.",
                "filename": file.filename,
                "file_size": len(file_content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/upload-status/{job_id}")
async def get_upload_status(job_id: str):
    """Get the status of an uploaded file"""
    job = job_tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "filename": job.filename,
        "status": job.status.value,
        "message": job.message,
        "progress": job.progress,
        "file_size": job.file_size
    }


@router.delete("/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up temporary files for a job"""
    job = job_tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up temporary file
    if job.temp_path and os.path.exists(job.temp_path):
        try:
            os.unlink(job.temp_path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file {job.temp_path}: {e}")
    
    # Remove from job tracker
    job_tracker.delete_job(job_id)
    
    return {"message": f"Job {job_id} cleaned up successfully"}


@router.get("/jobs")
async def list_active_jobs():
    """List all active jobs (for debugging)"""
    jobs = job_tracker.list_jobs()
    
    return {
        "active_jobs": len(jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at
            }
            for job in jobs.values()
        ]
    }