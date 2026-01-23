"""List files tool for MCP server."""

import os
from pathlib import Path
from typing import Optional
import fnmatch


def list_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = False,
) -> dict:
    """
    List files in a directory.

    Args:
        directory: Directory path to list
        pattern: Glob pattern to filter files (default: "*")
        recursive: Whether to list recursively

    Returns:
        Dict with 'files' list containing file info dicts
    """
    try:
        dir_path = Path(directory)

        if not dir_path.exists():
            return {"error": f"Directory not found: {directory}"}

        if not dir_path.is_dir():
            return {"error": f"Not a directory: {directory}"}

        files = []

        if recursive:
            # Use rglob for recursive
            for path in dir_path.rglob(pattern):
                if path.is_file():
                    files.append(_get_file_info(path))
        else:
            # Use glob for non-recursive
            for path in dir_path.glob(pattern):
                if path.is_file():
                    files.append(_get_file_info(path))

        return {
            "directory": str(directory),
            "pattern": pattern,
            "recursive": recursive,
            "count": len(files),
            "files": files,
        }

    except PermissionError:
        return {"error": f"Permission denied: {directory}"}
    except Exception as e:
        return {"error": str(e)}


def _get_file_info(path: Path) -> dict:
    """Get basic file info."""
    try:
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": True,
        }
    except Exception:
        return {
            "path": str(path),
            "name": path.name,
            "is_file": True,
        }
