from abc import ABCMeta
from typing import Dict
import pykka
from darc.darc.message import Message
import logging

class AbstractActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self._address_book: Dict[str, str] = dict()    # name -> addr
        self._instance: Dict[str, pykka.ThreadingActor] = dict() # addr -> pykka actor_ref
        self._message_box = []
        
    def on_receive(self, message):
        if message.to_agent in self._address_book:
            self.send(self._instance[self._address_book[message.to_agent]], message)
        else:
            ...

    def send(self, to_agent, message):
        to_agent.tell(message)

    def spawn_new_actor(self):
        raise NotImplementedError
