#!/usr/bin/env python3
"""
Web server launcher for Screenshot News Analyzer
"""
import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Now import the FastAPI app
from web.app import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Screenshot News Analyzer Web Interface...")
    print("📁 Project directory:", current_dir)
    print("🐍 Python path includes:", str(src_dir))
    print("🌐 Starting server on http://localhost:8001")
    print("📱 Open http://localhost:8001 in your browser")
    print("⏹️  Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )