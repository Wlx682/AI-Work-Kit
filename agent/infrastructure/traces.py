"""Local, runtime-neutral persistence for normalized agent traces."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from ..core.models import RunEvent, RunResult


TRACE_SCHEMA_VERSION = 1
DEFAULT_TRACE_DIRECTORY = Path(".runtime/agent/traces")


class TraceStore:
    """Store one complete RunResult per JSON file, keyed by run ID."""

    def __init__(self, directory: str | Path = DEFAULT_TRACE_DIRECTORY):
        self.directory = Path(directory)

    def save(self, result: RunResult) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(result.run_id)
        temporary_path = path.with_suffix(".json.tmp")
        document = _encode_tuples({
            "schema_version": TRACE_SCHEMA_VERSION,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "result": asdict(result),
        })
        temporary_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        os.replace(temporary_path, path)
        return path

    def load(self, run_id: str) -> RunResult:
        document = _decode_tuples(json.loads(self._path(run_id).read_text(encoding="utf-8")))
        if document.get("schema_version") != TRACE_SCHEMA_VERSION:
            raise ValueError(f"unsupported trace schema: {document.get('schema_version')}")
        result = document["result"]
        events = tuple(RunEvent(**event) for event in result["events"])
        return RunResult(
            run_id=result["run_id"],
            task=result["task"],
            outcome=result["outcome"],
            events=events,
            error=result.get("error"),
            warnings=tuple(result.get("warnings", [])),
            interrupts=tuple(result.get("interrupts", [])),
            thread_id=result.get("thread_id"),
            parent_run_id=result.get("parent_run_id"),
            recovered_from_checkpoint_id=result.get("recovered_from_checkpoint_id"),
            recovery_mode=result.get("recovery_mode"),
        )

    def _path(self, run_id: str) -> Path:
        if not run_id or Path(run_id).name != run_id:
            raise ValueError("run_id must be a simple filename")
        return self.directory / f"{run_id}.json"


def _encode_tuples(value):
    if isinstance(value, tuple):
        return {"__tuple__": [_encode_tuples(item) for item in value]}
    if isinstance(value, list):
        return [_encode_tuples(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode_tuples(item) for key, item in value.items()}
    return value


def _decode_tuples(value):
    if isinstance(value, dict) and set(value) == {"__tuple__"}:
        return tuple(_decode_tuples(item) for item in value["__tuple__"])
    if isinstance(value, list):
        return [_decode_tuples(item) for item in value]
    if isinstance(value, dict):
        return {key: _decode_tuples(item) for key, item in value.items()}
    return value
