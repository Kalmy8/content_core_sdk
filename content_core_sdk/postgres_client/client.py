"""
PostgreSQL client interface providing access to database entities.
"""
from __future__ import annotations
from functools import lru_cache
from typing import List, Callable, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from content_core_sdk.postgres_client.database import async_session_maker
from content_core_sdk.postgres_client.config import PostgresConfig
from content_core_sdk.postgres_client.models.character_model import Agent
from content_core_sdk.common.result import Result


class PostgresClient:
    """
    Client for PostgreSQL database operations.
    Provides a simplified interface for common database operations.
    """
    
    def __init__(self, config: PostgresConfig, session_factory: Callable[[], AsyncSession]) -> None:
        """
        Initialize the PostgreSQL client.
        
        Args:
            config: PostgreSQL connection configuration
            session_factory: Factory function that returns a new database session
        """
        self.config = config
        self.session_factory = session_factory
    
    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Context manager for database sessions with proper error handling.
        
        Automatically handles rollback on error and ensures session is closed.
        
        Yields:
            AsyncSession: Database session
        """
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    async def get_agent_by_name(self, name: str) -> Result[Agent | None]:
        """
        Get an agent by its unique name.
        
        Args:
            name: The unique name of the agent
            
        Returns:
            Result containing the agent if found, None if not found, or an error
        """
        try:
            async with self.session() as session:
                stmt = select(Agent).where(Agent.name == name)
                result = await session.execute(stmt)
                agent = result.scalars().first()
                return Result.success(agent)
        except Exception as e:
            return Result.error(f"Failed to get agent by name: {str(e)}", e)
    
    async def get_agent_by_ticker(self, ticker: str) -> Result[Agent | None]:
        """
        Get an agent by its unique ticker.
        
        Args:
            ticker: The unique ticker of the agent
            
        Returns:
            Result containing the agent if found, None if not found, or an error
        """
        try:
            async with self.session() as session:
                stmt = select(Agent).where(Agent.ticker == ticker)
                result = await session.execute(stmt)
                agent = result.scalars().first()
                return Result.success(agent)
        except Exception as e:
            return Result.error(f"Failed to get agent by ticker: {str(e)}", e)
    
    async def get_all_agents(self, limit: int = 100, offset: int = 0) -> Result[List[Agent] | None]:
        """
        Get all agents with pagination.
        
        Args:
            limit: Maximum number of agents to return
            offset: Number of agents to skip
            
        Returns:
            Result containing a list of agents or an error
        """
        try:
            async with await self.get_session() as session:
                stmt = select(Agent).limit(limit).offset(offset)
                result = await session.execute(stmt)
                agents = result.scalars().all()
                return Result.success(list(agents))
        except Exception as e:
            return Result.error(f"Failed to get all agents: {str(e)}", e)
    

@lru_cache(maxsize=1)
def get_postgres_client() -> Result[PostgresClient]:
    """
    Get a singleton instance of the PostgreSQL client.
    This function is cached to return the same instance for multiple calls.
    
    Returns:
        Result containing either the PostgreSQL client or an error
    """
    try:
        config = PostgresConfig()
        return Result.success(PostgresClient(
            config=config,
            session_factory=async_session_maker
        ))
    except Exception as e:
        return Result.error(f"Failed to initialize PostgreSQL client: {str(e)}", e) 