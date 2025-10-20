"""
URL and input validation utilities
"""

import validators
from urllib.parse import urlparse
from typing import Tuple


class URLValidator:
    """URL validation and normalization"""
    
    @staticmethod
    def is_valid(url: str) -> bool:
        """
        Check if URL is valid
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid, False otherwise
        """
        return validators.url(url) is True
    
    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize URL (add scheme if missing, etc.)
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @staticmethod
    def validate_and_normalize(url: str) -> Tuple[bool, str, str]:
        """
        Validate and normalize URL
        
        Args:
            url: URL to process
            
        Returns:
            Tuple of (is_valid, normalized_url, error_message)
        """
        if not url:
            return False, "", "URL cannot be empty"
        
        normalized = URLValidator.normalize(url)
        
        if not URLValidator.is_valid(normalized):
            return False, normalized, "Invalid URL format"
        
        return True, normalized, ""
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: URL to parse
            
        Returns:
            Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc or parsed.path


def validate_url(url: str) -> Tuple[bool, str, str]:
    """
    Convenience function for URL validation
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, normalized_url, error_message)
    """
    return URLValidator.validate_and_normalize(url)

