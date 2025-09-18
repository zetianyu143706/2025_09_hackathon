"""
Shared dependencies for the web application
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from src
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from azure_utils.storage import AzureStorageService
from config import config


def get_storage_service() -> AzureStorageService:
    """Get configured Azure Storage Service instance"""
    return AzureStorageService(config.AZURE_STORAGE_ACCOUNT_NAME)


def get_container_name() -> str:
    """Get the configured container name"""
    return config.AZURE_STORAGE_CONTAINER_NAME