"""Local, runtime-neutral persistence for normalized agent traces."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from .runtime import RunEvent, RunResult


TRACE_SCHEMA_VERSION = 1
DEFAULT_TRACE_DIRECTORY = Path(__file__).parent / "traces"


class TraceStore:
    """Store one complete RunResult per JSON file, keyed by run ID."""

    def __init__(self, directory: str | Path = DEFAULT_TRACE_DIRECTORY):
        self.directory = Path(directory)

    def save(self, result: RunResult) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(result.run_id)
        temporary_path = path.with_suffix(".json.tmp")
        document = {
            "schema_version": TRACE_SCHEMA_VERSION,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "result": asdict(result),
        }
        temporary_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        os.replace(temporary_path, path)
        return path

    def load(self, run_id: str) -> RunResult:
        document = json.loads(self._path(run_id).read_text(encoding="utf-8"))
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
        )

    def _path(self, run_id: str) -> Path:
        if not run_id or Path(run_id).name != run_id:
            raise ValueError("run_id must be a simple filename")
        return self.directory / f"{run_id}.json"
