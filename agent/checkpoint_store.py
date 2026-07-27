"""Durable LangGraph checkpoint storage for resumable agent runs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


DEFAULT_CHECKPOINT_PATH = Path(__file__).parent / ".checkpoints" / "runtime.sqlite"


def open_sqlite_checkpointer(
    path: str | Path = DEFAULT_CHECKPOINT_PATH,
) -> tuple[SqliteSaver, sqlite3.Connection]:
    """Open a durable checkpointer and return its owned SQLite connection."""
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, check_same_thread=False)
    return SqliteSaver(connection), connection
