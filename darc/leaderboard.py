from typing import List

from darc.darc.node import Node


class LeaderBoard(Node):
    def __init__(self) -> None:
        super().__init__()
        self.leaderboard: List[str] = []

    @Node.process(["Evaluator:LeaderBoard"])
    def update_leaderboard(self, entry: str) -> None:
        score_record = f"Updating leaderboard with new entry: {entry}"
        self.leaderboard.append(score_record)
