"""Configuration management for MediaAgent."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    openrouter_model: str = Field(
        default="deepseek/deepseek-chat",
        description="Default AI model"
    )
    app_host: str = Field(default="0.0.0.0", description="App host")
    app_port: int = Field(default=8080, description="App port")
    debug: bool = Field(default=False, description="Debug mode")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./media_agent.db",
        description="Database URL"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_config_dir() -> Path:
    """Get config directory."""
    return get_project_root() / "config"


def get_db_path() -> Path:
    """Get database file path."""
    return get_project_root() / "media_agent.db"
