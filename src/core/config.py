"""
AUTOFLOW OS - Application Configuration
Using Pydantic Settings for type-safe configuration management
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----------------------------------------
    # Application
    # ----------------------------------------
    app_name: str = "AUTOFLOW OS"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", description="development/staging/production")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    secret_key: str = Field(default="change-me-in-production")

    # ----------------------------------------
    # Telegram Bot
    # ----------------------------------------
    telegram_bot_token: str = Field(..., description="Telegram Bot Token from @BotFather")
    telegram_admin_ids: str = Field(default="", description="Comma-separated admin user IDs")

    @property
    def admin_ids(self) -> List[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.telegram_admin_ids:
            return []
        return [int(id.strip()) for id in self.telegram_admin_ids.split(",") if id.strip()]

    # ----------------------------------------
    # Database
    # ----------------------------------------
    database_url: str = Field(
        default="postgresql://autoflow:autoflow@localhost:5432/autoflow_db",
        description="PostgreSQL connection string",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    # ----------------------------------------
    # AI Configuration
    # ----------------------------------------
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    ai_model: str = Field(default="gpt-4-turbo-preview")

    @property
    def ai_provider(self) -> str:
        """Determine AI provider based on available keys."""
        if self.anthropic_api_key:
            return "anthropic"
        return "openai"

    # ----------------------------------------
    # 1C Integration
    # ----------------------------------------
    onec_api_url: str = Field(default="http://localhost:8080/api/v1")
    onec_api_token: Optional[str] = Field(default=None)
    onec_sync_interval: int = Field(default=300, description="Sync interval in seconds")

    # ----------------------------------------
    # SMS Gateway
    # ----------------------------------------
    sms_api_key: Optional[str] = Field(default=None)
    sms_sender_name: str = Field(default="AUTOFLOW")

    # ----------------------------------------
    # Server
    # ----------------------------------------
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    webhook_url: Optional[str] = Field(default=None)

    # ----------------------------------------
    # ChromaDB
    # ----------------------------------------
    chroma_persist_dir: str = Field(default="./data/chroma")
    chroma_collection_name: str = Field(default="autoflow_knowledge")

    # ----------------------------------------
    # Validators
    # ----------------------------------------
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return upper_v


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Usage:
        from src.core.config import get_settings
        settings = get_settings()
    """
    return Settings()


# Convenience alias
settings = get_settings()
