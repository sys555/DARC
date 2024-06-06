from darc.node import Node
from darc.message import Message
from darc.multi_addr import MultiAddr

from typing import List

import random

from loguru import logger


class Producer(Node):
    def __init__(self, node_addr=None, node_name="") -> None:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["Consumer:Producer"])
    def transport(self, message: List[Message]) -> str:
        valid_message = message[0]
        message_to_consumer = Message(
            message_name="Producer:Consumer", content=valid_message.content
        )
        msgs = []
        msgs.append(message_to_consumer)
        return msgs


class Consumer(Node):
    def __init__(self, node_addr=None, node_name="") -> None:
        super().__init__(node_addr=node_addr, node_name=node_name)

    @Node.process(["Producer:Consumer"])
    def act(self, message: List[Message]) -> str:
        return [self.consume()]

    def consume(self):
        return Message(
            message_name="Consumer:Producer",
            content=random.randint(1, 100),
        )


def compare_messages(message_box, mock_message):
    # 遍历列表中的所有消息
    for message in message_box:
        # 将每个消息的属性字典与 mock_message 的属性字典进行比较
        message_vars = vars(message)
        mock_message_vars = vars(mock_message)

        # 检查两个消息的属性是否完全相同
        if message_vars == mock_message_vars:
            return True  # 找到一个相同的消息，返回 True

    # 如果遍历结束后没有找到任何相同的消息，返回 False
    return False
