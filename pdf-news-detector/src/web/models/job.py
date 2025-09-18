"""
Job tracking models for the Screenshot News Analyzer
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time


class JobStatus(Enum):
    """Enumeration of possible job statuses"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTING_TEXT = "extracting_text"
    ANALYZING_TEXT = "analyzing_text"
    ANALYZING_IMAGES = "analyzing_images"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class JobInfo:
    """Information about a processing job"""
    job_id: str
    filename: str
    status: JobStatus
    message: str
    progress: int = 0
    file_size: int = 0
    temp_path: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "status": self.status.value,
            "message": self.message,
            "progress": self.progress,
            "file_size": self.file_size,
            "results": self.results,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_status(self, status: JobStatus, message: str, progress: int = None):
        """Update job status and timestamp"""
        self.status = status
        self.message = message
        self.updated_at = time.time()
        
        if progress is not None:
            self.progress = progress


class JobTracker:
    """In-memory job tracking system"""
    
    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
    
    def create_job(self, job_id: str, filename: str, file_size: int, temp_path: str = None) -> JobInfo:
        """Create a new job"""
        job = JobInfo(
            job_id=job_id,
            filename=filename,
            status=JobStatus.UPLOADED,
            message="File uploaded successfully, processing will start shortly",
            file_size=file_size,
            temp_path=temp_path
        )
        self._jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job by ID"""
        return self._jobs.get(job_id)
    
    def update_job(self, job_id: str, status: JobStatus, message: str, progress: int = None, results: Dict = None, error: str = None):
        """Update job status"""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.update_status(status, message, progress)
            
            if results is not None:
                job.results = results
            
            if error is not None:
                job.error = error
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False
    
    def list_jobs(self) -> Dict[str, JobInfo]:
        """List all jobs"""
        return self._jobs.copy()
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs older than specified hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_jobs = [
            job_id for job_id, job in self._jobs.items()
            if current_time - job.created_at > max_age_seconds
        ]
        
        for job_id in expired_jobs:
            self.delete_job(job_id)
        
        return len(expired_jobs)


# Global job tracker instance
job_tracker = JobTracker()