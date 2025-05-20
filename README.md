# Conga to Box DocGen Converter

This Streamlit application converts Conga Composer templates to Box DocGen templates while preserving document formatting and structure.

## Features

- Upload and convert single or multiple Conga templates
- AI-assisted conversion for complex patterns (optional)
- Validation of conversion quality
- Export to DOCX with preserved formatting and Box tags
- Batch processing support

## Requirements

- Python 3.8+
- Streamlit
- python-docx
- requests

## Installation

1. Clone this repository

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.streamlit/secrets.toml` file with your Box API credentials. Example:

   ```toml
   [box]
   # Choose one authentication method:
   
   # 1. Developer Token (easiest for testing)
   auth_method = "developer_token"
   developer_token = "your_developer_token_here"
   
   # 2. JWT Authentication (for production)
   # auth_method = "jwt"
   # config = """
   # {
   #   "boxAppSettings": {
   #     "clientID": "your_client_id",
   #     "clientSecret": "your_client_secret",
   #     "appAuth": {
   #       "publicKeyID": "your_public_key_id",
   #       "privateKey": "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...\n-----END ENCRYPTED PRIVATE KEY-----\n",
   #       "passphrase": "your_passphrase"
   #     }
   #   },
   #   "enterpriseID": "your_enterprise_id"
   # }
   # """
   
   # 3. OAuth 2.0 Client Credentials
   # auth_method = "oauth2_ccg"
   # client_id = "your_client_id"
   # client_secret = "your_client_secret"
   # enterprise_id = "your_enterprise_id"
   ```

### For Production Deployment

When deploying to Streamlit Cloud or another platform, set the secrets through the platform's secret management system. For Streamlit Cloud, use the "Advanced settings" when deploying to set the secrets.

## Usage

1. Run the Streamlit application:
   ```
   streamlit run main.py
   ```

2. Upload your Conga template(s) through the web interface

3. Configure conversion options:
   - Enable/disable Box AI assistance
   - Choose validation level
   - Enable batch processing for multiple files

4. Click "Convert Template" or "Start Batch Conversion"

5. Download the converted Box DocGen template(s)

## Box AI Integration

For complex conversions, the tool can leverage Box AI API. To use this feature:

1. Provide a valid Box API token in the sidebar
2. Ensure the token has access to Box AI endpoints
3. Enable the "Use Box AI for Complex Conversions" option

## Project Structure

- `app/app.py`: Main Streamlit application
- `app/parser.py`: Conga template parser
- `app/converter.py`: Conversion engine
- `app/validator.py`: Validation engine
- `app/box_ai_client.py`: Box AI API client
- `app/exporter.py`: DOCX export utility
- `main.py`: Application entry point
- `test_conversion.py`: Test script for conversion and export

## License

This project is licensed under the MIT License - see the LICENSE file for details.
