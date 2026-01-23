"""HTTP wrapper for MCP server.

This provides an HTTP/JSON-RPC interface to the MCP tools,
allowing the compliance service to call MCP servers over the network.
"""

import json
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel

from .tools.flight_log import get_flight_log
from .tools.pilot import get_pilot
from .tools.aircraft import get_aircraft
from .tools.mission import get_mission
from .tools.maintenance import get_maintenance_history
from .tools.list_files import list_files
from .tools.read_file import read_file
from .tools.file_metadata import get_file_metadata
from .database import get_db, seed_demo_data


# Create FastAPI app
app = FastAPI(
    title="UAVCrew Compliance MCP Server",
    description="HTTP interface for MCP tools",
    version="1.0.0",
)


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int | str | None = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    result: Any = None
    error: dict | None = None
    id: int | str | None = None


# Load API key from environment
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")


def verify_auth(authorization: str | None) -> bool:
    """Verify authorization header."""
    if not MCP_API_KEY:
        return True  # No auth if key not configured

    if not authorization:
        return False

    # Support both "Bearer <key>" and raw key
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    return token == MCP_API_KEY


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    if os.environ.get("SEED_DEMO_DATA", "true").lower() == "true":
        seed_demo_data()


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "mcp-server"}


@app.post("/mcp")
async def mcp_endpoint(
    request: JSONRPCRequest,
    authorization: str | None = Header(None),
):
    """
    MCP JSON-RPC endpoint.

    Handles tool calls in JSON-RPC 2.0 format.
    """
    if not verify_auth(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # Only handle tools/call method
    if request.method != "tools/call":
        return JSONRPCResponse(
            error={"code": -32601, "message": f"Method not found: {request.method}"},
            id=request.id,
        )

    params = request.params
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return JSONRPCResponse(
            error={"code": -32602, "message": "Missing tool name"},
            id=request.id,
        )

    # Call the appropriate tool
    db = get_db()

    try:
        if tool_name == "get_flight_log":
            result = get_flight_log(db, arguments.get("flight_id", ""))
        elif tool_name == "get_pilot":
            result = get_pilot(db, arguments.get("pilot_id", ""))
        elif tool_name == "get_aircraft":
            result = get_aircraft(db, arguments.get("aircraft_id", ""))
        elif tool_name == "get_mission":
            result = get_mission(db, arguments.get("flight_id", ""))
        elif tool_name == "get_maintenance_history":
            result = get_maintenance_history(
                db,
                arguments.get("aircraft_id", ""),
                arguments.get("limit", 10)
            )
        # File access tools (no database needed)
        elif tool_name == "list_files":
            result = list_files(
                arguments.get("directory", "."),
                arguments.get("pattern", "*"),
                arguments.get("recursive", False),
            )
        elif tool_name == "read_file":
            result = read_file(
                arguments.get("path", ""),
                arguments.get("max_bytes"),
                arguments.get("encoding", "utf-8"),
            )
        elif tool_name == "get_file_metadata":
            result = get_file_metadata(arguments.get("path", ""))
        else:
            return JSONRPCResponse(
                error={"code": -32602, "message": f"Unknown tool: {tool_name}"},
                id=request.id,
            )

        # Format result in MCP content format
        return JSONRPCResponse(
            result={
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, default=str),
                    }
                ]
            },
            id=request.id,
        )

    except Exception as e:
        return JSONRPCResponse(
            error={"code": -32000, "message": str(e)},
            id=request.id,
        )


@app.get("/tools")
async def list_tools(authorization: str | None = Header(None)):
    """List available MCP tools."""
    if not verify_auth(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    return {
        "tools": [
            {
                "name": "get_flight_log",
                "description": "Retrieve parsed flight log data for a specific flight",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "flight_id": {"type": "string", "description": "Unique flight identifier"}
                    },
                    "required": ["flight_id"]
                }
            },
            {
                "name": "get_pilot",
                "description": "Retrieve pilot certification and credentials",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pilot_id": {"type": "string", "description": "Pilot identifier"}
                    },
                    "required": ["pilot_id"]
                }
            },
            {
                "name": "get_aircraft",
                "description": "Retrieve aircraft registration and status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "aircraft_id": {"type": "string", "description": "Aircraft ID"}
                    },
                    "required": ["aircraft_id"]
                }
            },
            {
                "name": "get_mission",
                "description": "Retrieve mission planning data for a flight",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "flight_id": {"type": "string", "description": "Flight identifier"}
                    },
                    "required": ["flight_id"]
                }
            },
            {
                "name": "get_maintenance_history",
                "description": "Retrieve maintenance records for an aircraft",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "aircraft_id": {"type": "string", "description": "Aircraft identifier"},
                        "limit": {"type": "integer", "description": "Maximum records", "default": 10}
                    },
                    "required": ["aircraft_id"]
                }
            },
            # File access tools
            {
                "name": "list_files",
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory path to list"},
                        "pattern": {"type": "string", "description": "Glob pattern to filter files", "default": "*"},
                        "recursive": {"type": "boolean", "description": "List recursively", "default": False}
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "read_file",
                "description": "Read file content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"},
                        "max_bytes": {"type": "integer", "description": "Maximum bytes to read"},
                        "encoding": {"type": "string", "description": "Text encoding", "default": "utf-8"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "get_file_metadata",
                "description": "Get file metadata (size, type, dates)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File or directory path"}
                    },
                    "required": ["path"]
                }
            },
        ]
    }


def main():
    """Run the HTTP server."""
    import uvicorn

    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8200"))

    print(f"\nStarting MCP HTTP Server on {host}:{port}")
    print(f"  - Endpoint: http://{host}:{port}/mcp")
    print(f"  - Health:   http://{host}:{port}/health")
    print(f"  - Tools:    http://{host}:{port}/tools\n")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
