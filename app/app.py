"""
Main Streamlit application for Conga to Box DocGen template conversion
"""
import os
import io
import tempfile
import streamlit as st
import docx
from typing import Dict, List, Any, Optional

from parser import CongaTemplateParser
from converter import ConversionEngine
from validator import ValidationEngine
from box_ai_client import BoxAIClient
from exporter import DocxExporter


def main():
    """
    Main Streamlit application
    """
    st.set_page_config(
        page_title="Conga to Box DocGen Converter",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("Conga to Box DocGen Template Converter")
    st.write("Convert Conga Composer templates to Box DocGen format while preserving formatting")
    
    # Initialize session state
    if 'converted_docs' not in st.session_state:
        st.session_state.converted_docs = {}
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = {}
    if 'box_token' not in st.session_state:
        st.session_state.box_token = ""
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Box API Token
        st.session_state.box_token = st.text_input(
            "Box API Token (optional for AI-assisted conversion)",
            value=st.session_state.box_token,
            type="password"
        )
        
        # Processing options
        st.subheader("Processing Options")
        batch_mode = st.checkbox("Batch Processing Mode", value=False)
        use_ai = st.checkbox("Use Box AI for Complex Conversions", value=True)
        
        # Advanced options
        with st.expander("Advanced Options"):
            validation_level = st.selectbox(
                "Validation Level",
                ["Basic", "Standard", "Thorough"],
                index=1
            )
            
            preserve_formatting = st.checkbox("Preserve Document Formatting", value=True)
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Upload & Convert", "Mapping Rules", "Results"])
    
    # Tab 1: Upload & Convert
    with tab1:
        st.header("Upload Conga Templates")
        
        if batch_mode:
            uploaded_files = st.file_uploader(
                "Upload multiple templates",
                type=["docx"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                st.write(f"Uploaded {len(uploaded_files)} files")
                
                if st.button("Start Batch Conversion"):
                    with st.spinner("Converting templates..."):
                        process_batch_conversion(uploaded_files, use_ai, st.session_state.box_token)
        else:
            uploaded_file = st.file_uploader("Upload template", type=["docx"])
            
            if uploaded_file:
                st.write(f"Uploaded: {uploaded_file.name}")
                
                # Preview the uploaded file
                with st.expander("Preview Original Template"):
                    preview_docx(uploaded_file)
                
                if st.button("Convert Template"):
                    with st.spinner("Converting template..."):
                        process_single_conversion(uploaded_file, use_ai, st.session_state.box_token)
    
    # Tab 2: Mapping Rules
    with tab2:
        st.header("Mapping Rules")
        
        with st.expander("Merge Field Mappings"):
            st.code("""
            # Merge Field Mappings
            '&=Account.Name' -> 'account.name'
            '&=Contact.Name' -> 'contact.name'
            '&=Opportunity.Name' -> 'opportunity.name'
            '&=Date.Today' -> '{{date now format="dd-MM-yyyy"}}'
            """)
        
        with st.expander("Conditional Logic Mappings"):
            st.code("""
            # Equality Condition
            {IF "{{field}}" = "value" "true_result" "false_result"}
            ->
            {{#eq field "value"}}true_result{{else}}false_result{{/eq}}
            
            # Greater Than Condition
            {IF "{{field}}" > "value" "true_result" "false_result"}
            ->
            {{#gt field value}}true_result{{else}}false_result{{/gt}}
            """)
        
        with st.expander("Table Mappings"):
            st.code("""
            # Table Start
            {TABLE Group=collection_name}
            ->
            {{#each collection_name}}
            
            # Table End
            {END collection_name}
            ->
            {{/each}}
            """)
    
    # Tab 3: Results
    with tab3:
        st.header("Conversion Results")
        
        if st.session_state.converted_docs:
            for filename, doc_info in st.session_state.converted_docs.items():
                with st.expander(f"Converted: {filename}"):
                    # Display validation results
                    if filename in st.session_state.validation_results:
                        validation = st.session_state.validation_results[filename]
                        
                        st.subheader("Validation Results")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Syntax Valid", "✅" if validation['syntax_valid'] else "❌")
                        
                        with col2:
                            completeness = validation['completeness'] * 100
                            st.metric("Completeness", f"{completeness:.1f}%")
                        
                        if validation['errors']:
                            st.error(f"{len(validation['errors'])} errors found")
                            for error in validation['errors']:
                                st.write(f"- {error['type']}")
                        
                        if validation['warnings']:
                            st.warning(f"{len(validation['warnings'])} warnings found")
                            for warning in validation['warnings']:
                                st.write(f"- {warning['type']}")
                        
                        if 'ai_validation' in validation:
                            with st.expander("AI Validation Analysis"):
                                st.write(validation['ai_validation'])
                    
                    # Download button for the converted file
                    with open(doc_info['path'], "rb") as file:
                        st.download_button(
                            label="Download Converted Template",
                            data=file,
                            file_name=f"converted_{os.path.basename(filename)}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )


def process_single_conversion(uploaded_file, use_ai: bool, box_token: str) -> None:
    """
    Process a single file conversion
    
    Args:
        uploaded_file: Uploaded file object
        use_ai: Whether to use Box AI for complex conversions
        box_token: Box API token
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Initialize components
        parser = CongaTemplateParser(docx_file_path=tmp_path)
        
        # Initialize Box AI client if token is provided and AI is enabled
        box_ai_client = None
        if box_token and use_ai:
            box_ai_client = BoxAIClient(box_token)
        
        # Parse the template
        conga_tags = parser.parse()
        doc = parser.get_document()
        
        # Convert the template
        converter = ConversionEngine(box_ai_client=box_ai_client)
        converted_doc = converter.convert_template(doc, conga_tags)
        
        # Export the converted document
        output_dir = tempfile.mkdtemp()
        output_path = os.path.join(output_dir, f"converted_{uploaded_file.name}")
        
        exporter = DocxExporter()
        exported_path = exporter.export_docx(converted_doc, output_path)
        
        # Validate the conversion
        validator = ValidationEngine(box_ai_client=box_ai_client)
        
        # Extract text content for validation
        original_content = "\n".join([p.text for p in doc.paragraphs])
        converted_content = "\n".join([p.text for p in converted_doc.paragraphs])
        
        validation_results = validator.validate_conversion(
            original_content, 
            converted_content,
            conga_tags
        )
        
        # Store results in session state
        st.session_state.converted_docs[uploaded_file.name] = {
            'doc': converted_doc,
            'path': exported_path
        }
        
        st.session_state.validation_results[uploaded_file.name] = validation_results
        
        # Show success message
        st.success(f"Successfully converted {uploaded_file.name}")
        
        # Preview the converted document
        with st.expander("Preview Converted Template"):
            preview_docx_from_path(exported_path)
            
    except Exception as e:
        st.error(f"Error converting {uploaded_file.name}: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def process_batch_conversion(uploaded_files, use_ai: bool, box_token: str) -> None:
    """
    Process batch conversion of multiple files
    
    Args:
        uploaded_files: List of uploaded file objects
        use_ai: Whether to use Box AI for complex conversions
        box_token: Box API token
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize Box AI client if token is provided and AI is enabled
    box_ai_client = None
    if box_token and use_ai:
        box_ai_client = BoxAIClient(box_token)
    
    # Create output directory
    output_dir = tempfile.mkdtemp()
    
    for i, uploaded_file in enumerate(uploaded_files):
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Initialize components
            parser = CongaTemplateParser(docx_file_path=tmp_path)
            
            # Parse the template
            conga_tags = parser.parse()
            doc = parser.get_document()
            
            # Convert the template
            converter = ConversionEngine(box_ai_client=box_ai_client)
            converted_doc = converter.convert_template(doc, conga_tags)
            
            # Export the converted document
            output_path = os.path.join(output_dir, f"converted_{uploaded_file.name}")
            
            exporter = DocxExporter()
            exported_path = exporter.export_docx(converted_doc, output_path)
            
            # Validate the conversion
            validator = ValidationEngine(box_ai_client=box_ai_client)
            
            # Extract text content for validation
            original_content = "\n".join([p.text for p in doc.paragraphs])
            converted_content = "\n".join([p.text for p in converted_doc.paragraphs])
            
            validation_results = validator.validate_conversion(
                original_content, 
                converted_content,
                conga_tags
            )
            
            # Store results in session state
            st.session_state.converted_docs[uploaded_file.name] = {
                'doc': converted_doc,
                'path': exported_path
            }
            
            st.session_state.validation_results[uploaded_file.name] = validation_results
            
        except Exception as e:
            st.error(f"Error converting {uploaded_file.name}: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    # Complete the progress bar
    progress_bar.progress(1.0)
    status_text.text(f"Completed converting {len(uploaded_files)} files")
    
    # Create a zip file of all converted documents
    if len(uploaded_files) > 1:
        import shutil
        zip_path = os.path.join(tempfile.mkdtemp(), "converted_templates.zip")
        shutil.make_archive(zip_path[:-4], 'zip', output_dir)
        
        with open(zip_path, "rb") as file:
            st.download_button(
                label="Download All Converted Templates (ZIP)",
                data=file,
                file_name="converted_templates.zip",
                mime="application/zip"
            )


def preview_docx(uploaded_file) -> None:
    """
    Preview a DOCX file in Streamlit
    
    Args:
        uploaded_file: Uploaded file object
    """
    try:
        doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        
        # Display paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                st.write(paragraph.text)
        
        # Display tables
        for i, table in enumerate(doc.tables):
            st.write(f"Table {i+1}:")
            table_data = []
            
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            
            if table_data:
                st.table(table_data)
    
    except Exception as e:
        st.error(f"Error previewing document: {str(e)}")


def preview_docx_from_path(file_path: str) -> None:
    """
    Preview a DOCX file from a file path
    
    Args:
        file_path: Path to the DOCX file
    """
    try:
        doc = docx.Document(file_path)
        
        # Display paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                st.write(paragraph.text)
        
        # Display tables
        for i, table in enumerate(doc.tables):
            st.write(f"Table {i+1}:")
            table_data = []
            
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            
            if table_data:
                st.table(table_data)
    
    except Exception as e:
        st.error(f"Error previewing document: {str(e)}")


if __name__ == "__main__":
    main()
