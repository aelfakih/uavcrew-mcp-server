"""Read file tool for MCP server."""

import base64
import mimetypes
from pathlib import Path
from typing import Optional


# Binary file extensions
BINARY_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif",
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".bin", ".exe", ".dll", ".so",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
}


def read_file(
    path: str,
    max_bytes: Optional[int] = None,
    encoding: str = "utf-8",
) -> dict:
    """
    Read file content.

    Args:
        path: File path to read
        max_bytes: Maximum bytes to read (None for all)
        encoding: Text encoding (default: utf-8)

    Returns:
        Dict with 'content', 'size', 'encoding', 'is_binary' keys
    """
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {"error": f"File not found: {path}"}

        if not file_path.is_file():
            return {"error": f"Not a file: {path}"}

        # Get file size
        size = file_path.stat().st_size

        # Determine if binary
        ext = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(path)
        is_binary = (
            ext in BINARY_EXTENSIONS or
            (mime_type and not mime_type.startswith("text/"))
        )

        # Calculate bytes to read
        bytes_to_read = size
        if max_bytes is not None:
            bytes_to_read = min(size, max_bytes)

        # Read file
        with open(file_path, "rb") as f:
            raw_content = f.read(bytes_to_read)

        # Encode content
        if is_binary:
            content = base64.b64encode(raw_content).decode("ascii")
        else:
            try:
                content = raw_content.decode(encoding)
            except UnicodeDecodeError:
                # Fall back to binary handling
                is_binary = True
                content = base64.b64encode(raw_content).decode("ascii")

        return {
            "path": str(path),
            "content": content,
            "size": size,
            "bytes_read": len(raw_content),
            "encoding": "base64" if is_binary else encoding,
            "is_binary": is_binary,
            "truncated": bytes_to_read < size,
        }

    except PermissionError:
        return {"error": f"Permission denied: {path}"}
    except Exception as e:
        return {"error": str(e)}
