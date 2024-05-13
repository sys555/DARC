from abc import ABCMeta
from typing import Dict
import pykka
from darc.darc.message import Message
import logging

@pykka.traversable
class AbstractActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self.address_book: Dict[str, str] = dict()    # name -> addr
        self.instance: Dict[str, pykka.ThreadingActor] = dict() # addr -> pykka actor_ref
        self.message_box = []
        
    def on_receive(self, message: Message):
        self.message_box.append(message)
        ## user defined process & call send
        ...

    def send(self, message):
        if message.to_agent in self.address_book and self.address_book[message.to_agent] in self.instance:
            self.instance[self.address_book[message.to_agent]].tell(message)
        else:
            ...

    def spawn_new_actor(self):
        raise NotImplementedError
