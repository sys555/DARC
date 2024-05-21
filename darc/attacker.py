from typing import List

from darc.darc.message import Message
from darc.darc.node import Node


class Attacker(Node):
    @Node.process(["DatasetDB:Attacker"])
    def perform_attack(self, input_content: List[str]):
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        content = input_content[0]
        output_content = f"Attack on {content} completed, Dangerous Question1"
        msg = Message(message_name="Attacker:Filter", content=output_content)
        return [msg]

    @Node.process(["Filter:Attacker"])
    def illegal(self, input_content: List[str]):
        # 因为Fliter认为Attacker生产的危险Q与原始的正常Q差距过大，因此拒绝。
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        content = input_content[0]
        output_content = (
            f"Re-Attack on {content} completed, Dangerous Question1"
        )
        msg = Message(message_name="Attacker:Filter", content=output_content)
        return [msg]

    @Node.process(["Task:Attacker"])
    def handle_initial(self, initial_data: List[str]):
        content = initial_data[0]
        msg = Message(message_name="Attacker:DatasetDB", content=content)
        return [msg]
