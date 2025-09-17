from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os

class AzureStorageService:
    def __init__(self, storage_account_name):
        """Initialize Azure Storage Service with AAD authentication"""
        self.storage_account_name = storage_account_name
        credential = DefaultAzureCredential()
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        self.blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    
    def find_image_files(self, container_name):
        """Find all image files in the specified container"""
        container_client = self.blob_service_client.get_container_client(container_name)
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
        image_blobs = [
            blob.name for blob in container_client.list_blobs() 
            if any(blob.name.lower().endswith(ext) for ext in image_extensions)
        ]
        return image_blobs
    
    def blob_exists(self, container_name, blob_name):
        """Check if a specific blob exists in the container"""
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False
    
    def validate_image_files(self, container_name, file_names):
        """Validate which image files exist in the container from a given list
        
        Args:
            container_name (str): Name of the container
            file_names (list): List of file names to validate
            
        Returns:
            tuple: (existing_files, missing_files)
        """
        existing_files = []
        missing_files = []
        
        for file_name in file_names:
            if self.blob_exists(container_name, file_name):
                existing_files.append(file_name)
            else:
                missing_files.append(file_name)
        
        return existing_files, missing_files
    
    def download_image_blob(self, container_name, blob_name, local_path):
        """Download an image blob from Azure Storage to local path"""
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
    
    def upload_blob(self, container_name, blob_name, data, content_type="application/octet-stream"):
        """Upload data to a blob in Azure Storage"""
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Handle both string and bytes data
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        blob_client.upload_blob(
            data=data,
            overwrite=True,
            content_type=content_type
        )
    
    def list_all_blobs(self, container_name):
        """List all blobs in the specified container"""
        container_client = self.blob_service_client.get_container_client(container_name)
        return [blob.name for blob in container_client.list_blobs()]