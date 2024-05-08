from darc.darc.node import Node


class LeaderBoard(Node):
    def __init__(self, id=None):
        super().__init__(id)
        self.scores = {}

    @Node.process("update_scores")
    def update_scores(self, message):
        # Example logic for updating scores
        user_id = message["data"]["user_id"]
        score = message["data"]["score"]
        self.scores[user_id] = score
        print(f"Updated scores: {self.scores}")

    @Node.process("get_scores")
    def get_scores(self, message):
        # Example logic for retrieving scores
        print(f"Current scores: {self.scores}")
