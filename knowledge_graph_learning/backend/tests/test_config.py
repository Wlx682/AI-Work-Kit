"""Tests for local backend configuration loading."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from knowledge_graph_learning.backend.config import load_environment


class EnvironmentConfigTests(unittest.TestCase):
    def test_loads_deepseek_key_from_explicit_env_file(self):
        with TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("DEEPSEEK_API_KEY=from-file\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                loaded_path = load_environment(env_file)

                self.assertEqual(loaded_path, env_file.resolve())
                self.assertEqual(os.environ["DEEPSEEK_API_KEY"], "from-file")

    def test_process_environment_takes_precedence_over_env_file(self):
        with TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("DEEPSEEK_API_KEY=from-file\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {"DEEPSEEK_API_KEY": "from-process"},
                clear=True,
            ):
                load_environment(env_file)

                self.assertEqual(os.environ["DEEPSEEK_API_KEY"], "from-process")


if __name__ == "__main__":
    unittest.main()
