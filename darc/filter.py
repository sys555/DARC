import logging
from typing import List

from darc.darc.message import Message
from darc.darc.node import Node


class ev(Node):
    def __init__(self) -> None:
        super().__init__()


class Filter(Node):
    def __init__(self) -> None:
        super().__init__()

    @Node.process(["Attacker:Filter", "DatasetDB:Filter"])
    def apply_filter(self, input_content: List[str]):
        # input_content有两个部分，分别是来自Attacker和来自DatasetDB的消息， Filter需要合并两个消息进行处理
        logging.info("apply filter")
        thres = 0.5
        Attacker_Q, Normal_Q = input_content[:2]
        if self.diff(Attacker_Q, Normal_Q) > thres:
            msg = Message(message_name="Filter:Attacker", content=Normal_Q)
        else:
            msg = Message(
                message_name="Filter:LLM_with_PPL", content=Attacker_Q
            )
        return [msg]

    def diff(self, A, B):
        # import random

        # return random.random()
        # TODO: Attacker:Filter, Filter:Attacker, Attacker:Filter 消息终止问题
        return 0.1
