from darc.darc.node import Node


class DatasetDB(Node):
    def __init__(self, db: str) -> None:
        super().__init__()
        self.db: str = db

    @Node.process("Attacker")
    def handle_query(self, query: str) -> str:
        return f"Normal for {query} from {self.db}"
