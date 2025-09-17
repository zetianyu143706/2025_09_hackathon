import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple
from azure_utils.storage import AzureStorageService

def generate_report(
    image_score: float, 
    text_score: float, 
    pdf_name: str,
    image_details: Dict[str, Any] = None,
    text_details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generates a comprehensive credibility report and uploads it to Azure Blob Storage.
    
    Args:
        image_score: Image authenticity score (0-100)
        text_score: Text credibility score (0-100)
        pdf_name: Name of the analyzed PDF file
        image_details: Detailed image analysis results
        text_details: Detailed text analysis results
        
    Returns:
        Dict[str, Any]: The complete report data
    """
    
    # Calculate weighted final score (60% text, 40% image)
    # Text is weighted higher as it's often more reliable for fake news detection
    text_weight = 0.6
    image_weight = 0.4
    
    final_score = (text_score * text_weight) + (image_score * image_weight)
    
    # Determine verdict based on final score
    verdict = _get_verdict_from_score(final_score)
    
    # Create comprehensive report
    report = {
        "pdf_name": pdf_name,
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        "final_score": round(final_score, 1),
        "verdict": verdict,
        "score_breakdown": {
            "text_score": round(text_score, 1),
            "image_score": round(image_score, 1),
            "weights": {
                "text_weight": text_weight,
                "image_weight": image_weight
            }
        },
        "detailed_analysis": {
            "text_analysis": text_details or {"score": text_score, "source": "basic_analysis"},
            "image_analysis": image_details or {"score": image_score, "source": "basic_analysis"}
        },
        "metadata": {
            "analyzer_version": "1.0",
            "analysis_method": "azure_openai_hybrid"
        }
    }
    
    # Upload report to Azure Blob Storage using existing storage service
    _upload_report_to_blob(report, pdf_name)
    print(f"✅ Report uploaded to Azure Blob Storage: {pdf_name}_report.json")
    
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

def _upload_report_to_blob(report: Dict[str, Any], pdf_name: str) -> None:
    """Uploads the report to Azure Blob Storage using existing storage service."""
    
    # Use the existing Azure Storage Service
    storage_service = AzureStorageService("zetianyuhackathonsa")
    
    # Prepare report data
    report_json = json.dumps(report, indent=2, ensure_ascii=False)
    report_filename = f"{pdf_name}_report.json"
    
    # Upload to the report container using existing method
    container_name = "report"
    storage_service.upload_blob(
        container_name=container_name,
        blob_name=report_filename,
        data=report_json,
        content_type="application/json"
    )