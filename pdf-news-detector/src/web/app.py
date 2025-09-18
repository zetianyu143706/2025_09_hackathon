"""
Main FastAPI application for the Screenshot News Analyzer Web Interface
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import from src
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from config import config

# Initialize FastAPI app
app = FastAPI(
    title="Screenshot News Analyzer",
    description="Web interface for analyzing screenshot credibility using AI",
    version="1.0.0"
)

# Get template and static file paths
template_dir = current_dir / "templates"
static_dir = current_dir / "static"

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(template_dir))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with upload interface"""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/results/{job_id}", response_class=HTMLResponse)
async def results_page(request: Request, job_id: str):
    """Results page for a specific job"""
    return templates.TemplateResponse("results.html", {"request": request, "job_id": job_id})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Screenshot News Analyzer",
        "version": "1.0.0"
    }


@app.get("/api/config")
async def get_config():
    """Get basic configuration info (non-sensitive)"""
    return {
        "storage_account": config.AZURE_STORAGE_ACCOUNT_NAME,
        "container": config.AZURE_STORAGE_CONTAINER_NAME,
        "openai_endpoint": config.AZURE_OPENAI_ENDPOINT.replace("https://", "").split(".")[0] if config.AZURE_OPENAI_ENDPOINT else "not-configured"
    }


# Include route modules
from .routes import upload, status

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(status.router, prefix="/api", tags=["status"])


if __name__ == "__main__":
    # For local development
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )