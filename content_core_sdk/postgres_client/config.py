from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    """Configuration for PostgreSQL connection"""
    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=None,  # No default .env file, only use environment variables
        env_nested_delimiter="__",
        extra='ignore',
        case_sensitive=False
    )
    
    host: str
    port: int = 5432
    user: str
    password: str
    database: str
    min_connections: int = 1
    max_connections: int = 10
    connection_timeout: float = 60.0
    command_timeout: float = 30.0
    