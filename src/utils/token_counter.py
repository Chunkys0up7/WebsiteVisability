"""
Token counting utilities for LLM analysis
"""

import tiktoken
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token counting for various LLM models"""
    
    def __init__(self, model: str = "cl100k_base"):
        """
        Initialize token counter
        
        Args:
            model: Tiktoken model name (cl100k_base for GPT-4, GPT-3.5-turbo)
        """
        self.model = model
        try:
            self.encoding = tiktoken.get_encoding(model)
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding {model}: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not self.encoding:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return len(text) // 4
    
    def estimate_cost(
        self,
        tokens: int,
        cost_per_1k_tokens: float = 0.01
    ) -> float:
        """
        Estimate cost for token count
        
        Args:
            tokens: Number of tokens
            cost_per_1k_tokens: Cost per 1000 tokens
            
        Returns:
            Estimated cost in dollars
        """
        return (tokens / 1000) * cost_per_1k_tokens


def estimate_tokens(text: str, model: str = "cl100k_base") -> int:
    """
    Convenience function to estimate token count
    
    Args:
        text: Text to count tokens for
        model: Tiktoken model name
        
    Returns:
        Estimated token count
    """
    counter = TokenCounter(model)
    return counter.count_tokens(text)

