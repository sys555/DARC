import logging
from typing import List, Set, Union

import pykka
from loguru import logger

from darc.message import Message
from darc.multi_addr import MultiAddr


@pykka.traversable
class AbstractActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self._address_book: Set[str] = set()  # name -> addr
        self.instance = dict()  # addr
        self.message_box = []
        self._node_type = None
        self.node_addr = None
        self._node_alias = None

    def on_receive(self, message: Message):
        self.message_box.append(message)

    def send(self, message: "Message", next_hop_address):
        try:
            if isinstance(next_hop_address, MultiAddr):
                self.instance[next_hop_address].tell(message)

            elif isinstance(next_hop_address, str):
                self.instance[next_hop_address].tell(message)

            else:
                for next_actor_instance_addr in next_hop_address:
                    self.instance[next_actor_instance_addr].tell(message)
        except BaseException as e:
            logging.error(f"AbsActor send: {type(e)}, {str(e)}")

    def spawn_new_actor(self, cls, args: Union[List, str]):
        raise NotImplementedError
