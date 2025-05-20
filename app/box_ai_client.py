"""
Box AI API client for template conversion
"""
import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from boxsdk import Client
from boxsdk.exception import BoxAPIException

try:
    # For production
    from .auth import BoxAuthError, load_auth_config, BoxAuthenticator, AuthMethod
except ImportError:
    # For development
    from auth import BoxAuthError, load_auth_config, BoxAuthenticator, AuthMethod


class BoxAIClient:
    """
    Client for interacting with Box AI API
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Box AI client with authentication
        
        Args:
            config: Optional configuration dictionary or path to config file.
                   If None, will try to load from default location.
        """
        self.client = self._get_authenticated_client(config)
        self.base_url = "https://api.box.com/2.0"
    
    def _get_authenticated_client(self, config: Optional[Dict[str, Any]] = None) -> Client:
        """
        Get an authenticated Box client
        
        Args:
            config: Optional configuration dictionary or path to config file
            
        Returns:
            Authenticated Box Client
        """
        from .auth import get_authenticated_client
        try:
            return get_authenticated_client(config)
        except BoxAuthError as e:
            raise BoxAuthError(f"Failed to authenticate with Box: {str(e)}")
        
    def ask_ai(self, prompt: str, content: Optional[str] = None, 
               file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask Box AI a question about content or a file
        
        Args:
            prompt: The question to ask
            content: Text content to analyze (optional)
            file_id: Box file ID to analyze (optional)
            
        Returns:
            Dictionary containing the AI response
            
        Raises:
            BoxAPIException: If the API request fails
        """
        endpoint = f"{self.base_url}/ai/ask"
        
        payload = {
            "mode": "single_item_qa",
            "prompt": prompt
        }
        
        if file_id:
            payload["items"] = [{"id": file_id, "type": "file"}]
        elif content:
            payload["items"] = [{"id": "temp", "type": "file", "content": content}]
        
        response = self.client.make_request(
            'POST',
            endpoint,
            data=payload
        )
        return response.json()
        
    def generate_text(self, prompt: str, content: Optional[str] = None, 
                     file_id: Optional[str] = None,
                     system_prompt: Optional[str] = None,
                     max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Generate text using Box AI
        
        Args:
            prompt: The prompt for text generation
            content: Text content for context (optional)
            file_id: Box file ID for context (optional)
            system_prompt: System prompt to guide the AI (optional)
            max_tokens: Maximum number of tokens to generate (default: 2048)
            
        Returns:
            Dictionary containing the generated text
            
        Raises:
            BoxAPIException: If the API request fails
        """
        endpoint = f"{self.base_url}/ai/text_gen"
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        if file_id:
            payload["items"] = [{"id": file_id, "type": "file"}]
        elif content:
            payload["items"] = [{"id": "temp", "type": "file", "content": content}]
        
        response = self.client.make_request(
            'POST',
            endpoint,
            data=payload
        )
        return response.json()
        
    def extract_structured_metadata(self, content: str, 
                                   fields: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract structured metadata from content
        
        Args:
            content: Text content to extract metadata from
            fields: List of fields to extract
            
        Returns:
            Dictionary containing the extracted metadata
            
        Raises:
            BoxAPIException: If the API request fails
        """
        endpoint = f"{self.base_url}/ai/extract_structured"
        
        payload = {
            "items": [{"id": "temp", "type": "file", "content": content}],
            "fields": fields
        }
        
        response = self.client.make_request(
            'POST',
            endpoint,
            data=payload
        )
        return response.json()
    
    def get_file_content(self, file_id: str) -> str:
        """
        Get the content of a file from Box
        
        Args:
            file_id: The Box file ID
            
        Returns:
            File content as string
            
        Raises:
            BoxAPIException: If the file cannot be accessed
        """
        file_content = self.client.file(file_id).content()
        return file_content.decode('utf-8')
    
    def upload_file(self, file_path: str, folder_id: str = '0') -> Dict[str, Any]:
        """
        Upload a file to Box
        
        Args:
            file_path: Path to the local file to upload
            folder_id: ID of the target folder (default: root)
            
        Returns:
            Dictionary containing file metadata
            
        Raises:
            BoxAPIException: If the upload fails
        """
        folder = self.client.folder(folder_id)
        file_obj = folder.upload(file_path)
        return file_obj.response_object
