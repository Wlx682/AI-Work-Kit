"""Local HTTP adapter and command-line entry point for the learning backend."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from ..application.service import LearningApiError, LearningApiService
from ..config import load_environment


def make_learning_api_handler(service: LearningApiService):
    """Create a request handler class bound to one application service."""

    class LearningApiHandler(BaseHTTPRequestHandler):
        server_version = "NexusLearningApi/1.0"

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send(204, None)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/api/learning/health":
                self._send(200, {"status": "ok", "service": "knowledge-graph-learning"})
                return
            prefix = "/api/learning/courses/"
            if path.startswith(prefix):
                course_path = path[len(prefix):]
                recommendation_suffix = "/recommendation"
                if course_path.endswith(recommendation_suffix):
                    course_id = course_path[:-len(recommendation_suffix)]
                    self._dispatch(lambda: service.get_recommendation(course_id))
                    return
                self._dispatch(lambda: service.get_course(course_path))
                return
            self._send_error(LearningApiError("NOT_FOUND", "route not found", 404))

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                body = self._read_json()
            except LearningApiError as error:
                self._send_error(error)
                return
            routes: dict[str, Callable[[], dict[str, Any]]] = {
                "/api/learning/goals": lambda: service.create_goal(body.get("title")),
                "/api/learning/sessions": lambda: service.start_session(
                    body.get("course_id"), body.get("node_id")
                ),
                "/api/learning/evidence": lambda: service.submit_evidence(
                    body.get("session_id"), body.get("answer")
                ),
                "/api/learning/reviews": lambda: service.review_graph_update(
                    body.get("thread_id"),
                    body.get("parent_run_id"),
                    body.get("course_id"),
                    body.get("approved"),
                ),
            }
            operation = routes.get(path)
            if operation is None:
                self._send_error(LearningApiError("NOT_FOUND", "route not found", 404))
                return
            self._dispatch(operation, 201 if path == "/api/learning/goals" else 200)

        def _dispatch(
            self,
            operation: Callable[[], dict[str, Any]],
            success_status: int = 200,
        ) -> None:
            try:
                self._send(success_status, operation())
            except LearningApiError as error:
                self._send_error(error)
            except Exception as error:  # pragma: no cover - defensive boundary
                self._send_error(LearningApiError("INTERNAL_ERROR", str(error), 500))

        def _read_json(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                value = json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, json.JSONDecodeError) as error:
                raise LearningApiError("INVALID_JSON", "request body must be JSON") from error
            if not isinstance(value, dict):
                raise LearningApiError("INVALID_JSON", "request body must be an object")
            return value

        def _send_error(self, error: LearningApiError) -> None:
            self._send(
                error.status,
                {"error": {"code": error.code, "message": error.message}},
            )

        def _send(self, status: int, payload: dict[str, Any] | None) -> None:
            body = b"" if payload is None else json.dumps(
                payload, ensure_ascii=False
            ).encode("utf-8")
            self.send_response(status)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            if payload is not None:
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return LearningApiHandler


def serve(host: str, port: int, data_directory: str | Path) -> None:
    service = LearningApiService(data_directory)
    server = ThreadingHTTPServer((host, port), make_learning_api_handler(service))
    print(f"Knowledge Graph Learning API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        service.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the learning system API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--data-dir",
        default=".runtime/knowledge-graph-learning",
    )
    parser.add_argument(
        "--env-file",
        help="dotenv file to load; defaults to the repository root .env",
    )
    arguments = parser.parse_args()
    environment_path = load_environment(arguments.env_file)
    if os.environ.get("DEEPSEEK_API_KEY"):
        print("DeepSeek configuration loaded.")
    else:
        print(
            "Warning: DEEPSEEK_API_KEY is missing; checked process environment "
            f"and {environment_path}"
        )
    serve(arguments.host, arguments.port, arguments.data_dir)


if __name__ == "__main__":
    main()
