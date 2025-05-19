"""
DOCX export utility for preserving formatting and Box tags
"""
import os
import docx
from typing import Dict, List, Any, Optional


class DocxExporter:
    """
    Utility for exporting DOCX files with preserved formatting and Box tags
    """
    
    def __init__(self):
        """
        Initialize the DOCX exporter
        """
        pass
        
    def export_docx(self, doc: docx.Document, output_path: str) -> str:
        """
        Export document to DOCX format, preserving formatting and Box tags
        
        Args:
            doc: docx.Document object to export
            output_path: Path to save the exported file
            
        Returns:
            Path to the exported file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the document
        doc.save(output_path)
        
        return output_path
    
    def batch_export(self, docs: Dict[str, docx.Document], output_dir: str) -> Dict[str, str]:
        """
        Export multiple documents to DOCX format
        
        Args:
            docs: Dictionary mapping filenames to docx.Document objects
            output_dir: Directory to save the exported files
            
        Returns:
            Dictionary mapping original filenames to exported file paths
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = {}
        
        for filename, doc in docs.items():
            # Create output path
            base_name = os.path.basename(filename)
            output_path = os.path.join(output_dir, f"converted_{base_name}")
            
            # Export the document
            exported_path = self.export_docx(doc, output_path)
            exported_files[filename] = exported_path
            
        return exported_files
