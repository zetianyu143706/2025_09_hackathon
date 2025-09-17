import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
import base64
from typing import Tuple, Dict, Any

def analyze_image(image_bytes: bytes) -> Tuple[float, Dict[str, Any]]:
    """
    Analyzes an image to determine if it is AI-generated or authentic using Azure OpenAI Vision.
    
    Parameters:
        image_bytes (bytes): The raw image data as bytes
        
    Returns:
        Tuple[float, Dict[str, Any]]: (authenticity_score, detailed_analysis)
            - authenticity_score: 0-100 score (higher = more likely authentic/real)
            - detailed_analysis: Dictionary with breakdown and explanations
    """
    
    # Check if image data is valid
    if not image_bytes or len(image_bytes) < 100:
        return 0.0, {
            "error": "Invalid or insufficient image data",
            "image_size": len(image_bytes) if image_bytes else 0
        }
    
    try:
        # Azure OpenAI configuration
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4o")  # Your existing gpt-4o deployment
        
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
        
        # Convert image to base64 for API
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call Azure OpenAI Vision API
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content": _get_vision_system_prompt()
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image for authenticity and signs of AI generation or manipulation. Focus on detecting fake news imagery."
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
            temperature=0.2,  # Lower temperature for consistent analysis
            max_tokens=1000
        )
        
        # Parse the response
        analysis_result = response.choices[0].message.content
        authenticity_score, detailed_analysis = _parse_vision_response(analysis_result)
        
        return authenticity_score, detailed_analysis
        
    except openai.APIError as e:
        return 0.0, {
            "error": f"Azure OpenAI Vision API error: {str(e)}",
            "type": "api_error"
        }
    except Exception as e:
        return 0.0, {
            "error": f"Unexpected error in image analysis: {str(e)}",
            "type": "general_error"
        }

def _get_vision_system_prompt() -> str:
    """Returns the system prompt for image authenticity analysis."""
    return """You are an expert image forensics analyst specializing in detecting AI-generated and manipulated images, particularly in the context of fake news detection.

Analyze the image for:
1. AI_GENERATION_SIGNS (0-100): Look for AI artifacts like unnatural textures, impossible geometry, inconsistent lighting
2. MANIPULATION_DETECTION (0-100): Check for photo editing, compositing, or digital alterations
3. VISUAL_CONSISTENCY (0-100): Evaluate if lighting, shadows, perspectives are physically consistent
4. CONTENT_AUTHENTICITY (0-100): Assess if the scene/content appears genuine or staged
5. TECHNICAL_QUALITY (0-100): Check for compression artifacts, unusual metadata patterns

Respond ONLY in valid JSON format:
{
    "overall_score": <0-100>,
    "breakdown": {
        "ai_generation_signs": {"score": <0-100>, "reasoning": "specific observations"},
        "manipulation_detection": {"score": <0-100>, "reasoning": "specific observations"},
        "visual_consistency": {"score": <0-100>, "reasoning": "specific observations"},
        "content_authenticity": {"score": <0-100>, "reasoning": "specific observations"},
        "technical_quality": {"score": <0-100>, "reasoning": "specific observations"}
    },
    "red_flags": ["list of suspicious elements found"],
    "authentic_indicators": ["list of elements suggesting authenticity"],
    "verdict": "one of: HIGHLY_AUTHENTIC, AUTHENTIC, QUESTIONABLE, LIKELY_FAKE, HIGHLY_SUSPICIOUS"
}

Note: Higher scores indicate MORE AUTHENTIC/REAL images. Lower scores indicate AI-generated or manipulated content."""

def _parse_vision_response(response_text: str) -> Tuple[float, Dict[str, Any]]:
    """Parses the GPT Vision response and extracts authenticity score and detailed analysis."""
    try:
        # Try to parse as JSON
        analysis = json.loads(response_text)
        
        # Extract overall score
        overall_score = float(analysis.get("overall_score", 50))
        
        # Prepare detailed analysis
        detailed_analysis = {
            "overall_score": overall_score,
            "breakdown": analysis.get("breakdown", {}),
            "red_flags": analysis.get("red_flags", []),
            "authentic_indicators": analysis.get("authentic_indicators", []),
            "verdict": analysis.get("verdict", "UNKNOWN"),
            "source": "Azure OpenAI Vision analysis"
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
                "source": "Azure OpenAI Vision analysis (parsing error)"
            }
        except:
            return 0.0, {
                "error": "Complete parsing failure",
                "raw_response": response_text[:200],
                "source": "Azure OpenAI Vision analysis (critical error)"
            }