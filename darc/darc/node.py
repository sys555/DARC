from .actor import AbstractActor
from .message import Message
from typing import Dict, Set


class Node(AbstractActor):
    __instances__: Dict[str, "Node"] = dict()
    __first_init__: Set[str] = set()

    def __new__(cls, node_name, addr, *args, **kwargs):
        if addr not in cls.__first_init__:
            cls.__instances__[addr] = super().__new__(cls)
        return cls.__instances__[addr]

    def __init__(self, node_name, addr):
        if addr not in self.__first_init__:
            super().__init__()
            self._node_name = node_name
            self._addr = addr
            self.__first_init__.add(addr)

    def send(self, message: "Message"):
        pass

    def recv(self):
        pass

    def spawn_new_actor(self):
        pass

    @staticmethod
    def cast(message_type):
        def decorator(func):
            pass

        return decorator
