from abc import ABCMeta
from typing import Dict


class AbstractActor(metaclass=ABCMeta):
    def __init__(self):
        self._address_book = dict()

    def recv(self):
        raise NotImplementedError

    def send(self):
        raise NotImplementedError

    def spawn_new_actor(self, args_list):
        raise NotImplementedError
