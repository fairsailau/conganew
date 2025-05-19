""
Module for building prompts for AI-assisted template conversion.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ConversionContext:
    """Context for template conversion."""
    template_text: str = ""
    query_text: str = ""
    schema_data: Optional[Dict[str, Any]] = None
    custom_instructions: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to a dictionary."""
        return {
            "template_text": self.template_text,
            "query_text": self.query_text,
            "schema_fields": list(self.schema_data.keys()) if self.schema_data else [],
            "custom_instructions": self.custom_instructions
        }


class PromptBuilder:
    """Builder for creating prompts for AI-assisted template conversion."""
    
    def __init__(self, context: ConversionContext):
        """Initialize the prompt builder with conversion context.
        
        Args:
            context: Conversion context containing template and schema information
        """
        self.context = context
    
    def build_conversion_prompt(self) -> Dict[str, str]:
        """Build a prompt for converting a Conga template to Box DocGen format.
        
        Returns:
            Dict containing 'system_prompt' and 'user_prompt' strings
        """
        system_prompt = """You are an expert in document generation systems, specifically converting between Conga and Box DocGen templates. 
Your task is to convert the provided Conga template to Box DocGen format while preserving all functionality.

Key conversion rules:
1. Merge fields: '{{field_name}}' in Conga becomes '{{field_name}}' in Box DocGen
2. Conditional logic: Convert Conga's {IF} statements to Handlebars {{#if}} blocks
3. Loops: Convert Conga's {TABLE} or {LOOP} to Handlebars {{#each}} blocks
4. Date formatting: Convert Conga date formats to Box DocGen format
5. Special functions: Map Conga functions to their Box DocGen equivalents

Always maintain the original document structure and formatting as much as possible.
"""

        user_prompt = f"""Please convert the following Conga template to Box DocGen format.

CONGA TEMPLATE:
{template_text}

QUERY (if any):
{query_text}

SCHEMA FIELDS (if any):
{schema_fields}

CUSTOM INSTRUCTIONS:
{custom_instructions}

CONVERTED TEMPLATE:"""

        # Format the user prompt with the actual context
        user_prompt = user_prompt.format(
            template_text=self.context.template_text,
            query_text=self.context.query_text or "N/A",
            schema_fields="\n- ".join([""] + (self.context.schema_data.keys() if self.context.schema_data else [])),
            custom_instructions=self.context.custom_instructions or "None"
        )
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
    
    def build_validation_prompt(self, original_text: str, converted_text: str) -> Dict[str, str]:
        """Build a prompt for validating a converted template.
        
        Args:
            original_text: Original Conga template text
            converted_text: Converted Box DocGen template text
            
        Returns:
            Dict containing 'system_prompt' and 'user_prompt' strings
        """
        system_prompt = """You are a meticulous quality assurance specialist for document generation systems. 
Your task is to validate that the converted Box DocGen template matches the functionality of the original Conga template.

Check for:
1. All merge fields are correctly converted
2. Conditional logic works the same way
3. Loops and iterations are properly handled
4. Date formats and special functions are correctly mapped
5. No loss of functionality or data
6. No syntax errors in the converted template

Provide a detailed analysis of any issues found and suggestions for fixes.
"""

        user_prompt = f"""Please validate that the following converted Box DocGen template matches the functionality of the original Conga template.

ORIGINAL CONGA TEMPLATE:
{original_text}

CONVERTED BOX DOCGEN TEMPLATE:
{converted_text}

SCHEMA FIELDS (if any):
{schema_fields}

VALIDATION ANALYSIS:"""

        user_prompt = user_prompt.format(
            original_text=original_text,
            converted_text=converted_text,
            schema_fields="\n- ".join([""] + (self.context.schema_data.keys() if self.context.schema_data else []))
        )
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
