"""文件操作工具。对应架构图「MCP 工具总线 · 文件系统」。"""

import os
from . import registry


def read_file(path: str) -> str:
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(50_000)
        lines = content.splitlines()
        if len(lines) > 200:
            return "\n".join(lines[:200]) + f"\n... (truncated, {len(lines)} total lines)"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    path = os.path.expanduser(path)
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_directory(path: str = ".") -> str:
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return f"Error: not a directory: {path}"
    try:
        entries = sorted(os.listdir(path))
        result = []
        for e in entries[:100]:
            full = os.path.join(path, e)
            kind = "dir" if os.path.isdir(full) else "file"
            result.append(f"  [{kind}] {e}")
        header = f"Directory: {path} ({len(entries)} entries)"
        if len(entries) > 100:
            header += " (showing first 100)"
        return header + "\n" + "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {e}"


def register_all():
    registry.register(
        "read_file",
        "Read the content of a file.",
        {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "File path to read."}},
            "required": ["path"],
        },
        read_file,
    )
    registry.register(
        "write_file",
        "Write content to a file. Creates parent directories if needed.",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write."},
                "content": {"type": "string", "description": "Text content to write."},
            },
            "required": ["path", "content"],
        },
        write_file,
    )
    registry.register(
        "list_directory",
        "List files and directories at the given path.",
        {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory path.", "default": "."}},
            "required": [],
        },
        list_directory,
    )
