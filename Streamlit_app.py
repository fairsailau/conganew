"""
Streamlit application entry point

This file is used by Streamlit Cloud to run the application.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the Streamlit app
from app.app import main

if __name__ == "__main__":
    # Set the STREAMLIT_SERVER_HEADLESS environment variable
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Run the Streamlit app
    main()
