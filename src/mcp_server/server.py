"""MCP Server for drone compliance data.

Provides 3 generic database tools + file access tools.
All database operations are READ-ONLY.
"""

import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools.database import list_entities, describe_entity, query_entity
from .tools.list_files import list_files
from .tools.read_file import read_file
from .tools.file_metadata import get_file_metadata

# Create MCP server
server = Server("compliance-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        # === Database Tools (Generic, Read-Only) ===
        Tool(
            name="list_entities",
            description="List all available data entities (tables). Call this first to see what data is available.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="describe_entity",
            description="Describe the fields available for a specific entity. Call this to understand what data an entity contains.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "Entity name (e.g., pilots, aircraft, flights)"
                    }
                },
                "required": ["entity"]
            }
        ),
        Tool(
            name="query_entity",
            description="Query data from an entity. Get single record by ID, or multiple records with filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "Entity name (e.g., pilots, aircraft, flights)"
                    },
                    "id": {
                        "type": "string",
                        "description": "Optional: Get single record by ID"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional: Filter conditions as {field: value}",
                        "additionalProperties": True
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Specific fields to return"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records to return (default: 100)",
                        "default": 100
                    }
                },
                "required": ["entity"]
            }
        ),
        # === File Access Tools ===
        Tool(
            name="list_files",
            description="List files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files",
                        "default": "*"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="read_file",
            description="Read file content",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "max_bytes": {
                        "type": "integer",
                        "description": "Maximum bytes to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "Text encoding",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_file_metadata",
            description="Get file metadata (size, type, dates)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    }
                },
                "required": ["path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool invocations."""
    try:
        # Database tools (read-only)
        if name == "list_entities":
            result = list_entities()

        elif name == "describe_entity":
            result = describe_entity(arguments["entity"])

        elif name == "query_entity":
            result = query_entity(
                entity=arguments["entity"],
                id=arguments.get("id"),
                filters=arguments.get("filters"),
                fields=arguments.get("fields"),
                limit=arguments.get("limit", 100),
            )

        # File access tools
        elif name == "list_files":
            result = list_files(
                arguments["directory"],
                arguments.get("pattern", "*"),
                arguments.get("recursive", False),
            )

        elif name == "read_file":
            result = read_file(
                arguments["path"],
                arguments.get("max_bytes"),
                arguments.get("encoding", "utf-8"),
            )

        elif name == "get_file_metadata":
            result = get_file_metadata(arguments["path"])

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Entry point."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
