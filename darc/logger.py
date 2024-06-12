import json
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from darc.actor import AbstractActor
from darc.message import Message, get_default_message


class TaskStatus(Enum):
    CREATED = "C"
    IN_PROGRESS = "P"
    COMPLETED = "X"
    FAILED = "F"


@dataclass
class MASLog:
    node_name: str = field(default="")
    handle_name: str = field(default="")
    timestamp: str = field(default="")
    stage: TaskStatus = field(default=TaskStatus.CREATED)
    message: Message = field(default_factory=get_default_message)


def serialize_log(log: MASLog) -> str:
    try:
        # MASLog object -> JSON string
        log_dict = asdict(log)
        log_dict["stage"] = log.stage.name  # Enum -> name string
    except Exception as e:
        logger.error(f"logger, serialize_log, error: {type(e)}, {e}")
    return json.dumps(log_dict)


def deserialize_log(log_str: str) -> MASLog:
    try:
        # JSON string -> MASLog object
        log_data = json.loads(log_str)
        log_data["stage"] = TaskStatus[
            log_data["stage"]
        ]  # name string -> Enum
        message_data = log_data.get("message", {})
        log_data["message"] = Message(**message_data)
    except Exception as e:
        logger.error(f"logger, deserialize_log, error: {type(e)}, {e}")
    return MASLog(**log_data)


class MASLogger(AbstractActor):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self.logbook: List[MASLog] = []
            self.end_logbook: List[MASLog] = []
            self._initialized = True

    def on_receive(self, message: Message):
        self.log_message(message)

    def log_message(self, message: Message):
        try:
            log_entry = deserialize_log(message.content)
            if log_entry.message.message_name.split(":")[-1] == "END":
                self.end_logbook.append(log_entry)
            self.logbook.append(log_entry)
        except Exception as e:
            logger.error(f"logger, log_message, error: {type(e)}, {e}")

    def get_logs(
        self, task_id: Optional[str] = None, node_name: Optional[str] = None
    ) -> List[MASLog]:
        filtered_logs = [
            log
            for log in self.logbook
            if (task_id is None or log.message.task_id == task_id)
            and (node_name is None or log.node_name == node_name)
        ]
        return sorted(filtered_logs, key=lambda log: log.timestamp)

    def get_result(self, task_id: str = "") -> Optional[MASLog]:
        filtered_logs = [
            log
            for log in self.end_logbook
            if log is not None
            and (
                task_id == ""
                or (log.message is not None and log.message.task_id == task_id)
            )
        ]
        if not filtered_logs:
            return None
        return max(filtered_logs, key=lambda log: log.timestamp)
