"""多智能体角色包。四个纯独立 Agent：Planner / Predictor / Executor / Reviewer。

每个角色是一个"身份 + A2A 通信"的薄壳，只靠消息沟通；干活时统一调用
能力层（capabilities.act / planning / reviewing）和共享基础设施（world_model），
和单智能体共用同一份能力，不再各写一份执行/规划/评审逻辑。
"""

from .planner import Planner
from .predictor import Predictor
from .executor import Executor
from .reviewer import Reviewer

__all__ = ["Planner", "Predictor", "Executor", "Reviewer"]
