""
Module for parsing AI responses for template conversion.
"""
import re
import json
from typing import Dict, List, Optional, Any, Tuple


class AIResponseParser:
    """Parser for AI responses related to template conversion."""
    
    @staticmethod
    def parse_conversion_result(response: str) -> Dict[str, Any]:
        """Parse the AI's response for template conversion.
        
        Args:
            response: Raw response string from the AI
            
        Returns:
            Dict containing parsed components of the response
        """
        # Initialize result with default values
        result = {
            'content': '',
            'warnings': [],
            'confidence': 1.0,
            'metadata': {}
        }
        
        # Try to parse as JSON first (if the AI returns a structured response)
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                result.update({
                    'content': data.get('content', ''),
                    'warnings': data.get('warnings', []),
                    'confidence': float(data.get('confidence', 1.0)),
                    'metadata': data.get('metadata', {})
                })
                return result
        except (json.JSONDecodeError, TypeError):
            pass
        
        # If not JSON or parsing failed, treat the entire response as content
        result['content'] = response.strip()
        
        # Try to extract any warnings or notes from the response
        warning_patterns = [
            r'Note:\s*(.*?)(?=\n\n|$)',
            r'Warning:\s*(.*?)(?=\n\n|$)',
            r'Note that (.*?)(?=\n\n|$)'
        ]
        
        for pattern in warning_patterns:
            warnings = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if warnings:
                result['warnings'].extend([w.strip() for w in warnings if w.strip()])
        
        # Extract confidence if mentioned
        confidence_match = re.search(r'confidence[\s:]+([0-9.]+)', response, re.IGNORECASE)
        if confidence_match:
            try:
                result['confidence'] = float(confidence_match.group(1))
            except (ValueError, TypeError):
                pass
        
        return result
    
    @staticmethod
    def parse_validation_result(response: str) -> Dict[str, Any]:
        """Parse the AI's response for template validation.
        
        Args:
            response: Raw response string from the AI
            
        Returns:
            Dict containing validation results and issues
        """
        # Initialize result with default values
        result = {
            'is_valid': True,
            'issues': [],
            'confidence': 1.0,
            'suggestions': []
        }
        
        # Try to parse as JSON first
        try:
            data = json.loads(response)
            if isinstance(data, dict):
                result.update({
                    'is_valid': data.get('is_valid', True),
                    'issues': data.get('issues', []),
                    'confidence': float(data.get('confidence', 1.0)),
                    'suggestions': data.get('suggestions', [])
                })
                return result
        except (json.JSONDecodeError, TypeError):
            pass
        
        # If not JSON, try to parse the response text
        # Look for validation results in the text
        valid_match = re.search(r'validation\s+(?:result|status)[\s:]+(pass|fail|valid|invalid)', 
                              response, re.IGNORECASE)
        if valid_match:
            result['is_valid'] = valid_match.group(1).lower() in ('pass', 'valid')
        
        # Extract issues
        issue_sections = re.split(r'##?\s*(?:Issue|Problem|Error)', response, flags=re.IGNORECASE)
        if len(issue_sections) > 1:
            for section in issue_sections[1:]:
                # Extract issue description (first paragraph)
                description = section.split('\n\n')[0].strip()
                if description:
                    result['issues'].append({
                        'description': description,
                        'severity': 'error',
                        'location': None
                    })
        
        # Extract suggestions
        suggestion_sections = re.split(r'##?\s*Suggestion', response, flags=re.IGNORECASE)
        if len(suggestion_sections) > 1:
            for section in suggestion_sections[1:]:
                # Extract suggestion (first paragraph)
                suggestion = section.split('\n\n')[0].strip()
                if suggestion:
                    result['suggestions'].append(suggestion)
        
        # Extract confidence if mentioned
        confidence_match = re.search(r'confidence[\s:]+([0-9.]+)', response, re.IGNORECASE)
        if confidence_match:
            try:
                result['confidence'] = float(confidence_match.group(1))
            except (ValueError, TypeError):
                pass
        
        return result
