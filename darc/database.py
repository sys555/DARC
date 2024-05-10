from typing import List

from darc.darc.message import Message
from darc.darc.node import Node


class DatasetDB(Node):
    def __init__(self, db: str) -> None:
        super().__init__()

    @Node.process("Attacker:DatasetDB")
    def handle_Attacker_query(self, input_content: str) -> List[Message]:
        # input_content 是正常Q的SQL query
        # output_content是DB中的正常Q
        msgs = []
        table = "NormalQ"
        output_content = f"Normal Q for {input_content} from {table}"
        Message2Attacker = Message(
            message_name="DatasetDB:Attacker", content=output_content
        )
        Message2Filter = Message(
            message_name="DatasetDB:Filter", content=output_content
        )
        msgs.append(Message2Attacker)
        msgs.append(Message2Filter)
        return msgs

    @Node.process("Evaluator:DatasetDB")
    def handle_Evaluator_query(self, input_content: str) -> Message:
        # input_content 是危险QA对应的正常A的SQL query，根据id进行匹配
        # output_content 是DB中对应的正常A
        if 
        table = "Normal_A"
        output_content = f"Normal A for {input_content} from {table}"
        Message2Evaluator = Message(
            message_name="DatasetDB:Evaluator", content=output_content
        )
        return Message2Evaluator

    def parse_SQL_content(content:str):
        use_table = ("Norlmal_A", "Dang")