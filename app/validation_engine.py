"""
Validation engine for Box DocGen templates.

This module provides functionality to validate the syntax and semantics of
Box DocGen templates, including checking for proper Handlebars syntax,
field references, and template structure.
"""
import re
from typing import Dict, List, Optional, Any, Tuple, Set

from boxsdk import Client

from app.box_ai_client import BoxAIClient
from app.prompt_builder import PromptBuilder, ConversionContext
from app.response_parser import AIResponseParser


class ValidationEngine:
    """Engine for validating Box DocGen templates.
    
    This class provides methods to validate the syntax and semantics of
    Box DocGen templates, including checking for proper Handlebars syntax,
    field references, and template structure. It can also use AI for
    more advanced validation when available.
    """
    
    def __init__(self, box_ai_client: Optional[BoxAIClient] = None):
        """Initialize the validation engine.
        
        Args:
            box_ai_client: Optional BoxAIClient instance for AI-powered validation.
                         If provided, enables advanced validation using AI.
        """
        self.box_ai_client = box_ai_client
    
    def validate_template_syntax(self, template_text: str) -> Dict[str, Any]:
        """Validate the syntax of a Box DocGen template.
        
        This method checks for common syntax issues in Handlebars templates,
        including unclosed expressions, unknown helpers, and other potential
        problems that could cause rendering issues.
        
        Args:
            template_text: The template text to validate
            
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool indicating if template is valid
            - errors: List of error messages with line/column info
            - warnings: List of warning messages with line/column info
            - completeness: Float (0.0-1.0) indicating template completeness
        """
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        
        # Check for unclosed Handlebars expressions
        open_handles = self._find_unclosed_handlebars(template_text, errors)
        
        # Add errors for unclosed expressions
        for line_num, line in open_handles:
            errors.append({
                'line': line_num,
                'column': line.rfind('{{'),
                'message': 'Unclosed handlebars expression',
                'type': 'syntax_error'
            })
        
        # Check for common issues in Handlebars expressions
        self._check_handlebar_expressions(template_text, errors, warnings)
        
        # Calculate completeness score (simple heuristic)
        total_lines = len(template_text.split('\n'))
        error_lines = {e['line'] for e in errors}
        warning_lines = {w['line'] for w in warnings}
        
        if total_lines > 0:
            affected_lines = len(error_lines.union(warning_lines))
            completeness = 1.0 - (affected_lines / total_lines)
        else:
            completeness = 0.0
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'completeness': min(max(completeness, 0.0), 1.0)  # Ensure between 0 and 1
        }
    
    def _find_unclosed_handlebars(
        self, 
        template_text: str, 
        errors: List[Dict[str, Any]]
    ) -> List[Tuple[int, str]]:
        """Find unclosed Handlebars expressions in the template.
        
        Args:
            template_text: The template text to check
            errors: List to append any errors to
            
        Returns:
            List of (line_number, line_content) tuples for unclosed expressions
        """
        open_handles = []
        for i, line in enumerate(template_text.split('\n'), 1):
            # Find all {{ and }} in the line
            open_matches = [m.start() for m in re.finditer(r'\{\{', line)]
            close_matches = [m.start() for m in re.finditer(r'\}\}', line)]
            
            # Check for unclosed expressions
            if len(open_matches) > len(close_matches):
                open_handles.append((i, line))
            elif len(open_matches) < len(close_matches):
                if open_handles:
                    open_handles.pop()
                elif close_matches:
                    errors.append({
                        'line': i,
                        'column': close_matches[0],
                        'message': 'Unmatched closing handlebars',
                        'type': 'syntax_error'
                    })
        return open_handles
    
    def _check_handlebar_expressions(
        self, 
        template_text: str, 
        errors: List[Dict[str, Any]], 
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check for common issues in Handlebars expressions.
        
        Args:
            template_text: The template text to check
            errors: List to append any errors to
            warnings: List to append any warnings to
        """
        handlebar_exprs = re.finditer(r'\{\{(.*?)\}\}', template_text, re.DOTALL)
        
        for match in handlebar_exprs:
            expr = match.group(1).strip()
            line_num = template_text[:match.start()].count('\n') + 1
            
            # Check for empty expressions
            if not expr:
                errors.append({
                    'line': line_num,
                    'column': match.start(),
                    'message': 'Empty handlebars expression',
                    'type': 'syntax_error'
                })
                continue
            
            # Check for common typos in helpers
            self._check_helper_syntax(expr, line_num, match.start(), warnings)
    
    def _check_helper_syntax(
        self, 
        expr: str, 
        line_num: int, 
        column: int, 
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check for common syntax issues in Handlebars helpers.
        
        Args:
            expr: The Handlebars expression to check
            line_num: Line number of the expression
            column: Column number of the expression
            warnings: List to append any warnings to
        """
        if not expr.startswith('#'):
            return
            
        # List of known Handlebars helpers
        known_helpers = {'if', 'unless', 'each', 'with', 'lookup', 'log'}
        
        # Get the helper name (first word after #)
        helper = expr.split()[0][1:].split('.')[0]
        
        if helper not in known_helpers:
            warnings.append({
                'line': line_num,
                'column': column,
                'message': f'Unknown helper: {helper}',
                'type': 'unknown_helper',
                'suggestion': f'Did you mean one of: {sorted(known_helpers)}?'
            })
    
    def validate_template_semantics(
        self, 
        template_text: str, 
        schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Validate the semantics of a Box DocGen template against a schema.
        
        This method checks that all field references in the template exist in the
        provided schema, and that all required fields from the schema are used in
        the template.
        
        Args:
            template_text: The template text to validate
            schema: Optional JSON schema to validate against. If not provided,
                  returns a warning but no errors.
            
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool indicating if template is valid
            - errors: List of error messages with line/column info
            - warnings: List of warning messages with line/column info
        """
        if not schema:
            return {
                'is_valid': True, 
                'warnings': [{
                    'message': 'No schema provided for semantic validation',
                    'type': 'missing_schema',
                    'suggestion': 'Provide a JSON schema for more thorough validation'
                }], 
                'errors': []
            }
            
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        
        # Extract all field references from the template
        field_refs = self._extract_field_references(template_text)
        
        # Get schema information
        schema_fields = set(schema.get('properties', {}).keys())
        required_fields = set(schema.get('required', []))
        
        # Check each field reference against the schema
        self._check_field_references(
            template_text, 
            field_refs, 
            schema_fields, 
            warnings
        )
        
        # Check for required fields that are missing from the template
        self._check_required_fields(
            field_refs, 
            required_fields, 
            warnings
        )
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _extract_field_references(self, template_text: str) -> Set[str]:
        """Extract all field references from the template.
        
        Args:
            template_text: The template text to analyze
            
        Returns:
            Set of unique field references found in the template
        """
        field_refs = set()
        
        # Match field references in Handlebars expressions
        # Exclude helpers, partials, and other special syntax
        pattern = r'\{\{(?!\{|#|/|else|if|each|with|unless|lookup|log)([^}\s]+)'
        
        for match in re.finditer(pattern, template_text):
            field_ref = match.group(1).strip()
            # Remove any path navigation and array indices
            field_ref = field_ref.split('.')[-1].split('[')[0]
            if field_ref and not field_ref[0].isdigit():
                field_refs.add(field_ref)
        
        return field_refs
    
    def _check_field_references(
        self,
        template_text: str,
        field_refs: Set[str],
        schema_fields: Set[str],
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check that all field references exist in the schema.
        
        Args:
            template_text: The template text (for line number calculation)
            field_refs: Set of field references found in the template
            schema_fields: Set of fields defined in the schema
            warnings: List to append any warnings to
        """
        lines = template_text.split('\n')
        
        for ref in field_refs:
            # Skip built-in and special fields
            if ref.startswith('@') or ref in ['this', 'root']:
                continue
                
            if ref not in schema_fields:
                # Find the line number for the reference
                line_num = 1
                for i, line in enumerate(lines, 1):
                    if ref in line:
                        line_num = i
                        break
                
                warnings.append({
                    'line': line_num,
                    'column': 0,
                    'message': f'Field not found in schema: {ref}',
                    'type': 'unknown_field',
                    'suggestion': 'Check for typos or add this field to your schema'
                })
    
    def _check_required_fields(
        self,
        field_refs: Set[str],
        required_fields: Set[str],
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check that all required fields are used in the template.
        
        Args:
            field_refs: Set of field references found in the template
            required_fields: Set of required fields from the schema
            warnings: List to append any warnings to
        """
        missing_required = required_fields - field_refs
        
        for field in missing_required:
            warnings.append({
                'line': 1,  # Global issue, not tied to a specific line
                'column': 0,
                'message': f'Field not found in schema: {ref}',
                'type': 'unknown_field',
                'suggestion': 'Check for typos or add this field to your schema'
            })
    
    def _check_required_fields(
        self,
        field_refs: Set[str],
        required_fields: Set[str],
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check that all required fields are used in the template.
        
        Args:
            field_refs: Set of field references found in the template
            required_fields: Set of required fields from the schema
            warnings: List to append any warnings to
        """
        missing_required = required_fields - field_refs
        
        for field in missing_required:
            warnings.append({
                'line': 1,  # Global issue, not tied to a specific line
                'column': 0,
                'message': f'Required field not used in template: {field}',
                'type': 'missing_required_field',
                'suggestion': 'Consider adding this field to your template or marking it as optional in the schema'
            })
    
    def validate_conversion(
        self, 
        original_text: str, 
        converted_text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate that a converted template matches the original.
        
        This method validates that the conversion from the original template
        to the converted template was successful. It can use AI-based validation
        if an AI client is available, or fall back to rule-based validation.
        
        Args:
            original_text: Original template text before conversion
            converted_text: Converted template text to validate
            context: Optional context for validation, which may include:
                   - schema: JSON schema for the template
                   - instructions: Custom validation instructions
                   - metadata: Additional metadata about the conversion
            
        Returns:
            Dict containing validation results with keys:
            - is_valid: bool indicating if conversion is valid
            - confidence: Float (0.0-1.0) indicating confidence in validation
            - issues: List of issues found during validation
            - suggestions: List of suggestions for improvement
            - validation_method: 'ai' or 'rules' indicating which method was used
        """
        if self.box_ai_client:
            return self._validate_with_ai(original_text, converted_text, context or {})
        return self._validate_with_rules(original_text, converted_text, context or {})
    
    def _validate_with_ai(
        self, 
        original_text: str, 
        converted_text: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to validate the conversion.
        
        This method uses the Box AI client to validate the conversion by analyzing
        both the original and converted templates and providing feedback on any
        issues or potential improvements.
        
        Args:
            original_text: Original template text before conversion
            converted_text: Converted template text to validate
            context: Context for validation including schema and instructions
            
        Returns:
            Dict containing AI-based validation results
        """
        try:
            # Create a conversion context
            conv_context = ConversionContext(
                template_text=original_text,
                schema_data=context.get('schema'),
                custom_instructions=context.get('instructions', '')
            )
            
            # Build the validation prompt
            prompt_builder = PromptBuilder(conv_context)
            prompts = prompt_builder.build_validation_prompt(
                original_text, 
                converted_text
            )
            
            # Get AI response
            response = self.box_ai_client.generate_text(
                prompt=prompts['user_prompt'],
                system_prompt=prompts['system_prompt']
            )
            
            # Parse the response
            parser = AIResponseParser()
            result = parser.parse_validation_result(response)
            
            return {
                'is_valid': result.get('is_valid', False),
                'confidence': min(max(result.get('confidence', 0.5), 0.0), 1.0),
                'issues': result.get('issues', []),
                'suggestions': result.get('suggestions', []),
                'ai_analysis': response,
                'validation_method': 'ai'
            }
            
        except Exception as e:
            # Fall back to rules-based validation if AI validation fails
            return {
                **self._validate_with_rules(original_text, converted_text, context),
                'ai_error': str(e),
                'validation_method': 'ai_fallback_to_rules'
            }
    
    def _validate_with_rules(
        self, 
        original_text: str, 
        converted_text: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use rule-based validation for the conversion.
        
        This method performs basic validation using predefined rules to check
        for common issues in the converted template, such as remaining Conga
        syntax or significant content reduction.
        
        Args:
            original_text: Original template text before conversion
            converted_text: Converted template text to validate
            context: Context for validation (unused in rules-based validation)
            
        Returns:
            Dict containing rule-based validation results
        """
        # Basic validation that can be done without AI
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        
        # Check for any remaining Conga syntax in the converted text
        self._check_remaining_conga_syntax(converted_text, warnings)
        
        # Check for basic structure preservation
        self._check_content_preservation(original_text, converted_text, warnings)
        
        # Calculate confidence based on number of issues found
        confidence = self._calculate_confidence(errors, warnings)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'confidence': confidence,
            'validation_method': 'rules'
        }
    
    def _check_remaining_conga_syntax(
        self, 
        converted_text: str, 
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check for any remaining Conga syntax in the converted text.
        
        Args:
            converted_text: The converted template text to check
            warnings: List to append any warnings to
        """
        conga_patterns = [
            (r'\{IF\\b', 'IF statement not fully converted'),
            (r'\\{TABLE\\b', 'TABLE statement not fully converted'),
            (r'\\{LOOP\\b', 'LOOP statement not fully converted'),
            (r'\\{END\\b', 'END statement not fully converted'),
            (r'\\&[=+!]', 'Unconverted merge field'),
            (r'\\&[A-Za-z0-9_]', 'Unconverted merge field')
        ]
        
        for i, line in enumerate(converted_text.split('\\n'), 1):
            for pattern, message in conga_patterns:
                if re.search(pattern, line):
                    warnings.append({
                        'line': i,
                        'column': 0,
                        'message': message,
                        'type': 'unconverted_syntax',
                        'suggestion': 'Review the conversion of this Conga syntax to Handlebars'
                    })
    
    def _check_content_preservation(
        self,
        original_text: str,
        converted_text: str,
        warnings: List[Dict[str, Any]]
    ) -> None:
        """Check that the converted text preserves the original content structure.
        
        Args:
            original_text: The original template text
            converted_text: The converted template text
            warnings: List to append any warnings to
        """
        # Remove empty lines for comparison
        original_lines = [l.strip() for l in original_text.split('\\n') if l.strip()]
        converted_lines = [l.strip() for l in converted_text.split('\\n') if l.strip()]
        
        # Simple check for significant reduction in content
        if not original_lines:
            return
            
        content_ratio = len(converted_lines) / len(original_lines)
        
        if content_ratio < 0.5:  # Less than 50% of original lines
            warnings.append({
                'line': 1,
                'column': 0,
                'message': 'Significant reduction in content length after conversion',
                'type': 'content_reduction',
                'suggestion': 'Verify that all content was properly converted and not accidentally removed'
            })
    
    def _calculate_confidence(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> float:
        """Calculate a confidence score based on the number of issues found.
        
        Args:
            errors: List of error messages
            warnings: List of warning messages
            
        Returns:
            Float between 0.0 and 1.0 representing confidence in the conversion
        """
        if errors:
            return 0.3  # Low confidence if there are errors
        if warnings:
            return 0.7  # Medium confidence if there are only warnings
        return 1.0  # High confidence if no issues found
