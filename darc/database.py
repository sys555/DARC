from darc.darc.node import Node


class DatasetDB(Node):
    def __init__(self, db):
        super().__init__()
        self.db = db

    @Node.process("query")
    def handle_query(self, query):
        print(f"Handling query in {self.db}: {query}")
        return f"Query results for {query} from {self.db}"
