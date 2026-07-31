"""文件操作工具。对应架构图「MCP 工具总线 · 文件系统」。"""

import os
from . import registry


def read_file(path: str) -> dict:
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        return registry.error(f"file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(50_000)
        lines = content.splitlines()
        truncated = len(lines) > 200
        preview = "\n".join(lines[:200]) if truncated else content
        if truncated:
            preview += f"\n... (truncated, {len(lines)} total lines)"
        return registry.success(
            {"path": path, "content": preview, "truncated": truncated},
            preview,
        )
    except Exception as e:
        return registry.error(f"Error reading file: {e}")


def write_file(path: str, content: str) -> dict:
    path = os.path.expanduser(path)
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return registry.success(
            {"path": path, "bytes_written": len(content.encode("utf-8"))},
            f"Written {len(content.encode('utf-8'))} bytes to {path}",
        )
    except Exception as e:
        return registry.error(f"Error writing file: {e}")


def list_directory(path: str = ".") -> dict:
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return registry.error(f"not a directory: {path}")
    try:
        entries = sorted(os.listdir(path))
        result = []
        for e in entries[:100]:
            full = os.path.join(path, e)
            kind = "dir" if os.path.isdir(full) else "file"
            result.append({"name": e, "type": kind})
        header = f"Directory: {path} ({len(entries)} entries)"
        if len(entries) > 100:
            header += " (showing first 100)"
        text = header + "\n" + "\n".join(
            f"  [{entry['type']}] {entry['name']}" for entry in result
        )
        return registry.success(
            {"path": path, "entries": result, "truncated": len(entries) > 100},
            text,
        )
    except Exception as e:
        return registry.error(f"Error listing directory: {e}")


def register_all():
    registry.register(
        "read_file",
        "Read the content of a file.",
        {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "File path to read."}},
            "required": ["path"],
        },
        {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "truncated": {"type": "boolean"},
            },
            "required": ["path", "content", "truncated"],
            "additionalProperties": False,
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
        {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "bytes_written": {"type": "integer", "minimum": 0},
            },
            "required": ["path", "bytes_written"],
            "additionalProperties": False,
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
        {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"enum": ["file", "dir"]},
                        },
                        "required": ["name", "type"],
                        "additionalProperties": False,
                    },
                },
                "truncated": {"type": "boolean"},
            },
            "required": ["path", "entries", "truncated"],
            "additionalProperties": False,
        },
        list_directory,
    )
