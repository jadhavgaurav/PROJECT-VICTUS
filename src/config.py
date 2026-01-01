"""
Configuration settings for Project VICTUS
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Project VICTUS configuration settings loaded from .env file or environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API Keys
    OPENAI_API_KEY: str
    TAVILY_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    
    # Microsoft 365 Auth
    MS_CLIENT_ID: Optional[str] = None
    MS_CLIENT_SECRET: Optional[str] = None
    MS_TENANT_ID: Optional[str] = None
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = None
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # Application Config
    DATABASE_URL: str = "sqlite:///./chat_history.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Security
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Environment
    ENVIRONMENT: str = "development"
    
    # Production Settings
    DEBUG: bool = False

    def validate_settings(self) -> None:
        """Validate that required settings are present."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Production warnings
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "your-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be changed in production!")
            if "*" in self.CORS_ORIGINS:
                import warnings
                warnings.warn("CORS_ORIGINS is set to '*' in production. This is insecure!")

# Instantiate settings to be imported across the application
settings = Settings()

