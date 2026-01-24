"""
Data Adapter for MCP Server

Translates queries from the standard compliance schema to customer's actual database schema
using the data_mapping.yaml configuration.
"""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


class DataAdapter:
    """
    Adapts database queries to customer's schema using YAML mapping.

    The mapping file (data_mapping.yaml) defines:
    - Source tables for each entity (pilots, aircraft, flights, etc.)
    - Column mappings from customer columns to compliance schema
    - Optional filters

    Example mapping:
        entities:
          pilots:
            source_table: operators
            columns:
              id: operator_id
              name: full_name
              certificate_number: faa_cert_no
            filter: status = 'active'
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        mapping_path: Optional[Path] = None,
    ):
        """
        Initialize the data adapter.

        Args:
            db_url: Database connection URL (defaults to DATABASE_URL env var)
            mapping_path: Path to data_mapping.yaml (defaults to ./data_mapping.yaml)
        """
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.mapping_path = mapping_path or Path.cwd() / "data_mapping.yaml"

        self._engine = None
        self._session_factory = None
        self._mapping = None

    @property
    def engine(self):
        """Lazy-load database engine."""
        if self._engine is None:
            if not self.db_url:
                raise ValueError("DATABASE_URL not configured")
            self._engine = create_engine(self.db_url)
        return self._engine

    @property
    def mapping(self) -> dict:
        """Lazy-load data mapping configuration."""
        if self._mapping is None:
            if self.mapping_path.exists():
                with open(self.mapping_path) as f:
                    self._mapping = yaml.safe_load(f) or {}
            else:
                self._mapping = {}
        return self._mapping

    def get_session(self) -> Session:
        """Get a database session."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory()

    def get_entity_config(self, entity_name: str) -> Optional[dict]:
        """Get mapping configuration for an entity."""
        return self.mapping.get("entities", {}).get(entity_name)

    def build_select_query(
        self,
        entity_name: str,
        where_clause: Optional[str] = None,
        where_params: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> tuple[str, dict]:
        """
        Build a SELECT query using the mapping configuration.

        Args:
            entity_name: Entity type (pilots, aircraft, flights, etc.)
            where_clause: Additional WHERE conditions (e.g., "id = :id")
            where_params: Parameters for WHERE clause
            limit: Maximum rows to return

        Returns:
            Tuple of (SQL query string, parameters dict)
        """
        config = self.get_entity_config(entity_name)
        if not config:
            raise ValueError(f"No mapping configured for entity: {entity_name}")

        source_table = config.get("source_table")
        columns = config.get("columns", {})
        base_filter = config.get("filter")

        if not source_table:
            raise ValueError(f"No source_table configured for entity: {entity_name}")

        # Build SELECT clause with aliases
        select_parts = []
        for target_col, source_col in columns.items():
            if source_col:
                select_parts.append(f"{source_col} AS {target_col}")

        if not select_parts:
            raise ValueError(f"No columns mapped for entity: {entity_name}")

        select_clause = ", ".join(select_parts)

        # Build WHERE clause
        where_parts = []
        params = where_params or {}

        if base_filter:
            where_parts.append(f"({base_filter})")

        if where_clause:
            where_parts.append(f"({where_clause})")

        where_sql = " AND ".join(where_parts) if where_parts else "1=1"

        # Build full query
        query = f"SELECT {select_clause} FROM {source_table} WHERE {where_sql}"

        if limit:
            query += f" LIMIT {limit}"

        return query, params

    def query_one(
        self,
        entity_name: str,
        id_value: str,
        id_column: str = "id",
    ) -> Optional[dict]:
        """
        Query a single record by ID.

        Args:
            entity_name: Entity type
            id_value: ID value to look up
            id_column: Column name for ID (default: "id")

        Returns:
            Dict with mapped column names, or None if not found
        """
        config = self.get_entity_config(entity_name)
        if not config:
            return None

        # Get the source column name for the ID
        columns = config.get("columns", {})
        source_id_col = columns.get(id_column, id_column)

        query, params = self.build_select_query(
            entity_name,
            where_clause=f"{source_id_col} = :id_value",
            where_params={"id_value": id_value},
            limit=1,
        )

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            row = result.fetchone()

            if row:
                return dict(row._mapping)

        return None

    def query_many(
        self,
        entity_name: str,
        where_clause: Optional[str] = None,
        where_params: Optional[dict] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Query multiple records.

        Args:
            entity_name: Entity type
            where_clause: Optional WHERE conditions
            where_params: Parameters for WHERE clause
            limit: Maximum rows to return

        Returns:
            List of dicts with mapped column names
        """
        config = self.get_entity_config(entity_name)
        if not config:
            return []

        query, params = self.build_select_query(
            entity_name,
            where_clause=where_clause,
            where_params=where_params,
            limit=limit,
        )

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return [dict(row._mapping) for row in result]

    def is_entity_configured(self, entity_name: str) -> bool:
        """Check if an entity has mapping configuration."""
        config = self.get_entity_config(entity_name)
        return bool(config and config.get("source_table") and config.get("columns"))

    def get_configured_entities(self) -> list[str]:
        """Get list of entities that have mapping configuration."""
        entities = self.mapping.get("entities", {})
        return [
            name for name, config in entities.items()
            if config.get("source_table") and config.get("columns")
        ]


# Global adapter instance (lazy-loaded)
_adapter: Optional[DataAdapter] = None


def get_adapter() -> DataAdapter:
    """Get the global data adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = DataAdapter()
    return _adapter


def reset_adapter() -> None:
    """Reset the global adapter (useful for testing or config changes)."""
    global _adapter
    _adapter = None
