from abc import ABCMeta
from typing import Dict, List
from darc.darc.message import Message

class AbstractActor(metaclass=ABCMeta):
    def __init__(self):
        self._address_book: Dict[str, str] = dict()
        
    def recv(self):
        ...
        
    def send(self, message: Message):
        ...
        
    def spawn_new_actor(self):
        ...

    def process(self, data: str):
        return "process " + data