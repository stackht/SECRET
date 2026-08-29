"""Neo4j driver singleton.

Phase 1: scaffolding. Provides a lazily-created async driver. Phase 2 wires
this into the GraphService for traversal / materialization.
"""
from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase

from app.core.config import get_settings


class Neo4jConnection:
    """Holds a lazily created Neo4j async driver."""

    def __init__(self) -> None:
        self._driver: Optional[AsyncDriver] = None

    def _connect(self) -> AsyncDriver:
        settings = get_settings()
        return AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    @property
    def driver(self) -> AsyncDriver:
        """Return (creating if needed) the async driver."""
        if self._driver is None:
            self._driver = self._connect()
        return self._driver

    async def close(self) -> None:
        """Close the driver if open."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None


neo4j_connection = Neo4jConnection()
