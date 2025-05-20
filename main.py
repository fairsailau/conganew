"""
Main entry point for the Streamlit application
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import and run the app
from app.app import main

if __name__ == "__main__":
    main()
