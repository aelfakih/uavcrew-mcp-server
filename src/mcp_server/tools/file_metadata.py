"""File metadata tool for MCP server."""

import mimetypes
import os
from datetime import datetime
from pathlib import Path


def get_file_metadata(path: str) -> dict:
    """
    Get file metadata.

    Args:
        path: File path

    Returns:
        Dict with file metadata (size, type, created, modified, etc.)
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {"error": f"Path not found: {path}"}

        stat = file_path.stat()

        # Determine MIME type
        mime_type, encoding = mimetypes.guess_type(path)
        if mime_type is None:
            if file_path.is_dir():
                mime_type = "inode/directory"
            else:
                mime_type = "application/octet-stream"

        return {
            "path": str(path),
            "name": file_path.name,
            "is_file": file_path.is_file(),
            "is_directory": file_path.is_dir(),
            "size": stat.st_size if file_path.is_file() else None,
            "mime_type": mime_type,
            "encoding": encoding,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "mode": oct(stat.st_mode),
            "extension": file_path.suffix.lower() if file_path.is_file() else None,
        }

    except PermissionError:
        return {"error": f"Permission denied: {path}"}
    except Exception as e:
        return {"error": str(e)}
