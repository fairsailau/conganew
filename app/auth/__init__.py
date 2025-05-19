"""
Box Authentication Module

This module provides multiple authentication methods for Box API:
1. JWT (Server Authentication)
2. OAuth 2.0 with Client Credentials Grant
3. OAuth 2.0 with Authorization Code Grant
"""
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum
import json
from pathlib import Path

from boxsdk import JWTAuth, OAuth2, Client
from boxsdk.exception import BoxAPIException


class AuthMethod(Enum):
    """Supported authentication methods"""
    JWT = "jwt"
    OAUTH2_CCG = "oauth2_ccg"  # Client Credentials Grant
    OAUTH2_AC = "oauth2_ac"    # Authorization Code


class BoxAuthError(Exception):
    """Custom exception for authentication errors"""
    pass


class BoxAuthenticator:
    """
    Handles authentication with Box API using different methods
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the authenticator with configuration
        
        Args:
            config: Dictionary containing authentication configuration
        """
        self.config = config
        self._auth_method = self._determine_auth_method()
        self._client = None
    
    def _determine_auth_method(self) -> AuthMethod:
        """Determine which authentication method to use based on config"""
        if 'boxAppSettings' in self.config:
            return AuthMethod.JWT
        elif 'boxAppSettings' not in self.config and 'clientID' in self.config:
            if 'clientSecret' in self.config and 'enterpriseID' in self.config:
                return AuthMethod.OAUTH2_CCG
            return AuthMethod.OAUTH2_AC
        else:
            raise BoxAuthError("Could not determine authentication method from config")
    
    def authenticate(self) -> Client:
        """
        Authenticate with Box API based on the configured method
        
        Returns:
            Authenticated Box Client
        """
        try:
            if self._auth_method == AuthMethod.JWT:
                return self._authenticate_jwt()
            elif self._auth_method == AuthMethod.OAUTH2_CCG:
                return self._authenticate_oauth2_ccg()
            else:  # AuthMethod.OAUTH2_AC
                return self._authenticate_oauth2_ac()
        except BoxAPIException as e:
            raise BoxAuthError(f"Box API error during authentication: {str(e)}")
        except Exception as e:
            raise BoxAuthError(f"Authentication failed: {str(e)}")
    
    def _authenticate_jwt(self) -> Client:
        """Authenticate using JWT (Server Authentication)"""
        auth = JWTAuth.from_settings_dictionary(self.config)
        return Client(auth)
    
    def _authenticate_oauth2_ccg(self) -> Client:
        """Authenticate using OAuth 2.0 with Client Credentials Grant"""
        oauth = OAuth2(
            client_id=self.config['clientID'],
            client_secret=self.config['clientSecret']
        )
        
        # Get access token with client credentials grant
        access_token, _ = oauth.authenticate_instance()
        
        # Create client with the obtained token
        return Client(oauth)
    
    def _authenticate_oauth2_ac(self) -> Client:
        """
        Authenticate using OAuth 2.0 with Authorization Code Grant
        
        Note: This will prompt for user interaction to complete the OAuth flow
        """
        oauth = OAuth2(
            client_id=self.config['clientID'],
            client_secret=self.config.get('clientSecret', '')
        )
        
        # Generate auth URL
        auth_url, csrf_token = oauth.get_authorization_url('http://localhost')
        print(f"Please visit this URL to authorize the application: {auth_url}")
        
        # Get the authorization code from the user
        auth_code = input('Enter the authorization code: ')
        
        # Get access token
        access_token, refresh_token = oauth.authenticate(auth_code)
        
        return Client(oauth)


def load_auth_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load authentication configuration from a JSON file or environment variables
    
    Args:
        config_path: Path to JSON config file. If None, will look for BOX_CONFIG environment variable
        
    Returns:
        Dictionary containing authentication configuration
    """
    import os
    import json
    
    # Try to load from environment variable if no path provided
    if config_path is None:
        config_json = os.getenv('BOX_CONFIG')
        if not config_json:
            raise BoxAuthError("No config path provided and BOX_CONFIG environment variable not set")
        try:
            return json.loads(config_json)
        except json.JSONDecodeError as e:
            raise BoxAuthError(f"Invalid JSON in BOX_CONFIG: {str(e)}")
    
    # Load from file
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise BoxAuthError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise BoxAuthError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise BoxAuthError(f"Error loading config: {str(e)}")


def get_authenticated_client(config: Optional[Dict[str, Any]] = None) -> Client:
    """
    Helper function to get an authenticated Box client
    
    Args:
        config: Optional config dictionary. If None, will try to load from default location
        
    Returns:
        Authenticated Box Client
    """
    if config is None:
        config = load_auth_config()
    
    authenticator = BoxAuthenticator(config)
    return authenticator.authenticate()
