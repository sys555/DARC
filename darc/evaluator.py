from darc.darc.node import Node


class Evaluator(Node):
    def __init__(self, id=None, mode=None):
        super().__init__(id)
        self.mode = mode

    @Node.process("evaluate")
    def evaluate_data(self, message):
        # Example evaluation logic based on the mode
        if self.mode == "Attack":
            print(f"Evaluating data for vulnerabilities: {message['data']}")
        else:
            print(f"Evaluating data: {message['data']}")
