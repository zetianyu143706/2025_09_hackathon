"""
Status and job tracking routes for the Screenshot News Analyzer
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from src
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

router = APIRouter()

from web.models.job import job_tracker


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the current status of a job
    
    Returns:
        - job_id: The job identifier
        - status: Current status (uploaded, processing, completed, error)
        - message: Human-readable status message
        - progress: Progress percentage (0-100)
        - results: Analysis results (when completed)
        - error: Error message (if status is error)
    """
    job = job_tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = job.to_dict()
    
    # Remove sensitive information
    if "temp_path" in response:
        del response["temp_path"]
    
    return response


@router.get("/results/{job_id}")
async def get_job_results(job_id: str):
    """
    Get the analysis results for a completed job
    
    Returns the full analysis report when the job is completed
    """
    job = job_tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status.value != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed yet. Current status: {job.status.value}"
        )
    
    if not job.results:
        raise HTTPException(status_code=404, detail="No results available for this job")
    
    return {
        "job_id": job_id,
        "filename": job.filename,
        "status": job.status.value,
        "results": job.results
    }


@router.get("/jobs/summary")
async def get_jobs_summary():
    """Get a summary of all jobs"""
    jobs = job_tracker.list_jobs()
    
    status_counts = {}
    total_jobs = len(jobs)
    
    for job in jobs.values():
        status = job.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_jobs": total_jobs,
        "status_counts": status_counts,
        "jobs": [
            {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status.value,
                "progress": job.progress,
                "file_size": job.file_size,
                "created_at": job.created_at
            }
            for job in jobs.values()
        ]
    }