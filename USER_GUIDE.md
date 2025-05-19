# Conga to Box DocGen Converter - User Guide

This document provides instructions for using the Conga to Box DocGen Converter tool.

## Overview

The Conga to Box DocGen Converter is a Streamlit application that automates the conversion of Conga Composer templates to Box DocGen templates. The tool preserves document formatting and structure while replacing Conga tags with their Box DocGen equivalents.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (installed via `pip install -r requirements.txt`):
  - streamlit
  - python-docx
  - requests

### Installation

1. Extract the ZIP file to a directory of your choice
2. Open a terminal/command prompt and navigate to the extracted directory
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Streamlit application:
   ```
   streamlit run main.py
   ```
2. Your default web browser will open automatically with the application interface
3. If the browser doesn't open automatically, navigate to the URL shown in the terminal (typically http://localhost:8501)

## Using the Converter

### Single Template Conversion

1. In the "Upload & Convert" tab, upload a single Conga template DOCX file
2. Configure conversion options in the sidebar if needed
3. Click "Convert Template"
4. Once conversion is complete, preview the results and download the converted template

### Batch Conversion

1. Enable "Batch Processing Mode" in the sidebar
2. Upload multiple Conga template DOCX files
3. Click "Start Batch Conversion"
4. Once conversion is complete, download individual templates or the complete ZIP file

### Configuration Options

The sidebar provides several configuration options:

- **Box API Token**: Optional. Provide a valid Box API token to enable AI-assisted conversion for complex patterns
- **Batch Processing Mode**: Enable to convert multiple templates at once
- **Use Box AI for Complex Conversions**: Enable to use Box AI for handling complex conversion scenarios
- **Advanced Options**:
  - **Validation Level**: Choose between Basic, Standard, or Thorough validation
  - **Preserve Document Formatting**: Ensure document formatting is maintained in the output

## Understanding the Results

The "Results" tab provides detailed information about the conversion:

- **Validation Results**: Shows syntax validity and completeness percentage
- **Errors and Warnings**: Lists any issues found during conversion
- **AI Validation Analysis**: If Box AI was used, provides additional insights
- **Download Options**: Buttons to download the converted templates

## Troubleshooting

### Common Issues

1. **Unconverted Tags**: If some tags remain unconverted, try:
   - Enabling Box AI for complex conversions
   - Checking if the tag format is supported
   - Adding custom mapping rules

2. **Formatting Issues**: If formatting is not preserved correctly:
   - Ensure "Preserve Document Formatting" is enabled
   - Check if the document uses complex formatting features

3. **Box AI Connection Errors**:
   - Verify your Box API token is valid
   - Ensure your Box account has access to Box AI features

### Getting Help

If you encounter issues not covered in this guide, please contact support with:
- The original template file
- The conversion logs
- A description of the issue

## Advanced Usage

### Custom Mapping Rules

The "Mapping Rules" tab shows the default mappings used for conversion. For advanced users, these rules can be customized by modifying the `converter.py` file.
