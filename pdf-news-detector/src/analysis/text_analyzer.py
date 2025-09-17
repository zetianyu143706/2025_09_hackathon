import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json
from typing import Tuple, Dict, Any
from config import config

def analyze_text(text: str) -> Tuple[float, Dict[str, Any]]:
    """
    Analyzes the credibility of news text using Azure OpenAI Service.
    
    Args:
        text (str): The extracted text content from the PDF
        
    Returns:
        Tuple[float, Dict[str, Any]]: (credibility_score, detailed_reasons)
            - credibility_score: 0-100 score (higher = more credible)
            - detailed_reasons: Dictionary with breakdown and explanations
    """
    
    # Check if text is empty or too short
    if not text or len(text.strip()) < 50:
        return 0.0, {
            "error": "Insufficient text content for analysis",
            "text_length": len(text.strip()) if text else 0
        }
    
    try:
        # Azure OpenAI configuration from centralized config
        azure_endpoint = config.AZURE_OPENAI_ENDPOINT
        deployment_name = config.AZURE_OPENAI_VISION_DEPLOYMENT_NAME
        
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
        
        # Construct the analysis prompt
        prompt = _create_analysis_prompt(text)
        
        # Call Azure OpenAI API
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": _get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500
        )
        
        # Parse the response
        analysis_result = response.choices[0].message.content
        credibility_score, detailed_reasons = _parse_gpt_response(analysis_result)
        
        return credibility_score, detailed_reasons
        
    except openai.APIError as e:
        return 0.0, {
            "error": f"Azure OpenAI API error: {str(e)}",
            "type": "api_error"
        }
    except Exception as e:
        return 0.0, {
            "error": f"Unexpected error: {str(e)}",
            "type": "general_error"
        }

def _get_system_prompt() -> str:
    """Returns the system prompt for the credibility analysis."""
    return """You are an expert fact-checker and media literacy analyst. Your job is to evaluate the credibility of news content.

Analyze the text for:
1. FACTUAL_ACCURACY (0-100): How plausible and fact-based are the claims?
2. BIAS_NEUTRALITY (0-100): How neutral and objective is the reporting?
3. SOURCE_CREDIBILITY (0-100): Are sources mentioned? Are they credible?
4. LOGICAL_CONSISTENCY (0-100): Are arguments logical and consistent?
5. EMOTIONAL_MANIPULATION (0-100): Absence of emotional manipulation (higher = less manipulative)

Respond ONLY in valid JSON format:
{
    "overall_score": <0-100>,
    "breakdown": {
        "factual_accuracy": {"score": <0-100>, "reasoning": "explanation"},
        "bias_neutrality": {"score": <0-100>, "reasoning": "explanation"},
        "source_credibility": {"score": <0-100>, "reasoning": "explanation"},
        "logical_consistency": {"score": <0-100>, "reasoning": "explanation"},
        "emotional_manipulation": {"score": <0-100>, "reasoning": "explanation"}
    },
    "red_flags": ["list of concerning elements"],
    "positive_indicators": ["list of credible elements"],
    "verdict": "one of: HIGHLY_CREDIBLE, CREDIBLE, QUESTIONABLE, UNRELIABLE, HIGHLY_UNRELIABLE"
}"""

def _create_analysis_prompt(text: str) -> str:
    """Creates the analysis prompt with the text content."""
    return f"""Analyze the following news text for credibility:

TEXT TO ANALYZE:
---
{text}
---

Please evaluate this text according to the criteria specified in your system prompt and respond in the required JSON format."""

def _parse_gpt_response(response_text: str) -> Tuple[float, Dict[str, Any]]:
    """Parses the GPT response and extracts score and detailed reasons."""
    try:
        # Try to parse as JSON
        analysis = json.loads(response_text)
        
        # Extract overall score
        overall_score = float(analysis.get("overall_score", 0))
        
        # Prepare detailed reasons
        detailed_reasons = {
            "overall_score": overall_score,
            "breakdown": analysis.get("breakdown", {}),
            "red_flags": analysis.get("red_flags", []),
            "positive_indicators": analysis.get("positive_indicators", []),
            "verdict": analysis.get("verdict", "UNKNOWN"),
            "source": "Azure OpenAI GPT-4.1 analysis"
        }
        
        return overall_score, detailed_reasons
        
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
                "source": "Azure OpenAI GPT-4.1 analysis (parsing error)"
            }
        except:
            return 0.0, {
                "error": "Complete parsing failure",
                "raw_response": response_text[:200],
                "source": "Azure OpenAI GPT-4.1 analysis (critical error)"
            }