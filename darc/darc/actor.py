from typing import List, Set, Union

import pykka

from .message import Message


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
        if isinstance(next_hop_address, str):
            self._instance[next_hop_address].tell(message)
        else:
            for next_actor_instance_addr in next_hop_address:
                self._instance[next_actor_instance_addr].tell(message)

    def spawn_new_actor(self, cls, args: Union[List, str]):
        raise NotImplementedError
