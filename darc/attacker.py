from darc.darc.message import Message
from darc.darc.node import Node


class Attacker(Node):

    @Node.process(["DatasetDB:Attacker"])
    def perform_attack(self, input_content: str) -> Message:
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        output_content = (
            f"Attack on {input_content} completed, Dangerous Question1"
        )
        msg = Message(message_name="Attacker:Fliter", content=output_content)
        return msg

    @Node.process(["Fliter:Attacker"])
    def illegal(self, input_content: str) -> Message:
        # 因为Fliter认为Attacker生产的危险Q与原始的正常Q差距过大，因此拒绝。
        # input_content是从DB输入的正常Q的数据
        # output_content是通过正常的Q转化而来的异常Q
        output_content = (
            f"Re-Attack on {input_content} completed, Dangerous Question1"
        )
        msg = Message(message_name="Attacker:Fliter", content=output_content)
        return msg
