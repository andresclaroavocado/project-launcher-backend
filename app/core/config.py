"""
Multi-model configuration for AI-powered project architect
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Multi-Model Project Architect"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_HOSTS: list = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_HOSTS"
    )
    
    # AI APIs
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    GOOSE_AI_API_KEY: Optional[str] = Field(default=None, env="GOOSE_AI_API_KEY")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    # LLM Configuration
    MAX_TOKENS: int = Field(default=4000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    
    # Conversation
    MAX_CONVERSATION_LENGTH: int = Field(default=50, env="MAX_CONVERSATION_LENGTH")
    CONVERSATION_TIMEOUT: int = Field(default=3600, env="CONVERSATION_TIMEOUT")  # 1 hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings() 