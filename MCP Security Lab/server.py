"""Permission-aware MCP server (stdio) — risk-tagged tools + audit resources."""

from __future__ import annotations

import json
import warnings
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

warnings.filterwarnings("ignore", category=DeprecationWarning)

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE / "data"
BASE_DIR.mkdir(exist_ok=True)

DEFAULT_PERMISSIONS = {
    "read_file": "allow",
    "write_file": "ask",
    "delete_file": "deny",
    "execute_command": "deny",
}

mcp = FastMCP("Permission-Aware MCP Server")


def _safe_path(filepath: str) -> Path:
    path = (BASE_DIR / filepath).resolve()
    try:
        path.relative_to(BASE_DIR.resolve())
    except ValueError as e:
        raise ValueError("Access denied - path outside data directory") from e
    return path


def _append_audit(line: str) -> None:
    with open(BASE_DIR / "audit.log", "a", encoding="utf-8") as f:
        f.write(line)


@mcp.tool()
def read_file(filepath: str) -> str:
    """Read a file from the data directory. (Risk: LOW)"""
    try:
        file_path = _safe_path(filepath)
        if not file_path.exists():
            return f"Error: File {filepath} not found"
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """Write content to a file in the data directory. (Risk: MEDIUM)"""
    try:
        file_path = _safe_path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        _append_audit(f"[{datetime.now().isoformat()}] WRITE: {filepath}\n")
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"


@mcp.tool()
def delete_file(filepath: str) -> str:
    """Delete a file from the data directory. (Risk: HIGH)"""
    try:
        file_path = _safe_path(filepath)
        if not file_path.exists():
            return f"Error: File {filepath} not found"
        if file_path.is_dir():
            return f"Error: {filepath} is a directory"
        file_path.unlink()
        _append_audit(f"[{datetime.now().isoformat()}] DELETE: {filepath}\n")
        return f"Successfully deleted {filepath}"
    except Exception as e:
        return f"Error deleting file: {e}"


@mcp.tool()
def execute_command(command: str) -> str:
    """Simulate a system command. (Risk: CRITICAL) — never runs for real."""
    _append_audit(
        f"[{datetime.now().isoformat()}] EXECUTE (simulated): {command}\n"
    )
    return (
        f"Simulated execution of command: {command}\n"
        "(Actual execution disabled for security)"
    )


@mcp.resource("file://audit/log")
def get_audit_log() -> str:
    """Get the audit log of all operations."""
    audit_log = BASE_DIR / "audit.log"
    if not audit_log.exists():
        return "No audit log entries yet."
    return audit_log.read_text(encoding="utf-8")


@mcp.resource("file://config/permissions")
def get_permissions_config() -> str:
    """Get the current permissions configuration."""
    permissions_file = BASE_DIR / "permissions.json"
    if not permissions_file.exists():
        return json.dumps(DEFAULT_PERMISSIONS, indent=2)
    return permissions_file.read_text(encoding="utf-8")


@mcp.prompt()
def security_review(operation: str, risk_level: str) -> list[dict]:
    """Generate a security review prompt for an operation."""
    return [
        {
            "role": "user",
            "content": f"""Review this operation for security implications:

Operation: {operation}
Risk Level: {risk_level}

Please analyze:
1. What data or systems could be affected?
2. What are the potential security risks?
3. What safeguards should be in place?
4. Should this operation require user approval?
5. What should be logged for audit purposes?
""",
        }
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
