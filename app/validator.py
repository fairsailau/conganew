"""
Validation engine for checking conversion quality
"""
import re
from typing import Dict, List, Any, Optional
import docx
from box_ai_client import BoxAIClient


class ValidationEngine:
    """
    Engine for validating the conversion from Conga to Box DocGen
    """
    
    def __init__(self, box_ai_client: Optional[BoxAIClient] = None):
        """
        Initialize the validation engine
        
        Args:
            box_ai_client: BoxAIClient instance for AI-assisted validation
        """
        self.box_ai_client = box_ai_client
        
    def validate_conversion(self, original_content: str, converted_content: str, 
                           original_tags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the conversion by comparing original and converted templates
        
        Args:
            original_content: Original Conga template content
            converted_content: Converted Box DocGen template content
            original_tags: List of original Conga tags
            
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'syntax_valid': self._check_syntax(converted_content),
            'completeness': self._check_completeness(original_tags, converted_content),
            'errors': [],
            'warnings': []
        }
        
        # Check for common errors
        self._check_for_errors(converted_content, validation_results)
        
        # Use AI for additional validation if available
        if self.box_ai_client:
            ai_validation = self._ai_validation(original_content, converted_content)
            if ai_validation:
                validation_results['ai_validation'] = ai_validation
        
        return validation_results
        
    def _check_syntax(self, content: str) -> bool:
        """
        Check if the converted template has valid Box DocGen syntax
        
        Args:
            content: Converted template content
            
        Returns:
            True if syntax is valid, False otherwise
        """
        # Check for balanced handlebars
        open_tags = len(re.findall(r'\{\{[^}]+', content))
        close_tags = len(re.findall(r'\}\}', content))
        
        if open_tags != close_tags:
            return False
        
        # Check for balanced conditional blocks
        conditionals = {
            '#if': '/if',
            '#eq': '/eq',
            '#gt': '/gt',
            '#lt': '/lt',
            '#each': '/each'
        }
        
        for open_tag, close_tag in conditionals.items():
            open_count = len(re.findall(r'\{\{' + open_tag + r'[^}]+\}\}', content))
            close_count = len(re.findall(r'\{\{' + close_tag + r'\}\}', content))
            
            if open_count != close_count:
                return False
        
        return True
        
    def _check_completeness(self, original_tags: List[Dict[str, Any]], 
                           converted_content: str) -> float:
        """
        Check if all Conga tags have been converted
        
        Args:
            original_tags: List of original Conga tags
            converted_content: Converted template content
            
        Returns:
            Completeness score (0.0 to 1.0)
        """
        total_tags = len(original_tags)
        if total_tags == 0:
            return 1.0
            
        # Count how many original tags are no longer present
        converted_tags = 0
        
        for tag in original_tags:
            if tag['full_match'] not in converted_content:
                converted_tags += 1
        
        return converted_tags / total_tags
    
    def _check_for_errors(self, content: str, results: Dict[str, Any]) -> None:
        """
        Check for common errors in the converted template
        
        Args:
            content: Converted template content
            results: Dictionary to store errors and warnings
        """
        # Check for unconverted Conga tags
        conga_patterns = [
            (r'&=[A-Za-z0-9._]+', 'Unconverted Conga merge field'),
            (r'\{IF\s+', 'Unconverted Conga conditional'),
            (r'\{TABLE\s+', 'Unconverted Conga table start'),
            (r'\{END\s+', 'Unconverted Conga table end')
        ]
        
        for pattern, error_msg in conga_patterns:
            matches = re.findall(pattern, content)
            if matches:
                results['errors'].append({
                    'type': error_msg,
                    'instances': matches
                })
        
        # Check for malformed Box DocGen tags
        box_patterns = [
            (r'\{\{[^}]*\{\{', 'Nested Box DocGen tags'),
            (r'\}\}[^{]*\}\}', 'Consecutive closing tags'),
            (r'\{\{#[^}]+\}\}(?:(?!\{\{\/[^}]+\}\}).)*$', 'Unclosed conditional block')
        ]
        
        for pattern, error_msg in box_patterns:
            matches = re.findall(pattern, content)
            if matches:
                results['errors'].append({
                    'type': error_msg,
                    'instances': matches
                })
    
    def _ai_validation(self, original: str, converted: str) -> Optional[Dict[str, Any]]:
        """
        Use Box AI to validate the conversion
        
        Args:
            original: Original Conga template content
            converted: Converted Box DocGen template content
            
        Returns:
            Dictionary with AI validation results or None if not available
        """
        if not self.box_ai_client:
            return None
            
        # Limit content size for API
        original_sample = original[:2000] if len(original) > 2000 else original
        converted_sample = converted[:2000] if len(converted) > 2000 else converted
        
        prompt = f"""
        Compare these two templates and identify any issues or discrepancies:
        
        Original Conga template:
        {original_sample}
        
        Converted Box DocGen template:
        {converted_sample}
        
        Focus on:
        1. Missing fields or tags
        2. Incorrect syntax
        3. Logic errors in conditionals
        4. Table structure issues
        
        Return a JSON with these keys:
        - issues: array of specific issues found
        - quality_score: number from 0-10
        - recommendations: array of suggestions to improve conversion
        """
        
        response = self.box_ai_client.ask_ai(prompt, content=f"{original_sample}\n\n---\n\n{converted_sample}")
        if 'answer' in response:
            return {
                'ai_analysis': response['answer']
            }
            
        return None
