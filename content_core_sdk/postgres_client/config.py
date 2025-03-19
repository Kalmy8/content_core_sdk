from typing import Any
from pydantic import BaseSettings, Field


class PostgresConfig(BaseSettings):
    """Configuration for PostgreSQL connection"""
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(5432, env="POSTGRES_PORT")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    database: str = Field(..., env="POSTGRES_DB")
    min_connections: int = Field(1, env="POSTGRES_MIN_CONNECTIONS")
    max_connections: int = Field(10, env="POSTGRES_MAX_CONNECTIONS")
    connection_timeout: float = Field(60.0, env="POSTGRES_CONNECTION_TIMEOUT")
    command_timeout: float = Field(30.0, env="POSTGRES_COMMAND_TIMEOUT")
    
    @classmethod
    def from_env(cls) -> "PostgresConfig":
        """Creates a PostgresConfig instance from environment variables"""
        return cls() 