"""
Application settings and configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = "Web Scraper & LLM Analyzer"
    debug: bool = False
    log_level: str = "INFO"
    
    # Analysis Settings
    default_timeout: int = 30
    max_page_size_mb: int = 10
    enable_headless_browser: bool = True
    
    # Browser Settings
    browser_type: str = "chromium"  # chromium, firefox, webkit
    browser_headless: bool = True
    browser_timeout: int = 30000
    
    # Rate Limiting
    max_concurrent_analyses: int = 3
    request_delay_seconds: float = 1.0
    
    # Token Estimation
    default_token_model: str = "cl100k_base"
    
    # Export Settings
    export_dir: str = "./exports"
    enable_pdf_export: bool = True
    enable_json_export: bool = True
    
    # User Agent
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

