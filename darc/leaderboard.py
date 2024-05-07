from darc.node import Node
class LeaderBoard(Node):
    def __init__(self, id):
        super().__init__(id)
        self.scores = []

    @Node.process('update_scores')
    def update(self, score):
        self.scores.append(score)
        return f"Updated scores: {self.scores}"

    @Node.process('get_top')
    def get_top_scores(self, n=5):
        return sorted(self.scores, reverse=True)[:n]
