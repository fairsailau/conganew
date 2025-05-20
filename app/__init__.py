"""
Conga to Box DocGen Converter

This package provides tools for converting Conga templates to Box DocGen templates,
including parsing, conversion, validation, and export functionality.
"""

# Define __all__ first to avoid circular imports
__all__ = [
    'BoxAIClient',
    'BoxAIClientError',
    'BoxAuthError',
    'AuthMethod',
    'ConversionEngine',
    'DocxExporter',
    'CongaTemplateParser',
    'PromptBuilder',
    'ConversionContext',
    'CongaQueryLoader',
    'AIResponseParser',
    'JSONSchemaLoader'
]

# Import key components to make them available at the package level
# These imports are done after __all__ to ensure proper initialization
from .box_ai_client import BoxAIClient, BoxAIClientError, BoxAuthError, AuthMethod
from .prompt_builder import PromptBuilder, ConversionContext
from .response_parser import AIResponseParser
from .exporter import DocxExporter
from .query_loader import CongaQueryLoader
from .parser import CongaTemplateParser
from .conversion_engine import ConversionEngine

try:
    from .schema_loader import JSONSchemaLoader
except ImportError:
    JSONSchemaLoader = None
