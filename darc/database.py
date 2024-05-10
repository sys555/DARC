from typing import List, Optional

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
        output_content = self.excute_SQL(input_content)
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
    def handle_Evaluator_query(
        self, input_content: str
    ) -> Optional[Message]:  # 可能有返回值，也可能没有
        # input_content 是SQL query
        # output_content 是query的结果
        table = self.parse_SQL_content(input_content)
        if table == "Norlmal":
            output_content = self.excute_SQL(input_content)
            Message2Evaluator = Message(
                message_name="DatasetDB:Evaluator", content=output_content
            )
            return Message2Evaluator
        elif table == "Dangerous":
            self.excute_SQL(input_content)  # 直接执行SQL 无需返回值
        else:
            raise NotImplementedError

    def parse_SQL_content(self, content: str):
        # 解析SQL语句中访问的不同的table，执行不同的逻辑
        import numpy as np

        use_table = np.random.choice("Norlmal", "Dangerous")
        return use_table

    def excute_SQL(sql: str):
        # 假设这里有一段执行SQL的逻辑
        return f"result from {sql}"
