#!/usr/bin/env python3
"""
This is a simple redirector script that imports and runs the main Streamlit app.
It's needed for Streamlit Cloud deployment to find the entry point.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the main app
from app.app import main

if __name__ == "__main__":
    # Set the STREAMLIT_SERVER_HEADLESS environment variable
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Run the Streamlit app
    main()
