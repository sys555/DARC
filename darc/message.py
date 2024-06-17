import uuid
from dataclasses import dataclass
from typing import Union


@dataclass
class Message:
    message_name: str
    message_id: Union[uuid.UUID, str] = "None"
    from_agent: str = "None"
    to_agent: str = "None"
    content: str = "None"
    task_id: str = "None"
    from_agent_type: str = "None"
    from_node_type_name: str = "None"
    broadcasting: bool = True
    handle_name: str = "None"

    def __call__(
        self,
        message_id,
        from_agent,
        task_id,
        from_agent_type="RealNode",
        to_agent="None",
        content="None",
        from_node_type_name="None",
        broadcasting=True,
        handle_name="None",
    ):
        message_name = self.message_name
        return Message(
            message_name=message_name,
            message_id=message_id or str(uuid.uuid4()),
            from_agent=from_agent,
            from_agent_type=from_agent_type,
            to_agent=to_agent,
            content=content,
            task_id=task_id,
            broadcasting=broadcasting,
            from_node_type_name=from_node_type_name,
            handle_name=handle_name,
        )


def get_default_message():
    # defualt factory
    return Message(message_name="")
