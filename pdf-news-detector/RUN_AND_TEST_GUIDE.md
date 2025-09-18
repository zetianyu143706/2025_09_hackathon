# Screenshot News Analyzer - Run and Test Guide

## **Project Overview**

This is a sophisticated AI-powered news credibility analysis system that processes **screenshots** to determine if news content is authentic or fake. The system has both:

1. **CLI Mode**: Command-line interface for processing specific screenshots
2. **Web Mode**: Modern FastAPI web application with upload interface

### **Key Features:**
- 🔍 **OCR Text Extraction** using GPT-4.1 Vision
- 🖼️ **Image Authenticity Analysis** (AI-generated vs real)  
- ⚖️ **Text-Image Consistency** checking
- 📊 **Comprehensive Credibility Scoring** (0-100)
- ☁️ **Azure Integration** (Storage + OpenAI)
- 🌐 **Web Interface** with real-time progress

---

## **How to Run the Project**

### **Prerequisites & Setup**

**0. Install Python (if not already installed):**

If you get "Python was not found" error, you need to install Python:

**Option A: Install from Microsoft Store (Recommended):**
```powershell
# Open Microsoft Store and search for "Python 3.11" or "Python 3.12"
# Or run this command to open the store directly:
start ms-windows-store://pdp/?productid=9NRWMJP3717K
```

**Option B: Download from Python.org:**
1. Go to https://python.org/downloads/
2. Download Python 3.11 or 3.12
3. Run installer with "Add Python to PATH" checked

**Option C: Use Windows Package Manager:**
```powershell
# Install Python via winget
winget install Python.Python.3.11
```

**Verify Python Installation:**
```powershell
# Test these commands (try each one):
python --version
py --version
python3 --version

# If none work, restart PowerShell after installation
```

1. **Install Dependencies:**
```powershell
# Navigate to project directory
cd "c:\Users\zetianyu\source\repos\fun\pdf-news-detector"

# Install Python dependencies
pip install -r requirements.txt
```

2. **Azure Authentication:**
   - The project uses **Azure Managed Identity** (no API keys needed)
   - Ensure you're logged into Azure CLI: `az login`
   - Or configure Azure credentials in your environment

3. **Environment Variables** (Optional - has defaults):
```powershell
# Set these if you want to override defaults
$env:AZURE_OPENAI_ENDPOINT = "https://zetianyu-hackathon.openai.azure.com/"
$env:AZURE_OPENAI_VISION_DEPLOYMENT_NAME = "gpt-4.1"
$env:AZURE_STORAGE_ACCOUNT_NAME = "zetianyuhackathonsa"
$env:AZURE_STORAGE_CONTAINER_NAME = "screenshot"
```

### **Option 1: CLI Mode (Command Line)**

**List Available Screenshots:**
```powershell
# First, navigate to the project directory
cd "c:\Users\zetianyu\source\repos\fun\pdf-news-detector"

# Then list available screenshots:
py src/main.py --list-available

# Alternative commands if py doesn't work:
# python src/main.py --list-available
# python3 src/main.py --list-available
```

**Process Specific Screenshots:**
```powershell
# Navigate to the project directory
cd "c:\Users\zetianyu\source\repos\fun\pdf-news-detector"

# Single screenshot
py src/main.py --screenshots "screenshot1.jpg"

# Multiple screenshots  
py src/main.py --screenshots "image1.png" "image2.jpg" "news_post.webp"
```

**Example Output:**
```
[INFO] Starting analysis of 1 screenshot(s)...
Processing screenshot: breaking_news.jpg
Extracting content using OCR...
Extracted text length: 245
Detected 2 image region(s)
Analyzing text credibility...
Analyzing image authenticity...
Analyzing text-image consistency...
Generating analysis report...
[SUCCESS] Analysis completed for breaking_news.jpg
Final Score: 72.4
Verdict: CREDIBLE
```

### **Option 2: Web Mode (Recommended)**

**Start the Web Server:**
```powershell
# Method 1: Using the custom launcher (Recommended)
py run_web.py

# Method 2: Alternative direct command
py -m uvicorn src.web.app:app --host 0.0.0.0 --port 8001 --reload
```

**Access the Web Interface:**
- Open browser to: `http://localhost:8001`
- Upload screenshots via drag-and-drop interface
- View real-time analysis progress
- See detailed results with visualizations

**✅ Server Status**: When running correctly, you should see:
```
🚀 Starting Screenshot News Analyzer Web Interface...
🌐 Starting server on http://localhost:8001
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**Web Features:**
- ✅ Drag & drop file upload
- ✅ Real-time progress updates
- ✅ Visual credibility scores  
- ✅ Detailed analysis breakdown
- ✅ Mobile-responsive design

---

## **How to Test the Project**

### **1. System Health Check**
```powershell
# Navigate to the project directory
cd "c:\Users\zetianyu\source\repos\fun\pdf-news-detector"

# Run the built-in test utility
python test_screenshot_system.py
```

**Expected Output:**
```
🧪 Testing Screenshot Analysis System...
✅ All modules imported successfully
🗄️ Testing Storage Configuration...
✅ Found X screenshot(s) in 'screenshot' container
⚙️ Testing Environment Configuration...
✅ Azure OpenAI endpoint: https://zetianyu-hackathon.openai.azure.com/
✅ Vision deployment: gpt-4.1
🖼️ Testing Screenshot Validation...
✅ Screenshot analysis system ready!
```

### **2. Web Interface Testing**

**Start Web Server:**
```powershell
cd src
uvicorn web.app:app --port 8001 --reload
```

**Test Endpoints:**
```powershell
# Health check
curl http://localhost:8000/health

# Configuration check  
curl http://localhost:8000/api/config
```

**Manual Web Testing:**
1. Go to `http://localhost:8000`
2. Upload a test image (JPG/PNG/WEBP)
3. Watch progress updates
4. Verify results display

### **3. API Testing with Sample Files**

**Test Upload API:**
```powershell
# Upload a file via API
curl -X POST "http://localhost:8000/api/upload" -F "file=@test_image.jpg"
```

**Check Job Status:**
```powershell
# Replace JOB_ID with actual ID from upload response
curl http://localhost:8000/api/status/JOB_ID
```

### **4. End-to-End Analysis Testing**

**Create Test Screenshots:**
```powershell
# You can test with any news screenshot images:
# - Social media posts (Twitter, Facebook, Instagram)
# - News website screenshots  
# - Mobile app screenshots
# Supported formats: .jpg, .jpeg, .png, .webp, .bmp, .tiff
```

**Test CLI Analysis:**
```powershell
# First, list what's available
python src/main.py --list-available

# Then process a test file
python src/main.py --screenshots "your_test_image.jpg"
```

### **5. Error Handling Testing**

**Test Invalid Files:**
```powershell
# Test with non-existent file
python src/main.py --screenshots "nonexistent.jpg"

# Test with invalid file type via web interface
# Upload a .txt file and verify proper error message
```

**Test Azure Connection Issues:**
```powershell
# Temporarily set invalid endpoint to test error handling
$env:AZURE_OPENAI_ENDPOINT = "invalid"
python test_screenshot_system.py
```

---

## **Expected Results & Outputs**

### **CLI Mode Results:**
- **Console Output**: Real-time processing status
- **Azure Storage**: JSON reports uploaded to 'report' container
- **Analysis Scores**: Text credibility, image authenticity, consistency scores
- **Final Verdict**: HIGHLY_CREDIBLE, CREDIBLE, QUESTIONABLE, UNRELIABLE, etc.

### **Web Mode Results:**
- **Visual Dashboard**: Color-coded credibility scores
- **Progress Updates**: Real-time status during analysis
- **Detailed Breakdown**: Text analysis, image analysis, consistency check
- **JSON Export**: Full analysis report available for download

### **Sample Analysis Report:**
```json
{
  "screenshot_name": "news_post.jpg",
  "final_score": 78.5,
  "verdict": "CREDIBLE",
  "score_breakdown": {
    "text_score": 82.0,
    "image_score": 71.0, 
    "consistency_score": 80.0
  },
  "detailed_analysis": {
    "text_analysis": {
      "red_flags": ["Emotional language detected"],
      "positive_indicators": ["Sources cited", "Factual claims"]
    },
    "image_analysis": {
      "verdict": "AUTHENTIC",
      "red_flags": []
    }
  }
}
```

---

## **Troubleshooting**

### **Python Installation Issues:**

**Problem: "Python was not found" error**
```powershell
# Solutions (try in order):

# 1. Try different Python commands:
python --version
py --version  
python3 --version

# 2. Install Python from Microsoft Store:
start ms-windows-store://pdp/?productid=9NRWMJP3717K

# 3. Or download from python.org:
# Visit https://python.org/downloads/ and install Python 3.11+

# 4. Add Python to PATH (if manually installed):
# During installation, check "Add Python to PATH"
# Or manually add: C:\Python311\Scripts\ and C:\Python311\

# 5. Use py launcher (usually works):
py -m pip install -r requirements.txt
py src/main.py --list-available
```

### **Common Issues:**

1. **Import Errors**: 
   ```powershell
   # Ensure all dependencies installed
   pip install -r requirements.txt
   ```

2. **Azure Auth Issues**: 
   ```powershell
   # Login to Azure
   az login
   ```

3. **Port Conflicts**: 
   ```powershell
   # Change port
   uvicorn web.app:app --port 8080
   ```

4. **No Screenshots Found**: 
   - Upload test images to Azure Storage 'screenshot' container

5. **Web Interface Not Loading**: 
   - Check firewall settings
   - Try `http://127.0.0.1:8000`

### **Debug Mode:**
```powershell
# Enable verbose logging
$env:LOG_LEVEL = "DEBUG"
uvicorn web.app:app --log-level debug
```

---

## **Quick Start Commands**

### **For CLI Testing:**
```powershell
# 1. Navigate to project directory
cd "c:\Users\zetianyu\source\repos\fun\pdf-news-detector"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test system
python test_screenshot_system.py

# 4. List available screenshots
python src/main.py --list-available

# 5. Process a screenshot
python src/main.py --screenshots "your_image.jpg"
```

### **For Web Testing:**
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start web server
cd src
uvicorn web.app:app --port 8000 --reload

# 3. Open browser to http://localhost:8000
# 4. Upload and test screenshots
```

---

## **API Endpoints Reference**

### **Web Interface:**
- `GET /` - Upload interface
- `GET /results/{job_id}` - Results page

### **API Endpoints:**
- `GET /health` - Health check
- `GET /api/config` - Configuration info
- `POST /api/upload` - Upload screenshot
- `GET /api/status/{job_id}` - Job status
- `GET /api/results/{job_id}` - Analysis results

---

## **File Format Support**

**Supported Image Formats:**
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.webp` - WebP images
- `.bmp` - Bitmap images
- `.tiff` - TIFF images

**File Size Limits:**
- Maximum: 10MB per file
- Minimum: 1KB (to ensure valid image data)

---

## **Azure Configuration**

### **Required Azure Resources:**
1. **Azure OpenAI Service** with GPT-4.1 Vision deployment
2. **Azure Storage Account** with blob containers:
   - `screenshot` - Input images
   - `report` - Generated analysis reports

### **Authentication:**
- Uses **Azure Managed Identity** (recommended)
- Or Azure CLI authentication (`az login`)
- No API keys required in code

---

This project is production-ready with both CLI and web interfaces, comprehensive error handling, and Azure cloud integration. The web interface is particularly user-friendly for non-technical users to analyze news screenshot credibility.