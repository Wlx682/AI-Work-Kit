"""统一行动空间入口。导入时自动注册所有工具。"""

from .file_ops import register_all as _reg_files
from .shell import register_all as _reg_shell

_reg_files()
_reg_shell()

from .registry import get_function, get_all_schemas, list_tools  # noqa: E402
