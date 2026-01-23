"""MCP Server for drone compliance data."""

import json
import os
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools.flight_log import get_flight_log
from .tools.pilot import get_pilot
from .tools.aircraft import get_aircraft
from .tools.mission import get_mission
from .tools.maintenance import get_maintenance_history
from .tools.list_files import list_files
from .tools.read_file import read_file
from .tools.file_metadata import get_file_metadata
from .database import get_db, seed_demo_data

# Create MCP server
server = Server("compliance-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_flight_log",
            description="Retrieve parsed flight log data for a specific flight",
            inputSchema={
                "type": "object",
                "properties": {
                    "flight_id": {
                        "type": "string",
                        "description": "Unique flight identifier"
                    }
                },
                "required": ["flight_id"]
            }
        ),
        Tool(
            name="get_pilot",
            description="Retrieve pilot certification and credentials",
            inputSchema={
                "type": "object",
                "properties": {
                    "pilot_id": {
                        "type": "string",
                        "description": "Pilot identifier or certificate number"
                    }
                },
                "required": ["pilot_id"]
            }
        ),
        Tool(
            name="get_aircraft",
            description="Retrieve aircraft registration and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "aircraft_id": {
                        "type": "string",
                        "description": "Aircraft ID or FAA registration"
                    }
                },
                "required": ["aircraft_id"]
            }
        ),
        Tool(
            name="get_mission",
            description="Retrieve mission planning data for a flight",
            inputSchema={
                "type": "object",
                "properties": {
                    "flight_id": {
                        "type": "string",
                        "description": "Flight identifier"
                    }
                },
                "required": ["flight_id"]
            }
        ),
        Tool(
            name="get_maintenance_history",
            description="Retrieve maintenance records for an aircraft",
            inputSchema={
                "type": "object",
                "properties": {
                    "aircraft_id": {
                        "type": "string",
                        "description": "Aircraft identifier"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records to return",
                        "default": 10
                    }
                },
                "required": ["aircraft_id"]
            }
        ),
        # File access tools
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
    db = get_db()

    try:
        if name == "get_flight_log":
            result = get_flight_log(db, arguments["flight_id"])
        elif name == "get_pilot":
            result = get_pilot(db, arguments["pilot_id"])
        elif name == "get_aircraft":
            result = get_aircraft(db, arguments["aircraft_id"])
        elif name == "get_mission":
            result = get_mission(db, arguments["flight_id"])
        elif name == "get_maintenance_history":
            limit = arguments.get("limit", 10)
            result = get_maintenance_history(db, arguments["aircraft_id"], limit)
        # File access tools (no database needed)
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
    # Seed demo data if in development
    if os.environ.get("SEED_DEMO_DATA", "true").lower() == "true":
        seed_demo_data()

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
