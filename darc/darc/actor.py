from abc import ABCMeta
from typing import Dict, List, Union, Tuple, Set
import pykka
from .message import Message
from .multi_addr import MultiAddr


@pykka.traversable
class AbstractActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self._address_book: Set[str] = set()  # name -> addr
        self._instance = dict()  # addr
        self._message_box = []
        self._node_type = None
        self._node_addr = None
        self._node_alias = None

    def on_receive(self, message: Message):
        raise NotImplementedError

    def send(self, message: "Message", next_hop_address: List | str = []):
        if isinstance(next_hop_address, MultiAddr):
            self._instance[next_hop_address].send(message)

        else:
            for next_actor_instance_addr in next_hop_address:
                self._instance[next_actor_instance_addr].send(message)

    def spawn_new_actor(self, cls, args: Union[List, str]):
        raise NotImplementedError
