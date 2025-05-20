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

# Lazy imports to avoid circular dependencies
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING or 'sphinx' in sys.modules:
    # Import all components for type checking and documentation
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
        JSONSchemaLoader = None  # type: ignore
else:
    # For runtime, use lazy imports
    BoxAIClient = None
    BoxAIClientError = None
    BoxAuthError = None
    AuthMethod = None
    PromptBuilder = None
    ConversionContext = None
    AIResponseParser = None
    DocxExporter = None
    CongaQueryLoader = None
    CongaTemplateParser = None
    ConversionEngine = None
    JSONSchemaLoader = None

    def __getattr__(name):
        if name in __all__:
            import importlib
            module = importlib.import_module(f'app.{name.lower()}')
            value = getattr(module, name)
            globals()[name] = value
            return value
        raise AttributeError(f"module 'app' has no attribute '{name}'")
