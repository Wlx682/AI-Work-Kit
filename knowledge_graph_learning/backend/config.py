"""Local configuration loading for the learning backend."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = REPOSITORY_ROOT / ".env"


def load_environment(env_file: str | Path | None = None) -> Path:
    """Load local secrets without overriding an existing process environment."""
    path = DEFAULT_ENV_FILE if env_file is None else Path(env_file).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    load_dotenv(dotenv_path=path, override=False)
    return path
