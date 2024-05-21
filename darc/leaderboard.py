import json
from typing import List

from darc.darc.node import Node


class LeaderBoard(Node):
    def __init__(self) -> None:
        super().__init__()
        self.leaderboard: List[List[str]]

    @Node.process(["AttackEvaluator:LeaderBoard"])
    def update_leaderboard(self, entry: List[str]) -> None:
        entry = json.loads(entry[0])
        self.leaderboard.append(entry)
        return
