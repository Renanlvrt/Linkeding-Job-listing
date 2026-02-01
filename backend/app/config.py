"""
Configuration settings using Pydantic Settings.
Loads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""  # For HS256 JWT verification (optional)
    
    # Gemini AI
    gemini_api_key: str = ""
    
    # RapidAPI (for LinkedIn scraping)
    rapidapi_key: str = ""
    
    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"
    production_url: str = ""  # Set in production via env var
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
