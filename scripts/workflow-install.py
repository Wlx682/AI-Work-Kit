#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".workflows" / "install.json"
BLUEPRINT_DIR = ROOT / ".workflows" / "blueprints"
CACHE_SCHEMA_VERSION = 1
DEFAULT_CACHE_FILE = Path.home() / ".cache" / "ai-work-kit" / "workflow-install-state.json"


STATUS_ORDER = {"ok": 0, "warn": 1, "block": 2}


class InstallError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallError(f"{path.relative_to(ROOT)} JSON 解析失败: {exc}") from exc
    if not isinstance(data, dict):
        raise InstallError(f"{path.relative_to(ROOT)} 顶层必须是 object")
    return data


def resolve_path(value: str) -> Path:
    if value.startswith("~"):
        return Path(value).expanduser()
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def result(status: str, capability: str, message: str) -> dict[str, str]:
    return {"status": status, "capability": capability, "message": message}


def split_command(command: str) -> list[str]:
    import shlex

    return shlex.split(command)


def run_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(split_command(command), cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def cache_file_path(explicit: str | None) -> Path:
    override = explicit or os.environ.get("AI_WORK_KIT_INSTALL_CACHE")
    return Path(override).expanduser().resolve() if override else DEFAULT_CACHE_FILE


def load_cache(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schemaVersion": CACHE_SCHEMA_VERSION, "roots": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schemaVersion": CACHE_SCHEMA_VERSION, "roots": {}}
    if not isinstance(data, dict) or data.get("schemaVersion") != CACHE_SCHEMA_VERSION or not isinstance(data.get("roots"), dict):
        return {"schemaVersion": CACHE_SCHEMA_VERSION, "roots": {}}
    return data


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            json.dump(cache, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            temp_name = handle.name
        Path(temp_name).replace(path)
    finally:
        if temp_name:
            temp_path = Path(temp_name)
            if temp_path.exists():
                temp_path.unlink()


def hash_path(hasher: Any, label: str, path: Path) -> None:
    hasher.update(f"{label}\0{path}\0".encode("utf-8"))
    if not path.exists():
        hasher.update(b"missing\0")
        return
    if path.is_file():
        hasher.update(b"file\0")
        try:
            hasher.update(path.read_bytes())
        except OSError as exc:
            hasher.update(f"unreadable:{exc.__class__.__name__}\0".encode("utf-8"))
        return
    if path.is_dir():
        hasher.update(b"dir\0")
        try:
            children = sorted(item for item in path.rglob("*") if item.is_file())
        except OSError as exc:
            hasher.update(f"unreadable:{exc.__class__.__name__}\0".encode("utf-8"))
            return
        for child in children:
            try:
                relative = child.relative_to(path)
                stat_result = child.stat()
            except OSError:
                continue
            hasher.update(f"{relative}\0{stat_result.st_size}\0{stat_result.st_mtime_ns}\0".encode("utf-8"))
        return
    hasher.update(b"other\0")


def static_fingerprint(requires: list[str], manifest: dict[str, Any]) -> str:
    capabilities = manifest.get("capabilities", {})
    hasher = hashlib.sha256()
    hasher.update(f"schema:{CACHE_SCHEMA_VERSION}\0root:{ROOT.resolve()}\0".encode("utf-8"))
    hash_path(hasher, "installer", Path(__file__).resolve())
    hash_path(hasher, "manifest", MANIFEST)
    for capability in sorted(requires):
        cap = capabilities.get(capability, {})
        static_config = {key: value for key, value in cap.items() if key != "portGuard"}
        hasher.update(json.dumps(static_config, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        for command in cap.get("commands", []) or []:
            hasher.update(f"command:{command}:{shutil.which(str(command)) or 'missing'}\0".encode("utf-8"))
        for entry in cap.get("paths", []) or []:
            path_value = entry if isinstance(entry, str) else str(entry.get("path", ""))
            hash_path(hasher, f"{capability}:path", resolve_path(str(path_value)))
        for entry in cap.get("globalFiles", []) or []:
            path_value = str(entry.get("path", ""))
            hash_path(hasher, f"{capability}:global", resolve_path(path_value))
        hook = cap.get("hook")
        if isinstance(hook, dict):
            hash_path(hasher, f"{capability}:hook-source", resolve_path(str(hook.get("source", ""))))
            hash_path(hasher, f"{capability}:hook-target", resolve_path(str(hook.get("target", ""))))
        for path_value in cap.get("fingerprintPaths", []) or []:
            hash_path(hasher, f"{capability}:fingerprint", resolve_path(str(path_value)))
    return hasher.hexdigest()


def cache_profiles(cache: dict[str, Any]) -> dict[str, Any]:
    roots = cache.setdefault("roots", {})
    root_entry = roots.setdefault(str(ROOT.resolve()), {})
    return root_entry.setdefault("profiles", {})


def mark_cache(cache: dict[str, Any], fingerprint: str, workflow: str) -> None:
    profiles = cache_profiles(cache)
    previous = profiles.get(fingerprint, {})
    workflows = sorted(set([*(previous.get("workflows", []) or []), workflow]))
    profiles[fingerprint] = {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "workflows": workflows,
    }


def check_commands(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for command in cap.get("commands", []) or []:
        if shutil.which(str(command)):
            items.append(result("ok", capability, f"命令可用: {command}"))
        else:
            items.append(result("block", capability, f"缺少命令: {command}"))
    return items


def check_paths(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for entry in cap.get("paths", []) or []:
        if isinstance(entry, str):
            path_value, expected = entry, "any"
        else:
            path_value, expected = str(entry.get("path", "")), str(entry.get("type", "any"))
        path = resolve_path(path_value)
        if expected == "file":
            ok = path.is_file()
        elif expected == "dir":
            ok = path.is_dir()
        else:
            ok = path.exists()
        if ok:
            items.append(result("ok", capability, f"路径存在: {path_value}"))
        else:
            items.append(result("block", capability, f"路径缺失: {path_value}"))
    return items


def check_global_files(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for entry in cap.get("globalFiles", []) or []:
        path_value = str(entry.get("path", ""))
        path = resolve_path(path_value)
        if not path.is_file():
            items.append(result("block", capability, f"全局文件缺失: {path_value}"))
            continue
        text = path.read_text(encoding="utf-8")
        missing = [needle for needle in entry.get("contains", []) or [] if str(needle) not in text]
        if missing:
            items.append(result("block", capability, f"全局文件缺少工作流优先级声明: {path_value} -> {', '.join(missing)}"))
        else:
            items.append(result("ok", capability, f"全局指令已声明: {path_value}"))
    return items


def check_sync(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    command = cap.get("syncCheckCommand")
    if not command:
        return []
    proc = run_command(str(command))
    if proc.returncode == 0:
        line = (proc.stdout or "").strip().splitlines()[-1:] or [str(command)]
        return [result("ok", capability, line[0])]
    detail = (proc.stderr or proc.stdout or "").strip().splitlines()
    return [result("block", capability, f"Skill 多端不同步: {'; '.join(detail[:3])}")]


def check_hook(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    hook = cap.get("hook")
    if not isinstance(hook, dict):
        return []
    source = resolve_path(str(hook.get("source", "")))
    target = resolve_path(str(hook.get("target", "")))
    if not source.is_file():
        return [result("block", capability, f"hook 源文件缺失: {display_path(source)}")]
    if not target.exists():
        return [result("block", capability, f"hook 未安装: {display_path(target)}")]
    items: list[dict[str, str]] = []
    if not target.is_file():
        items.append(result("block", capability, f"hook 目标不是文件: {display_path(target)}"))
    elif source.read_bytes() != target.read_bytes():
        items.append(result("block", capability, f"hook 与源脚本不一致: {display_path(target)}"))
    else:
        items.append(result("ok", capability, f"hook 已安装且同步: {display_path(target)}"))
    if hook.get("executable"):
        mode = target.stat().st_mode if target.exists() else 0
        if mode & stat.S_IXUSR:
            items.append(result("ok", capability, f"hook 可执行: {display_path(target)}"))
        else:
            items.append(result("block", capability, f"hook 不可执行: {display_path(target)}"))
    return items


def check_port_guard(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    guard = cap.get("portGuard")
    if not isinstance(guard, dict):
        return []
    host = str(guard.get("host", "127.0.0.1"))
    port = int(guard.get("port", 0))
    probe = str(guard.get("probePath", "/"))
    expected = [str(item) for item in guard.get("expectedJsonKeys", []) or []]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        code = sock.connect_ex((host, port))
    finally:
        sock.close()
    if code != 0:
        return [result("ok", capability, f"端口可用: {host}:{port}")]
    url = f"http://{host}:{port}{probe}"
    try:
        with urlopen(url, timeout=1.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return [result("block", capability, f"端口被占用但不是可识别看板: {host}:{port} ({exc})")]
    missing = [key for key in expected if key not in payload]
    if missing:
        return [result("block", capability, f"端口被其他服务占用: {host}:{port}，缺少响应字段 {', '.join(missing)}")]
    return [result("ok", capability, f"端口已由 AI-Work-Kit 看板占用: {host}:{port}")]


def apply_hook(cap: dict[str, Any]) -> list[str]:
    hook = cap.get("hook")
    if not isinstance(hook, dict):
        return []
    source = resolve_path(str(hook.get("source", "")))
    target = resolve_path(str(hook.get("target", "")))
    if not source.is_file():
        raise InstallError(f"hook 源文件缺失: {display_path(source)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if hook.get("executable"):
        target.chmod(target.stat().st_mode | stat.S_IXUSR)
    return [f"已安装 hook: {display_path(target)}"]


def apply_sync(cap: dict[str, Any]) -> list[str]:
    command = cap.get("syncCommand")
    if not command:
        return []
    proc = run_command(str(command))
    if proc.returncode != 0:
        raise InstallError((proc.stderr or proc.stdout or str(command)).strip())
    return [line for line in (proc.stdout or "").splitlines() if line.strip()]


def load_blueprint(name: str) -> dict[str, Any]:
    path = BLUEPRINT_DIR / f"{name}.json"
    if not path.is_file():
        raise InstallError(f"蓝图不存在: .workflows/blueprints/{name}.json")
    return load_json(path)


def workflow_names(explicit: str | None) -> list[str]:
    if explicit:
        return [explicit]
    return sorted(path.stem for path in BLUEPRINT_DIR.glob("*.json"))


def static_capability_results(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    items.extend(check_commands(capability, cap))
    items.extend(check_paths(capability, cap))
    items.extend(check_global_files(capability, cap))
    items.extend(check_sync(capability, cap))
    items.extend(check_hook(capability, cap))
    if not items:
        items.append(result("ok", capability, "无静态检查项"))
    return items


def runtime_capability_results(capability: str, cap: dict[str, Any]) -> list[dict[str, str]]:
    return check_port_guard(capability, cap)


def check_workflow(name: str, manifest: dict[str, Any], cache: dict[str, Any], refresh: bool = False) -> dict[str, Any]:
    bp = load_blueprint(name)
    enablement = bp.get("enablement")
    if not isinstance(enablement, dict):
        return {"workflow": name, "results": [result("block", "enablement", "蓝图缺少 enablement 声明")]}
    requires = enablement.get("requires")
    if not isinstance(requires, list) or not all(isinstance(item, str) and item for item in requires):
        return {"workflow": name, "results": [result("block", "enablement", "enablement.requires 必须是非空字符串数组")]}
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, dict):
        raise InstallError(".workflows/install.json 缺少 capabilities")
    fingerprint = static_fingerprint(requires, manifest)
    hit = not refresh and fingerprint in cache_profiles(cache)
    results: list[dict[str, str]] = []
    if hit:
        results.append(result("ok", "install-cache", f"电脑/Kit 静态环境缓存有效: {fingerprint[:12]}"))
        static_ok = True
    else:
        for capability in requires:
            cap = capabilities.get(capability)
            if not isinstance(cap, dict):
                results.append(result("block", capability, f"安装清单缺少能力: {capability}"))
                continue
            results.extend(static_capability_results(capability, cap))
        static_ok = not any(item["status"] == "block" for item in results)
        if static_ok:
            mark_cache(cache, fingerprint, name)
            results.append(result("ok", "install-cache", f"电脑/Kit 静态环境已检查并缓存: {fingerprint[:12]}"))

    for capability in requires:
        cap = capabilities.get(capability)
        if isinstance(cap, dict):
            results.extend(runtime_capability_results(capability, cap))
    return {
        "workflow": name,
        "results": results,
        "cache": {
            "hit": hit,
            "fingerprint": fingerprint[:12],
            "static_ok": static_ok,
        },
    }


def summarize(reports: list[dict[str, Any]]) -> str:
    worst = "ok"
    for report_item in reports:
        for item in report_item["results"]:
            if STATUS_ORDER[item["status"]] > STATUS_ORDER[worst]:
                worst = item["status"]
    return worst


def print_human(reports: list[dict[str, Any]]) -> None:
    for report_item in reports:
        print(f"# workflow-install: {report_item['workflow']}")
        for item in report_item["results"]:
            print(f"{item['status'].upper()}:{item['capability']}: {item['message']}")


def apply_workflow(name: str, manifest: dict[str, Any], sync_skills: bool) -> list[str]:
    bp = load_blueprint(name)
    requires = bp.get("enablement", {}).get("requires", [])
    capabilities = manifest.get("capabilities", {})
    actions: list[str] = []
    if "pre-commit-hook" in requires:
        actions.extend(apply_hook(capabilities["pre-commit-hook"]))
    if sync_skills and "skills" in requires:
        actions.extend(apply_sync(capabilities["skills"]))
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="检查或安装 AI-Work-Kit workflow 启用前置环境。")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="缓存感知地检查 workflow 启用环境；首次通过后记录静态环境指纹")
    check.add_argument("--workflow", help="蓝图 name；不传则检查全部蓝图")
    check.add_argument("--cache-file", help="覆盖电脑级静态检查缓存路径（测试或隔离环境使用）")
    check.add_argument("--refresh", action="store_true", help="忽略缓存并重新执行静态环境检查")
    check.add_argument("--json", action="store_true", help="输出 JSON")

    apply = sub.add_parser("apply", help="安装可自动修复的本地启用项")
    apply.add_argument("--workflow", required=True, help="蓝图 name")
    apply.add_argument("--sync-skills", action="store_true", help="同时运行 Skill 多端同步（会覆盖项目同名全局 Skill）")
    apply.add_argument("--cache-file", help="覆盖电脑级静态检查缓存路径（测试或隔离环境使用）")
    apply.add_argument("--json", action="store_true", help="输出 JSON")

    args = parser.parse_args()
    try:
        manifest = load_json(MANIFEST)
        cache_path = cache_file_path(getattr(args, "cache_file", None))
        cache = load_cache(cache_path)
        actions: list[str] = []
        if args.command == "apply":
            actions = apply_workflow(args.workflow, manifest, args.sync_skills)
        reports = []
        for name in workflow_names(getattr(args, "workflow", None)):
            reports.append(check_workflow(name, manifest, cache, refresh=args.command == "apply" or getattr(args, "refresh", False)))
        if any(report.get("cache", {}).get("static_ok") and not report.get("cache", {}).get("hit") for report in reports):
            save_cache(cache_path, cache)
    except InstallError as exc:
        print(f"BLOCKED:workflow-install:{exc}", file=sys.stderr)
        return 1

    payload = {"actions": actions, "reports": reports, "status": summarize(reports), "cacheFile": str(cache_path)}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for action in actions:
            print(f"APPLY: {action}")
        print_human(reports)
    return 1 if payload["status"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
