"""安全宪法层。对应架构图「安全宪法层：最小权限 · 审批 · 审计追踪」。

所有工具调用在执行前必须经过安全层审核。
安全层决定：放行 / 需要人工审批 / 拒绝。
"""

import datetime

DANGEROUS_PATTERNS = ["rm -rf", "rm -r /", "mkfs", "dd if=", "> /dev/", "chmod 777"]

_audit_log: list[dict] = []


def check(tool_name: str, args: dict) -> dict:
    """审核一次工具调用。

    Returns:
        {"allowed": True} — 放行
        {"allowed": False, "reason": str} — 拒绝
        {"needs_approval": True, "reason": str} — 需要人工确认
    """
    if tool_name == "run_shell":
        cmd = args.get("command", "")
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd:
                return {"needs_approval": True, "reason": f"危险命令模式: {pattern}"}

    if tool_name == "write_file":
        path = args.get("path", "")
        if path.startswith("/etc/") or path.startswith("/usr/"):
            return {"allowed": False, "reason": f"禁止写入系统目录: {path}"}

    return {"allowed": True}


def request_approval(tool_name: str, args: dict, reason: str) -> bool:
    """请求用户人工审批。"""
    print(f"\n🛡️  安全审批请求")
    print(f"   工具: {tool_name}")
    print(f"   参数: {args}")
    print(f"   原因: {reason}")
    confirm = input("   确认执行? (y/N): ")
    approved = confirm.lower() == "y"
    log(tool_name, args, "approved" if approved else "rejected_by_user")
    return approved


def log(tool_name: str, args: dict, result: str):
    """记录审计日志。"""
    entry = {
        "time": datetime.datetime.now().isoformat(),
        "tool": tool_name,
        "args": args,
        "result": result,
    }
    _audit_log.append(entry)


def get_audit_log() -> list[dict]:
    return list(_audit_log)
