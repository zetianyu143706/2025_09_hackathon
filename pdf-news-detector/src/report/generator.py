import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple
from azure_utils.storage import AzureStorageService

def generate_report(
    image_score: float, 
    text_score: float, 
    consistency_score: float,
    screenshot_name: str,
    image_details: Dict[str, Any] = None,
    text_details: Dict[str, Any] = None,
    consistency_details: Dict[str, Any] = None,
    layout_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive credibility report and uploads it to Azure Blob Storage.
    
    Args:
        image_score: Image authenticity score (0-100)
        text_score: Text credibility score (0-100)
        consistency_score: Text-image consistency score (0-100)
        screenshot_name: Name of the analyzed screenshot file
        image_details: Detailed image analysis results
        text_details: Detailed text analysis results
        consistency_details: Detailed consistency analysis results
        layout_info: Screenshot layout and source analysis
        
    Returns:
        Dict[str, Any]: The complete report data
    """
    
    # Calculate weighted final score (40% text, 35% consistency, 25% image)
    # Consistency is heavily weighted as it's crucial for detecting misleading content
    text_weight = 0.4
    consistency_weight = 0.35
    image_weight = 0.25
    
    final_score = (text_score * text_weight) + (consistency_score * consistency_weight) + (image_score * image_weight)
    
    # Determine verdict based on final score
    verdict = _get_verdict_from_score(final_score)
    
    # Create comprehensive report
    report = {
        "screenshot_name": screenshot_name,
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        "final_score": round(final_score, 1),
        "verdict": verdict,
        "input_source": {
            "type": "screenshot",
            "original_filename": screenshot_name,
            "source_type": layout_info.get("source_type", "unknown") if layout_info else "unknown",
            "platform": layout_info.get("platform", "unknown") if layout_info else "unknown",
            "layout_type": layout_info.get("layout_type", "unknown") if layout_info else "unknown"
        },
        "score_breakdown": {
            "text_score": round(text_score, 1),
            "image_score": round(image_score, 1),
            "consistency_score": round(consistency_score, 1),
            "weights": {
                "text_weight": text_weight,
                "consistency_weight": consistency_weight,
                "image_weight": image_weight
            }
        },
        "detailed_analysis": {
            "text_analysis": text_details or {"score": text_score, "source": "basic_analysis"},
            "image_analysis": image_details or {"score": image_score, "source": "basic_analysis"},
            "consistency_analysis": consistency_details or {"score": consistency_score, "source": "basic_analysis"}
        },
        "metadata": {
            "analyzer_version": "2.0",
            "analysis_method": "screenshot_ocr_hybrid",
            "layout_analysis": layout_info or {}
        }
    }
    
    # Upload report to Azure Blob Storage using existing storage service
    report_filename = _upload_report_to_blob(report, screenshot_name)
    print(f"✅ Report uploaded to Azure Blob Storage: {report_filename}")
    
    return report

def _get_verdict_from_score(score: float) -> str:
    """Maps numerical score to verdict category."""
    if score >= 80:
        return "HIGHLY_CREDIBLE"
    elif score >= 60:
        return "CREDIBLE"
    elif score >= 40:
        return "QUESTIONABLE"
    elif score >= 20:
        return "UNRELIABLE"
    else:
        return "HIGHLY_UNRELIABLE"

def _upload_report_to_blob(report: Dict[str, Any], screenshot_name: str) -> str:
    """Uploads the report to Azure Blob Storage using existing storage service.
    
    Returns:
        str: The filename of the uploaded report
    """
    
    # Use the existing Azure Storage Service
    storage_service = AzureStorageService("zetianyuhackathonsa")
    
    # Generate timestamp for unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Prepare report data
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    # Remove file extension from screenshot_name if present
    base_name = os.path.splitext(screenshot_name)[0]
    report_filename = f"{base_name}_{timestamp}_report.json"
    
    # Upload to the report container using existing method
    container_name = "report"
    storage_service.upload_blob(
        container_name=container_name,
        blob_name=report_filename,
        data=report_json,
        content_type="application/json"
    )
    
    return report_filename