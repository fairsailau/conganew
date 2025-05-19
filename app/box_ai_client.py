"""
Box AI API client for template conversion
"""
import requests
from typing import Dict, List, Any, Optional, Union


class BoxAIClient:
    """
    Client for interacting with Box AI API
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the Box AI client
        
        Args:
            access_token: Box API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.box.com/2.0"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
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
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()
        
    def generate_text(self, prompt: str, content: Optional[str] = None, 
                     file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text using Box AI
        
        Args:
            prompt: The prompt for text generation
            content: Text content for context (optional)
            file_id: Box file ID for context (optional)
            
        Returns:
            Dictionary containing the generated text
        """
        endpoint = f"{self.base_url}/ai/text_gen"
        
        payload = {
            "prompt": prompt
        }
        
        if file_id:
            payload["items"] = [{"id": file_id, "type": "file"}]
        elif content:
            payload["items"] = [{"id": "temp", "type": "file", "content": content}]
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
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
        """
        endpoint = f"{self.base_url}/ai/extract_structured"
        
        payload = {
            "items": [{"id": "temp", "type": "file", "content": content}],
            "fields": fields
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()
