"""
Module for loading and validating JSON schemas for template conversion.
"""
import json
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

__all__ = ['JSONSchemaLoader']


class JSONSchemaLoader:
    """Loader for JSON schemas used in template validation."""
    
    def __init__(self, schema_data: Optional[Union[Dict, str, Path]] = None):
        """Initialize the schema loader.
        
        Args:
            schema_data: Schema data as a dict, JSON string, or file path
        """
        self.schema = {}
        self._load_schema(schema_data)
    
    def _load_schema(self, schema_data: Optional[Union[Dict, str, Path]]) -> None:
        """Load schema from various input types.
        
        Args:
            schema_data: Schema data as a dict, JSON string, or file path
        """
        if not schema_data:
            return
            
        try:
            if isinstance(schema_data, dict):
                self.schema = schema_data
            elif isinstance(schema_data, (str, Path)):
                # Try to load from file if path exists
                path = Path(schema_data)
                if path.exists() and path.is_file():
                    with open(path, 'r', encoding='utf-8') as f:
                        self.schema = json.load(f)
                else:
                    # Try to parse as JSON string
                    self.schema = json.loads(str(schema_data))
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid schema data: {str(e)}")
    
    def validate_against_schema(self, data: Dict) -> Dict[str, Any]:
        """Validate data against the loaded schema.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict with validation results
        """
        if not self.schema:
            return {
                'is_valid': True,
                'errors': [],
                'warnings': [{'message': 'No schema loaded for validation'}]
            }
            
        # This is a simplified validation - in a real implementation,
        # you would use a proper JSON Schema validator like jsonschema
        errors = []
        
        # Check required fields
        required_fields = self.schema.get('required', [])
        for field in required_fields:
            if field not in data:
                errors.append({
                    'field': field,
                    'message': f'Missing required field: {field}',
                    'type': 'required_field_missing'
                })
        
        # Check field types
        properties = self.schema.get('properties', {})
        for field, value in data.items():
            if field not in properties:
                continue
                
            field_schema = properties[field]
            field_type = field_schema.get('type')
            
            if not field_type:
                continue
                
            # Simple type checking
            type_check = self._check_type(value, field_type)
            if not type_check['valid']:
                errors.append({
                    'field': field,
                    'message': f'Invalid type for {field}: expected {field_type}, got {type(value).__name__}',
                    'type': 'invalid_type',
                    'expected': field_type,
                    'actual': type(value).__name__
                })
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'schema': self.schema
        }
    
    def _check_type(self, value: Any, expected_type: Union[str, List[str]]) -> Dict[str, Any]:
        """Check if a value matches the expected type.
        
        Args:
            value: Value to check
            expected_type: Expected type(s) as string or list of strings
            
        Returns:
            Dict with validation result
        """
        if isinstance(expected_type, list):
            # Check if any of the types match
            for t in expected_type:
                if self._check_single_type(value, t):
                    return {'valid': True}
            return {'valid': False}
        else:
            return {'valid': self._check_single_type(value, expected_type)}
    
    def _check_single_type(self, value: Any, type_str: str) -> bool:
        """Check if a value matches a single type.
        
        Args:
            value: Value to check
            type_str: Type string ('string', 'number', 'integer', 'boolean', 'array', 'object')
            
        Returns:
            bool: True if type matches, False otherwise
        """
        if type_str == 'string':
            return isinstance(value, str)
        elif type_str == 'number':
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif type_str == 'integer':
            return isinstance(value, int) and not isinstance(value, bool)
        elif type_str == 'boolean':
            return isinstance(value, bool)
        elif type_str == 'array':
            return isinstance(value, list)
        elif type_str == 'object':
            return isinstance(value, dict)
        elif type_str == 'null':
            return value is None
        else:
            # Unknown type - assume valid
            return True
    
    def get_field_names(self) -> List[str]:
        """Get all field names defined in the schema.
        
        Returns:
            List of field names
        """
        return list(self.schema.get('properties', {}).keys())
    
    def get_field_type(self, field_name: str) -> Optional[str]:
        """Get the type of a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field type as string, or None if field not found
        """
        field = self.schema.get('properties', {}).get(field_name, {})
        return field.get('type') if field else None
    
    def get_field_description(self, field_name: str) -> Optional[str]:
        """Get the description of a field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Field description, or None if not available
        """
        field = self.schema.get('properties', {}).get(field_name, {})
        return field.get('description')
    
    def is_required(self, field_name: str) -> bool:
        """Check if a field is required.
        
        Args:
            field_name: Name of the field
            
        Returns:
            bool: True if field is required, False otherwise
        """
        return field_name in self.schema.get('required', [])
    
    def get_schema(self) -> Dict:
        """Get the loaded schema.
        
        Returns:
            Dict containing the schema
        """
        return self.schema
