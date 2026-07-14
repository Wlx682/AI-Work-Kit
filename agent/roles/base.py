"""角色基类。所有 A2A 角色的共同能力：有名字、能往消息总线发消息。"""

from ..a2a import Message, MessageBus


class BaseAgent:
    """独立 Agent 基类。

    子类只需定义 name 和自己的职责方法（handle）。
    发消息统一走 send()，保证每次沟通都留痕。
    """

    name: str = "Agent"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    def send(self, recipient: str, intent: str, content: object):
        """向另一个 Agent 发消息（经总线留痕）。"""
        self.bus.send(Message(self.name, recipient, intent, content))
