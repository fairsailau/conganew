"""
Box AI API client for template conversion
"""
import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from boxsdk import Client
from boxsdk.exception import BoxAPIException


class BoxAIClientError(Exception):
    """Base exception for Box AI client errors."""
    pass


class BoxAuthError(Exception):
    """Custom exception for Box authentication errors."""
    pass


class AuthMethod:
    """Authentication method enum."""
    JWT = 'jwt'
    OAUTH2_CCG = 'oauth2_ccg'  # Client Credentials Grant
    OAUTH2_AC = 'oauth2_ac'    # Authorization Code
    DEVELOPER_TOKEN = 'developer_token'  # Developer token for testing


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
            config: Configuration dictionary with authentication details
            
        Returns:
            Authenticated Box Client
        """
        from boxsdk import OAuth2, Client
        
        if not config:
            raise BoxAuthError("No authentication configuration provided")
            
        auth_method = config.get('auth_method')
        
        if auth_method == AuthMethod.JWT:
            from boxsdk import JWTAuth
            try:
                auth = JWTAuth.from_settings_dictionary(config)
                return Client(auth)
            except Exception as e:
                raise BoxAuthError(f"JWT authentication failed: {str(e)}")
            
        elif auth_method in [AuthMethod.OAUTH2_CCG, AuthMethod.OAUTH2_AC]:
            try:
                oauth = OAuth2(
                    client_id=config.get('clientID'),
                    client_secret=config.get('clientSecret')
                )
                
                if auth_method == AuthMethod.OAUTH2_CCG:
                    # For Client Credentials Grant
                    access_token, _ = oauth.authenticate_instance()
                    return Client(oauth)
                else:
                    # For Authorization Code Grant
                    auth_url, _ = oauth.get_authorization_url('http://localhost')
                    st.warning(f'Please visit this URL to authorize this application: {auth_url}')
                    auth_code = st.text_input('Enter the authorization code:')
                    if auth_code:
                        access_token, refresh_token = oauth.authenticate(auth_code)
                        return Client(oauth)
                    raise BoxAuthError("Authorization code is required")
            except Exception as e:
                raise BoxAuthError(f"OAuth 2.0 authentication failed: {str(e)}")
                
        elif auth_method == AuthMethod.DEVELOPER_TOKEN:
            try:
                developer_token = config.get('developerToken')
                if not developer_token:
                    raise BoxAuthError("Developer token is required")
                    
                oauth = OAuth2(
                    client_id=None,  # Not needed for developer token
                    client_secret=None,
                    access_token=developer_token
                )
                return Client(oauth)
            except Exception as e:
                raise BoxAuthError(f"Developer token authentication failed: {str(e)}")
            
        else:
            raise BoxAuthError(f"Unsupported authentication method: {auth_method}")
        
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
