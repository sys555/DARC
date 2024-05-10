from darc.darc.node import Node
from darc.darc.message import Message

class DatasetDB(Node):
    def __init__(self, db: str) -> None:
        super().__init__()
        self.db: str = db

    @Node.process("Attacker:DatasetDB")
    def handle_Attacker_query(self, query: str) -> str:
        result = f"Normal Q for {query} from {self.db}"
        Message2Attacker = Message(message_name='DatasetDB:Attacker', content=result)
        Message2Filter = Message(message_name='DatasetDB:Filter', content=result)
        msgs = []
        msgs.append(Message2Attacker)
        msgs.append(Message2Filter)
        return msgs
    