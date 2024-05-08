from typing import Any, Callable, Dict, List


class Node:
    _id_counter: int = 0
    message_handlers: Dict[str, List[Callable[..., Any]]] = (
        {}
    )  # Class-level attribute shared by all instances

    def __init__(self) -> None:
        self.id: int = Node._id_counter
        Node._id_counter += 1

    @classmethod
    def process(cls, message_type: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if message_type not in cls.message_handlers:
                cls.message_handlers[message_type] = []
            cls.message_handlers[message_type].append(func)
            return func

        return decorator

    def handle_message(
        self, message_type: str, *args: Any, **kwargs: Any
    ) -> Any:
        if message_type in self.message_handlers:
            for handler in self.message_handlers[message_type]:
                return handler(self, *args, **kwargs)
        raise ValueError(f"No handler for message type: {message_type}")
