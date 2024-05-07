from darc.node import Node


class Evaluator(Node):
    def __init__(self, id, mode=None):
        super().__init__(id)
        self.mode = mode

    @Node.process("evaluate")
    def evaluate_data(self, data):
        return f"Evaluation in {self.mode} mode: {data}"
