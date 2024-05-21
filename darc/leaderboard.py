import json
from typing import Dict, List

from loguru import logger

from darc.darc.node import Node


class LeaderBoard(Node):
    def __init__(self) -> None:
        super().__init__()
        self.leaderboard: List[Dict[str, str]] = []

    @Node.process(["AttackEvaluator:LeaderBoard"])
    def update_leaderboard(self, entry: List[str]) -> None:
        logger.info(entry)
        task_id = entry[-1]
        record: Dict[str, str] = json.loads(entry[0])
        record["task_id"] = task_id[:8]
        self.leaderboard.append(record)
        return
