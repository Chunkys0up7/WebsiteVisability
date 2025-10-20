"""
General utility functions
"""

import re
from urllib.parse import urlparse
from typing import Optional
from difflib import SequenceMatcher


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


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


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable string
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    return SequenceMatcher(None, text1, text2).ratio()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_text_preview(text: str, max_words: int = 50) -> str:
    """
    Extract preview of text (first N words)
    
    Args:
        text: Full text
        max_words: Maximum number of words
        
    Returns:
        Text preview
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'


def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    return len(text.split())


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary value
    
    Args:
        dictionary: Dictionary to search
        *keys: Nested keys to traverse
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    for key in keys:
        if isinstance(dictionary, dict):
            dictionary = dictionary.get(key, default)
        else:
            return default
    return dictionary

