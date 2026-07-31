"""Shell 执行工具。对应架构图「代码即行动 · 沙箱执行」。"""

import os
import subprocess
import datetime
from . import registry


def run_shell(command: str) -> dict:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        stdout = result.stdout[:10_000]
        stderr = result.stderr[:10_000]
        if result.returncode != 0:
            text = stderr or stdout or f"command exited with code {result.returncode}"
            return registry.error(text)
        text = stdout or stderr or "(no output)"
        return registry.success(
            {"command": command, "stdout": stdout, "stderr": stderr, "exit_code": result.returncode},
            text,
        )
    except subprocess.TimeoutExpired:
        return registry.error("command timed out after 30 seconds")
    except Exception as e:
        return registry.error(f"Error running command: {e}")


def get_current_time() -> dict:
    now = datetime.datetime.now()
    return registry.success(
        {"timestamp": now.isoformat(), "timezone": str(now.astimezone().tzinfo)},
        now.strftime("%Y-%m-%d %H:%M:%S (%A)"),
    )


def register_all():
    registry.register(
        "run_shell",
        "Run a shell command and return its output.",
        {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "Shell command to execute."}},
            "required": ["command"],
        },
        {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer", "const": 0},
            },
            "required": ["command", "stdout", "stderr", "exit_code"],
            "additionalProperties": False,
        },
        run_shell,
    )
    registry.register(
        "get_current_time",
        "Get the current date and time.",
        {"type": "object", "properties": {}, "required": []},
        {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "timezone": {"type": "string"},
            },
            "required": ["timestamp", "timezone"],
            "additionalProperties": False,
        },
        get_current_time,
    )
