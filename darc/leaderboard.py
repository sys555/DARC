from typing import List

from darc.darc.node import Node


class LeaderBoard(Node):
    def __init__(self) -> None:
        super().__init__()
        self.leaderboard: List[str] = []

    @Node.process("update_leaderboard")
    def update_leaderboard(self, entry: str) -> str:
        print(f"Updating leaderboard with new entry: {entry}")
        self.leaderboard.append(entry)
        return f"Updated leaderboard: {self.leaderboard}"
