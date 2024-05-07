from abc import ABCMeta
from typing import Dict


class AbstractActor(metaclass=ABCMeta):
    def __init__(self):
        self._address_book: Dict[str, str] = dict()
    
    def recv():
        raise NotImplementedError
    
    def send():
        raise NotImplementedError
    
    def spawn_new_actor():
        raise NotImplementedError
    
