from darc.darc.node import Node


class Filter(Node):
    def __init__(self, id):
        super().__init__(id)

    @Node.process("filter")
    def apply_filter(self, data):
        return f"Filtered data: {data}"
