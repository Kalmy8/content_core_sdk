from functools import lru_cache
from typing import Any, AsyncGenerator
import asyncpg
from asyncpg import Pool, Connection
from content_core_sdk.postgres_client.config import PostgresConfig


class PostgresService:
    def __init__(self, config: PostgresConfig) -> None:
        self.config = config
        self._pool: Pool | None = None

    async def _get_pool(self) -> Pool:
        """
        Lazily initialize the connection pool.
        
        Returns:
            Connection pool instance
        """
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                timeout=self.config.connection_timeout,
                command_timeout=self.config.command_timeout
            )
        return self._pool

    async def execute(self, query: str, *args: Any) -> str:
        """
        Execute a SQL query that doesn't return rows.
        
        Args:
            query: SQL query to execute
            args: Query parameters
            
        Returns:
            Command completion tag
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """
        Execute a query and return all results as a list.
        
        Args:
            query: SQL query to execute
            args: Query parameters
            
        Returns:
            List of records
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """
        Execute a query and return the first row.
        
        Args:
            query: SQL query to execute
            args: Query parameters
            
        Returns:
            First record or None if no rows returned
        """
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def transaction(self) -> Connection:
        """
        Get a connection with a transaction started.
        
        Returns:
            Database connection with active transaction
        """
        pool = await self._get_pool()
        return await pool.acquire()

    async def close(self) -> None:
        """Cleanup all resources"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None


@lru_cache(maxsize=1)
def get_postgres_service() -> PostgresService:
    """
    Returns a singleton instance of PostgresService.
    """
    config = PostgresConfig.from_env()
    return PostgresService(config=config) 