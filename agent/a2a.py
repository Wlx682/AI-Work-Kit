"""A2A 消息协议。对应架构图「多智能体协作层」的通信基础。

多智能体之间不靠函数传参，而是靠「消息」沟通：
每条消息带 发信人 / 收信人 / 意图 / 内容，全部留痕，可回放。
这是 A2A（Agent to Agent）的核心——谁对谁说了什么，一目了然。
"""

from dataclasses import dataclass, field


@dataclass
class Message:
    """一条 A2A 消息。"""
    sender: str        # 发信 Agent 名
    recipient: str     # 收信 Agent 名
    intent: str        # 意图：plan / result / review / revise
    content: object     # 内容（字符串或结构化数据）


class MessageBus:
    """消息总线：承载所有 Agent 之间的消息，按时间留痕。"""

    def __init__(self):
        self.history: list[Message] = []

    def send(self, msg: Message):
        """投递一条消息，并打印留痕。"""
        self.history.append(msg)
        preview = str(msg.content)
        if len(preview) > 80:
            preview = preview[:80] + "..."
        print(f"   ✉️  {msg.sender} → {msg.recipient} [{msg.intent}]: {preview}")

    def last(self, intent: str | None = None, recipient: str | None = None) -> Message | None:
        """回看最近一条匹配的消息（按意图 / 收信人过滤）。"""
        for msg in reversed(self.history):
            if intent and msg.intent != intent:
                continue
            if recipient and msg.recipient != recipient:
                continue
            return msg
        return None

    def transcript(self) -> list[Message]:
        """返回完整对话记录，可回放。"""
        return list(self.history)
