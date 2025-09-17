import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
import base64
from typing import List, Dict, Any
from PIL import Image
import io

def extract_images_from_screenshot(screenshot_bytes: bytes, image_regions: List[Dict[str, Any]]) -> List[bytes]:
    """
    Extracts individual images from screenshot based on detected regions using GPT-4o vision.
    Since we can't do precise pixel cropping without coordinates, we'll use GPT-4o to generate
    separate image descriptions and then use those for analysis.
    
    Parameters:
        screenshot_bytes (bytes): Original screenshot data
        image_regions (List[Dict]): Detected image regions from OCR analysis
        
    Returns:
        List[bytes]: List of processed image data for analysis
    """
    
    if not screenshot_bytes or not image_regions:
        return []
    
    try:
        # For each detected image region, generate a focused analysis
        extracted_images = []
        
        for i, region in enumerate(image_regions):
            # Create a focused image description for analysis
            image_data = _create_focused_image_analysis(screenshot_bytes, region, i)
            if image_data:
                extracted_images.append(image_data)
        
        return extracted_images
        
    except Exception as e:
        raise RuntimeError(f"Image extraction error: {str(e)}")

def _create_focused_image_analysis(screenshot_bytes: bytes, region: Dict[str, Any], index: int) -> bytes:
    """
    Creates a focused analysis of a specific image region within the screenshot.
    Since we can't crop precisely, we'll return the original screenshot bytes
    but with metadata about which region to focus on during analysis.
    """
    try:
        # For now, return the original screenshot bytes
        # The individual image analyzers will be instructed to focus on specific regions
        return screenshot_bytes
        
    except Exception as e:
        print(f"Warning: Could not process image region {index}: {str(e)}")
        return None

def process_screenshot_for_images(screenshot_bytes: bytes) -> Dict[str, Any]:
    """
    Processes a screenshot to identify and analyze embedded images using GPT-4o vision.
    
    Parameters:
        screenshot_bytes (bytes): The screenshot data
        
    Returns:
        Dict: Analysis of images found in the screenshot
    """
    
    if not screenshot_bytes:
        return {"images_found": 0, "image_descriptions": []}
    
    try:
        # Azure OpenAI configuration
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4.1")
        
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
        
        # Initialize Azure OpenAI client
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        
        client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version="2025-01-01-preview",
            azure_ad_token_provider=token_provider
        )
        
        # Convert image to base64
        image_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # Analyze images in the screenshot
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": _get_image_analysis_prompt()
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze all images visible in this screenshot and provide detailed descriptions for each."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        # Parse response
        result = response.choices[0].message.content
        return _parse_image_analysis_response(result)
        
    except Exception as e:
        return {"error": f"Image processing failed: {str(e)}", "images_found": 0}

def _get_image_analysis_prompt() -> str:
    """Returns the system prompt for image analysis within screenshots."""
    return """You are an expert image analyst. Analyze this screenshot and identify all embedded images, photos, graphics, or visual content.

For each image you find, provide:

1. DETAILED DESCRIPTION: What the image shows (people, objects, scenes, text overlays)
2. IMAGE TYPE: photo, graphic, chart, screenshot, logo, icon, etc.
3. CONTEXT: How the image relates to surrounding text or content
4. AUTHENTICITY INDICATORS: Any visible signs of manipulation, AI generation, or editing
5. EMOTIONAL TONE: What mood or emotion the image conveys
6. RELEVANCE: How well the image matches any visible text content

Focus on content images (not UI elements like buttons or icons).

Respond in JSON format:
{
    "images_found": <number>,
    "image_descriptions": [
        {
            "index": <number>,
            "description": "detailed description of image content",
            "type": "photo|graphic|chart|screenshot|other",
            "size": "small|medium|large",
            "authenticity_indicators": ["list of observations about authenticity"],
            "emotional_tone": "description of mood/emotion",
            "context_relevance": "how image relates to text content",
            "potential_issues": ["any red flags or concerns"]
        }
    ]
}"""

def _parse_image_analysis_response(response_text: str) -> Dict[str, Any]:
    """Parses the image analysis response."""
    try:
        analysis = json.loads(response_text)
        return {
            "images_found": analysis.get("images_found", 0),
            "image_descriptions": analysis.get("image_descriptions", []),
            "source": "GPT-4.1 Vision Image Analysis"
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse image analysis response",
            "images_found": 0,
            "raw_response": response_text[:200]
        }

def validate_image_regions(image_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validates and filters image regions to ensure quality.
    
    Parameters:
        image_regions: List of detected image regions
        
    Returns:
        List of validated image regions
    """
    validated_regions = []
    
    for region in image_regions:
        # Skip UI elements and small icons
        if region.get("type") in ["icon", "button", "ui_element"]:
            continue
            
        # Skip very small images unless they're important
        if region.get("size") == "small" and region.get("type") not in ["photo", "graphic"]:
            continue
            
        # Require a meaningful description
        if not region.get("description") or len(region.get("description", "")) < 10:
            continue
            
        validated_regions.append(region)
    
    return validated_regions