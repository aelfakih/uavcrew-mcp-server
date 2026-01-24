"""MCP tools for compliance data access.

Database tools (read-only):
- list_entities: Discover available data
- describe_entity: See fields for an entity
- query_entity: Query data with filters

File tools (read-only):
- list_files: List directory contents
- read_file: Read file content
- get_file_metadata: Get file info
"""

from .database import list_entities, describe_entity, query_entity
from .list_files import list_files
from .read_file import read_file
from .file_metadata import get_file_metadata

__all__ = [
    # Database tools (generic, read-only)
    "list_entities",
    "describe_entity",
    "query_entity",
    # File tools (read-only)
    "list_files",
    "read_file",
    "get_file_metadata",
]
