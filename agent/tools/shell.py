"""Shell 执行工具。对应架构图「代码即行动 · 沙箱执行」。"""

import os
import subprocess
import datetime
from . import registry


def run_shell(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n--- stderr ---\n" if output else "") + result.stderr
        if result.returncode != 0:
            output += f"\n(exit code: {result.returncode})"
        return output[:10_000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30 seconds"
    except Exception as e:
        return f"Error running command: {e}"


def get_current_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")


def register_all():
    registry.register(
        "run_shell",
        "Run a shell command and return its output.",
        {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "Shell command to execute."}},
            "required": ["command"],
        },
        run_shell,
    )
    registry.register(
        "get_current_time",
        "Get the current date and time.",
        {"type": "object", "properties": {}, "required": []},
        get_current_time,
    )
