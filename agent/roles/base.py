"""角色基类。角色只持有身份定义，不承担 Team 的路由职责。"""

from ..core.definition import AgentDefinition, load_agent_definition


class BaseAgent:
    """独立 Agent 基类。

    子类只需定义 name 和自己的职责方法。
    角色间的路由和交接留痕由 Team Graph 负责。
    """

    name: str = "Agent"
    definition_id: str = ""

    def __init__(self, definition: AgentDefinition | None = None):
        self.definition = definition or load_agent_definition(self.definition_id)
