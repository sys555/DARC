from typing import List

from darc.darc.message import Message
from darc.darc.node import Node


class DatasetDB(Node):
    def __init__(self, db: str) -> None:
        super().__init__()
        self.db: str = db

    @Node.process(["Attacker:DatasetDB"])
    def handle_task(self, initial_data: List[str]):
        data = initial_data[0]
        message_attacker = Message(
            message_name="DatasetDB:Attacker",
            content=f"Query results for {data} from {self.db}",
        )
        message_filter = Message(
            message_name="DatasetDB:Filter",
            content=f"Query results for {data} from {self.db}",
        )
        message_evaluator = Message(
            message_name="DatasetDB:AttackEvaluator",
            content=f"Query results for {data} from {self.db}",
        )
        target = [message_attacker, message_filter, message_evaluator]
        return target
