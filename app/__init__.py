"""
Conga to Box DocGen Converter

This package provides tools for converting Conga templates to Box DocGen templates,
including parsing, conversion, validation, and export functionality.
"""

# Import key components to make them available at the package level
from .parser import CongaTemplateParser
from .conversion_engine import ConversionEngine
from .exporter import DocxExporter
from .box_ai_client import BoxAIClient, BoxAIClientError, BoxAuthError, AuthMethod
from .prompt_builder import PromptBuilder, ConversionContext
from .query_loader import CongaQueryLoader
from .response_parser import AIResponseParser
from .exporter import DocxExporter
from .box_ai_client import BoxAIClient
from .schema_loader import JSONSchemaLoader
from .query_loader import CongaQueryLoader
from .template_generator import DocGenTemplateGenerator
from .prompt_builder import PromptBuilder, ConversionContext
from .response_parser import AIResponseParser

__all__ = [
    'CongaTemplateParser',
    'ConversionEngine',
    'ValidationEngine',
    'DocxExporter',
    'BoxAIClient',
    'JSONSchemaLoader',
    'CongaQueryLoader',
    'DocGenTemplateGenerator',
    'PromptBuilder',
    'ConversionContext',
    'AIResponseParser'
]
