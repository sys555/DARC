from darc.node import Node


class DatasetDB(Node):
    def __init__(self, id, db=None):
        super().__init__(id)
        self.database = db

    @Node.process("query")
    def execute_query(self, query_string):
        return f"Results for {query_string} from {self.database}"
