from darc.darc.node import Node


class Filter(Node):
    @Node.process("filter")
    def apply_filter(self, message):
        print("Applying filter to:", message["data"])
