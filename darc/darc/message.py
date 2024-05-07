from dataclasses import dataclass
import uuid


@dataclass
class Message:
    message_name: str
    message_id: uuid.uuid4 = "None"
    from_agent: str = "None"
    to_agent: str = "None"
    content: str = "None"
    task_id: str = "None"
    broadcasting: bool = True

    def __call__(
        self, message_id, from_agent, to_agent, content, task_id, broadcasting=True
    ):
        message_name = self.message_name
        return Message(
            message_name=message_name,
            message_id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            task_id=task_id,
            broadcasting=broadcasting,
        )
