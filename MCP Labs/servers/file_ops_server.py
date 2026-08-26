"""File Operations MCP Server — progress, elicitation, resources, prompts.

Sandbox root: MCP Labs/workspace/ (not arbitrary CWD).

Run: python servers/file_ops_server.py
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
BASE_DIR = (HERE.parent / "workspace").resolve()
BASE_DIR.mkdir(parents=True, exist_ok=True)


class DocumentGeneratorSchema(BaseModel):
    """Elicitation schema for documentation generation."""

    file_path: str = Field(description="Relative path of the file to document")
    name: str = Field(description="Documentation file name to create")


mcp = FastMCP("File Operations MCP Server")


def get_path(relative_path: str) -> Path:
    """Resolve path under BASE_DIR; reject escapes."""
    # Treat empty / "." as sandbox root
    rel = (relative_path or ".").strip() or "."
    candidate = (BASE_DIR / rel).resolve()
    try:
        candidate.relative_to(BASE_DIR)
    except ValueError as e:
        raise ValueError("Path is outside workspace sandbox") from e
    return candidate


@mcp.tool()
async def write_file(file_path: str, content: str, ctx: Context) -> str:
    """Create/overwrite a file in the workspace with UTF-8 content (reports progress)."""
    try:
        path = get_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        total = max(len(content), 1)
        chunk_size = max(total // 10, 1)
        written = 0
        with open(path, "w", encoding="utf-8") as f:
            for i in range(0, len(content), chunk_size):
                f.write(content[i : i + chunk_size])
                written = min(i + chunk_size, total)
                await ctx.report_progress(
                    progress=written,
                    total=total,
                    message=f"Writing progress: {written}/{total}",
                )
                time.sleep(0.05)

        await ctx.report_progress(progress=total, total=total, message="Write complete")
        await ctx.info(f"File written successfully to: {file_path}")
        return f"File written successfully to: {file_path}"
    except Exception as e:
        await ctx.error(f"Error creating file: {e}")
        raise


@mcp.tool()
async def delete_file(file_path: str, ctx: Context) -> str:
    """Delete a file from the workspace (not directories)."""
    try:
        path = get_path(file_path)
        if path.is_file():
            path.unlink()
            await ctx.info(f"Successfully deleted file {file_path}")
            return f"Successfully deleted file {file_path}"
        if path.is_dir():
            await ctx.warning(f"Error: {file_path} is a directory, not a file")
            return f"Error: {file_path} is a directory, not a file"
        await ctx.warning(f"File not found: {file_path}")
        return f"File not found: {file_path}"
    except Exception as e:
        await ctx.error(f"Error deleting file: {e}")
        return f"Error deleting file: {e}"


@mcp.resource("file:///{file_name}")
async def read_file_resource(file_name: str) -> dict:
    """Read file content as an MCP resource (file:/// URI)."""
    try:
        path = get_path(file_name)
        if not path.exists() or not path.is_file():
            return {"error": f"Error: {file_name} is not a valid file"}
        return {"file_content": path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}


@mcp.resource("dir://.")
async def list_files_resource() -> dict:
    """List files/directories in the workspace root."""
    try:
        path = get_path(".")
        if not path.exists() or not path.is_dir():
            return {"error": f"{path} is not a valid directory"}

        items = []
        for item in path.iterdir():
            stat = item.stat()
            items.append(
                {
                    "name": item.name,
                    "path": str(item.relative_to(BASE_DIR)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
            )
        return {"items": items}
    except Exception as e:
        return {"error": f"Error listing files: {e}"}


@mcp.prompt()
async def code_review(file_path: str, ctx: Context) -> str:
    """Build a code-review prompt from a workspace file."""
    try:
        path = get_path(file_path)
        if not path.exists() or not path.is_file():
            error_msg = f"Error: {file_path} is not a valid file"
            await ctx.warning(error_msg)
            raise FileNotFoundError(error_msg)

        current_code = path.read_text(encoding="utf-8").strip()
        language = path.suffix.lower()
        prompt = f"""You are an expert code editor. Review the following code quality.

File: {file_path}
Language (file suffix): {language or "unknown"}

Current code:
'''
{current_code}
'''

Provide a comprehensive evaluation of the code:
""".strip()
        await ctx.info("Successfully returned prompt")
        return prompt
    except Exception as e:
        await ctx.error(f"Error preparing code review prompt: {e}")
        raise


@mcp.prompt()
async def documentation_generator(ctx: Context) -> str:
    """Elicit file + doc name, then build a documentation prompt."""
    try:
        result = await ctx.elicit(
            message="Please provide the subject file name and the documentation file name",
            response_type=DocumentGeneratorSchema,
        )

        # FastMCP may return action wrappers; support .data or direct model
        data = getattr(result, "data", result)
        if getattr(result, "action", None) in ("decline", "cancel"):
            raise RuntimeError("Elicitation declined by client")

        file_path = data.file_path if hasattr(data, "file_path") else data["file_path"]
        doc_name = data.name if hasattr(data, "name") else data["name"]

        path = get_path(file_path)
        if not path.exists() or not path.is_file():
            error_msg = f"Error: {file_path} is not a valid file"
            await ctx.warning(error_msg)
            raise FileNotFoundError(error_msg)

        code = path.read_text(encoding="utf-8").strip()
        language = path.suffix.lower()

        prompt = f"""You are an expert technical writer and documentation specialist. Create documentation for the following code file:

File: {file_path}
Language (file suffix): {language or "unknown"}

Current code:
'''
{code}
'''

Use MCP tools available to you to create the separate documentation file:
- **CRITICAL DETAIL: Name that separate document EXACTLY: {doc_name}**
- Add the .md suffix yourself if the name doesn't include it already""".strip()

        await ctx.info("Successfully returned prompt")
        return prompt
    except Exception as e:
        await ctx.error(f"Error generating code documentation prompt: {e}")
        raise


if __name__ == "__main__":
    print(f"Starting File Operations Server (sandbox={BASE_DIR})...")
    mcp.run()
