import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
import base64
from typing import Tuple, Dict, Any, List

def extract_content_from_screenshot(image_bytes: bytes) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extracts text and identifies image regions from screenshots using GPT-4o Vision OCR.
    
    Parameters:
        image_bytes (bytes): The raw screenshot data as bytes
        
    Returns:
        Tuple[str, List[Dict], Dict]: (text_content, image_regions, layout_info)
            - text_content: All extracted text from the screenshot
            - image_regions: List of detected image regions with descriptions
            - layout_info: Layout analysis including source type and structure
    """
    
    if not image_bytes or len(image_bytes) < 1000:
        raise ValueError("Invalid or insufficient image data for OCR processing")
    
    try:
        # Azure OpenAI configuration
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4.1")
        
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
        
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
        
        # Convert image to base64 for API
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call Azure OpenAI Vision API for OCR
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": _get_ocr_system_prompt()
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text content and analyze the layout of this screenshot. Identify any embedded images and their locations. IMPORTANT: Return ONLY valid JSON in the exact format specified in the system prompt. The 'extracted_text' field must be a single string containing all text concatenated together, NOT an object or array."
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
            temperature=0.0,  # Zero temperature for maximum consistency
            max_tokens=2000
        )
        
        # Parse the response
        analysis_result = response.choices[0].message.content
        text_content, image_regions, layout_info = _parse_ocr_response(analysis_result)
        
        return text_content, image_regions, layout_info
        
    except openai.APIError as e:
        raise RuntimeError(f"Azure OpenAI Vision API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"OCR processing error: {str(e)}")

def _get_ocr_system_prompt() -> str:
    """Returns the system prompt for screenshot OCR and layout analysis."""
    return """You are an expert OCR and layout analysis system specializing in processing screenshots of media content including news articles, social media posts, and web content.

Analyze this screenshot and extract:

1. TEXT EXTRACTION (OCR):
   - Extract ALL readable text with high accuracy
   - Preserve text hierarchy (headlines, body, captions, metadata)
   - Include visible timestamps, usernames, and engagement metrics
   - Maintain logical reading order

2. IMAGE REGION DETECTION:
   - Identify all image areas (photos, graphics, videos, thumbnails)
   - Provide descriptions of what each image shows
   - Note image positions relative to text content
   - Distinguish between content images and UI elements

3. LAYOUT ANALYSIS:
   - Determine source type (news website, social media, mobile app, etc.)
   - Identify content structure (header, main content, sidebar, comments)
   - Analyze content hierarchy and relationships
   - Detect visible metadata (dates, sources, engagement)

4. SOURCE DETECTION:
   - Identify platform (Twitter/X, Facebook, Instagram, news site, etc.)
   - Note any visible branding or UI indicators
   - Detect mobile vs desktop layout

CRITICAL: Respond ONLY in valid JSON format. Do not include any explanations, comments, or text outside the JSON object.

The "extracted_text" field MUST be a single string containing all text, not an object or array.

Example format:
{
    "extracted_text": "Angela Eichhorst September 17, 2025 I wear orange to protect myself and to show respect for every other hunter in the field CONNECTICUT SENTINEL",
    "image_regions": [
        {
            "description": "detailed description of the image content",
            "position": "relative position (top, middle, bottom, left, right)",
            "type": "photo|graphic|video|thumbnail|icon",
            "size": "small|medium|large",
            "context": "relationship to surrounding text"
        }
    ],
    "layout_analysis": {
        "source_type": "news_website|social_media|mobile_app|browser|other",
        "platform": "twitter|facebook|instagram|news_site|unknown",
        "layout_type": "desktop|mobile|tablet",
        "content_structure": {
            "headline": "main headline if present",
            "body_text": "main content text",
            "metadata": "visible dates, sources, authors",
            "engagement": "likes, shares, comments if visible"
        }
    },
    "text_regions": [
        {
            "type": "headline|body|caption|metadata|comment",
            "content": "text content",
            "position": "location in layout"
        }
    ]
}

Focus on accuracy and completeness. Extract every piece of readable text and identify all visual content."""

def _parse_ocr_response(response_text: str) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """Parses the GPT OCR response and extracts structured data."""
    try:
        # Clean the response text to handle potential formatting issues
        cleaned_response = response_text.strip()
        
        # Parse JSON response
        analysis = json.loads(cleaned_response)
        
        # Extract text content - handle both string and object formats
        extracted_text_field = analysis.get("extracted_text", "")
        
        if isinstance(extracted_text_field, str):
            # Expected format: simple string
            text_content = extracted_text_field
        elif isinstance(extracted_text_field, dict):
            # GPT returned structured object - flatten it to string
            text_parts = []
            
            # Extract metadata
            if "metadata" in extracted_text_field:
                metadata = extracted_text_field["metadata"]
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        if value:
                            text_parts.append(str(value))
            
            # Extract body text
            if "body" in extracted_text_field:
                body = extracted_text_field["body"]
                if isinstance(body, list):
                    text_parts.extend([str(item) for item in body if item])
                elif body:
                    text_parts.append(str(body))
            
            # Extract captions
            if "caption" in extracted_text_field:
                caption = extracted_text_field["caption"]
                if isinstance(caption, list):
                    text_parts.extend([str(item) for item in caption if item])
                elif caption:
                    text_parts.append(str(caption))
            
            # Extract branding
            if "branding" in extracted_text_field:
                branding = extracted_text_field["branding"]
                if isinstance(branding, list):
                    text_parts.extend([str(item) for item in branding if item])
                elif branding:
                    text_parts.append(str(branding))
            
            # Extract other text
            if "other_text" in extracted_text_field:
                other = extracted_text_field["other_text"]
                if isinstance(other, list):
                    text_parts.extend([str(item) for item in other if item])
                elif other:
                    text_parts.append(str(other))
            
            # Join all text parts
            text_content = " ".join(text_parts) if text_parts else ""
        else:
            # Fallback: convert whatever we got to string
            text_content = str(extracted_text_field)
        
        # Extract image regions
        image_regions = analysis.get("image_regions", [])
        
        # Extract layout information
        layout_info = {
            "source_type": analysis.get("layout_analysis", {}).get("source_type", "unknown"),
            "platform": analysis.get("layout_analysis", {}).get("platform", "unknown"),
            "layout_type": analysis.get("layout_analysis", {}).get("layout_type", "unknown"),
            "content_structure": analysis.get("layout_analysis", {}).get("content_structure", {}),
            "text_regions": analysis.get("text_regions", [])
        }
        
        return text_content, image_regions, layout_info
        
    except json.JSONDecodeError as e:
        # Provide more detailed error information
        error_msg = f"Failed to parse OCR response as JSON: {str(e)}"
        print(f"DEBUG: JSON Parse Error - {error_msg}")
        print(f"DEBUG: Response text length: {len(response_text)}")
        print(f"DEBUG: First 500 chars: {response_text[:500]}")
        print(f"DEBUG: Last 500 chars: {response_text[-500:]}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error processing OCR response: {str(e)}"
        print(f"DEBUG: Processing Error - {error_msg}")
        raise ValueError(error_msg)

def validate_screenshot(image_bytes: bytes) -> bool:
    """
    Validates if the provided image is suitable for OCR processing.
    
    Parameters:
        image_bytes (bytes): Image data to validate
        
    Returns:
        bool: True if image is valid for processing
    """
    if not image_bytes:
        return False
    
    # Check minimum size (at least 1KB)
    if len(image_bytes) < 1000:
        return False
    
    # Check for common image file headers
    image_headers = [
        b'\xff\xd8\xff',  # JPEG
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'RIFF',  # WebP (contains RIFF)
        b'GIF87a',  # GIF87a
        b'GIF89a',  # GIF89a
    ]
    
    for header in image_headers:
        if image_bytes.startswith(header):
            return True
    
    return False