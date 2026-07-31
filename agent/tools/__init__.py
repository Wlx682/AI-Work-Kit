"""统一行动空间入口。导入时自动注册所有工具。"""

from .file_ops import register_all as _reg_files
from .shell import register_all as _reg_shell

_reg_files()
_reg_shell()

from .registry import (  # noqa: E402
    get_all_schemas,
    get_function,
    get_output_schema,
    list_tools,
    validate_tool_result,
)
