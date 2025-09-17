import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
import base64
from typing import Tuple, Dict, Any, List

def analyze_consistency(text: str, image_bytes_list: List[bytes]) -> Tuple[float, Dict[str, Any]]:
    """
    Analyzes the consistency between text content and images to detect mismatched or misleading combinations.
    This focuses specifically on entity-object alignment, action-event alignment, and contextual contradictions.
    
    Parameters:
        text (str): The extracted text content from the PDF
        image_bytes_list (List[bytes]): List of raw image data as bytes
        
    Returns:
        Tuple[float, Dict[str, Any]]: (consistency_score, detailed_analysis)
            - consistency_score: 0-100 score (higher = more consistent)
            - detailed_analysis: Dictionary with breakdown and explanations
    """
    
    # Validate inputs
    if not text or len(text.strip()) < 50:
        return 0.0, {
            "error": "Insufficient text content for consistency analysis",
            "text_length": len(text.strip()) if text else 0
        }
    
    if not image_bytes_list or len(image_bytes_list) == 0:
        return 50.0, {
            "warning": "No images provided for consistency analysis",
            "text_only_analysis": True,
            "consistency_score": 50.0
        }
    
    # Limit to first 2 images for API efficiency and focus
    images_to_analyze = image_bytes_list[:2]
    
    try:
        # Azure OpenAI configuration - use GPT-4.1 vision deployment
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4.1")  # Updated to use new deployment
        
        if not azure_endpoint:
            return 0.0, {
                "error": "AZURE_OPENAI_ENDPOINT environment variable not set",
                "type": "configuration_error"
            }
        
        # Initialize Azure OpenAI client with AAD authentication
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        
        client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version="2025-01-01-preview",
            azure_ad_token_provider=token_provider
        )
        
        # Prepare message content with text and images
        message_content = [
            {
                "type": "text",
                "text": f"""Analyze the consistency between this text content and the accompanying images using the specific logic checks below:

TEXT CONTENT:
{text[:2000]}  # Limit text for API efficiency

Please perform detailed consistency analysis focusing on:
1. Entity-Object Alignment
2. Action-Event Alignment  
3. Contextual Contradiction Detection"""
            }
        ]
        
        # Add images to the message
        for i, image_bytes in enumerate(images_to_analyze):
            if image_bytes and len(image_bytes) > 100:  # Validate image data
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high"
                    }
                })
        
        # Call Azure OpenAI Vision API
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": _get_consistency_system_prompt()
                },
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            temperature=0.1,  # Very low temperature for consistent logical analysis
            max_tokens=1500
        )
        
        # Parse the response
        analysis_result = response.choices[0].message.content
        consistency_score, detailed_analysis = _parse_consistency_response(analysis_result)
        
        # Add metadata
        detailed_analysis["images_analyzed"] = len(images_to_analyze)
        detailed_analysis["total_images_available"] = len(image_bytes_list)
        detailed_analysis["text_length"] = len(text)
        
        return consistency_score, detailed_analysis
        
    except openai.APIError as e:
        return 0.0, {
            "error": f"Azure OpenAI Vision API error: {str(e)}",
            "type": "api_error"
        }
    except Exception as e:
        return 0.0, {
            "error": f"Unexpected error in consistency analysis: {str(e)}",
            "type": "general_error"
        }

def _get_consistency_system_prompt() -> str:
    """Returns the system prompt for text-image consistency analysis."""
    return """You are an expert consistency analyzer specializing in detecting mismatched text-image combinations in news content.

Perform detailed analysis using these specific logic checks:

1. ENTITY-OBJECT ALIGNMENT (0-100):
   - Detect main objects/entities in the image (e.g., plane, fire, airport, people, buildings)
   - Detect main entities mentioned in the text
   - Compare overlap and compute entity_consistency_score
   - Higher score = better alignment between text entities and image objects

2. ACTION-EVENT ALIGNMENT (0-100):
   - From text: extract verbs/actions (e.g., "landing," "crashing," "celebrating," "protesting")
   - From image: infer likely scene/action (e.g., fire + aircraft = crash scenario, crowds + signs = protest)
   - If mismatched → lower event_plausibility_score
   - Higher score = actions in text match what's happening in image

3. CONTEXTUAL CONTRADICTION DETECTION (0-100):
   - Check for direct contradictions:
     * Text says "peaceful landing" but image shows "flames"
     * Text says "daytime event" but image is clearly night
     * Text says "celebration" but image shows distress/damage
     * Text mentions specific locations that don't match image setting
   - Higher score = fewer contradictions (more consistent)

4. OVERALL CONSISTENCY (0-100):
   - Weighted average: Entity (30%) + Action (40%) + Context (30%)
   - Provide short natural language explanation summarizing key mismatches

Respond ONLY in valid JSON format:
{
    "overall_score": <0-100>,
    "breakdown": {
        "entity_consistency_score": {"score": <0-100>, "reasoning": "specific entity alignment observations"},
        "event_plausibility_score": {"score": <0-100>, "reasoning": "specific action-event alignment observations"},
        "contextual_contradiction_score": {"score": <0-100>, "reasoning": "specific contradiction findings"}
    },
    "detected_entities": {
        "text_entities": ["list of main entities from text"],
        "image_objects": ["list of main objects/entities detected in image"]
    },
    "detected_actions": {
        "text_actions": ["list of actions/verbs from text"],
        "image_scene": "description of what's happening in the image"
    },
    "contradictions_found": ["list of specific contradictions between text and image"],
    "consistency_summary": "brief explanation of key consistency issues or confirmations",
    "verdict": "one of: HIGHLY_CONSISTENT, CONSISTENT, SOMEWHAT_INCONSISTENT, INCONSISTENT, HIGHLY_CONTRADICTORY"
}

Note: Higher scores indicate better consistency. Lower scores suggest mismatched or misleading text-image combinations."""

def _parse_consistency_response(response_text: str) -> Tuple[float, Dict[str, Any]]:
    """Parses the GPT response and extracts consistency score and detailed analysis."""
    try:
        # Try to parse as JSON
        analysis = json.loads(response_text)
        
        # Extract overall score
        overall_score = float(analysis.get("overall_score", 50))
        
        # Prepare detailed analysis
        detailed_analysis = {
            "overall_score": overall_score,
            "breakdown": analysis.get("breakdown", {}),
            "detected_entities": analysis.get("detected_entities", {}),
            "detected_actions": analysis.get("detected_actions", {}),
            "contradictions_found": analysis.get("contradictions_found", []),
            "consistency_summary": analysis.get("consistency_summary", "Unable to analyze"),
            "verdict": analysis.get("verdict", "UNKNOWN"),
            "source": "Azure OpenAI GPT-4.1 Vision consistency analysis"
        }
        
        return overall_score, detailed_analysis
        
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract score manually
        try:
            # Look for score patterns in the response
            import re
            score_match = re.search(r'overall[_\s]*score["\s:]*(\d+)', response_text, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))
            else:
                score = 50.0  # Default neutral score
            
            return score, {
                "error": "Failed to parse structured response",
                "raw_response": response_text[:500],  # First 500 chars
                "extracted_score": score,
                "source": "Azure OpenAI GPT-4.1 Vision consistency analysis (parsing error)"
            }
        except:
            return 0.0, {
                "error": "Complete parsing failure",
                "raw_response": response_text[:200],
                "source": "Azure OpenAI GPT-4.1 Vision consistency analysis (critical error)"
            }

def analyze_single_image_consistency(text: str, image_bytes: bytes) -> Tuple[float, Dict[str, Any]]:
    """
    Convenience function to analyze consistency between text and a single image.
    
    Parameters:
        text (str): The text content
        image_bytes (bytes): Single image data
        
    Returns:
        Tuple[float, Dict[str, Any]]: (consistency_score, detailed_analysis)
    """
    return analyze_consistency(text, [image_bytes])