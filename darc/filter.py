from darc.darc.node import Node


class Filter(Node):
    def __init__(self) -> None:
        super().__init__()

    @Node.process("filter")
    def apply_filter(self, data: str) -> str:
        print(f"Filtering data: {data}")
        return f"Filtered data: {data}"
