""
Module for loading and processing Conga query files.
"""
import re
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class CongaQueryLoader:
    """Loader for Conga query files."""
    
    def __init__(self, query_data: Optional[Union[Dict, str, Path]] = None):
        """Initialize the query loader.
        
        Args:
            query_data: Query data as a dict, JSON string, or file path
        """
        self.queries = {}
        self._load_queries(query_data)
    
    def _load_queries(self, query_data: Optional[Union[Dict, str, Path]]) -> None:
        """Load queries from various input types.
        
        Args:
            query_data: Query data as a dict, JSON string, or file path
        """
        if not query_data:
            return
            
        try:
            if isinstance(query_data, dict):
                self.queries = query_data
            elif isinstance(query_data, (str, Path)):
                # Try to load from file if path exists
                path = Path(query_data)
                if path.exists() and path.is_file():
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Try to parse as JSON first
                        try:
                            self.queries = json.loads(content)
                        except json.JSONDecodeError:
                            # If not JSON, treat as SOQL/SOSL query
                            self.queries = {'default': content}
                else:
                    # Try to parse as JSON string
                    try:
                        self.queries = json.loads(str(query_data))
                    except json.JSONDecodeError:
                        # Treat as a single query
                        self.queries = {'default': str(query_data)}
        except Exception as e:
            raise ValueError(f"Error loading query data: {str(e)}")
    
    def get_query(self, query_name: str = 'default') -> Optional[str]:
        """Get a query by name.
        
        Args:
            query_name: Name of the query to retrieve
            
        Returns:
            Query string if found, None otherwise
        """
        # If no queries loaded, return None
        if not self.queries:
            return None
            
        # If query_name is 'default' and we have a single query, return it
        if query_name == 'default' and len(self.queries) == 1:
            return next(iter(self.queries.values()))
            
        # Otherwise try to get the named query
        return self.queries.get(query_name)
    
    def get_all_queries(self) -> Dict[str, str]:
        """Get all loaded queries.
        
        Returns:
            Dict mapping query names to query strings
        """
        return self.queries
    
    def extract_query_metadata(self, query: str) -> Dict[str, Any]:
        """Extract metadata from a SOQL/SOSL query.
        
        Args:
            query: The query string to analyze
            
        Returns:
            Dict containing extracted metadata
        """
        if not query:
            return {}
            
        metadata = {
            'type': 'unknown',
            'object': None,
            'fields': [],
            'conditions': [],
            'limit': None,
            'order_by': [],
            'is_count': False
        }
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        # Check query type
        query_upper = query.upper()
        
        if query_upper.startswith('SELECT'):
            metadata['type'] = 'SOQL'
            
            # Extract fields
            field_match = re.search(r'SELECT\s+(.*?)\s+FROM', query_upper, re.IGNORECASE | re.DOTALL)
            if field_match:
                fields_str = query[field_match.start(1):field_match.end(1)]
                metadata['fields'] = [f.strip() for f in fields_str.split(',')]
            
            # Extract object
            from_match = re.search(r'FROM\s+([\w\.]+)', query_upper, re.IGNORECASE)
            if from_match:
                metadata['object'] = query[from_match.start(1):from_match.end(1)]
            
            # Check for COUNT
            if 'COUNT()' in query_upper or 'COUNT_DISTINCT(' in query_upper:
                metadata['is_count'] = True
            
            # Extract WHERE conditions
            where_match = re.search(r'WHERE\s+(.*?)(?:\s+GROUP BY|\s+ORDER BY|\s+LIMIT|\s+OFFSET|\s*$)', 
                                 query_upper, re.IGNORECASE | re.DOTALL)
            if where_match:
                where_clause = query[where_match.start(1):where_match.end(1)]
                metadata['conditions'] = self._extract_conditions(where_clause)
            
            # Extract ORDER BY
            order_match = re.search(r'ORDER BY\s+(.*?)(?:\s+LIMIT|\s+OFFSET|\s*$)', 
                                 query_upper, re.IGNORECASE | re.DOTALL)
            if order_match:
                order_clause = query[order_match.start(1):order_match.end(1)]
                metadata['order_by'] = [o.strip() for o in order_clause.split(',')]
            
            # Extract LIMIT
            limit_match = re.search(r'LIMIT\s+(\d+)', query_upper, re.IGNORECASE)
            if limit_match:
                metadata['limit'] = int(query[limit_match.start(1):limit_match.end(1)])
                
        elif query_upper.startswith('FIND'):
            metadata['type'] = 'SOSL'
            # TODO: Add SOSL-specific parsing
        
        return metadata
    
    def _extract_conditions(self, where_clause: str) -> List[Dict[str, Any]]:
        """Extract conditions from a WHERE clause.
        
        Args:
            where_clause: The WHERE clause string
            
        Returns:
            List of condition dictionaries
        """
        if not where_clause:
            return []
            
        # This is a simplified implementation
        # A real implementation would need to handle nested conditions, logical operators, etc.
        conditions = []
        
        # Split by AND/OR, but not inside quotes or parentheses
        # This is a simple approximation and may not handle all cases
        parts = re.split(r'\s+(?:AND|OR)\s+(?=(?:[^\"\']*[\"\'][^\"\']*[\"\'])*[^\"\']*$)', 
                        where_clause, flags=re.IGNORECASE)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Simple pattern matching for field operator value
            match = re.match(r'([\w\.]+)\s*([=!<>]+|LIKE|IN|NOT\s+IN|INCLUDES|EXCLUDES)\s*(.+)', part, re.IGNORECASE)
            if match:
                field, operator, value = match.groups()
                conditions.append({
                    'field': field.strip(),
                    'operator': operator.strip().upper(),
                    'value': value.strip()
                })
        
        return conditions
    
    def get_referenced_fields(self, query_name: str = 'default') -> List[str]:
        """Get fields referenced in a query.
        
        Args:
            query_name: Name of the query
            
        Returns:
            List of field names
        """
        query = self.get_query(query_name)
        if not query:
            return []
            
        metadata = self.extract_query_metadata(query)
        fields = set(metadata.get('fields', []))
        
        # Add fields from conditions
        for condition in metadata.get('conditions', []):
            fields.add(condition.get('field', '').split('.')[-1])
        
        # Add fields from ORDER BY
        for order in metadata.get('order_by', []):
            # Remove ASC/DESC and whitespace
            field = re.sub(r'\s+(?:ASC|DESC)$', '', order, flags=re.IGNORECASE).strip()
            fields.add(field)
        
        return sorted(f for f in fields if f)
