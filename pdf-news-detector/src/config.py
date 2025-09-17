"""
Configuration module for the PDF News Detector system.
Handles environment variables and default settings.
"""
import os
from typing import Optional

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass

class Config:
    """Configuration class for the application"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv(
        "AZURE_OPENAI_ENDPOINT", 
        "https://zetianyu-hackathon.openai.azure.com/"
    )
    
    AZURE_OPENAI_VISION_DEPLOYMENT_NAME: str = os.getenv(
        "AZURE_OPENAI_VISION_DEPLOYMENT_NAME", 
        "gpt-4.1"
    )
    
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", 
        "2025-01-01-preview"
    )
    
    # Azure Storage Configuration
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv(
        "AZURE_STORAGE_ACCOUNT_NAME", 
        "zetianyuhackathonsa"
    )
    
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv(
        "AZURE_STORAGE_CONTAINER_NAME", 
        "screenshot"
    )
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.AZURE_OPENAI_ENDPOINT:
            print("❌ AZURE_OPENAI_ENDPOINT is required")
            return False
            
        if not cls.AZURE_STORAGE_ACCOUNT_NAME:
            print("❌ AZURE_STORAGE_ACCOUNT_NAME is required")
            return False
            
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)"""
        print("🔧 Current Configuration:")
        print(f"   Azure OpenAI Endpoint: {cls.AZURE_OPENAI_ENDPOINT}")
        print(f"   Vision Deployment: {cls.AZURE_OPENAI_VISION_DEPLOYMENT_NAME}")
        print(f"   API Version: {cls.AZURE_OPENAI_API_VERSION}")
        print(f"   Storage Account: {cls.AZURE_STORAGE_ACCOUNT_NAME}")
        print(f"   Container Name: {cls.AZURE_STORAGE_CONTAINER_NAME}")

# Global config instance
config = Config()