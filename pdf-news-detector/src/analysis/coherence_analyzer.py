import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
import base64
from typing import Tuple, Dict, Any, List

def analyze_coherence(text: str, image_bytes_list: List[bytes]) -> Tuple[float, Dict[str, Any]]:
    """
    Analyzes the coherence between text content and images to detect mismatched or misleading combinations.
    This is crucial for fake news detection where images might be unrelated to the text content.
    
    Parameters:
        text (str): The extracted text content from the PDF
        image_bytes_list (List[bytes]): List of raw image data as bytes
        
    Returns:
        Tuple[float, Dict[str, Any]]: (coherence_score, detailed_analysis)
            - coherence_score: 0-100 score (higher = more coherent/consistent)
            - detailed_analysis: Dictionary with breakdown and explanations
    """
    
    # Validate inputs
    if not text or len(text.strip()) < 50:
        return 0.0, {
            "error": "Insufficient text content for coherence analysis",
            "text_length": len(text.strip()) if text else 0
        }
    
    if not image_bytes_list or len(image_bytes_list) == 0:
        return 50.0, {
            "warning": "No images provided for coherence analysis",
            "text_only_analysis": True,
            "coherence_score": 50.0
        }
    
    # Limit to first 3 images for API efficiency
    images_to_analyze = image_bytes_list[:3]
    
    try:
        # Azure OpenAI configuration - reuse the vision deployment (GPT-4o)
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_VISION_DEPLOYMENT_NAME", "gpt-4o")
        
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
                "text": f"""Analyze the coherence between this text content and the accompanying images. 
                
TEXT CONTENT:
{text[:2000]}  # Limit text for API efficiency

Please evaluate if the images are relevant, consistent, and appropriately support the text content."""
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
                    "content": _get_coherence_system_prompt()
                },
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            temperature=0.2,  # Lower temperature for consistent analysis
            max_tokens=1200
        )
        
        # Parse the response
        analysis_result = response.choices[0].message.content
        coherence_score, detailed_analysis = _parse_coherence_response(analysis_result)
        
        # Add metadata
        detailed_analysis["images_analyzed"] = len(images_to_analyze)
        detailed_analysis["total_images_available"] = len(image_bytes_list)
        detailed_analysis["text_length"] = len(text)
        
        return coherence_score, detailed_analysis
        
    except openai.APIError as e:
        return 0.0, {
            "error": f"Azure OpenAI Vision API error: {str(e)}",
            "type": "api_error"
        }
    except Exception as e:
        return 0.0, {
            "error": f"Unexpected error in coherence analysis: {str(e)}",
            "type": "general_error"
        }

def _get_coherence_system_prompt() -> str:
    """Returns the system prompt for text-image coherence analysis."""
    return """You are an expert media analyst specializing in detecting misleading or fake news through text-image coherence analysis.

Analyze the relationship between the text content and accompanying images for:

1. CONTENT_RELEVANCE (0-100): How relevant are the images to the text content?
2. FACTUAL_CONSISTENCY (0-100): Do the images support or contradict the textual claims?
3. CONTEXTUAL_APPROPRIATENESS (0-100): Are the images used in appropriate context?
4. TEMPORAL_CONSISTENCY (0-100): Do image timestamps/context match the text timeline?
5. EMOTIONAL_ALIGNMENT (0-100): Does the emotional tone of images match the text?

Common red flags to detect:
- Stock photos used as if they were from the specific event
- Images from different time periods or locations
- Manipulated captions or misleading context
- Images that contradict the textual narrative
- Emotional manipulation through unrelated imagery

Respond ONLY in valid JSON format:
{
    "overall_score": <0-100>,
    "breakdown": {
        "content_relevance": {"score": <0-100>, "reasoning": "specific observations"},
        "factual_consistency": {"score": <0-100>, "reasoning": "specific observations"},
        "contextual_appropriateness": {"score": <0-100>, "reasoning": "specific observations"},
        "temporal_consistency": {"score": <0-100>, "reasoning": "specific observations"},
        "emotional_alignment": {"score": <0-100>, "reasoning": "specific observations"}
    },
    "coherence_issues": ["list of specific coherence problems found"],
    "positive_indicators": ["list of elements showing good text-image alignment"],
    "verdict": "one of: HIGHLY_COHERENT, COHERENT, SOMEWHAT_COHERENT, INCOHERENT, HIGHLY_MISLEADING",
    "risk_assessment": "assessment of potential misinformation risk based on coherence analysis"
}

Note: Higher scores indicate better coherence between text and images. Lower scores suggest potential misinformation or misleading content."""

def _parse_coherence_response(response_text: str) -> Tuple[float, Dict[str, Any]]:
    """Parses the GPT response and extracts coherence score and detailed analysis."""
    try:
        # Try to parse as JSON
        analysis = json.loads(response_text)
        
        # Extract overall score
        overall_score = float(analysis.get("overall_score", 50))
        
        # Prepare detailed analysis
        detailed_analysis = {
            "overall_score": overall_score,
            "breakdown": analysis.get("breakdown", {}),
            "coherence_issues": analysis.get("coherence_issues", []),
            "positive_indicators": analysis.get("positive_indicators", []),
            "verdict": analysis.get("verdict", "UNKNOWN"),
            "risk_assessment": analysis.get("risk_assessment", "Unable to assess"),
            "source": "Azure OpenAI Vision coherence analysis"
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
                "source": "Azure OpenAI Vision coherence analysis (parsing error)"
            }
        except:
            return 0.0, {
                "error": "Complete parsing failure",
                "raw_response": response_text[:200],
                "source": "Azure OpenAI Vision coherence analysis (critical error)"
            }

def analyze_single_image_coherence(text: str, image_bytes: bytes) -> Tuple[float, Dict[str, Any]]:
    """
    Convenience function to analyze coherence between text and a single image.
    
    Parameters:
        text (str): The text content
        image_bytes (bytes): Single image data
        
    Returns:
        Tuple[float, Dict[str, Any]]: (coherence_score, detailed_analysis)
    """
    return analyze_coherence(text, [image_bytes])