#!/usr/bin/env python3
"""
Streamlit application entry point for deployment.

This file is used by Streamlit Cloud to run the application.
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = str(Path(__file__).parent / "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Import the main app
from app import main

if __name__ == "__main__":
    # Set the STREAMLIT_SERVER_HEADLESS environment variable
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Run the Streamlit app
    main()
